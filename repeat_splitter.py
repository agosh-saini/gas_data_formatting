# ----
# Author: Agosh Saini
# Contact: contact@agoshsaini.com   
# -----
# This file is a class for data processing and formatting

##### IMPORTS #####

import pandas as pd
import re
import os

##### CLASS DEFINITION #####

class cycle_data_formatter:

    def __init__(self, filepath=None, data=None, output_dir="repeat_data"):
        """
        Initializes the CycleDataFormatter with the data filepath or DataFrame and output directory.

        Parameters:
            filepath (str): Path to the input data file. Optional if data is provided.
            data (DataFrame): DataFrame containing the input data. Optional if filepath is provided.
            output_dir (str): Directory to save the output files. Defaults to "repeat_data".
        """

        # Initialize instance variables
        self.filepath = filepath
        self.output_dir = output_dir
        self.data = data

        if self.data is not None:
            self.validate_data()


        # Initialize other variables
        self.baseline_data = None
        self.date_format = None
        self.base_filename = None
        self.repeat_count = None  
        
        # Create output directory if it does not exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Check if data is provided; if not, load data from the file
        if self.data is None and self.filepath is not None:
            self.load_data()
        elif self.data is None:
            raise ValueError("Either filepath or data (DataFrame) must be provided.")

        # Parse filename details if filepath is provided
        if self.filepath is not None:
            self.parse_filename_details()


    def validate_data(self):
        """
        Validates the structure and content of the input data.

        Parameters:
            None
        """
        required_columns = ['Cycle']
        for col in required_columns:
            if col not in self.data.columns:
                raise ValueError(f"Required column '{col}' is missing from the data.")


    def load_data(self):

        """
        Loads the data from the specified filepath and extracts baseline data.

        Parameters:
            None
        """

        # Check if file exists before loading
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"File not found: {self.filepath}")
        
        # Load data from the file
        print(f"Loading data from {self.filepath}")
        self.data = pd.read_csv(self.filepath)

        # Ensure 'Cycle' column is present
        if 'Cycle' not in self.data.columns:
            raise ValueError("The 'Cycle' column is missing in the data.")    

        ''' Removing the following code block as it is not needed for the current implementation '''

        '''  
        # Extract baseline data (assumed labeled "Pre")
        self.baseline_data = self.data[self.data['Cycle'].str.contains('pre', case=False, na=False)]

        if self.baseline_data.empty:
            print("Warning: Baseline data is empty. Ensure the 'Cycle' column contains 'Pre' labeled rows.")
        '''

    def parse_filename_details(self):
        """
        Parses details from the filename, such as the date and repeat count.

        Parameters:
            None
        """

        # Extract date and repeat count from the filename
        self.base_filename = os.path.splitext(os.path.basename(self.filepath))[0]
        date_match = re.search(r'\d{8}', self.base_filename)
        repeat_match = re.search(r'rep=(\d+)', self.base_filename)
        
        # Check if date and repeat count are found in the filename
        if date_match:
            self.date_format = date_match.group(0)
        else:
            raise ValueError("Date not found in filename. Expected format YYYYMMDD.")
        
        # Check if repeat count is found in the filename
        if repeat_match:
            self.repeat_count = int(repeat_match.group(1))
        else:
            raise ValueError("Repeat count not found in filename. Expected format 'rep=N'.")

    def save_cycle(self, cycle_combined, repeat_num):
        """
        Saves the given cycle data to a file with the specified repeat number.

        Parameters:
            cycle_combined (DataFrame): Combined DataFrame of "On" and "Off" cycle data.
            repeat_num (int): The current repeat number for the cycle.
        """
        # Check if the combined data is empty before saving
        if cycle_combined.empty:
            print(f"Warning: Combined cycle data is empty for repeat {repeat_num}. Skipping save.")
            return

        # Ensure the output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

        # Save the combined cycle data to a CSV file
        output_filename = os.path.join(self.output_dir, f"{self.date_format}_{self.base_filename}_rep={repeat_num}.csv")
        cycle_combined.to_csv(output_filename, index=False)

        print(f"File {output_filename} has been saved.")


    def process_cycles(self):
        """
        Processes the data to find each "Run-On" and "Off" cycle pair by repeat number,
        combining and saving them together.

        Parameters:
            None
        """
        # Validate 'Cycle' column
        if 'Cycle' not in self.data.columns:
            raise ValueError("The 'Cycle' column is missing in the data.")

        # Prepare regex patterns for matching cycles
        on_pattern = r"Run-On Cycle \(Repeat (\d+)\)"
        off_pattern = r"Off Cycle \(Repeat (\d+)\)"

        # Extract and filter "Run-On" and "Off" cycles
        on_cycles = self.data[self.data['Cycle'].str.contains(on_pattern, case=False, na=False, regex=True)]
        off_cycles = self.data[self.data['Cycle'].str.contains(off_pattern, case=False, na=False, regex=True)]

        # Extract repeat numbers
        on_cycles['Repeat'] = on_cycles['Cycle'].str.extract(on_pattern, expand=False).astype(int)
        off_cycles['Repeat'] = off_cycles['Cycle'].str.extract(off_pattern, expand=False).astype(int)

        # Find unique repeats in both "Run-On" and "Off" cycles
        on_repeats = set(on_cycles['Repeat'])
        off_repeats = set(off_cycles['Repeat'])
        all_repeats = sorted(on_repeats & off_repeats)  # Only consider repeats that exist in both

        if not all_repeats:
            raise ValueError("No matching 'Run-On' and 'Off' cycle pairs found.")

        # Process each repeat
        for repeat_num in all_repeats:
            try:
                # Select "Run-On" and "Off" cycle data for this repeat
                on_data = on_cycles[on_cycles['Repeat'] == repeat_num]
                off_data = off_cycles[off_cycles['Repeat'] == repeat_num]

                # Combine the data for this repeat
                combined_data = pd.concat([on_data, off_data])

                # Save combined cycle data
                self.save_cycle(combined_data, repeat_num)
            except Exception as e:
                print(f"Error processing repeat {repeat_num}: {e}")


    def run(self):
        """
        Runs the data processing and saving of cycles.
        """
        # Ensure repeat count is set if no filepath was provided
        if self.repeat_count is None:
            raise ValueError("Repeat count must be specified when providing data directly.")

        self.process_cycles()


#### EXAMPLE USAGE ####
if __name__ == "__main__":
    # Example with a DataFrame input
    df = pd.DataFrame({
        "Cycle": ["Pre", "On1", "Off1", "On2", "Off2"],
        "Data": [1, 2, 3, 4, 5]
    })
    formatter = cycle_data_formatter(data=df, output_dir="repeat_data")
    formatter.repeat_count = 2  # Set repeat count manually when using a DataFrame
    formatter.run()
