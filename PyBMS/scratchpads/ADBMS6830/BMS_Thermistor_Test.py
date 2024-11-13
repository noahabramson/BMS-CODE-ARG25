from Engine.BMS import BMS
from Engine.Devices.ADBMS6830 import ADBMS6830
from Engine.Interfaces.USB_TO_SPI_BYTE import USB_TO_SPI_BYTE
import Engine.plthelper as plthelper
import time

##MASTER INTIATES START -> SENDS ADDRESS (7-bit) and R/W (1-bit)

def main():
    interface = USB_TO_SPI_BYTE('COM3', 115200, stdout=False)
    bms = BMS(interface)
    board_list = [{'Device': ADBMS6830},{'Device': ADBMS6830}]

    delay_between_measurements = 5
    device = [0, 1]

    loops = 1

    slave_address = 0b11001010 #last zero is to make it eight bits
    slave_read_bit = 0b00000001
    slave_write_bit = 0b00000000

    HS_MASTER_CODE = 0b00001111 # last 3 don't matter

    setup_byte = 0b10000010  #
    config_byte = 0b01100001 # REG,SCAN1,SCAN0, CS[3:0],






    setup_list = [
        {"command": "$SPI_WAKEUP$", "arguments": {"Wakeup Time": 400}},
        {"command": "$DELAY_MS$", "arguments": {"Delay": 10}},
        {"command": "$SPI_WAKEUP$", "arguments": {"Wakeup Time": 10}},
        {"command": "WRCOMM", "arguments": {"D0": slave_address+slave_write_bit, # D0 is the address byte, contains address of mux and R/W bit
                                            "ICOM0": 0b0110, #ICOM0 contains the start signal
                                            "FCOM0": 0b0000, #and FCOM0 will have the master generate an acknowledge signal
                                            "D1": setup_byte, "D2": config_byte,
                                            "ICOM1": 0b0000, "FCOM1": 0b0000,
                                            "ICOM2": 0b0000, "FCOM2": 0b0000
        }},
        {"command": "$DELAY_MS$", "arguments": {"Delay": 10}},
        {"command": "$SPI_WAKEUP$", "arguments": {"Wakeup Time": 10}},
    ]

    init_list = [
        {"command": "STCOMM"}, #send address, setup, and config
        {"command": "$DELAY_MS$", "arguments": {"Delay": 100}},
        {"command": "WRCOMM", "arguments": {"ICOM0": 0b0001, #ICOM0 contains the start signal
                                            "ICOM1": 0b0110,
                                            "ICOM2": 0b0111,
                                            "D1": slave_address+slave_read_bit,
        }},
        {"command": "STCOMM"},  # send address, setup, and config
        {"command": "$DELAY_MS$", "arguments": {"Delay": 100}},
        {"command": "SNAP"},
        {"command": "RDCOMM", "map_key": "val"},
        {"command": "UNSNAP"},
    ]

    # Setup chip
    _ = bms.run_generic_command_list(setup_list, board_list)
    # Do first read from chip
    results = bms.run_generic_command_list(init_list, board_list)
    interface.close()

    therm_raw = results['val'][1]["D1"]
    print(therm_raw)

if __name__ == "__main__":
    main()