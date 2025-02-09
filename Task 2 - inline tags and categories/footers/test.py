import re, pywikibot

def extract_category_blocks(wikitext):
    """
    Extracts blocks of categories from the given wikitext of a Wikipedia article on arywiki.

    Parameters:
    wikitext (str): The wikitext to be parsed.

    Returns:
    list: A list of category blocks, each block containing the categories as a string.
    """
    # Regular expression to match category blocks
    category_block_pattern = r'(\[\[تصنيف:.*?\]\](?:[\s\n]*\[\[تصنيف:.*?\]\])*)'
    
    # Find all category blocks in the wikitext
    category_blocks = re.findall(category_block_pattern, wikitext, re.DOTALL)
    
    # Clean up each block by stripping extra whitespace/newlines
    cleaned_blocks = [block.strip() for block in category_blocks]
    
    return cleaned_blocks


OLD_SOURCE_TAG1 = "{{مراجع}}"
OLD_SOURCE_TAG1_PTRN = r'\{\{مراجع\|\d{2}em\}\}'
OLD_SOURCE_TAG2 = "<\s*references\s*/>"
NEW_SOURCE_TAG = "{{عيون}}"
NEW_SOURCE_TAG_PTRN = r'\{\{عيون\|\d{2}em\}\}'

###Save messages
CORRECT_SOURCE_TAG_MESSAGE = "إصلاح طّاڭ د عيون لكلام."
ADD_SOURCE_TAG_MESSAGE ="زيادة د طّاڭ د عيون لكلام."

def check_has_source_tag(text):
    """
    Checks if the pattern {{عيون|XXem}} (where XX is any two-digit number) exists in the given text.

    Parameters:
    text (str): The input text to search.

    Returns:
    bool: True if the pattern exists, False otherwise.
    """
    pattern = r'\{\{عيون\|\d{2}em\}\}'
    return bool(re.search(pattern, text)) or NEW_SOURCE_TAG in text


def setSourceTag(page,text):
    has_source_tag = check_has_source_tag(text)
    
    if not has_source_tag:
        temp = text
        text = text.replace(OLD_SOURCE_TAG1,NEW_SOURCE_TAG)

        new_pattern = r'{{عيون|\1em}}'

        matches = re.findall(OLD_SOURCE_TAG1_PTRN, text)
    
        for match in matches:
            # Replace 'مراجع' with 'عيون' in the matched text
            updated_match = match.replace('مراجع', 'عيون')
            
            # Replace the old matched text with the updated matched text in the whole text
            text = text.replace(match, updated_match)
           
        if text != temp:
            has_source_tag = True
            #MESSAGE += CORRECT_SOURCE_TAG_MESSAGE+SPACE
            text = re.sub(OLD_SOURCE_TAG2,"",text) #ensure removal of the other tag, only one is needed
            #print("changing old source tag (1) with new one")

        temp = text
        #new_text = new_text.replace(OLD_SOURCE_TAG2,NEW_SOURCE_TAG)
        text = re.sub(OLD_SOURCE_TAG2,NEW_SOURCE_TAG,text)
            
        if text != temp:
            has_source_tag = True
            #MESSAGE += CORRECT_SOURCE_TAG_MESSAGE+SPACE
            text = text.replace(OLD_SOURCE_TAG1,"") #ensure removal of the other tag, only one is needed
            #print("changing old source tag (2) with new one")

    if not has_source_tag:
        text+="\n"+NEW_SOURCE_TAG
        #MESSAGE += ADD_SOURCE_TAG_MESSAGE+SPACE

    return text #,MESSAGE

# Example usage:
wikitext_example = """
Some text before categories

[[:تصنيف:صحافة]]
[[تصنيف:تواصل]]

Some text in between

[[تصنيف:إعلام]]
"""

print(extract_category_blocks(wikitext_example))



site = pywikibot.Site()

title = "تأمين معبر لݣرݣرات 2020"

page = pywikibot.Page(site,title)

print(extract_category_blocks(page.text))

text = setSourceTag(page,page.text)
print(text[-1000:])


def remove_extra_empty_lines(text):
    """
    Removes extra empty lines from the given text, ensuring at most one empty line
    exists between two non-empty lines. Handles lines containing only spaces as empty.

    Parameters:
    text (str): The input text.

    Returns:
    str: The modified text with extra empty lines removed.
    """
    # Pattern to match multiple empty lines (lines with only spaces or nothing)
    cleaned_text = re.sub(r'(\n\s*\n)+', '\n\n', text)
    
    # Return the cleaned text
    return cleaned_text.strip()

# Example usage:
text_example = """
This is a line.

   

Another line.

   


Yet another line.
"""
print(remove_extra_empty_lines(text_example))
