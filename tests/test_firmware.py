import os
import re
import glob
import pytest
import subprocess
import urllib.request
from bs4 import BeautifulSoup

DOWNLOADED_VERSION = ''


@pytest.mark.run(order=1)
def test_firmware_directory_exists():
    ''' Do we have a firmware directory to store and retrieve firmware bins from '''
    assert(os.path.isdir("firmware") is True)


@pytest.mark.run(after='test_firmware_directory_exists')
def test_latest_firmware_version():
    ''' Get/Find the latest firmware version '''
    global DOWNLOADED_VERSION

    downloaded = True
    firmware_downloaded = False

    # Download the latest firmware version if we do not have a copy already
    url = 'https://micropython.org/download'
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page.read(), 'html.parser')
    hrefs = soup.findAll('a', text=re.compile('esp32-'))

    # Find the nightly build. We determine this by using the name
    # with more hyphens in it. This is prone to change
    href = ''
    for ref in hrefs:
        if ref.contents[0].count('-') > 2:
            href = ref
            break

    DOWNLOADED_VERSION = href.contents[0]
    download_url = '{0}{1}'.format(url.replace('/download', ''), href['href'])
    bins = glob.glob('firmware/*.bin')

    # Do we already have the firmware?
    for name in bins:
        if DOWNLOADED_VERSION in name:
            firmware_downloaded = True
            break

    # If not downloaded download it
    if not firmware_downloaded:
        of = '-Ofirmware/{0}'.format(DOWNLOADED_VERSION)
        sp = subprocess.run(['wget', of, download_url], stdout=subprocess.PIPE)
        if sp.returncode != 0:
            downloaded = False

    assert(downloaded is True)


@pytest.mark.run(after='test_latest_firmware_version')
def test_flash_firmware():
    global DOWNLOADED_VERSION

    flashed = False

    # Flash the esp32 device with the firmware
    erase = [
        'esptool.py', '-p', '/dev/ttyUSB0',
        '--baud', '115200', '--after', 'no_reset', 'erase_flash'
    ]
    cmd = subprocess.run(erase, stdout=subprocess.PIPE)
    if cmd.returncode == 0:
        flash = [
            'esptool.py', '--chip', 'esp32', '-p', '/dev/ttyUSB0',
            '--baud', '115200', 'write_flash', '-z', '--flash_mode', 'dio',
            '--flash_freq', '40m', '--flash_size', '4MB', '0x1000',
            './firmware/{0}'.format(DOWNLOADED_VERSION)
        ]
        cmd = subprocess.run(flash, stdout=subprocess.PIPE)
        if cmd.returncode == 0:
            flashed = True
    assert(flashed is True)


@pytest.mark.run(after='test_flash_firmware')
def test_firmware_loaded():
    global DOWNLOADED_VERSION

    rshell_completed = False
    firmware_uploaded = False

    # Use rshell to copy the firmware_version.py code to the esp32 and
    # execute it so the output can be copied back for the tests to examine

    rshell_cmd = [
        'rshell', '-p', '/dev/ttyUSB0', '--baud', '115200',
        '-f', './rshell/get_version.rshell'
    ]
    cmd = subprocess.run(rshell_cmd, stdout=subprocess.PIPE)
    if cmd.returncode == 0:
        rshell_completed = True

    # Shorten the downloaded version name
    version = DOWNLOADED_VERSION[DOWNLOADED_VERSION.rindex('-'):].replace('.bin', '')

    # Look for the downloaded version name in the outputted file from the esp32 device
    with open('./archive/firmware_version.txt') as f:
        esp32_output = ''.join(f.readlines())
        if version in esp32_output:
            firmware_uploaded = True

    assert(rshell_completed is True)
    assert(firmware_uploaded is True)
