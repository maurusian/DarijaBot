import json
import pandas as pd

def create_summary(data):
    summary_data = []

    for word, editors in data.items():
        unique_editors = len(editors)
        total_count = sum(editors.values())
        summary_data.append({
            'Word': word,
            'Unique Editors': unique_editors,
            'Total Uses': total_count
        })

    # Convert summary data to DataFrame
    summary_df = pd.DataFrame(summary_data)

    # Sort by Unique Editors (desc), then Total Uses (desc), then Word (asc)
    summary_df = summary_df.sort_values(by=['Unique Editors', 'Total Uses', 'Word'], 
                                        ascending=[False, False, True])
    return summary_df

# Load the cleaned JSON data
with open('word_struct_cleaned.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Generate summary DataFrame
summary_df = create_summary(data)

# Output summary to Excel
summary_df.to_excel('word_summary_report.xlsx', index=False)
