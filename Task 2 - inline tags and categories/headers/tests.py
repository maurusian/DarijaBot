import pywikibot
from pywikibot import textlib
import re

def remove_comments(text):
    """Remove commented-out sections from wiki text."""
    return re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

def has_pictures(page_name):
    text = remove_comments(page.text)
    if any(ext in text for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg']):
        return True
    if '<gallery>' in text:
        return True
    
    return False


if __name__ == "__main__":
    title = "فاس"

    site = pywikibot.Site()

    page = pywikibot.Page(site,title)

    print(has_pictures(page))
