# ----
# Author: Agosh Saini
# Contact: contact@agoshsaini.com   
# -----
# This file is a class for data processing and formatting 

import numpy as np
import pandas as pd
from os.path import basename

class data_format:
    def __init__(self, filepath, data, analytes, materials, sat_ppm) -> None:
        self.filepath = filepath
        self.data = data # should be pandas df
        self.analytes = analytes # should be a set
        self.materials = materials # should be a set
        self.label = ["ON (Cycling)", "OFF (Cycling)"]
        self.sat_ppm = sat_ppm # should be a dictionary
        self.final_data = None
        self.ppm = None
        self.current_analyte = None
        self.current_material = None
    
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
        
        
    
    def split_flows(self, data=None):

        if data is None:
            df  = self.data 

        # Extract the values into new columns A, B, and C
        df[['A', 'B', 'C']] = df['Flow [A:B:C]'].str.extract(r'\[([+-]?\d*\.?\d+):([+-]?\d*\.?\d+):([+-]?\d*\.?\d+)\]')
        df.dropna(subset=['A', 'B', 'C'], inplace=True)

        
        df[['A', 'B', 'C']] = df[['A', 'B', 'C']].astype(float).clip(lower=0)

        self.data = df

        return self.data
    
    def extract_labeled_data(self, data=None):

        # this function extracts on and off cycling data and also the ppm associated
        if data is None:
            df  = self.data

        # Filtering the DataFrame
        filtered_df = df[df['Stage'].isin(self.label)]

        # Creating a new DataFrame with only the required columns
        self.data = filtered_df[['Stage', 'Current (uA)', 'Time (s)', 'A', 'B', 'C']]

        return self.data
    
    def extract_material(self, filepath=None, materials=None):
        # this function allows for extraction of material from filepath 

        if filepath is None:
            filepath = self.filepath

        if materials is None:
            materials = self.materials
    
        # check to see if values are valid for gasses
        if not any(material in filepath for material in materials):
            raise ValueError("None of the analytes are found in the filepath.")

        # extract the analyte in question
        for material in materials:
            if material in filepath:
                self.current_material = material
                return material  
        
        

    def calcualte_ppm(self, df=None, columns=None):
        if df is None:
            df = self.data

        max_ppm = self.sat_ppm[self.current_analyte]

        df_cycling = df[df['Stage'].isin(['ON (Cycling)', 'OFF (Cycling)'])]

        # Ensure there is data to work with
        if df_cycling.empty or df_cycling['C'].isna().all() or df_cycling['A'].isna().all():
            print("No valid data to calculate ppm.")
            return None

        avg_C = np.nanmean(df_cycling['C'])
        avg_A = np.nanmean(df_cycling['A'])

        if any(df_cycling['C'] + df_cycling['A']) == 0:
            print("Division by zero encountered while calculating ppm.")
            return None

        ppm = max_ppm * df_cycling['C'] / (df_cycling['C'] + df_cycling['A'])

        self.ppm = ppm.values

        return ppm.values

    def extend_df_with_nans(dataframe, target_length):
        additional_rows = target_length - len(dataframe)
        if additional_rows > 0:
            # Create a DataFrame of NaNs with the same columns
            nan_df = pd.DataFrame(np.nan, index=range(additional_rows), columns=dataframe.columns)
            # Concatenate the original DataFrame with the NaN DataFrame
            extended_df = pd.concat([dataframe, nan_df], ignore_index=True)
            return extended_df
        return dataframe    
        
    def format_data(self, data=None):

        if data is None:
            df  = self.data

        # Creating DataFrame slices for 'ON' and 'OFF'
        on_data = df[df['Stage'] == 'ON (Cycling)']
        off_data = df[df['Stage'] == 'OFF (Cycling)']

        filename = basename(self.filepath) 

        if len(self.ppm.astype(float)) <= 0:
            ppm = np.array([0])
        else:
            ppm = self.ppm.astype(float)

        if len(on_data["Current (uA)"].values.astype(float)) <= 0:
            on = np.array([0])
        else:
            on = on_data["Current (uA)"].values.astype(float)

        if len(off_data["Current (uA)"].values.astype(float)) <= 0:
            off = np.array([0])
        else:
            off = off_data["Current (uA)"].values.astype(float)


        # Create a DataFrame with repeating scalar values to match the length of on_data
        self.final_data = {
            'filename': filename,
            'Analyte': self.current_analyte,
            'Material': self.current_material,
            'ppm': ppm,
            'ON': on,
            'OFF': off
        }

        return self.final_data

    def format(self):
        self.extract_analyte()
        self.extract_material()
        self.split_flows()
        self.extract_labeled_data()
        self.calcualte_ppm()
        self.format_data()

        return self.final_data



    