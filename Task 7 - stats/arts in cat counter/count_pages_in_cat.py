#from pgvbotLib import *
import pywikibot
from copy import deepcopy
#from sys import argv
import re, sys, os
from datetime import datetime
#import Levenshtein
from fuzzywuzzy import fuzz

SAVE_MESSAGE = "تّصنيفات لي ناقصين تزادو من ويكيپيديا ب {}"

DATE_FORMAT = "%Y-%m-%d %H:%M"

START_TIME_STR = "2022-01-15 00:00"

FIND_CAT = "تصنيف:المغريب"

LOG_FILE = "log.txt"

IGNORE_FILE = "ignore.txt"

MOROCCO_FILE = "MOROCCO.txt"
NOT_MOROCCO_FILE = "NOTMOROCCO.txt"

SAVE_MESSAGE = "أپدييت ديال لحساب د لمقالات من "+datetime.strptime(START_TIME_STR,DATE_FORMAT).strftime("%Y.%m.%d")
#print(SAVE_MESSAGE)
MOROCCO_COUNT_TEMPLATE = "قالب:حساب د لمقالات د لمغريب"
BOT_TAG_TEMPLATE = "<noinclude>{{پاج كيعمرها بوت2}}</noinclude>"

def load_ignore_list():
    with open(IGNORE_FILE,'r',encoding="utf-8") as ig:
        ignore_list = list(filter(None,ig.read().split('\n')))
    return ignore_list

def load_morocco_list():
    with open(MOROCCO_FILE,'r',encoding="utf-8") as m:
        morocco_list = list(filter(None,m.read().split('\n')[:-1]))
    return morocco_list

def load_not_morocco_list():
    with open(NOT_MOROCCO_FILE,'r',encoding="utf-8") as nm:
        not_morocco_list = list(filter(None,nm.read().split('\n')[:-1]))
    return not_morocco_list

IGNORE_LIST = load_ignore_list()
MOROCCO_LIST = load_morocco_list()
#print(MOROCCO_LIST)
#print(len(MOROCCO_LIST))
NOT_MOROCCO_LIST = load_not_morocco_list()

def log(message):
    with open(LOG_FILE,'a',encoding='utf-8') as log:
        log.write(str(message)+'\n')

def isUnderCat(page, target_cat, cat_list):
    cats = list(page.categories())
    if len(cats) == 0:
        log("no categories found for page :"+page.title())
        return False
    if target_cat in cats:
        return True

    temp_cat_list = deepcopy(cat_list) #assignment alone creates a shallow copy

    cat_list += cats

    cat_list = list(set(cat_list))

    log('length temp_cat_list '+str(len(temp_cat_list)))
    log('length cat_list '+str(len(cat_list)))

    if len(temp_cat_list) == len(cat_list):
        log("no new categories discovered for page :"+page.title())
        return False
    
    cats = sorted(cats,key = lambda x:fuzz.partial_ratio(FIND_CAT[6:],x.title()[6:]),reverse=True)
    for category in cats:
        if not category.isHiddenCategory() and category.title() not in IGNORE_LIST:
            log("going through categories of page "+page.title())
            if isUnderCat(category, target_cat, cat_list):
                return True
            
    log("Page "+page.title()+" is not under category "+target_cat.title())
    return False


site = pywikibot.Site()

title = "بيل كلينطون"

page = pywikibot.Page(site,title)

#print(list(page.categories())[1].isHiddenCategory())
"""
for category in page.categories():
    cat_title = category.title()
    print(cat_title)
    print("String distance :"+str(fuzz.partial_ratio(FIND_CAT[6:],cat_title[6:]))



target_cat = pywikibot.Category(site,FIND_CAT)

t1 = datetime.now()

print(isUnderCat(page, target_cat, []))

t2 = datetime.now()

print(t2-t1)

"""

START_TIME = datetime.strptime(START_TIME_STR,DATE_FORMAT)

last_changes = site.recentchanges(reverse=True, bot = False, start=START_TIME, namespaces=[0], redirect=False)

#print(help(site.recentchanges))

pool = list(set([pywikibot.Page(site, item['title']) for item in last_changes])) # if (item['type'] == 'new')

pool_size = len(list(deepcopy(pool)))
print('Pool size: '+str(pool_size))

i = 1
#counter = 0
target_cat = pywikibot.Category(site,FIND_CAT)

for page in pool:
    print('*********'+str(i)+'/'+str(pool_size))
    
    #print(dir(page))
    #print(list(page.revisions())[-1]['timestamp'])
    page_title = page.title()
    if page_title not in MOROCCO_LIST and page_title not in NOT_MOROCCO_LIST and page.exists() and page.text != "":
        creation_time = list(page.revisions())[-1]['timestamp']
        if creation_time >= START_TIME:
            if isUnderCat(page, target_cat, []):
            
                #counter+=1
                #print(counter)
                with open('MOROCCO.txt','a',encoding='utf-8') as m:
                    m.write(page_title+'\n')
            else:
                with open('NOTMOROCCO.txt','a',encoding='utf-8') as nm:
                    nm.write(page_title+'\n')
    
    i+=1

MOROCCO_LIST = load_morocco_list()
print("Total created pages: "+str(len(MOROCCO_LIST)))

template_page = pywikibot.Page(site,MOROCCO_COUNT_TEMPLATE)

template_page.text = BOT_TAG_TEMPLATE+'\n\n'+str(len(MOROCCO_LIST))

template_page.save(SAVE_MESSAGE)

#"""
    
