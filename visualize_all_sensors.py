############
# Author: Agosh Saini
# Contact: contact@agoshsaini.com
############
# This is a script for visiualizing all sensors in the dataset to select which to discard
###########

######## IMPORTS ########
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

###### Script ######

# Open a file dialog to select the file
root = tk.Tk()
root.withdraw()

# Get the file path
file_path = filedialog.askopenfilename()

# Read the data
data = pd.read_csv(file_path)

# Get the columns
columns = data.columns

# Plot all the sensors
fig, ax = plt.subplots(ncols=4, nrows=2, figsize=(20, 20))

# Flatten the axes array for easier indexing
ax = ax.flatten()


i = 0

for column in columns:
    if 'Relay' in column:
        data[column].plot(ax=ax[i], label=column)  # Use the correct subplot
        ax[i].set_title(column)
        i += 1

plt.tight_layout()

def on_click(event):

    for a in ax:
        if a == event.inaxes:
            fig_fullscreen, ax_fullscreen = plt.subplots(figsize=(10, 6))

            for line in a.get_lines():  # Copy lines from the clicked subplot
                ax_fullscreen.plot(line.get_xdata(), line.get_ydata(), label=line.get_label())

            ax_fullscreen.set_title(a.get_title())
            ax_fullscreen.legend()
            plt.show()

# Connect the click event to the handler
fig.canvas.mpl_connect('button_press_event', on_click)

# Show the main plot
plt.show()

# Ask the user to select which sensors to discard
discard_sensors = input("Enter the Relay Numbers to discard separated by commas: ")
discard_sensors = discard_sensors.split(',')

# Create Columns Titles From Numbers
discard_sensors = [f'Relay {sensor} Resistance' for sensor in discard_sensors]

# Remove the sensors
data.drop(columns=discard_sensors, inplace=True)

# Save the data
data.to_csv(file_path, index=False)
