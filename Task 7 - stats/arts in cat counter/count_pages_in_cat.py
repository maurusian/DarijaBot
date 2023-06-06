#from pgvbotLib import *
import pywikibot
from copy import deepcopy
#from sys import argv
import re, sys, os
from datetime import datetime
#import Levenshtein
from fuzzywuzzy import fuzz
from sys import argv
import json, traceback

batch_filename = "ميدياويكي:عطاشة7.1.json"


SAVE_MESSAGE = "تّصنيفات لي ناقصين تزادو من ويكيپيديا ب {}"

DATE_FORMAT = "%Y-%m-%d %H:%M"

START_TIME_STR = "2023-01-01 00:00"

FIND_CAT = "تصنيف:لمغريب"

TEST_FIND_CAT = "تصنيف:لجغرافيا د لمغريب"

LOG_FILE = "log.txt"

IGNORE_FILE = "ignore.txt"

#MOROCCO_FILE = "MOROCCO.txt"
#NOT_MOROCCO_FILE = "NOTMOROCCO.txt"

LOCAL_LOG = "task7.1.log"

SAVE_MESSAGE = "أپدييت ديال لحساب د لمقالات من "+datetime.strptime(START_TIME_STR,DATE_FORMAT).strftime("%Y.%m.%d")
#print(SAVE_MESSAGE)
MOROCCO_COUNT_TEMPLATE = "موضيل:حساب د لمقالات د لمغريب"
TEST_TEMPLATE = "موضيل:تيست ديال عطاشة 7.1"
BOT_TAG_TEMPLATE = "<noinclude>{{پاج كيعمرها بوت2}}</noinclude>"

FOOTER = "<noinclude>{{شرح}}</noinclude>"

JOB_ID_MSG_PART = "نمرة د دّوزة {}"

def read_json(site):
    batch = pywikibot.Page(site,batch_filename)

    jason = json.loads(batch.text)

    return jason

def print_to_console_and_log(MSG):
    MESSAGE = MSG+'\n'
    with open(LOCAL_LOG,'a') as log:
        log.write(MESSAGE)
    print(MSG)

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

#IGNORE_LIST = load_ignore_list()
#MOROCCO_LIST = load_morocco_list()
#print(MOROCCO_LIST)
#print(len(MOROCCO_LIST))
#NOT_MOROCCO_LIST = load_not_morocco_list()

def log(message):
    with open(LOG_FILE,'a',encoding='utf-8') as log:
        log.write(str(message)+'\n')

def isUnderCat(page, target_cat, cat_list):
    isUnderCat.count = 0
    def _isUnderCat(page, target_cat, cat_list, c):
        isUnderCat.count+=1
        if isUnderCat.count > 15:
            return False
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
                if _isUnderCat(category, target_cat, cat_list,isUnderCat.count):
                    return True
                
        log("Page "+page.title()+" is not under category "+target_cat.title())
        return False
    return _isUnderCat(page, target_cat, cat_list, isUnderCat.count)

def get_next_subcats(subcats): #subcats is a Python set
    tmp_subcats = subcats
    for subcat in tmp_subcats:
        #print(list(subcat.subcategories()))
        subcats = subcats.union(set(list(subcat.subcategories())))

    return subcats

def get_full_subcat_stack(target_cat):
    subcat_stack = get_next_subcats(set([target_cat]))
    tmp_stack = subcat_stack
    subcat_stack = get_next_subcats(subcat_stack)
    
    while tmp_stack != subcat_stack:
        print("in")
        tmp_stack = subcat_stack
        subcat_stack = get_next_subcats(subcat_stack)
        
    return subcat_stack

def filter_arts_by_creation_date(arts, creation_date):
    tmp_arts = deepcopy(arts)
    for art in tmp_arts:
        if  art.oldest_revision["timestamp"] < START_TIME:
            arts.remove(art)
    return arts


def count_cat_articles(target_cat,start_time):
    
    subcats = get_full_subcat_stack(target_cat)

    #print(subcats)
    
    articles = set()
    
    for mem in subcats:
        articles = articles.union(filter_arts_by_creation_date(set(list(mem.articles())),start_time))

    #filtered_articles = filter_arts_by_creation_date(articles, START_TIME)
    #print(filtered_articles)

    return len(articles)

site = pywikibot.Site()

#START_TIME = datetime.strptime(START_TIME_STR,DATE_FORMAT)

#last_changes = site.recentchanges(reverse=True, bot = False, start=START_TIME, namespaces=[0], redirect=False)

print_to_console_and_log('Number of passed arguments: '+str(len(argv)))
if len(argv)>2:
    local_args = argv[2:]
else:
    local_args = None

JOB_ID = None
if len(local_args)>1:
    JOB_ID = local_args[-1]
    print_to_console_and_log('Job ID '+str(JOB_ID))

#print(help(site.recentchanges))

"""
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
"""

jason = read_json(site)
for job in jason:
    
    START_TIME = datetime.strptime(job["count_from_date"],DATE_FORMAT)
    template_page = pywikibot.Page(site,job["tracking_template"])

    template_page.text = BOT_TAG_TEMPLATE+'\n\n'+str(count_cat_articles(pywikibot.Category(site,job["tracked_cat"]),START_TIME))+FOOTER

    if JOB_ID is not None:
        MESSAGE+=" - "+JOB_ID_MSG_PART.format(JOB_ID)

    template_page.save(SAVE_MESSAGE)

#"""
    
