import json
import pandas as pd
from collections import defaultdict

def load_allowed_characters(filename):
    # Load the allowed characters from the first column of the Excel file
    df = pd.read_excel(filename, usecols=[0]) #, skiprows=1)  # Skip header
    # Convert the column to a set of characters for faster lookups
    allowed_characters = set(df.iloc[:, 0].astype(str).str.strip())
    return allowed_characters

def clean_up_json(data, allowed_characters):
    cleaned_data = defaultdict(lambda: defaultdict(int))

    for key, value in data.items():
        # Filter the key to keep only allowed characters
        new_key = ''.join(c for c in key if c in allowed_characters)

        # Skip keys that become empty
        if not new_key.strip():
            continue

        # Consolidate values if keys collide after cleaning
        for user, count in value.items():
            cleaned_data[new_key][user] += count

    # Convert back to a regular dictionary for output
    return dict(cleaned_data)

# Example usage
allowed_characters = load_allowed_characters('arywiki characters frequency.xlsx')

with open('cleaned_word_struct_no_equal.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

cleaned_data = clean_up_json(data, allowed_characters)

with open('word_struct_cleaned.json', 'w', encoding='utf-8') as file:
    json.dump(cleaned_data, file, ensure_ascii=False, indent=4)
