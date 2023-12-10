import json
import os
import csv

class FileFunctions:
    def __init__(self, file_name: str = None, template_name: str = None):

        self.base_dict = {'template_name': template_name, 
                          'image_file_name': file_name,
                          'region_1': { 'title': None, 
                                        'key_values': {}
                                    },                 
                        }
        
        self.latest_key: str
        self.latest_region: str = 'region_1'

    def add_image_file_name(self, image_file_name: str):
        self.base_dict['image_file_name'] = image_file_name

    def add_region(self):
        region_number = len(self.base_dict) - 1
        self.base_dict[f'region_{region_number}'] = {'title': None, 'key_values': {}}
        self.latest_region = f'region_{region_number}'

    def add_title(self, title):
        self.base_dict[self.latest_region]['title'] = title

    def add_title_by_region(self, title, region):
        self.base_dict[region]['title'] = title

    def add_key(self, key):
        self.base_dict[self.latest_region]['key_values'][f'{key}'] = 0
        self.latest_key = f'{key}'

    def add_value(self, value):
        self.base_dict[self.latest_region]['key_values'][self.latest_key] = value

    def add_value_by_key(self, value, key):
        self.base_dict[self.latest_region]['key_values'][key] = value

    def save_template_json(self):
        file_path = self.create_file_path(self.base_dict.get('template_name'))
        with open(file_path, 'w') as file:
            json.dump(self.base_dict, file)
        
    @staticmethod
    def create_file_path(template_name: str) -> str:
        storage_directory = os.path.join(os.path.dirname(__file__), '..', '..', 'json_templates')
        absolute_path = os.path.abspath(storage_directory)
        file_path = os.path.join(absolute_path, f'{template_name}.json')

        return file_path

    @staticmethod
    def export_json_csv(template_name: str):

        file_path = FileFunctions.create_file_path(template_name=template_name)

        with open(file_path, 'r') as json_file:
            data = json.load(json_file)

        # Extract keys from the JSON data
        keys = set()
        for region in data.values():
            print(region)
            for key in region['key_values'].keys():
                keys.add(key)

        # Prepare CSV file
        csv_file_path = file_path.replace('.json', '.csv')
        with open(csv_file_path, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=['template_name', 'image_file_name', 'region', 'title'] + list(keys))
            writer.writeheader()

            # Write data to CSV file
            for region_num, region in data.items():
                for key, value in region['key_values'].items():
                    row = {
                        'template_name': data['template_name'],
                        'image_file_name': data['image_file_name'],
                        'region': region_num,
                        'title': region['title']
                    }
                    row[key] = value
                    writer.writerow(row)

        print(f"CSV file exported successfully: {csv_file_path}")

if __name__ == '__main__':

# ----- Example of using the functions to create a JSON file -----

    # FileFunctions.export_json_csv('demo1')

    template_name = input("What is the name of this template? ")

    dict = FileFunctions(template_name=template_name)

    while True:

        dict.add_title(input("What is the title of this region? "))

        while True:
            dict.add_key(input("What is the key? "))
            dict.add_value(input("What is the value? "))
            if input("Do you want to add another key? ") == 'no':
                break

        if input("Do you want to add another region? ") == 'no':
            print(dict.base_dict)
            dict.save_template_json()
            # FileFunctions.export_json_csv(dict.base_dict.get('template_name'))
            break

        else:
            dict.add_region()
