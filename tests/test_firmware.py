import os
import re
import glob
import subprocess
import urllib.request
from bs4 import BeautifulSoup

DOWNLOADED_VERSION = ''


def test_firmware_directory_exists():
    ''' Do we have a firmware directory to store and retrive firmware bins from '''
    assert(os.path.isdir("firmware") is True)


def test_latest_firmware_version():
    ''' Get/Find the latest firmware version '''
    global DOWNLOADED_VERSION

    downloaded = True
    firmware_downloaded = False
    url = 'https://micropython.org/download'
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page.read(), 'html.parser')
    hrefs = soup.findAll('a', text=re.compile('esp32-'))

    href = ''
    # Find the nightly build, at the moment it is the one with more hyphens
    for ref in hrefs:
        if ref.contents[0].count('-') > 2:
            href = ref
            break

    download_url = '{0}{1}'.format(url.replace('/download', ''), href['href'])
    bins = glob.glob('firmware/*.bin')
    DOWNLOADED_VERSION = href.contents[0]

    # Do we already have the firmware already?
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


def test_flash_firmware():
    global DOWNLOADED_VERSION
    flashed = False

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


def test_firmware_loaded():
    got_version_file = False
    version_uploaded = False
    copy_write_copy = [
        'rshell', '-p', '/dev/ttyUSB0', '--baud', '115200',
        '-f', './rshell/get_version.rshell'
    ]
    cmd = subprocess.run(copy_write_copy, stdout=subprocess.PIPE)
    if cmd.returncode == 0:
        got_version_file = True

    with open('./archive/firmware_version.txt') as f:
        version = ''.join(f.readlines())
        if ("sysname='esp32'" in version) and ("release" in version):
            version_uploaded = True

    assert(got_version_file is True)
    assert(version_uploaded is True)
