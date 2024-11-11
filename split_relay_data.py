# ----
# Author: Agosh Saini
# Contact: contact@agoshsaini.com   
# -----
# This file is a class for data processing and formatting

import os
import pandas as pd
import matplotlib.pyplot as plt

class SplitRelayData:
    def __init__(self, filename, data):
        self.data = data
        self.file_name = filename
        self.relays = self.get_active_relays()  # Call get_active_relays here to ensure it's set
        if not self.relays:
            print("No active relays found in the data.")
            self.sensor_names = []
        else:
            self.sensor_names = self.get_sensor_name()

    def get_active_relays(self):
        """
        Input: None
        Output: List of active relays
        This function returns a list of active relays by checking each relay column's existence and uniqueness.
        """
        relays = []
        for i in range(8):
            column_name = f'Relay {i+1} Resistance'
            if column_name in self.data.columns and self.data[column_name].nunique() > 1:
                relays.append(i + 1)  # Relay numbers are 1-based
        self.relays = relays
        return relays

    def get_sensor_name(self):
        """
        Input: None
        Output: List of sensor names
        This function takes input from the user for the sensor names.
        """
        sensor_names = []
        print(f'File: {self.file_name}')
        sensor_name = input("Enter a base sensor material ID for the relays: ")
        
        for relay in self.relays:
            sensor_names.append(f'{sensor_name}.{relay}')
        return sensor_names



    def generate_files(self, graph=False):
        """
        Input: None
        Output: None
        This function generates CSV files for each sensor's data.
        """


        # Check if there are any active relays to process
        if not self.relays:
            print("No active relays to generate files for.")
            return
        
        # Create output folder if it doesn't exist
        os.makedirs('relay_data', exist_ok=True)

        # Create output folder for graphs if it doesn't exist
        if graph:
            os.makedirs('relay_graphs', exist_ok=True)

        sensor_relay_zip = zip(self.sensor_names, self.relays)

        for sensor, relay in sensor_relay_zip:
            column_name = f'Relay {relay} Resistance'
            if column_name in self.data.columns:  # Check if column exists
                data_dict = {
                    "Time": self.data["Elapsed Time (s)"].values.astype(float),
                    "Resistance": self.data[column_name].values.astype(float),
                    "Cycle": self.data["Cycle"].values.astype(str)
                }
                df = pd.DataFrame(data_dict)
                df.to_csv(f'relay_data/{self.file_name}_{sensor}.csv', index=False)
                print(f"File {self.file_name}_{sensor}.csv has been saved.")

                if graph:
                    on_data = df[df['Cycle'].str.contains('on', case=False, na=False)]
                    off_data = df[df['Cycle'].str.contains('off', case=False, na=False)]
                    baseline_data = df[df['Cycle'].str.contains('pre', case=False, na=False)]
                    plt.scatter(on_data["Time"], on_data['Resistance'], label="ON", s=1)
                    plt.scatter(off_data["Time"], off_data["Resistance"], label="OFF", s=1)
                    plt.scatter(baseline_data["Time"], baseline_data["Resistance"], label="Baseline", s=1)
                    plt.xlabel("Time (s)")
                    plt.ylabel("Resistance")
                    plt.title(f"{self.file_name}_{sensor}")
                    plt.savefig(f'relay_graphs/{self.file_name}_{sensor}.png')
                    plt.close()
            else:
                print(f"Warning: {column_name} does not exist in the data.")
    


if __name__ == "__main__":
    path = input("Enter the path to the input file containing relay data: ")
    data = pd.read_csv(path)
    splitter = SplitRelayData(path[:-4], data)
    splitter.generate_files(graph=True)
