"""
this is the main script for rev0 module testing and will output at a GPIO if there's a fault
The fault is defined as active low
Known issues:
print_battery_pack function causes so many errors (good idea in concept but need to figure out a better solution)
fault_list stuff needs a solution as written in
no print for thermistors in pack

Potential issues:
modulus setup in if elif statements for voltage list generation
The if-else may be able to be removed entirely if anyone has a smart solution for this
"""

from Engine.BMS import BMS
from Engine.Devices.ADBMS6830 import ADBMS6830
#from Engine.Interfaces.USB_TO_SPI_BYTE import USB_TO_SPI_BYTE
from Engine.Interfaces.Virtual_SPI import Virtual_SPI
import matplotlib.pyplot as plt
import Engine.plthelper as plthelper
import numpy as np
import time
import threading


def print_battery_pack(voltage_list):
    # Set up the plot with a larger figure size for better readability
    fig, ax = plt.subplots(figsize=(27, 8))  # Adjust width to ensure cells are wide enough
    im = ax.imshow(voltage_list, cmap="coolwarm", aspect="auto", vmin=3.0, vmax=4.2)
    cbar = plt.colorbar(im, label="Voltage (V)")

    # Add labels
    ax.set_title("Battery Pack Cell Voltages")
    ax.set_xlabel("Cell Number (Columns)")
    ax.set_ylabel("Module (Rows)")

    # Display values in cells, rotated vertically
    text_annotations = [[ax.text(j, i, f"{voltage_list[i, j]:.3f} V",
                                 ha="center", va="center", color="black", fontsize=10, rotation=90)
                         # Rotate text 90 degrees
                         for j in range(voltage_list.shape[1])] for i in range(voltage_list.shape[0])]

    # Function to update the plot in a separate thread
    def update_plot():
        while True:
            # Update cell voltages with new data (replace with actual data collection code)
            voltage_list[:] = np.random.uniform(3.0, 4.2, size=(6, 23))  # Simulated update

            # Update the heatmap and text annotations without creating new objects
            im.set_data(voltage_list)
            for i in range(voltage_list.shape[0]):
                for j in range(voltage_list.shape[1]):
                    text_annotations[i][j].set_text(f"{voltage_list[i, j]:.3f} V")  # Update with 3 decimal places

            # Refresh plot with minimal processing
            fig.canvas.draw_idle()  # Schedule a redraw to reduce resource usage
            plt.pause(0.1)  # Small pause to process events and reduce CPU usage

    # Start the plot update in a background thread
    plot_thread = threading.Thread(target=update_plot, daemon=True)
    plot_thread.start()
    """
    # Main program loop (demonstration) - this loop can continue indefinitely
    while True:
        # Perform other tasks here
        print("Main program is running without delay...")
        time.sleep(0.5)  # Simulating other operations in the main program
    """

def voltage_to_temp(gpio_voltage):
    temp = gpio_voltage * 10  #not correct at all
    return temp


