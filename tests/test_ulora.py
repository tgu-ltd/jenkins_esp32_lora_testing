import subprocess
import pytest


@pytest.mark.run(after='test_firmware_loaded')
def test_lora_uploaded():
    rshell_completed = False
    rshell_cmd = [
        'rshell', '-p', '/dev/ttyUSB0', '--baud', '115200',
        '-f', './rshell/lora.rshell'
    ]
    cmd = subprocess.run(rshell_cmd, stdout=subprocess.PIPE)
    if cmd.returncode == 0:
        rshell_completed = True

    assert(rshell_completed is True)


@pytest.mark.run(after='test_lora_uploaded')
def test_lora_chirp_output_file():

    expected_lines = 10
    correct_sequence = 0
    with open('./archive/lora_output.txt', 'r') as f:
        for i, line in enumerate(f.readlines()):
            if '{0} RSSI:'.format(i) in line:
                correct_sequence += 1
            else:
                break

    assert(correct_sequence == expected_lines)
