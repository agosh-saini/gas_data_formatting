############
# Author: Agosh Saini
# Contact: contact@agoshsaini.com
############
# This is a script for visualizing all sensors in the dataset to select which to discard
###########

######## IMPORTS ########
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog


###### CLASS DEFINITION ######
class SensorVisualizer:
    def __init__(self, select_folder=False):
        if select_folder:
            self.data, self.path = self.get_data()
        else:
            self.data = None
            self.path = None

    def update_data(self):
        self.data, self.path = self.get_data()

    def get_data(self):
        root = tk.Tk()
        root.withdraw()

        # Get the file path
        file_path = filedialog.askopenfilename()

        if not file_path:
            raise ValueError("No file selected.")

        # Read the data
        data = pd.read_csv(file_path)

        return data, file_path

    def on_click(self, event, ax):
        for a in ax:
            if a == event.inaxes:
                fig_fullscreen, ax_fullscreen = plt.subplots(figsize=(10, 6))

                for line in a.get_lines():  # Copy lines from the clicked subplot
                    ax_fullscreen.plot(line.get_xdata(), line.get_ydata(), label=line.get_label())

                ax_fullscreen.set_title(a.get_title())
                ax_fullscreen.legend()
                plt.show()

    def visualize_sensors(self):
        # Get the columns
        columns = self.data.columns

        # Plot all the sensors
        fig, ax = plt.subplots(ncols=4, nrows=2, figsize=(20, 20))

        # Flatten the axes array for easier indexing
        ax = ax.flatten()

        # Plot all the sensors
        i = 0

        for column in columns:
            if 'Relay' in column:
                self.data[column].plot(ax=ax[i], label=column)
                ax[i].set_title(column)
                i += 1
        
        plt.tight_layout()

        # Connect the click event to the handler
        fig.canvas.mpl_connect('button_press_event', lambda event: self.on_click(event, ax))

        # Show the main plot
        plt.show()

    def save_data(self):
        # Save the data
        self.data.to_csv(self.path, index=False)

    def discard_sensors(self):
        # Ask the user to select which sensors to discard
        discard_sensors = input("Enter the Relay Numbers to discard separated by commas (Or na to discard none): ")

        # Parse the input
        discard_sensors = discard_sensors.split(',')

        # Check if the input is valid
        if discard_sensors == ['na']:
            print("No sensors to discard.")
            return None
        elif  not all(sensor.isdigit() and 1 <= int(sensor) <= 8 for sensor in discard_sensors):
            print("Invalid input. Please enter valid numbers between 1 and 8 separated by commas.")
            return None

        # Create Columns Titles From Numbers
        sensor_columns = [f'Relay {sensor.strip()} Resistance' for sensor in discard_sensors]

        # Remove the sensors
        for column in sensor_columns:
            if column in self.data.columns:
                self.data.drop(columns=column, inplace=True)
            else:
                print(f"Warning: Column '{column}' does not exist in the data.")


##### MAIN #####

if __name__ == "__main__":

    # Create the SensorVisualizer Object
    sensor_visualizer = SensorVisualizer()

    # Loop until the user wants to stop
    while input("Do you want to discard sensors? (y/n): ") == "y": 
        # Update the data
        sensor_visualizer.update_data()

        # Visualize the sensors
        sensor_visualizer.visualize_sensors()

        # Discard the sensors
        sensor_visualizer.discard_sensors()

        # Save the data
        sensor_visualizer.save_data()

    print("Data saved successfully.")
