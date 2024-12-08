import pandas as pd

def excel_column_to_list(filename, column_name):
    # Load the Excel file and specified column
    df = pd.read_excel(filename, usecols=[column_name])
    
    # Convert the column to a list
    keys_list = df[column_name].dropna().tolist()
    
    return keys_list

# Define the Excel file and column name
filename = 'keys_starting_with_letter.xlsx'  # Replace with your file name
column_name = 'Keys'  # Replace with the column name if different

# Convert and print the list
keys_list = excel_column_to_list(filename, column_name)
print("Python list of keys from the Excel sheet:")
print(keys_list)