def main():
    RUN_ALWAYS = True  ## THIS IS A USELESS VARIABLE atm

    bms_fault = 0
    CI_fault = 0
    OV_fault = 0
    UV_fault = 0
    OT_fault = 0
    UT_fault = 0
    OW_fault = 0

    module_series = 23  # either 16 or 23

    module_count = 6  # should ideally be 1 or 6 but can add other options

    chip_count = 12  # this is what I'll actually use #should be 1 or 2 or 12 and should help define module_series

    OV_threshold = 4.35  # threshold in volts
    UV_threshold = 3

    OT_threshold = 60  # temperature in degrees C
    UT_threshold = -20

    CI_threshold = 0.5  # threshold in volts

    cell_read_option = 'FC'  # pick between FC, AC, C, or S #only FC and C implemented but easy to implement otherwise

    raw_temperature_list = np.zeros((module_count, 20))
    voltage_list = np.zeros((module_count, module_series))  # voltage list comprises all voltages in the pack
    temperature_list = np.zeros((module_count, 20))  # 20 thermistors being utilized at this time

    OV_fault_storage = np.zeros((module_count, module_series))  # add to array
    UV_fault_storage = np.zeros((module_count, module_series))

    # OW_fault_storage = np.zeros((module_count, module_series))

    # CI_fault_storage = np.zeros((module_count, module_series))

    # OT_fault_storage = np.zeros((module_count, module_series))

    # UT_fault_storage = np.zeros((module_count, module_series))

    past_loop_faults = np.array([])
    current_loop_faults = np.array([])
    fault_holder = 0


    #interface = USB_TO_SPI_BYTE('COM3', 115200, stdout=False)
    interface = Virtual_SPI('data.txt')  # switch comments between this line and above if connecting to hardware vs not
    bms = BMS(interface)
    board_list = [{"Device": ADBMS6830}, {"Device": ADBMS6830}, {"Device": ADBMS6830}, {"Device": ADBMS6830},
                  {"Device": ADBMS6830}, {"Device": ADBMS6830}, {"Device": ADBMS6830}, {"Device": ADBMS6830},
                  {"Device": ADBMS6830}, {"Device": ADBMS6830}, {"Device": ADBMS6830}, {"Device": ADBMS6830}]
    # look into numpy things

    initial_list = [
        {"command": "$SPI_WAKEUP$", "arguments": {"wakeup_time": 400}},  # SPI port not awake initally
        {"command": "$DELAY_MS$", "arguments": {"Delay": 10}},
        {"command": "$SPI_WAKEUP$", "arguments": {"Wakeup Time": 10}},
        {"command": "WRCFGA", "arguments": {"REFON": True, 'FC': 7}},
        # Activate ADC Cell and ADC Spins
        {"command": "ADCV", "arguments": {"CONT": True}},
        {"command": "ADAX", "arguments": {"CH": 0000, "PUP": 1}},
        # set OV and UV threshold
        {"command": "WRCFGB", "arguments": {"VUV": UV_threshold, "VOV": OV_threshold}},
        # Give some time to start up the adc's
        {"command": "$DELAY_MS$", "arguments": {"Delay": 10}},
        {"command": "$SPI_WAKEUP$", "arguments": {"Wakeup Time": 10}},

    ]

    if cell_read_option == "FC":
        command_list = [
            {"command": "ADAX", "arguments": {"CH": 0000, "PUP": 1}},

            {"command": "$DELAY_MS$", "arguments": {"Delay": 2}},

            {"command": "SNAP"},

            {"command": "RDFCA", "map_key": "val"},
            {"command": "RDFCB", "map_key": "val"},
            {"command": "RDFCC", "map_key": "val"},
            {"command": "RDFCD", "map_key": "val"},
            {"command": "RDFCE", "map_key": "val"},
            {"command": "RDFCF", "map_key": "val"},

            {"command": "RDSTATD", "map_key": "val"},  #read for cell voltage faults

            {"command": "RDASALL", "map_key": "val"},

            {"command": "UNSNAP"}
        ]
    elif cell_read_option == "C":
        command_list = [
            # Thermistor readings
            {"command": "ADAX", "arguments": {"CH": 0000, "PUP": 1}},

            {"command": "$DELAY_MS$", "arguments": {"Delay": 2}},

            {"command": "SNAP"},

            {"command": "RDCVA", "map_key": "val"},
            {"command": "RDCVB", "map_key": "val"},
            {"command": "RDCVC", "map_key": "val"},
            {"command": "RDCVD", "map_key": "val"},
            {"command": "RDCVE", "map_key": "val"},
            {"command": "RDCVF", "map_key": "val"},

            {"command": "RDSTATD", "map_key": "val"},  # read for cell voltage faults

            {"command": "RDASALL", "map_key": "val"},

            {"command": "UNSNAP"}
        ]
    else:
        command_list = []

        """ ####THIS IS ALL WORK IN PROGRESS
        open_wire_list_algorithm_list = [ # open wire detection is a bit trickier
            ### OPEN WIRE DETECTION SEQUENCE WITH BUILT IN DELAYS
            {"command": "ADSV", "arguments": {"DCP": 0, "CONT": 1, "OW": 0}},
            # {"command": "$DELAY_MS$", "arguments": {"Delay": 10}},
            {"command": "ADSV", "arguments": {"DCP": 0, "CONT": 0, "OW": 1}},
            # {"command": "$DELAY_MS$", "arguments": {"Delay": 10}},
            {"command": "ADSV", "arguments": {"DCP": 0, "CONT": 0, "OW": 2}},
            # {"command": "$DELAY_MS$", "arguments": {"Delay": 10}},
        ]

        end_list = [ #whichever commands we want to run at the end of our loop
            {"command": "CLRCELL"},
        ]
        """

    _ = bms.run_generic_command_list(initial_list, board_list)
    counter = 0

    while 1:  # run unless some exit condition is met (break statement)

        if bms_fault == 1:
            ##GPIO = LOW
            x = 2  # placeholder so code runs
        else:
            ##GPIO = HIGH
            x = 2  # placeholder so code runs

        results = bms.run_generic_command_list(command_list, board_list)

        """voltage list generation"""

        if module_series == 16:  # work in progress
            x = 2  # placeholder so code runs
        elif module_series == 23:
            for module in range(module_count):  # chip that data is being pulled from
                for module_cell in range(module_series):  # cell number
                    chip_select = (int) (module_cell/12) + module * 2  # cell number from chip's perspective (starts at 1 goes to 12/11)
                    chip_cell = 1 + module_cell % 12

                    key = cell_read_option + str(chip_cell) + "V"
                    voltage_list[module][module_cell] = results['val'][chip_select][key]

                    OV_key = "C" + str(chip_cell) + "OV"  # OV check
                    OV_fault = results['val'][chip_select][OV_key]

                    UV_key = "C" + str(chip_cell) + "UV"
                    UV_fault = results['val'][chip_select][UV_key]

                    if OV_fault == 1:
                        current_loop_faults = np.append(current_loop_faults, (OV_key, chip_select, voltage_list[module][module_cell]))
                    if UV_fault == 1:
                        current_loop_faults = np.append(current_loop_faults, (UV_key, chip_select, voltage_list[module][module_cell]))
        else:
            continue

        """GPIO (thermistor) fault check"""

        for module in range(module_count):
            for thermistor in range(20):
                chip_select = (int) (thermistor / 10) + module * 2  # cell number from chip's perspective (starts at 1 goes to 12/11)
                chip_thermistor = 1 + thermistor % 10

                key = "G" + str(chip_thermistor) + "V"
                temperature_list[module][thermistor] = results['val'][chip_select][key]
                """INSERT TEMPERATURE CONVERSION"""  # AND SAVE THE TEMPERATURE NOT THE VOLTAGE (CURRENT IMPLEMENTATION)
                if temperature_list[module][thermistor] >= OT_threshold:
                    key = "T" + str(chip_thermistor) + "OT"
                    current_loop_faults = np.append(current_loop_faults, (key, chip_select, temperature_list[module][thermistor]))
                    OT_fault = 1
                if temperature_list[module][thermistor] <= UT_threshold:
                    key = "T" + str(chip_thermistor) + "UT"
                    current_loop_faults = np.append(current_loop_faults, (key, chip_select, temperature_list[module][thermistor]))
                    UT_fault = 1

        """
        OPEN WIRE CHECK TO BE IMPLEMENTED AT A LATER DATE
        """

        """CELL IMBALANCE FAULT CHECK"""

        highest_cell = np.max(voltage_list)  # lower than it will ever be
        lowest_cell = np.min(voltage_list)
        if highest_cell-lowest_cell >= CI_threshold:
            CI_fault = 1
            max_index = np.unravel_index(np.argmax(voltage_list), voltage_list.shape)
            max_index = (max_index[0], max_index[1] + 1)
            min_index = np.unravel_index(np.argmin(voltage_list), voltage_list.shape)
            min_index = (min_index[0], min_index[1] + 1)
            max_key = "C" + str(max_index[1] % 12) + "CI"
            min_key = "C" + str(min_index[1] % 12) + "CI"
            current_loop_faults = np.append(current_loop_faults, (max_key, (int) (max_index[1]/12) + max_index[0] * 2, highest_cell))
            current_loop_faults = np.append(current_loop_faults, (min_key, (int) (min_index[1]/12) + min_index[0] * 2, lowest_cell))

        if current_loop_faults.size == 0: #goes through all faults and activates bms fault
            bms_fault = 0
            #GPIO = HIGH
        else:
            bms_fault = 1
            #GPIO = LOW

        if (past_loop_faults.size != 0 and current_loop_faults.size != 0) and (not (past_loop_faults == current_loop_faults)):
            for fault in current_loop_faults:
                if not(np.isin(fault, past_loop_faults)):
                    # send message over CAN saying new fault
                    x = 2 # placeholder so code runs
            for fault in past_loop_faults:
                if not(np.isin(fault, current_loop_faults)):
                    # send message over CAN saying fault no longer
                    x = 2 # placeholder so code runs

        past_loop_faults = current_loop_faults

        """DO NOT UNCOMMENT THIS AT THIS TIME"""
        #print_battery_pack(voltage_list)  # have this update live with a python library
        # #figured out a solution that'll be implemented later
        #counter += 1  # implemented in case I want to run it for testing and not have it loop

    interface.close()  # never close interface unless loop has been exited


if __name__ == "__main__":
    main()
