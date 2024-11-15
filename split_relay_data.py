# ----
# Author: Agosh Saini
# Contact: contact@agoshsaini.com   
# -----
# This file is a class for splitting relay data into separate files for each sensor.

###### IMPORTS ######

import os
import pandas as pd
import matplotlib.pyplot as plt
import re

###### CLASS DEFINITION ######

class SplitRelayData:
    def __init__(self, filename, data, sensor_match=None):
        """
        This class is used to split relay data into separate files for each sensor.

        Parameters:
            filename (str): The name of the input file containing relay data.
            data (DataFrame): The DataFrame containing relay data.

        Optional Parameters:
            sensor_match (str): The pattern to match the sensor name in the filename. If not provided, it defaults to 'PN'.
        """
        self.data = data
        self.file_name = filename
        self.sensor_match = sensor_match or 'PN'
        self.relays = self.get_active_relays()

        if not self.relays:
            print("No active relays found in the data.")
            self.sensor_names = []
        else:
            self.sensor_names = self.get_sensor_name()

    def get_active_relays(self):
        """
        Identifies active relays by checking for existence and uniqueness of their resistance data.

        Returns:
            list: A list of active relay numbers.
        """
        relays = []

        for i in range(8):
            column_name = f'Relay {i + 1} Resistance'
            if column_name in self.data.columns and self.data[column_name].nunique() > 1:
                relays.append(i + 1)  # Relay numbers are 1-based

        return relays

    def get_sensor_name(self):
        """
        Extracts sensor names for each active relay from the filename or prompts the user for input.

        Returns:
            list: A list of sensor names for each relay.
        """
        sensor_names = []
        print(f'File: {self.file_name}')
        match = re.search(fr'{re.escape(self.sensor_match)}\d+', self.file_name)

        sensor_name = match.group(0) if match else input("Enter the sensor name: ")

        for relay in self.relays:
            sensor_names.append(f'{sensor_name}.{relay}')

        return sensor_names

    def generate_files(self, graph=False):
        """
        Generates CSV files for each sensor's data and optionally creates scatter plots.

        Parameters:
            graph (bool): If True, scatter plots will be generated for each sensor's data.
        """
        if not self.relays:
            print("No active relays to generate files for.")
            return

        # Ensure output directories exist
        os.makedirs('relay_data', exist_ok=True)
        if graph:
            os.makedirs('relay_graphs', exist_ok=True)

        for sensor, relay in zip(self.sensor_names, self.relays):
            column_name = f'Relay {relay} Resistance'
            if column_name in self.data.columns:
                self._save_sensor_data(sensor, column_name, graph)
            else:
                print(f"Warning: {column_name} does not exist in the data.")

    def _save_sensor_data(self, sensor, column_name, graph):
        """
        Saves individual sensor data to a CSV file and generates a scatter plot if required.

        Parameters:
            sensor (str): Sensor name.
            column_name (str): Column name for relay resistance.
            graph (bool): Whether to generate scatter plots.
        """
        data_dict = {
            "Time": self.data["Elapsed Time (s)"].values.astype(float),
            "Resistance": self.data[column_name].values.astype(float),
            "Cycle": self.data["Cycle"].values.astype(str)
        }

        df = pd.DataFrame(data_dict)
        output_csv = f'relay_data/{self.file_name}_{sensor}.csv'
        df.to_csv(output_csv, index=False)
        print(f"File {output_csv} has been saved.")

        if graph:
            self._generate_scatter_plot(df, sensor)

    def _generate_scatter_plot(self, df, sensor):
        """
        Generates a scatter plot for the sensor data.

        Parameters:
            df (DataFrame): The DataFrame containing sensor data.
            sensor (str): Sensor name for labeling the plot.
        """
        on_data = df[df['Cycle'].str.contains('on', case=False, na=False)]
        off_data = df[df['Cycle'].str.contains('off', case=False, na=False)]

        plt.scatter(on_data["Time"], on_data['Resistance'], label="ON", s=1)
        plt.scatter(off_data["Time"], off_data["Resistance"], label="OFF", s=1)

        plt.xlabel("Time (s)")
        plt.ylabel("Resistance")
        plt.title(f"{self.file_name}_{sensor}")
        plt.legend()
        plt.savefig(f'relay_graphs/{self.file_name}_{sensor}.png')
        plt.close()
        print(f"Scatter plot saved for {sensor}.")

#### MAIN FUNCTION ####

if __name__ == "__main__":
    path = input("Enter the path to the input file containing relay data: ")
    try:
        data = pd.read_csv(path)
        splitter = SplitRelayData(filename=path[:-4], data=data)
        splitter.generate_files(graph=True)
    except FileNotFoundError:
        print(f"Error: File {path} not found.")
    except pd.errors.EmptyDataError:
        print(f"Error: The file {path} is empty or invalid.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")