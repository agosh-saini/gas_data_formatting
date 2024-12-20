############
# Author: Agosh Saini
# Contact: contact@agoshsaini.com   
############
# This file is a class for data processing and formatting
############

###### IMPORTS ######
import numpy as np
import pandas as pd
import re

from os.path import basename

##### CLASS #####

class data_format:
    
    def __init__(self, filepath, data, analytes, materials, ppm=None, sensor_type=None):

        '''
        Constructor for the data_format class.

        Parameters:
            filepath (str): The path to the file containing the data.
            data (DataFrame): The DataFrame containing the data.
            analytes (set): The set of analytes to be extracted.
            materials (set): The set of materials to be extracted.
            sensor_type (str): The type of sensor used (optional).
        '''

        # Initialize the class variables
        self.filepath = filepath

        self.data = data 

        self.analytes = analytes 
        self.materials = materials 
        self.label = ["Pre", "On", "Off"]
        self.sensor_type = sensor_type
        
        # Initialize the following variables to None
        self.avg_timestep = None
        self.final_data = None

        self.ppm = []

        self.current_analyte = []
        self.current_material = []

        self.baseline = None

        self.ppm = ppm

    
    def update_value(self, filepath=None, data=None, analytes=None):

        """
        This function allows for updating the values of the class variables.

        Parameters:
            filepath (str): The path to the file containing the data.
            data (DataFrame): The DataFrame containing the data.
            analytes (set): The set of analytes to be extracted.
        """
        
        if filepath is not None:
            self.filepath = filepath

        if data is not None:
            self.data = data 

        if analytes is not None:
            self.analytes = analytes          
        

    def extract_avg_timestep(self, data=None):
        '''
        This function extracts the average timestep from the data.

        Parameters:
            data (DataFrame): The DataFrame containing the data.
        '''
        if data is None:
            data = self.data

        # Extracting the average timestep from the data
        time = np.array(data['Time'].values, dtype=float)
        time_diff = np.diff(time)
        self.avg_timestep = np.mean(time_diff)

        return self.avg_timestep

    def extract_analyte(self, filepath=None, analytes=None):
        
        '''
        This function allows for extraction of analytes from filepath.

        Parameters:
            filepath (str): The path to the file containing the data.
            analytes (set): The set of analytes to be extracted.
        '''

        if filepath is None: 
            filepath = self.filepath

        if analytes is None: 
            analytes = self.analytes

        # Check to see if any of the analytes are valid in the filepath
        found_analytes = [analyte for analyte in analytes if analyte in filepath]
        
        if not found_analytes:
            raise ValueError(f"None of the analytes are found in the filepath. Found: {filepath}")
        
        # Append each found analyte to current_analyte in the order of appearance
        self.current_analyte.extend(found_analytes)

        return found_analytes
            
    
    def extract_labeled_data(self, data=None):

        '''
        This function extracts the labeled data from the DataFrame.

        Parameters:
            data (DataFrame): The DataFrame containing the data
        '''

        if data is None:
            data = self.data

        # Creating a new DataFrame with only the required columns
        self.data = data[['Cycle', 'Resistance', 'Time']]

        return self.data
    
    def extract_material(self, filepath=None, materials=None):

        '''
        This function allows for extraction of materials from filepath.

        Parameters:
            filepath (str): The path to the file containing the data.
            materials (set): The set of materials to be extracted.
        '''

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

        '''
        This function allows for extraction of ppm values from filepath.

        Parameters:
            filepath (str): The path to the file containing the data.
            ppm (list): The list of ppm values to be
        '''

        if filepath is None:
            filepath = self.filepath

        if self.ppm is None:

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

        '''
        This function formats the data into a dictionary.

        Parameters:
            data (DataFrame): The DataFrame containing the data
        '''

        if data is None:
            data = self.data

        # Creating DataFrame slices for 'ON', 'OFF', and 'Baseline'

        on_data = data[data['Cycle'].str.contains('on', case=False, na=False)]
        off_data = data[data['Cycle'].str.contains('off', case=False, na=False)]

        ''' Removing the 'pre' data from the 'ON' and 'OFF' data slices ''' 
        '''
        baseline_data = data[data['Cycle'].str.contains('pre', case=False, na=False)]
        '''

        final_data_array = []

        # Minimum number of data points required for 5 seconds of data
        min_data_points = int(5 / self.avg_timestep)

        # Extact reps
        reps = set([re.findall(r'\d+', cycle)[0] for cycle in data['Cycle'] if re.findall(r'\d+', cycle)])


        for i in range(len(self.ppm)):

            specific_on_data = on_data[on_data['Cycle'].str.contains('on', case=False, na=False)]
            specific_off_data = off_data[off_data['Cycle'].str.contains('off', case=False, na=False)]

            # Check if each slice has at least 10 seconds of data
            if len(specific_on_data) >= min_data_points and len(specific_off_data) >= min_data_points:
                
                date_format = re.findall(r'\d{8}', basename(self.filepath))[0]

                # Construct dictionary for each concentration level with all values in arrays
                entry = {
                    'from_file': basename(self.filepath),
                    'filename': f'{date_format}_{self.current_material}_{self.current_analyte[0]}_{self.ppm[i]}ppm_cycle{i + 1}',
                    'Analyte': self.current_analyte,
                    'Sensor Type': None,
                    'RC_on': None,
                    'RC_off': None,
                    'Material': self.current_material,
                    'ppm': self.ppm[i],
                    'timestep': self.avg_timestep,
                    'ON': specific_on_data['Resistance'].values.astype(float),
                    'OFF': specific_off_data['Resistance'].values.astype(float),
                }

                # Append the entry to the final data array
                if self.sensor_type is not None:
                    entry['Sensor Type'] = self.sensor_type
                    entry['filename'] = entry['filename'] + f'_{self.sensor_type}'

                final_data_array.append(entry)

        self.final_data = final_data_array

        return final_data_array

    def format(self):
        '''
        This function formats the data into a dictionary.

        Returns:
            final_data (list): The list of dictionaries containing the formatted data.
        '''
        self.extract_analyte()
        self.extract_avg_timestep()
        self.extract_material()
        self.extract_labeled_data()
        self.extract_ppm()
        self.format_data()

        return self.final_data

##### MAIN ######
if __name__ == "__main__":
                
    analytes = set(["H2"])

    materials = set(["CuOxSnOx"])

    filepath = "relay_data/20241105_PN1_CuOxSnOx_H2_1250ppm_2500ppm_3750ppm_1_PN1.2.csv"
    data = pd.read_csv(filepath)

    formatter = data_format(filepath, data, analytes, materials)

    formatted_data = formatter.format()

    print(formatted_data)