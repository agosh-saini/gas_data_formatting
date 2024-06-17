import json
import os
import pycatch22 as catch22



# bring in data
class fe_catch_22:

    def __init__(self, file=None, key_vars=['filename', 'Analyte', 'Material'],
                    attributes=['ppm', "ON", "OFF"]) -> None:
        self.file = file
        self.key_vars = key_vars
        self.attributes = attributes

     
    def append_jsons(self, file, summaries, data=None) -> None:
        
        if data is None:
            with open(file, 'r') as json_file:
                data = json.load(json_file)


        data.update(summaries)

        with open(file, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        pass       

    def extract_data(self, data=None, file=None, append_in_place=False):

        if data is None:

            if file is None: 
                file = self.file

            with open(file, 'r') as json_file:
                data = json.load(json_file)
        

        values = [None] * len(self.attributes)

        for i, value in enumerate(self.attributes):
            results = catch22.catch22_all(data.get(value), catch24=True)
            values[i] = dict(zip(results['names'], results['values']))
        self.values = values

        attribute_key = [attribute + "_summary" for attribute in self.attributes]

        self.attribute_dicts = dict(zip(attribute_key, values))

        if append_in_place is True: 
            self.append_jsons(file, self.attribute_dicts)

        return [attribute_key, values]
    

if __name__ == "__main__":
    file_name = ''
    
    fe = fe_catch_22()


    

        