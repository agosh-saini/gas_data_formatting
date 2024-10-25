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
    def __init__(self, filepath, data, analytes, materials, sat_ppm) -> None:
        self.filepath = filepath
        self.data = data # should be pandas df
        self.analytes = analytes # should be a set
        self.materials = materials # should be a set
        self.label = ["Pre", "On", "Off"]
        self.sat_ppm = sat_ppm # should be a dictionary
        self.avg_timestep = None
        self.final_data = None
        self.ppm = None
        self.current_analyte = None
        self.current_material = None
        self.baseline = None
    
    def update_value(self, filepath=None, data=None, analytes=None, sat_ppm=None) -> None:
        # this function allows you to update the dataset without creating a new instance
        if filepath is not None:
            self.filepath = filepath

        if data is not None:
            self.data = data 

        if analytes is not None:
            self.analytes = analytes
            
        if sat_ppm is not None:
            self.sat_ppm = sat_ppm           
        
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
        # this function allows for extraction of analyte 

        if filepath is None: 
            filepath = self.filepath

        if analytes is None: 
            analytes = self.analytes
    
        # check to see if values are valid for gasses
        if not any(analyte in filepath for analyte in analytes):
            raise ValueError("None of the analytes are found in the filepath.")

        # extract the analyte in question
        for analyte in analytes:
            if analyte in filepath:
                self.current_analyte = analyte
                return analyte  
        
    
    def extract_labeled_data(self, data=None):
        # this function extracts on and off cycling data and also the ppm associated
        if data is None:
            data = self.data

        # Creating a new DataFrame with only the required columns
        self.data = data[['Cycle', 'Resistance', 'Time']]

        return self.data
    
    def extract_material(self, filepath=None, materials=None):
        # this function allows for extraction of material from filepath 

        if filepath is None:
            filepath = self.filepath

        if materials is None:
            materials = self.materials
    
        # check to see if values are valid for gasses
        if not any(material in filepath for material in materials):
            raise ValueError("None of the materials are found in the filepath.")

        # extract the analyte in question
        for material in materials:
            if material in filepath:
                self.current_material = material
                return material  
        
    def extract_ppm(self, filepath=None, ppm=None):
        # this function allows for extraction of material from filepath 

        if filepath is None:
            filepath = self.filepath

        if ppm is None:
            ppm = self.ppm

        # extract the analyte in question
        match = re.search(r'(\d+)ppm', filepath)
        if match:
            self.ppm = match.group(1)
            return match.group(1)
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
    sat_ppm = {
                "data": 28483
            }
                
    analytes = set(["data", "Water", "EtOH", "Ace"])

    materials = set(["log"])

    filepath = "example_data\data_log_20241018_133756_25ppm.csv"
    data = pd.read_csv(filepath)

    formatter = data_format(filepath, data, analytes, materials, sat_ppm)

    formatted_data = formatter.format()

    print(formatted_data)