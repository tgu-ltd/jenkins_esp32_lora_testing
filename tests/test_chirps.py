import subprocess
import pytest
import time
import os


@pytest.mark.second_to_last
def test_sdr_listen_for_silence():
    ''' Test that the SDR is receiving nothing with squelch set to 10 '''
    output_file = './archive/silence.raw'

    os.system('rtl_fm -l 10 -s 38400 -f 868.00M -g 0 | tee {0} 2>&1 1>/dev/null &'.format(output_file))
    time.sleep(15)
    os.system('pkill -9 rtl_fm')
    file_size = os.path.getsize(output_file)
    assert(file_size <= 0)


@pytest.mark.last
def test_sdr_listen_for_lora_chirp():
    ''' Test the SDR is receiving the lora chirp with squelch set to 10'''
    chirped = False
    output_file = './archive/chirp.raw'

    os.system('rtl_fm -l 10 -s 38400 -f 868.00M -g 0 | tee {0} 2>&1 1>/dev/null &'.format(output_file))
    rshell_cmd = [
        'rshell', '-p', '/dev/ttyUSB0', '--baud', '115200', '-f', './rshell/lora.rshell'
    ]
    rtn = subprocess.run(rshell_cmd, stdout=subprocess.PIPE)
    if rtn.returncode == 0:
        chirped = True
    os.system('pkill -9 rtl_fm')
    file_size = os.path.getsize(output_file)
    assert(chirped is True)
    assert(file_size > 800000)
