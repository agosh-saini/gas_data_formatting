# ----
# Author: Agosh Saini
# Contact: contact@agoshsaini.com   
# -----
# This file is a class for splitting one relay file into multiple single data file

#### IMPORTS ####
import pandas as pd


#### CLASSES ####
class SplitRelayData:
    def __init__(self, filename, data):
        self.data = data
        self.file_name = filename
        self.sensor_names = self.get_sensor_name()

    def get_sensor_name(self):

        '''
        Input: None
        Output: List of sensor names

        This function will take the input from the user for the sensor names
        '''

        sensor_names = []

        sensor_name = input("Enter the sensor material IDs for the relays: ")

        for i in range(8):
            sensor_names.append(f'{sensor_name}.{i+1}')

        return sensor_names


    def generate_files(self):

        '''
        Input: None
        Output: None

        This function will generate the files for the sensor data
        '''

        data = self.data

        for i, sensor in enumerate(self.sensor_names):

            data_dict = {
                "Time": data["Elapsed Time (s)"].values.astype(float),
                "Resistance": data[f'Relay {i+1} Resistance'].values.astype(float),
                "Cycle": data["Cycle"].values.astype(str)
            }

            df = pd.DataFrame(data_dict)

            df.to_csv(f'relay_data/{self.file_name}_{sensor}.csv', index=False)
            print(f"File {self.file_name}_{sensor}.csv has been saved.")


#### MAIN ####
if __name__ == "__main__":
    path = "data_log_20241018_133756.csv"
    data = pd.read_csv(path)
    splitter = SplitRelayData(path[:-4], data)
    splitter.generate_files()