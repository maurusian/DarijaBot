import json
import pandas as pd
from collections import defaultdict

def create_letter_summary(data):
    letter_data = defaultdict(lambda: defaultdict(int))

    # Create dictionary mapping each letter to editors and their counts
    for word, editors in data.items():
        for letter in set(word):  # Use set to avoid duplicating letters within the same word
            for editor, count in editors.items():
                letter_data[letter][editor] += count

    # Convert letter_data to a JSON-compatible format
    letter_data_json = {letter: dict(editors) for letter, editors in letter_data.items()}
    
    # Prepare summary data for the Excel sheet
    summary_data = []
    for letter, editors in letter_data.items():
        unique_editors = len(editors)
        total_count = sum(editors.values())
        summary_data.append({
            'Letter': letter,
            'Unique Editors': unique_editors,
            'Total Uses': total_count
        })

    # Convert summary data to DataFrame for Excel
    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values(by=['Unique Editors', 'Total Uses', 'Letter'], 
                                        ascending=[False, False, True])

    return letter_data_json, summary_df

# Load the cleaned JSON data
with open('word_struct_cleaned.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Generate letter summary data
letter_data_json, summary_df = create_letter_summary(data)

# Output the new JSON dataset
with open('letter_data.json', 'w', encoding='utf-8') as file:
    json.dump(letter_data_json, file, ensure_ascii=False, indent=4)

# Output the summary to an Excel sheet
summary_df.to_excel('letter_summary_report.xlsx', index=False)
