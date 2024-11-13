"""

import time
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Simulate a function to get the temperature reading from a thermistor
def get_temperature(module, thermistor):
    # Replace with actual sensor reading code
    return random.uniform(20, 80)  # Simulating a temperature range from 20 to 80 °C

def get_all_temperatures():
    # Retrieve temperatures for all modules and thermistors
    temperatures = []
    for module in range(6):  # Modules 0 through 5
        module_temps = [get_temperature(module, thermistor) for thermistor in range(20)]
        temperatures.append(module_temps)
    return np.array(temperatures)  # Convert to numpy array for heatmap display

# Initialize the plot
plt.ion()  # Enable interactive mode
fig, ax = plt.subplots(figsize=(10, 5))

# Set up the color map and the heatmap
cmap = plt.get_cmap('coolwarm')  # Use a colormap that transitions from cool to warm
norm = mcolors.Normalize(vmin=20, vmax=80)  # Temperature range for color scaling

# Initial heatmap plot
temperatures = get_all_temperatures()
heatmap = ax.imshow(temperatures, cmap=cmap, norm=norm, aspect='auto')

# Add color bar once
cbar = plt.colorbar(heatmap, ax=ax)
cbar.set_label("Temperature (°C)")

# Label the axes
ax.set_title("Thermistor Temperatures Across Modules")
ax.set_xlabel("Thermistors (1-20 per module)")
ax.set_ylabel("Modules (1-6)")

# Continuously update the heatmap
while True:
    # Get the current temperature readings
    temperatures = get_all_temperatures()

    # Update the heatmap with new data
    heatmap.set_data(temperatures)

    # Redraw the plot
    plt.draw()
    plt.pause(1)  # Pause to update every second

"""