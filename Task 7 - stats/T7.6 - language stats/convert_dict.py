import json

WORD_STRUCT_FILENAME = "word_struct.json"

def load_word_structure():
    """
    Loads a word structure from a JSON file.

    Returns:
    dict: The word structure loaded from the file.
    """
    try:
        with open(WORD_STRUCT_FILENAME, 'r', encoding='utf-8') as file:
            word_structure = json.load(file)
        return word_structure
    except FileNotFoundError:
        print(f"The file at {WORD_STRUCT_FILENAME} was not found.")
        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON from the file.")
        return {}

def convert_dict(input_dict):
    result_dict = {}
    for key, value in input_dict.items():
        sub_dict = {}
        for entry in value:
            sub_dict[entry["user"]] = entry["count"]
        result_dict[key] = sub_dict
    return result_dict

def save_word_structure(word_structure):
    """
    Saves a word structure to a JSON file.

    Args:
    word_structure (dict): The word structure to save.
    
    """
    try:
        with open(WORD_STRUCT_FILENAME, 'w', encoding='utf-8') as file:
            json.dump(word_structure, file, ensure_ascii=False, indent=4)
        print(f"Word structure saved to {WORD_STRUCT_FILENAME}.")
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")

if __name__=="__main__":

    
    word_struct = load_word_structure()
    new_word_struct = convert_dict(word_struct)
    save_word_structure(new_word_struct)
    #"""
