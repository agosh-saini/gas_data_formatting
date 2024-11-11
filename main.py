# ----
# Author: Agosh Saini
# Contact: contact@agoshsaini.com   
# -----
# This file is a class for data processing and formatting 

import pandas as pd
import gas_data_formatting 
import split_relay_data
import json_db
import os
import matplotlib.pyplot as plt
from shutil import rmtree
from time import time

def main(input_file=None):

    if input_file is None:
        input_file = input('Enter the path to the input file containing relay data: ')

    data = pd.read_csv(input_file)

    file_name = os.path.splitext(os.path.basename(input_file))[0]

    output_folder = os.curdir + '/relay_data'
    json_folder = os.curdir + '/json_folder'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    if not os.path.exists(json_folder):
        os.makedirs(json_folder)

    relay_current_files = set(os.listdir(output_folder))

    analytes = set(["H2", 'dryair', "EtOH.Water"])

    materials = set(["CuOxSnOx"])

    # Split relay data into multiple files
    spliter = split_relay_data.SplitRelayData(file_name, data)
    spliter.generate_files(graph=True)
    sensor_name_base = spliter.sensor_names[0].split('.')[0]

    # Process and format the relay data
    for i, file in enumerate(os.listdir(output_folder)):

        if file in relay_current_files:
            continue

        # Skip the file if it is not a CSV file
        filepath = os.path.join(output_folder, file)
        data = pd.read_csv(filepath)
        
        # Skip the file if it is not a CSV file
        if not filepath.endswith('.csv'):
            continue

        # Format the data
        formatter = gas_data_formatting.data_format(filepath, data, analytes, materials, sensor_type=f"{sensor_name_base}.{i+1}")   
        formatted_data = formatter.format()

        for i in range(len(formatted_data)):
            formatted_data[i]['filename'] = f"{formatted_data[i]['filename']}_{int(time())}"

        # Save the formatted data as a JSON file
        for i in range(len(formatted_data)):
            json_file = db_json.save_summary_as_json(formatted_data[i], json_folder)

        print(f'{file_name} JSON file saved at: {json_file}')        
    
    rmtree(output_folder)

if __name__ == '__main__':
    db_json = json_db.json_db()   

    method = input('Enter the method of data processing (F - File, D - Directory): ')

    if method == 'F':
        # Run the main function
        main()
    elif method == 'D':

        # Get list of files in directory
        folder = 'data'
        files = os.listdir(folder)

        for file in files:
            # Run the main functionPN1
            main(os.path.join(folder, file))

