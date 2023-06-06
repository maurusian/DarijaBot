import pywikibot
from arywikibotlib import interlink_page
import json, re, traceback
#from copy import deepcopy
#import re
#from openpyxl import Workbook

#langxx_cat_ttl = "Category:Lang-x templates"


site = pywikibot.Site()

jobid = input("Job ID: ")

JOB_PAGE_TITLE_PTRN = f"ميدياويكي:عطاشة33.خدمة{jobid}.json"

TEMPLATE_ARY_NS = "موضيل"



batch_filename = JOB_PAGE_TITLE_PTRN

def read_json(site):
    batch = pywikibot.Page(site,batch_filename)

    print(batch_filename)

    jason = json.loads(batch.text)

    return jason

def get_ary_page(lang_page):
    try:
        item = pywikibot.ItemPage.fromPage(lang_page)
        if "arywiki" in item.sitelinks.keys():
            #print(str(item.sitelinks["arywiki"]))
            ary_page = pywikibot.Page(site,str(item.sitelinks["arywiki"])[2:-2])
            print("ary page: "+ary_page.title())
            return ary_page
    except:
        print(traceback.format_exc())
        return None

    

def get_var_value(TITLE_PART,title):
    value = title.replace(TITLE_PART,"").strip()

    return value

def write_to_interlink_log(MSG):
    WIKILOG = pywikibot.Page(site,WIKILOG_PAGE_TITLE)
    WIKILOG.text+="\n*"+MSG
    WIKILOG.save(LOG_SAVE_MSG)

jason = read_json(site)

MAIN_CAT = jason["MAIN_CAT"]

LANG = jason["LANG"]

TITLE_STRUCT = jason["TITLE_STRUCT"]

CREATE_TMP_SAVE_MESSAGE = jason["CREATE_TMP_SAVE_MESSAGE"]

print(TITLE_STRUCT)

VAR = re.search(r"\{\w+\}?",TITLE_STRUCT).group(0)

print(VAR)

TITLE_PART = TITLE_STRUCT.split('{')[0]

MOVE_OPTIONS = jason["MOVE_OPTIONS"]

KEYWORDS = None

if MOVE_OPTIONS is not None and len(MOVE_OPTIONS)>0:
    KEYWORDS = MOVE_OPTIONS[0]["KEYWORDS"]

print(KEYWORDS)

site_lang = pywikibot.Site(LANG,"wikipedia")

MAIN_CAT_PAGE = pywikibot.Category(site_lang,MAIN_CAT)

TEMPLATES = MAIN_CAT_PAGE.articles()

#print(TEMPLATES)

for tmp in TEMPLATES:
    print(tmp)
    var_title = get_var_value(TITLE_PART,tmp.title())
    var_page_ary = get_ary_page(pywikibot.Page(site_lang,var_title))
    ary_tmp_title1 = tmp.title().replace("Category",TEMPLATE_ARY_NS)
    ary_tmp_title2 = ary_tmp_title1
    for key,value in KEYWORDS.items():
        ary_tmp_title2 = ary_tmp_title2.replace(key,value)
    ary_titles = [ary_tmp_title1,ary_tmp_title2]
    if var_page_ary is not None:                        
        
        ary_tmp_title3 = ary_tmp_title1.replace(var_title,var_page_ary.title())

        ary_tmp_title4 = ary_tmp_title2.replace(var_title,var_page_ary.title())

        ary_titles = [ary_tmp_title1,ary_tmp_title2,ary_tmp_title3,ary_tmp_title4]
    
    TO_ADD = True
    for ary_title in ary_titles:
        
        ary_page = pywikibot.Page(site,ary_title)
        if ary_page.text != "":
            TO_ADD = False

    item = None
    #ADD_REDIR = False
    if TO_ADD:
        try:
            item = pywikibot.ItemPage.fromPage(tmp)
            #print(list(item.sitelinks.keys()))
            #break
            if "arywiki" in item.sitelinks.keys():
                TO_ADD = False
                
        except:
            print(traceback.format_exc())
            print("no Wikidata item")
            #TO_ADD = True

    if TO_ADD:
        ary_page = pywikibot.Page(site,ary_titles[-1])
        ary_page.text = tmp.text
        ary_page.save(CREATE_TMP_SAVE_MESSAGE)
        if item is not None:
            interlink_page(ary_page,tmp,"ary")
            
        
