import time
from sx127x import SX127x
from controller_esp32 import ESP32Controller


def get_lora():
    ''' Setup and return a LoRa Esp32 controller'''
    params = {
        'frequency': 868E6,  # 169E6, 433E6, 434E6, 866E6, 868E6*, 915E6
        'tx_power_level': 5,  # 2
        'signal_bandwidth': 20.8E3,  # 7.8E3, 10.4E3, 15.6E3, 20.8E3, 31.25E3, 41.7E3, 62.5E3, 125E3*, 250E3
        'spreading_factor': 5,
        'coding_rate': 5,
        'preamble_length': 12,
        'implicitHeader': False,
        'sync_word': 0x12,
        'enable_CRC': False
    }
    controller = ESP32Controller()
    return controller.add_transceiver(
        SX127x(name='LoraTx', parameters=params),
        pin_id_ss=ESP32Controller.PIN_ID_FOR_LORA_SS,
        pin_id_RxDone=ESP32Controller.PIN_ID_FOR_LORA_DIO0
    )


def main():
    ''' Send 10 LoRa Chirps out and write to file '''
    output = []
    loop = range(10)
    lora = get_lora()
    for i in loop:
        payload = "{0}".format(i)
        lora.println(payload)
        rssi = '{0} RSSI: {1}\n'.format(payload, lora.packetRssi())
        output.append(rssi)
        time.sleep(1)
    with open('./lora_output.txt', 'w') as f:
        f.write(''.join(output))


if __name__ in ['__main__', 'main']:
    main()
