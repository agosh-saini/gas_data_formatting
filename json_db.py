import json
import os
import re
import numpy as np

'''
Contact: Agosh Saini (as7saini@uwaterloo.ca)
---------
This class handles the database generation for data management for the experiments being conducted
'''


class json_db:

    # initializing class
    def __init__(self, directory='json_folder'):
        self.directory =  directory
        pass
    
    def save_summary_as_json(self, data_dict, directory=None):
        if directory is None: directory = self.directory

        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)
        
        # Use the 'filename' attribute to create a unique filename
        filename_without_ext = re.sub(r'\.txt$', '', data_dict['filename'], flags=re.IGNORECASE)
        json_filename = os.path.join(directory, filename_without_ext + '.json')
    
        # Convert numpy arrays to lists
        for key, value in data_dict.items():
            if isinstance(value, np.ndarray):
                data_dict[key] = value.tolist()
        
        # Save the data dictionary as a JSON file
        with open(json_filename, 'w') as json_file:
            json.dump(data_dict, json_file, indent=4)

