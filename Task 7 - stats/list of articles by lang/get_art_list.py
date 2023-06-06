#from pgvbotLib import *
import pywikibot
from arywikibotlib import get_all_subcategories
import pywikibot.data.api as api
import traceback
from copy import deepcopy
#from sys import argv
#import re, sys, os
#from datetime import datetime, timedelta
#import Levenshtein
#from fuzzywuzzy import fuzz

MAX_ARTICLE_COUNT = 1000

SMALL_ART_LIMIT = 3000

MIN_VIEWS = 10000

GET_FROM_LANGS = ["en","fr","ar","es"]

WRITE_TO_LANGS = ["ar","ary","shi"]

MOROCCO_CATS = {"en":"Category:Morocco"
               ,"fr":"Catégorie:Maroc"
               ,"ar":"تصنيف:المغرب"
               ,"es":"Categoría:Marruecos"
               ,"shi":"Taggayt:Lmɣrib"
               ,"ary":"تصنيف:لمغريب"
               }

#IGNORE_LIST = ["CommonsDelinker"]

SAVE_MESSAGE = ""

SAVE_PAGE = ""

LOG_FILE = "log.txt"

HEADER = ""

FOOTER = """

"""

BODY = """

"""

"""
site = pywikibot.Site()

en_site = pywikibot.Site("en", "wikipedia")

test_title = "لمغريب"
test_en_title = "Morocco"
test_qcode = "Q1028"

wkdt_site = pywikibot.Site("wikidata", "wikidata")
test_item = pywikibot.Page(wkdt_site, test_qcode)

test_page = pywikibot.Page(site,test_title)

test_en_page = pywikibot.Page(en_site,test_en_title)


req = api.Request(site=site, parameters={'action': 'query', #https://www.wikidata.org/w/api.php?action=query&titles=Q42&prop=pageviews
                                        'titles': test_item.title(),
                                        'prop': 'pageviews'})


req = api.Request(site=en_site, parameters={'action': 'query', #https://www.wikidata.org/w/api.php?action=query&titles=Q42&prop=pageviews
                                        'titles': test_en_page.title(),
                                        'prop': 'pageviews'})


print(sum([int(x) for x in req.submit()['query']['pages'][str(test_en_page.pageid)]['pageviews'].values()]))
"""

def has_wikipedia_article(qcode, lang):
    lang_site = pywikibot.Site(lang, "wikipedia")
    repo = lang_site.data_repository()
    item = pywikibot.ItemPage(repo, qcode)
    try:
        item.get()
        
    except pywikibot.NoPage:
        return False
    
    return True

def filter1_items(qcodes):
    new_qcodes = set()
    for qcode in qcodes:
        wkdt_site = pywikibot.Site("wikidata", "wikidata")
        item = pywikibot.Page(wkdt_site, qcode)
        if has_wikipedia_article(qcode, "ar") and has_wikipedia_article(qcode, "ary"): # and has_wikipedia_article(qcode, "shi"):
            for lang in WRITE_TO_LANGS:
                lang_site = pywikibot.Site(lang, "wikipedia")
                repo = lang_site.data_repository()
                item = pywikibot.ItemPage(repo, qcode)
                lang_title = str(item.sitelinks.get(f'{lang}wiki'))[2:-2].strip()
                if lang_title != "":
                    lang_page = pywikibot.Page(lang_site, str(item.sitelinks.get(f'{lang}wiki'))[2:-2])
                    #print()
                    if len(lang_page.text) < 3000:
                        new_qcodes.add(qcode)
                        break
                else:
                    new_qcodes.add(qcode)
        else:
            new_qcodes.add(qcode)
            
    return new_qcodes

def get_total_views(site,page):
    
    req = api.Request(site=site, parameters={'action': 'query', #https://www.wikidata.org/w/api.php?action=query&titles=Q42&prop=pageviews
                                        'titles': page.title(),
                                        'prop': 'pageviews'})

    return sum([int(x) for x in req.submit()['query']['pages'][str(page.pageid)]['pageviews'].values() if x is not None])

def filter2_items(qcodes):
   
    qcode_views = {}
    for qcode in qcodes:
        total_views = 0
        for lang in GET_FROM_LANGS+WRITE_TO_LANGS:
            lang_site = pywikibot.Site(lang, "wikipedia")
            repo = lang_site.data_repository()
            item = pywikibot.ItemPage(repo, qcode)
            lang_title = str(item.sitelinks.get(f'{lang}wiki'))[2:-2].strip()
            if lang_title != "":
                lang_page = pywikibot.Page(lang_site, str(item.sitelinks.get(f'{lang}wiki'))[2:-2])
                total_views+=get_total_views(lang_site,lang_page)
                if total_views > MIN_VIEWS:
                    break

                
        qcode_views[qcode] = total_views

    return set([qc for qc in qcode_views.keys() if qcode_views[qc] > MIN_VIEWS])
        


cats = set()
qcodes =  set()
for lang in ["ary","shi"]:
    print("starting treatment for lang "+lang)
    lang_site = pywikibot.Site(lang, "wikipedia")
    lang_cat_title = MOROCCO_CATS[lang]
    
    cats = cats.union(get_all_subcategories(lang_site,lang_cat_title))

    articles = set()
    for cat in cats:
        articles = articles.union(set(cat.articles()))

    lang_qcodes = set()
    for a in articles:
        try:
            lang_qcodes.add(a.data_item().id)
        except:
            #print(traceback.format_exc())
            continue
    lang_qcodes = filter1_items(lang_qcodes)
    qcodes = filter2_items(qcodes.union(lang_qcodes))
    print("ended treatment for lang "+lang)

print('|'.join(list(qcodes)[:1000]))
