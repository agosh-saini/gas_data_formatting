# ----
# Author: Agosh Saini
# Contact: contact@agoshsaini.com   
# -----
# This file is a class for data processing and formatting

import numpy as np
import pandas as pd
from os.path import basename
import re

class data_format:
    def __init__(self, filepath, data, analytes, materials, sensor_type=None) -> None:
        self.filepath = filepath
        self.data = data # should be pandas df
        self.analytes = analytes # should be a set
        self.materials = materials # should be a set
        self.label = ["Pre", "On", "Off"]
        self.avg_timestep = None
        self.final_data = None
        self.ppm = []
        self.current_analyte = []
        self.current_material = []
        self.baseline = None
        self.sensor_type = sensor_type
    
    def update_value(self, filepath=None, data=None, analytes=None) -> None:
        # this function allows you to update the dataset without creating a new instance
        if filepath is not None:
            self.filepath = filepath

        if data is not None:
            self.data = data 

        if analytes is not None:
            self.analytes = analytes          
        
    def extract_avg_timestep(self, data=None):
        # this function extracts the average timestep from the data
        if data is None:
            data = self.data

        # Extracting the average timestep from the data
        time = data['Time'].values
        time_diff = np.diff(time)
        self.avg_timestep = np.mean(time_diff)

        return self.avg_timestep

    def extract_analyte(self, filepath=None, analytes=None):
        # This function allows for extraction of analytes

        if filepath is None: 
            filepath = self.filepath

        if analytes is None: 
            analytes = self.analytes

        # Check to see if any of the analytes are valid in the filepath
        found_analytes = [analyte for analyte in analytes if analyte in filepath]
        
        if not found_analytes:
            raise ValueError("None of the analytes are found in the filepath.")
        
        # Append each found analyte to current_analyte in the order of appearance
        self.current_analyte.extend(found_analytes)
        return found_analytes
            
    
    def extract_labeled_data(self, data=None):
        # this function extracts on and off cycling data and also the ppm associated
        if data is None:
            data = self.data

        # Creating a new DataFrame with only the required columns
        self.data = data[['Cycle', 'Resistance', 'Time']]

        return self.data
    
    def extract_material(self, filepath=None, materials=None):
        # This function allows for extraction of materials from filepath

        if filepath is None:
            filepath = self.filepath

        if materials is None:
            materials = self.materials

        # Check to see if any of the materials are valid in the filepath
        found_materials = [material for material in materials if material in filepath]

        if not found_materials:
            raise ValueError("None of the materials are found in the filepath.")

        # Append each found material to current_material in the order of appearance
        self.current_material.extend(found_materials)
        return found_materials

        
    def extract_ppm(self, filepath=None, ppm=None):
        # This function allows for extraction of material from filepath

        if filepath is None:
            filepath = self.filepath

        if ppm is None:
            ppm = self.ppm

        # Extract all ppm values in question
        matches = re.findall(r'(\d+)ppm', filepath)
        if matches:
            # Convert matches to integers or keep as strings if desired
            ppm_values = [int(match) for match in matches]
            self.ppm = ppm_values
            return ppm_values
        else:
            raise ValueError("No ppm value found in the filepath.")
            
    def format_data(self, data=None):
        if data is None:
            data = self.data

        # Creating DataFrame slices for 'ON' and 'OFF'
        on_data = data[data['Cycle'].str.contains('on', case=False, na=False)]
        off_data = data[data['Cycle'].str.contains('off', case=False, na=False)]
        baseline_data = data[data['Cycle'].str.contains('pre', case=False, na=False)]

        filename = basename(self.filepath) 

        if len(on_data["Resistance"].values.astype(float)) <= 0:
            on = np.array([0])
        else:
            on = on_data["Resistance"].values.astype(float)

        if len(off_data["Resistance"].values.astype(float)) <= 0:
            off = np.array([0])
        else:
            off = off_data["Resistance"].values.astype(float)

        if len(baseline_data["Resistance"].values.astype(float)) <= 0:
            baseline = np.array([0])
        else:
            baseline = baseline_data["Resistance"].values.astype(float)

        # Create a DataFrame with repeating scalar values to match the length of on_data

        self.final_data = {
            'filename': filename,
            'Analyte': self.current_analyte,
            'Material': self.current_material,
            'ppm': self.ppm,
            'timestep': self.avg_timestep,
            'ON': on,
            'OFF': off,
            'Baseline': baseline
        }

        if self.sensor_type is not None:
            self.final_data['Sensor Type'] = self.sensor_type

        return self.final_data

    def format(self):
        self.extract_analyte()
        self.extract_avg_timestep()
        self.extract_material()
        self.extract_labeled_data()
        self.extract_ppm()
        self.format_data()

        return self.final_data

### MAIN ###
if __name__ == "__main__":
                
    analytes = set(["data", "Water", "EtOH", "Ace"])

    materials = set(["log", "mat"])

    filepath = "example_data\data_water_log_mat_25ppm_50ppm.csv"
    data = pd.read_csv(filepath)

    formatter = data_format(filepath, data, analytes, materials)

    formatted_data = formatter.format()

    print(formatted_data)