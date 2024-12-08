import json
import pandas as pd

def find_keys_starting_with(data, start_letter):
    # Filter keys that start with the given letter
    matching_keys = [key for key in data.keys() if key.startswith(start_letter)]
    return matching_keys

# Load the JSON data
with open('word_struct_cleaned.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Define the starting letter
start_letter = "و"  # Replace "A" with the letter you want to filter by

# Find matching keys
matching_keys = find_keys_starting_with(data, start_letter)

# Convert the matching keys to a DataFrame for Excel output
df = pd.DataFrame(matching_keys, columns=["Keys"])

# Output to an Excel file
df.to_excel('keys_starting_with_letter_w.xlsx', index=False)
