import pywikibot, re
from pywikibot import pagegenerators
from datetime import datetime, timedelta
import json
from copy import deepcopy

WORD_STRUCT_FILENAME = "word_struct.json"
RECENT_PAGES_FILENAME = "recent_pages.txt"

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

def load_recent_pages():
    try:
        with open(RECENT_PAGES_FILENAME, 'r', encoding='utf-8') as file:
            recent_pages = [recent.strip() for recent in file.read().splitlines()]
        return recent_pages
    except FileNotFoundError:
        print(f"The file at {RECENT_PAGES_FILENAME} was not found.")
        return []

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


def save_recent_pages(title):
    with open(RECENT_PAGES_FILENAME,"a",encoding="utf-8") as rec:
        rec.write(title+'\n')

def get_first_revision_text(page):
    """
    Retrieves the text and the username of the editor of the first revision of a Wikipedia article.

    Args:
    page (str): Wikipedia page.

    Returns:
    tuple: The text of the first revision of the article and the username of the editor.
    """
    # Connect to Wikipedia
    #site = pywikibot.Site('ary', 'wikipedia')
    
    # Get the page object
    #page = pywikibot.Page(site, page_title)
    
    # Get the first revision of the page
    first_revision = page.oldest_revision
    
    # Fetch the text of the first revision
    first_revision_text = page.getOldVersion(first_revision.revid)

    # Get the username of the editor of the first revision
    #username = first_revision.user

    return first_revision_text #, username


def remove_wiki_markup(raw_text):
    """
    Removes Wikipedia markup from the given text, including categories, references, file/image links, and formats links to show actual text.

    Args:
    raw_text (str): The raw text of a Wikipedia page.

    Returns:
    str: The cleaned text without Wikipedia markup.
    """
    # Remove file and image links (in English and Arabic)
    text = re.sub(r'\[\[File:.*?\]\]|\[\[Image:.*?\]\]|\[\[فيشي:.*?\]\]', '', raw_text)

    # Remove templates
    text = re.sub(r'\{\{.*?\}\}', '', text)

    # Remove references, including nested references
    text = re.sub(r'<ref[^>]*?>.*?</ref>|<ref[^>]*?/>', '', text, flags=re.DOTALL)

    # Remove categories (both in English "Category" and Arabic "تصنيف")
    text = re.sub(r'\[\[Category:.*?\]\]|\[\[تصنيف:.*?\]\]', '', text)

    # Replace links of the form [[article title|actual_text]] with actual_text
    text = re.sub(r'\[\[(?:[^\]|]*\|)?([^\]]+)\]\]', r'\1', text)

    # Remove titles
    text = re.sub(r'={2,}.*?={2,}', '', text)

    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)

    # Remove bold and italic markup
    text = re.sub(r"'''?([^']+)'''?", r'\1', text)

    return text.strip()


def extract_unique_words_darija(text):
    """
    Adjusted function to extract unique Arabic words from the given text, 
    ignoring numbers, non-word characters, and Latin letters, and ensuring 
    words mixed with numbers are split correctly.

    Args:
    text (str): The text from which to extract words.

    Returns:
    list: A list of unique Arabic words.
    """
    # Remove non-Arabic characters and numbers, replace with space
    clean_text = re.sub(r'[^ءاإآأ-يڭݣگڤپ\s]', ' ', text)

    # Replace digits with space
    clean_text = re.sub(r'\d+', ' ', clean_text)

    # Normalize multiple spaces to a single space
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    # Split the text into words and return unique words
    words = clean_text.split()

    return list(set(words))

def is_user_anonymous(username, site):
    """
    Checks if the given username represents an anonymous user on the specified site.

    Args:
    username (str): The username to check.
    site (pywikibot.Site): The site instance.

    Returns:
    bool: True if the user is anonymous, False otherwise.
    """
    user = pywikibot.User(site, username)
    return user.isAnonymous()


def update_word_counts(word_structure, word_list, user):
    """
    Updates the given structure with the words entered by a user, keeping track of the number of times 
    the user has entered each word. This allows the possibility of running the program multiple times
    without corrupting the old data or reloading words from already processed pages, in order to add
    words from new pages to the dictionary. This is also useful during development and maintenance of
    the code.

    Args:
    word_structure (dict): The structure to be updated.
    word_list (list): A list of words entered by the user.
    user (str): The username of the user who entered the words.

    Returns:
    dict: The updated structure.
    """
    for word in word_list:
        # Check if the word is already in the structure
        if word in word_structure:
            # Check if this user has already entered this word
            found_user = False
            #print("word: ",word)
            #print("value: ",word_structure[word])
            for word_user, word_count in word_structure[word].items():
                if word_user == user:
                    # Increment the count for this user
                    word_structure[word][user] += 1
                    found_user = True
                    break
            
            # If this user has not entered this word before, add a new entry
            if not found_user:
                word_structure[word][user] = 1
        else:
            # Add the word with the user and initial count
            word_structure[word] = {}
            word_structure[word][user] = 1

    return word_structure

def is_bot_user(user_name, site):
    """
    Check if the user belongs to the 'bot' group.

    Args:
    user_name (str): The username of the user.
    site (pywikibot.Site): The site instance.

    Returns:
    bool: True if the user is a bot, False otherwise.
    """
    user = pywikibot.User(site, user_name)
    return 'bot' in user.groups()


if __name__ == "__main__":
    site = pywikibot.Site('ary', 'wikipedia')
    site.login()
    i = 1
    articles = site.allpages(namespace=0, filterredir=False)
    articles_clone = list(deepcopy(articles))
    pool_size = len(articles_clone)
    print("Pool size:",pool_size)
    word_structure = load_word_structure()
    recent_pages = load_recent_pages()
    print("Recent pages:",len(recent_pages))
    print(recent_pages)
    for page in articles:
        print(f"********* {i} /",pool_size)
        if page.title() not in recent_pages:
            #print(page.title(),"already treated")
            #print(page.title())
            username = page.oldest_revision.user
            #print(username)
            if is_user_anonymous(username, site):
                username = "anonymous"
            if not username.lower().endswith('bot') and not is_bot_user(username, site):
                initial_page_text = get_first_revision_text(page)

                if initial_page_text is not None: #some first revisions may have been deleted
                
                    clean_text = remove_wiki_markup(initial_page_text)
                    
                    word_list = extract_unique_words_darija(clean_text)

                    word_structure =  update_word_counts(word_structure, word_list, username)

                    save_word_structure(word_structure)

            save_recent_pages(page.title())
        i+=1


    
    
