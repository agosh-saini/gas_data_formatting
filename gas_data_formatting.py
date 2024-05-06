# ----
# Author: Agosh Saini
# Contact: contact@agoshsaini.com   
# -----
# This file is a class for data processing and formatting 

import numpy as np
import pandas as pd
import relation_db as db
from os.path import basename

class data_format:
    def __init__(self, filepath, data, analytes, sat_ppm):
        self.filepath = filepath
        self.data = data # should be pandas df
        self.analytes = analytes # should be a set
        self.label = ["ON (Cycling)", "OFF (Cycling)"]
        self.sat_ppm = sat_ppm # should be a dictionary
        self.final_data = None
        self.ppm = None
        self.current_analyte = None
    
    def update_value(self, filepath=None, data=None, analytes=None, sat_ppm=None):
        # this function allows you to update the dataset without creating a new instance
        if filepath is not None:
            self.filepath = filepath

        if data is not None:
            self.data = data 

        if analytes is not None:
            self.analytes = analytes
            
        if sat_ppm is not None:
            self.sat_ppm = sat_ppm           
       
        return None
    
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
        
        return None
    
    def split_flows(self, data=None):

        if data is None:
            df  = self.data 

        # Using str.extract to split the 'data' column into three new columns
        df[['A', 'B', 'C']] = df['Flow [A:B:C]'].str.extract(r'\[([+-]?\d*\.?\d+):([+-]?\d*\.?\d+):([+-]?\d*\.?\d+)\]')

        df.dropna(subset=['A', 'B', 'C'], inplace=True)

        # Convert extracted strings to integers
        df[['A', 'B', 'C']] = df[['A', 'B', 'C']].astype(float)

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

    def calcualte_ppm(self, df=None, columns=None):
        if df is None:
            df = self.data

        max_ppm = self.sat_ppm[self.current_analyte]

        df_on = df[df['Stage'] == 'ON (Cycling)']

        # Ensure there is data to work with
        if df_on.empty or df_on['C'].isna().all() or df_on['A'].isna().all():
            print("No valid data to calculate ppm.")
            return None

        avg_C = np.nanmean(df_on['C'])
        avg_A = np.nanmean(df_on['A'])

        if any(df_on['C'] + df_on['A']) == 0:
            print("Division by zero encountered while calculating ppm.")
            return None

        ppm = max_ppm * df_on['C'] / (df_on['C'] + df_on['A'])

        self.ppm = ppm.values

        return ppm

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

        # Create a DataFrame with repeating scalar values to match the length of on_data
        self.final_data = {
            'filename': filename,
            'Analyte': self.current_analyte,
            'ppm': self.ppm,
            'ON': on_data["Current (uA)"].values,
            'OFF': off_data["Current (uA)"].values
        }

        return self.final_data

    def format(self):
        self.extract_analyte()
        self.split_flows()
        self.extract_labeled_data()
        self.calcualte_ppm()
        self.format_data()

        return self.final_data



# Test
if __name__ == '__main__':
    sat_ppm = {
                    "Water": 28483,
                    "EtOH":	70825,
                    "Ace":	282973,
                    "IPA": 	52302
                }
                
    analytes = set(["IPA", "Water", "EtOH", "Ace"])
    filepath = "20240409_ASS_Water_SnO2_2D_90sccm_2.txt"
    data = pd.read_csv(filepath)

    formatter = data_format(filepath, data, analytes, sat_ppm)


    formatted_data = formatter.format()

    hub = db.relation_db("formatted_data.db")
    db_path, db_name = hub.create_db()
    hub.create_table()
    hub.add_to_table(formatted_data["filename"], formatted_data['Analyte'], str(formatted_data['ppm']),
                    str(formatted_data['ON']), str(formatted_data['OFF']))



    