

interface = USB_TO_SPI_BYTE('COM4', 115200, stdout=False)
bms = BMS(interface)
board_list = [{'Device': ADBMS6830}]

#{'command': 'The name of the command', "arguments": {the bitfields that can be selected,
# for example 'CONT': True, "map_key": "the key where the results are written to"}},
