import pywikibot
from copy import deepcopy
from datetime import datetime
from fuzzywuzzy import fuzz

FIND_CAT = "تصنيف:لمغريب"

FIND_CAT = "تصنيف:لجغرافيا د لمغريب"

title = "لمغريب"

LOG_FILE = "log.txt"

IGNORE_FILE = "ignore.txt"

DATE_FORMAT = "%Y-%m-%d %H:%M"

START_TIME_STR = "2022-07-01 00:00"

START_TIME = datetime.strptime(START_TIME_STR,DATE_FORMAT)

site = pywikibot.Site()

def log(message):
    with open(LOG_FILE,'a',encoding='utf-8') as log:
        print(str(message))
        log.write(str(message)+'\n')

def load_ignore_list():
    with open(IGNORE_FILE,'r',encoding="utf-8") as ig:
        ignore_list = list(filter(None,ig.read().split('\n')))
    return ignore_list

IGNORE_LIST = load_ignore_list()

def isUnderCat(page, target_cat, cat_list):
    isUnderCat.count = 0
    def _isUnderCat(page, target_cat, cat_list, c):
        isUnderCat.count+=1
        if isUnderCat.count > 15:
            return False
        cats = list(page.categories())
        #print("Categories: "+str(cats))
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

page = pywikibot.Page(site,title)

#print(isUnderCat(page, pywikibot.Category(site,FIND_CAT), []))

#print(pywikibot.Page(site,FIND_CAT).oldest_revision)
#print([cat for cat in pywikibot.Category(site,FIND_CAT).articles()])

print(count_cat_articles(pywikibot.Category(site,FIND_CAT),START_TIME))


