import pandas as pd
import re

def clean_keys_with_pipe(filename):
    # Load the Excel file
    df = pd.read_excel(filename)
    
    # Define Arabic character range and unwanted strings
    arabic_pattern = re.compile(r'[\u0600-\u06FF]')
    unwanted_strings = ["تصغير|", "بك|", "|الصورة", "|عنوان", "|تاريخ", "|صورة="]

    # Function to check if a row contains Arabic or unwanted strings
    def should_remove(row):
        key = str(row['Keys_with_Pipe'])  # Ensure key is treated as a string
        
        # Check if key contains only English letters/symbols (no Arabic)
        if not arabic_pattern.search(key):
            return True
        
        # Check for unwanted strings
        for unwanted in unwanted_strings:
            if unwanted in key:
                return True
        
        return False

    # Apply the filter to remove rows matching criteria
    df = df[~df.apply(should_remove, axis=1)]

    # Save the cleaned data to a new Excel file
    df.to_excel('cleaned_keys_with_pipe.xlsx', index=False)

# Define the Excel file to clean
filename = 'keys_with_pipe.xlsx'

# Run the cleaning function
clean_keys_with_pipe(filename)
