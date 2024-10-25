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

if __name__ == '__main__':
    db_json = json_db.json_db()
    
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

        sat_ppm = {
                "data": 28483
            }
                
        analytes = set(["data", "Water", "EtOH", "Ace"])

        materials = set(["log"])
        
        # Split relay data into multiple files
        spliter = split_relay_data.SplitRelayData(file_name, data)
        spliter.generate_files()

        # Process and format the relay data
        for file in os.listdir(output_folder):

            # Skip the file if it is not a CSV file
            filepath = os.path.join(output_folder, file)
            data = pd.read_csv(filepath)
            
            # Skip the file if it is not a CSV file
            if not filepath.endswith('.csv'):
                continue

            # Format the data
            formatter = gas_data_formatting.data_format(filepath, data, analytes, materials, sat_ppm)
            formatted_data = formatter.format()

            # Save the formatted data as a JSON file
            json_file = db_json.save_summary_as_json(formatted_data, json_folder)

            print(f'{file_name} JSON file saved at: {json_file}')
           

    main()
