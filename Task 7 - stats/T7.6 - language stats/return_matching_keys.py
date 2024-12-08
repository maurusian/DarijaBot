import json

def find_keys_containing_string(data, search_string):
    matching_keys = [key for key in data.keys() if search_string in key]
    return matching_keys

# Load the JSON data
with open('word_struct_cleaned.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Define the search string
search_string = "هاد"

# Find and print matching keys
matching_keys = find_keys_containing_string(data, search_string)
print("Keys containing '{}':".format(search_string))
print(matching_keys)
