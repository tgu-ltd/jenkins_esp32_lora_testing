import time
from lora.sx127x import SX127x
from lora.controller_esp32 import ESP32Controller


def get_lora():
    params = {
        'frequency': 868E6,  # 169E6, 433E6, 434E6, 866E6, 868E6*, 915E6
        'tx_power_level': 2,  # 2
        'signal_bandwidth': 125E3,  # 7.8E3, 10.4E3, 15.6E3, 20.8E3, 31.25E3, 41.7E3, 62.5E3, 125E3*, 250E3
        'spreading_factor': 8,
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
    lora = get_lora()
    for i in range(10):
        payload = "{0}".format(i)
        lora.println(payload)
        with open('lora_output.txt', 'w') as f:
            f.write("{0} RSSI: {1}".format(payload, lora.packetRssi()))
        time.sleep(1)


if __name__ == '__main__':
    main()
