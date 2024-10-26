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

def main():
    input_file = input('Enter the path to the input file containing relay data: ')

    data = pd.read_csv(input_file)

    file_name = os.path.splitext(os.path.basename(input_file))[0]

    output_folder = os.curdir + '/relay_data'
    json_folder = os.curdir + '/json_folder'
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    if not os.path.exists(json_folder):
        os.makedirs(json_folder)

    analytes = set(["data", "water", "EtOH", "Ace"])

    materials = set(["log", "mat"])

    # Split relay data into multiple files
    spliter = split_relay_data.SplitRelayData(file_name, data)
    spliter.generate_files()
    sensor_name_base = spliter.sensor_names[0].split('.')[0]

    # Process and format the relay data
    for i, file in enumerate(os.listdir(output_folder)):

        # Skip the file if it is not a CSV file
        filepath = os.path.join(output_folder, file)
        data = pd.read_csv(filepath)
        
        # Skip the file if it is not a CSV file
        if not filepath.endswith('.csv'):
            continue

        # Format the data
        formatter = gas_data_formatting.data_format(filepath, data, analytes, materials, sensor_type=f"{sensor_name_base}.{i+1}")   
        formatted_data = formatter.format()

        # Save the formatted data as a JSON file
        json_file = db_json.save_summary_as_json(formatted_data, json_folder)

        print(f'{file_name} JSON file saved at: {json_file}')

if __name__ == '__main__':
    db_json = json_db.json_db()         

    # Run the main function
    main()
