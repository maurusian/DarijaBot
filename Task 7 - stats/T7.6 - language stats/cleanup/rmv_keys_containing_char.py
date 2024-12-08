import json

def remove_keys_with_pipe(data):
    # Create a new dictionary excluding keys that contain "|"
    cleaned_data = {key: value for key, value in data.items() if "=" not in key}
    return cleaned_data

# Load the JSON data
with open('cleaned_word_struct_no_pipe.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Remove keys containing the pipe character
cleaned_data = remove_keys_with_pipe(data)

# Save the cleaned data to a new JSON file
with open('cleaned_word_struct_no_equal.json', 'w', encoding='utf-8') as file:
    json.dump(cleaned_data, file, ensure_ascii=False, indent=4)
