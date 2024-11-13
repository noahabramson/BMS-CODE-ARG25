from Engine.BMS import BMS
from Engine.Devices.ADBMS6830 import ADBMS6830
from Engine.Interfaces.USB_TO_SPI_BYTE import USB_TO_SPI_BYTE
import Engine.plthelper as plthelper
import time


def main():
    interface = USB_TO_SPI_BYTE('COM3', 115200, stdout=False)
    bms = BMS(interface)
    board_list = [{'Device': ADBMS6830}]

    delay_between_measurements = 8  # in ms
    device = 0  # Only 1 device in the chain


    init_list = [
        {"command": "$SPI_WAKEUP$", "arguments": {"Wakeup Time": 400}},
        {"command": "$DELAY_MS$", "arguments": {"Delay": 10}},
        {"command": "$SPI_WAKEUP$", "arguments": {"Wakeup Time": 10}},
        {"command": "WRCFGA", "arguments": {"REFON": True, 'FC': 7}},

        {"command": "WRCFGB", "arguments": {"VOV": 959, "VUV": 543}}, # 3.8 and 2.8 V

        # Activate ADC Cell and ADC Spins
        {"command": "ADCV", "arguments": {"CONT": True}},
        # Give some time to startup the adc's
        {"command": "$DELAY_MS$", "arguments": {"Delay": 10}},
        {"command": "$SPI_WAKEUP$", "arguments": {"Wakeup Time": 10}},
    ]

    loop_list = [
        # Stop updating registers
        {"command": "SNAP"},
        # Read Cells
        {"command": "RDCVA", "map_key": "val"},
        {"command": "RDCVB", "map_key": "val"},
        {"command": "RDCVC", "map_key": "val"},
        {"command": "RDCVD", "map_key": "val"},
        {"command": "RDCVE", "map_key": "val"},
        {"command": "RDCVF", "map_key": "val"},
        {"command": "RDFCA", "map_key": "val"},
        {"command": "RDFCB", "map_key": "val"},
        {"command": "RDFCC", "map_key": "val"},
        {"command": "RDFCD", "map_key": "val"},
        {"command": "RDFCE", "map_key": "val"},
        {"command": "RDFCF", "map_key": "val"},
        {"command": "RDACA", "map_key": "val"},
        {"command": "RDACB", "map_key": "val"},
        {"command": "RDACC", "map_key": "val"},
        {"command": "RDACD", "map_key": "val"},
        {"command": "RDACE", "map_key": "val"},
        {"command": "RDACF", "map_key": "val"},
        {"command": "RDSVA", "map_key": "val"},
        {"command": "RDSVB", "map_key": "val"},
        {"command": "RDSVC", "map_key": "val"},
        {"command": "RDSVD", "map_key": "val"},
        {"command": "RDSVE", "map_key": "val"},
        {"command": "RDSVF", "map_key": "val"},

        {"command": "RDSTATD", "map_key": "val"},
        {"command": "RDCFGB", "map_key": "val"},

        # Release registers
        {"command": "UNSNAP"},
        {"command": "$DELAY_MS$", "arguments": {"Delay": delay_between_measurements}},
    ]

    _ = bms.run_generic_command_list(init_list, board_list)
    counter = 0
    while(1):
        results = bms.run_generic_command_list(loop_list, board_list)
        OV_C1 = results['val'][device]["C1OV"]
        UV_C1 = results['val'][device]["C1UV"]
        VUV = results['val'][device]["VUV"]
        VOV = results['val'][device]["VOV"]
        print("VUV: " + str(VUV))
        print("VOV: " + str(VOV))



        print(OV_C1)
        print(UV_C1)
        if(OV_C1):
            print("OV FAULT!")
            break
        elif(UV_C1):
            print("UV FAULT!")
            break
        counter += 1
        print("counter: " + str(counter))

    interface.close()

if __name__ == "__main__":
    main()