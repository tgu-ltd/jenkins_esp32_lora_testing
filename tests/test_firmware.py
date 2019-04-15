import os
import re
import glob
import subprocess
import urllib.request
from bs4 import BeautifulSoup

VERSION = ''

def test_firmware_directory_exists():
    ''' Do we have a firmware directory to store and retrive firmware bins from '''
    assert(os.path.isdir("firmware") is True)


def test_latest_firmware_version():
    ''' Get/Find the latest firmware version '''
    global VERSION

    downloaded = True
    firmware_downloaded = False
    url = 'https://micropython.org/download'
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page.read(), 'html.parser')
    href = soup.findAll('a', text=re.compile('esp32-'))[1]  # Get the second firware version
    download_url = '{0}{1}'.format(url.replace('/download', ''), href['href'])
    bins = glob.glob('firmware/*.bin')
    VERSION = href.contents[0]

    # Do we already have the firmware?
    for name in bins:
        if VERSION in name:
            firmware_downloaded = True
            break

    # If not download it
    if not firmware_downloaded:
        of = '-Ofirmware/{0}'.format(VERSION)
        sp = subprocess.run(['wget', of, download_url], stdout=subprocess.PIPE)
        if sp.returncode != 0:
            downloaded = False

    assert(downloaded is True)


def test_flash_firmware():
    global VERSION
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
            './firmware/{0}'.format(VERSION)
        ]
        cmd = subprocess.run(flash, stdout=subprocess.PIPE)
        if cmd.returncode == 0:
            flashed = True
    assert(flashed is True)
