# ----
# Author: Agosh Saini
# Contact: contact@agoshsaini.com   
# -----
# This file is a class for data processing and formatting 

import numpy as np
import pandas as pd
import gas_data_formatting as gdf
from PyQt5.QtWidgets import QApplication, QFileDialog
import relation_db as db


if __name__ == '__main__':

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
    print("Selected file paths:")
    for filename in file_paths:
        print(filename)

    sat_ppm = {
                "Water": 28483,
                "EtOH":	70825,
                "Ace":	282973,
                "IPA": 	52302
            }
                
    analytes = set(["IPA", "Water", "EtOH", "Ace"])
   
    for filename in file_paths:

        data = pd.read_csv(filename)

        formatter = gdf.data_format(filename, data, analytes, sat_ppm)

        formatted_data = formatter.format()

        hub = db.relation_db("formatted_data.db")
        db_path, db_name = hub.create_db()
        hub.create_table()
        hub.add_to_table(formatted_data["filename"], formatted_data['Analyte'], str(formatted_data['ppm']),
                        str(formatted_data['ON']), str(formatted_data['OFF']))
