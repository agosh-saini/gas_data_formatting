# ----
# Author: Agosh Saini
# Contact: contact@agoshsaini.com   
# -----
# This file is a class for data processing and formatting 

import pandas as pd
import gas_data_formatting as gdf
from PyQt5.QtWidgets import QApplication, QFileDialog
import json_db
import fe_catch_22
import os


if __name__ == '__main__':
    db_json = json_db.json_db()
    fe = fe_catch_22.fe_catch_22()

    # Create a PyQt application
    app = QApplication([])

    # Open a file dialog window for selecting multiple files
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.ExistingFiles)
    file_dialog.setNameFilter("All files (*.*)")
    file_paths = []
    if file_dialog.exec_():
        file_paths = file_dialog.selectedFiles()


    # Print the list of selected file paths
    #print("Selected file paths:")
    for filename in file_paths:
        print(filename)

    sat_ppm = {
                "Water": 28483,
                "EtOH":	70825,
                "Ace":	282973,
                "IPA": 	52302
            }
                
    analytes = set(["IPA", "Water", "EtOH", "Ace"])

    materials = set(["SnO2"])
   
   # save all the files selected
    for filename in file_paths:

        data = pd.read_csv(filename)

        formatter = gdf.data_format(filename, data, analytes, materials, sat_ppm)

        formatted_data = formatter.format()

        key, values = fe.extract_data(data=formatted_data)

        extracted_features = dict(zip(key, values))
        
        formatted_data.update(extracted_features)

        saved = db_json.save_summary_as_json(formatted_data)

        if os.path.isfile(saved):
            print(f'Completed processing of {filename}')
        else:
            raise Exception(f'Unable to process {filename}')


        