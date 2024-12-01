#######
#  Author: Agosh Saini
# Contact: contact@agoshsaini.com   
#######
# This file is a class for data processing and formatting 
#######


###### IMPORTS ######
import pandas as pd
import gas_data_formatting 
import split_relay_data
import json_db
import os
import time 
import re

from shutil import rmtree
from repeat_splitter import cycle_data_formatter


###### FUNCTIONS ######

def clear_folder(folder):
    """
    Safely clears all contents of a folder.

    Parameters:
        folder (str): Path to the folder to clear.
    """

    # Check if the folder exists, and clear it if it does
    if os.path.exists(folder):

        # Iterate through all files and subdirectories in the folder
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)

            # Attempt to remove the file or directory
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove the file or link

                elif os.path.isdir(file_path):
                    rmtree(file_path)  # Remove the directory

            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
                
    else:
        os.makedirs(folder)  # Create the folder if it does not exist

def main(input_file=None, data=None, rep_method='R'):
    """
    Main function for processing and formatting relay data.

    Parameters:
        input_file (str): Path to the input file containing relay data (optional if data is provided).
        data (DataFrame): DataFrame containing relay data (optional if input_file is provided).
    """

    # Define folders for output
    output_folder = os.path.join(os.curdir, 'relay_data')
    repeat_output_folder = os.path.join(os.curdir, 'repeat_data')
    json_folder = os.path.join(os.curdir, 'json_folder')

    # Ensure necessary output directories exist, but do not clear json_folder to preserve JSON files

    for folder in [output_folder, repeat_output_folder]:
        clear_folder(folder)

    if not os.path.exists(json_folder):
        os.makedirs(json_folder)

    # Set up cycle_data_formatter for splitting data into repeats
    if data is None:

        if input_file is None:
            input_file = input('Enter the path to the input file containing relay data: ')

        formatter = cycle_data_formatter(filepath=input_file, output_dir=repeat_output_folder)

    else:
        formatter = cycle_data_formatter(filepath="provided_data", data=data, output_dir=repeat_output_folder)

    ####### Split the input data into repeats and save each repeat as a separate file #######
    formatter.run()

    ########## Process and format relay data for each repeat ##########

    analytes = {"Ace"}
    materials = {"CuOxSnOx"}

    db_json = json_db.json_db()

    for idx, repeat_file in enumerate(os.listdir(repeat_output_folder)):

        repeat_file_path = os.path.join(repeat_output_folder, repeat_file)

        if not repeat_file_path.endswith('.csv'):
            continue

        # Print the repeat file to confirm it's being processed
        print(f"Processing repeat file: {repeat_file}")

        repeat_data = pd.read_csv(repeat_file_path)

        # Extract base filename for clarity
        file_name = os.path.splitext(repeat_file)[0]
        file_name = file_name[9:]  # Adjust if necessary for naming consistency

        # Initialize SplitRelayData to split relay data for the current repeat file
        spliter = split_relay_data.SplitRelayData(file_name, repeat_data)
        spliter.generate_files(graph=True)

        if rep_method == 'R':
            # **Step 3: Format relay data and save to JSON immediately after generating graphs**
            for relay_file in os.listdir(output_folder):

                relay_file_path = os.path.join(output_folder, relay_file)

                if not relay_file.endswith('.csv'):
                    continue

                # Make sure we are only processing files related to the current repeat
                if not relay_file.startswith(file_name):
                    continue

                relay_data = pd.read_csv(relay_file_path)

                if relay_data.empty:
                    print(f"Skipping empty relay data for file: {relay_file_path}")
                    continue

                # Base name extraction
                relay_base_name = os.path.splitext(os.path.basename(relay_file_path))[0]

                # Deduce sensor name base (PN sensor label) and use repeat information from file_name
                sensor_name_base = re.findall(r'PN\d+\.\d+', relay_base_name)[0] if 'PN' in relay_base_name else input('Enter the sensor name base: ')

                # Generate the unique JSON filename using the PN sensor label, repeat, and timestamp
                timestamp = int(time.time())
                json_filename_base = f"{relay_base_name}_{timestamp}"

                # Process and format the relay data using gas_data_formatting
                formatter = gas_data_formatting.data_format(
                    filepath=relay_file_path, 
                    data=relay_data, 
                    analytes=analytes, 
                    materials=materials, 
                    sensor_type=sensor_name_base
                )

                formatted_data = formatter.format()

                for entry in formatted_data:
                    print(entry['ON'])

                
                # Save formatted data as JSON
                for entry in formatted_data:
                    # Prepare the base path for the JSON file
                    json_file_path = os.path.join(json_folder, f"{json_filename_base}.json")

                    # Check if file already exists, if it does, append a counter to ensure uniqueness
                    counter = 1
                    
                    while os.path.exists(json_file_path):
                        json_file_path = os.path.join(json_folder, f"{json_filename_base}_{counter}.json")
                        counter += 1

                    # Set file name to json file name
                    entry['filename'] = os.path.splitext(os.path.basename(json_file_path))[0]

                    try:
                        # Save the summary as JSON using the updated unique filename
                        db_json.save_summary_as_json(entry, json_folder)
                        print(f'JSON file saved at: {json_file_path}')
                    except Exception as e:
                        print(f"Erfror saving JSON for file {json_filename_base}: {e}")

        if rep_method == 'C':

            # **Step 3: Format relay data and save to JSON immediately after generating graphs**
            for relay_file in os.listdir(output_folder):

                relay_file_path = os.path.join(output_folder, relay_file)

                if not relay_file.endswith('.csv'):
                    continue

                # Make sure we are only processing files related to the current repeat
                if not relay_file.startswith(file_name):
                    continue

                relay_data = pd.read_csv(relay_file_path)

                if relay_data.empty:
                    print(f"Skipping empty relay data for file: {relay_file_path}")
                    continue

                # Base name extraction
                relay_base_name = os.path.splitext(os.path.basename(relay_file_path))[0]

                # Deduce sensor name base (PN sensor label) and use repeat information from file_name
                sensor_name_base = re.findall(r'PN\d+\.\d+', relay_base_name)[0] if 'PN' in relay_base_name else input('Enter the sensor name base: ')

                # Generate the unique JSON filename using the PN sensor label, repeat, and timestamp
                timestamp = int(time.time())
                json_filename_base = f"{relay_base_name}_{timestamp}"

                extract_ppm = re.findall(r'(\d+)ppm', relay_base_name)

                formatted_data = []

                formatter = gas_data_formatting.data_format(
                    filepath=relay_file_path,
                    data=relay_data,
                    analytes=analytes,
                    materials=materials,
                    sensor_type=sensor_name_base,
                    ppm=[extract_ppm[idx]]
                )
                
                formatted_data = formatter.format()
                
                for entry in formatted_data:
                    # Prepare the base path for the JSON file
                    json_file_path = os.path.join(json_folder, f"{json_filename_base}.json")

                    # Check if file already exists, if it does, append a counter to ensure uniqueness
                    counter = 1

                    while os.path.exists(json_file_path):
                        json_file_path = os.path.join(json_folder, f"{json_filename_base}_{counter}.json")
                        counter += 1

                    # Set file name to json file name

                    entry['filename'] = os.path.splitext(os.path.basename(json_file_path))[0]

                    try:
                        # Save the summary as JSON using the updated unique filename
                        db_json.save_summary_as_json(entry, json_folder)
                        print(f'JSON file saved at: {json_file_path}')
                    except Exception as e:
                        print(f"Error saving JSON for file {json_filename_base}: {e}")
                    
                      

    # Final cleanup of temporary folders after processing the current input file
    clear_folder(repeat_output_folder)
    clear_folder(output_folder)


if __name__ == '__main__':
    db_json = json_db.json_db()

    method = input('Enter the method of data processing (F - File, D - Directory): ')
    rep_or_cascase = input('Enter the method of data processing (R - Repeat PPM, C - Cascade PPM): ')

    if method == 'F':
        # Run the main function with a single file input
        main(rep_method=rep_or_cascase)
    elif method == 'D':
        # Process all files in a specified directory
        folder = 'data'
        files = os.listdir(folder)
        for file in files:
            print(f'Processing file: {file}')
            main(os.path.join(folder, file), rep_method=rep_or_cascase)

        # Remove temp forlders
        os.rmdir('relay_data')
        os.rmdir('repeat_data')


