import pywikibot
import pywikibot.data.api as api
import traceback, os, json
from copy import deepcopy
import time


DATA_FOLDER = "./data2/"

MAX_ARTICLE_COUNT = 1000

SMALL_ART_LIMIT = 3000

MIN_VIEWS = 10000

def has_wikipedia_article(qcode, lang):
    lang_site = pywikibot.Site(lang, "wikipedia")
    repo = lang_site.data_repository()
    item = pywikibot.ItemPage(repo, qcode)
    try:
        item.get()
        
    except pywikibot.NoPage:
        return False
    
    return True
