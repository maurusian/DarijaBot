import json
import pandas as pd

char = "|"

def find_keys_with_pipe(data):
    # Collect keys that contain the "|" character
    matching_keys = [key for key in data.keys() if char in key]
    return matching_keys

# Load the JSON data
with open('word_struct.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Find matching keys
matching_keys = find_keys_with_pipe(data)

# Convert the matching keys to a DataFrame for Excel output
df = pd.DataFrame(matching_keys, columns=["Keys_with_Pipe"])

# Output to an Excel file
df.to_excel('keys_with_pipe.xlsx', index=False)
