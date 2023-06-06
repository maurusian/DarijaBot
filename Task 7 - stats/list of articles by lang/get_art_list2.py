import pywikibot
from arywikibotlib import get_all_subcategories
import pywikibot.data.api as api
import traceback, os, json
from copy import deepcopy

DATA_FOLDER = "./data2/politicians/"

FILENAME = "moroccan_politicians_ar_new.json"

TARGET_LANG = "ar"

MAX_ARTICLE_COUNT = 1000

SMALL_ART_LIMIT = 3000

MIN_VIEWS_BY_LANG = {'ar':10, 'ary':50, 'shi':50}


MIN_VIEWS = MIN_VIEWS_BY_LANG[TARGET_LANG]

GET_FROM_LANGS = ["en","fr","es"] #"ar",
WRITE_TO_LANGS = [TARGET_LANG] #,"ary","shi"]

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
    add_new_qcodes = set()
    impr_qcodes = set()
    for qcode in qcodes:
        wkdt_site = pywikibot.Site("wikidata", "wikidata")
        item = pywikibot.Page(wkdt_site, qcode)
        if has_wikipedia_article(qcode, TARGET_LANG): # and has_wikipedia_article(qcode, "ary") and has_wikipedia_article(qcode, "shi"):
            for lang in WRITE_TO_LANGS:
                lang_site = pywikibot.Site(lang, "wikipedia")
                repo = lang_site.data_repository()
                item = pywikibot.ItemPage(repo, qcode)
                lang_title = str(item.sitelinks.get(f'{lang}wiki'))[2:-2].strip()
                if lang_title != "":
                    lang_page = pywikibot.Page(lang_site, str(item.sitelinks.get(f'{lang}wiki'))[2:-2])
                    #print()
                    if len(lang_page.text) < 3000:
                        impr_qcodes.add(qcode)
                        #break
                else:
                    add_new_qcodes.add(qcode)
        else:
            add_new_qcodes.add(qcode)
            
    return add_new_qcodes, impr_qcodes

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

if __name__=="__main__":
    print("starting...")
    qcodes = set()
    # file in os.listdir(DATA_FOLDER):

    filepath = DATA_FOLDER + FILENAME

    with open(filepath,'r',encoding="utf-8") as f:

        jason = json.loads(f.read())

        for elem in jason:
            qcodes.add(elem["item"].split('/')[-1])
    """
    with open("all_qcodes.txt","w") as qc:
        for qcode in qcodes:
            qc.write(str(qcodes)+"\n")
    """
    
    add_qcodes, impr_qcodes = filter1_items(qcodes)
    add_qcodes = filter2_items(add_qcodes)
    impr_qcodes = filter2_items(impr_qcodes)

    print("Articles to add: ")
    print('|'.join(list(add_qcodes)[:1000]))
    print("Articles to improve: ")
    print('|'.join(list(impr_qcodes)[:1000]))
