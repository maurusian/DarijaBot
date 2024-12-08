import json
import pandas as pd
from collections import defaultdict

def analyze_editors(data):
    editor_stats = defaultdict(lambda: {'Unique Words': 0, 'Total Uses': 0})

    for word, editors in data.items():
        for editor, count in editors.items():
            # Update total uses for each editor
            editor_stats[editor]['Total Uses'] += count
            # Count unique words (increment only once per word for each editor)
            editor_stats[editor]['Unique Words'] += 1

    # Convert the editor statistics to a DataFrame
    editor_stats_df = pd.DataFrame([
        {'Editor': editor, 'Unique Words': stats['Unique Words'], 'Total Uses': stats['Total Uses']}
        for editor, stats in editor_stats.items()
    ])

    # Sort by the number of unique words introduced in descending order
    editor_stats_df = editor_stats_df.sort_values(by='Unique Words', ascending=False)

    return editor_stats_df

# Load the JSON data
with open('word_struct_cleaned.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Generate and sort editor statistics DataFrame
editor_stats_df = analyze_editors(data)

# Output the statistics to an Excel sheet
editor_stats_df.to_excel('editor_statistics.xlsx', index=False)
