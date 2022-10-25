import pywikibot
import json, traceback
from arywikibotlib import *
from copy import deepcopy
import os, sys

batch_filename = "ميدياويكي:عطاشة25.خدمة1.json"
wkdt_filename = "ميدياويكي:عطاشة25.خدمة1.ويكيداطا.json"

WIKILOG_PAGE_TITLE = "خدايمي:DarijaBot/عطاشة 25: لمصاوبة د تصنيفات من ويكيداطا"

CREATE_CAT_MESSAGE = batch_filename[10:-5]+':'+" تصنيف جديد تصاوب"
SAVE_MESSAGE = batch_filename[10:-5]+':'+" زيادة د تصنيف"
INTERLINK_FAILED_MSG = "تّصنيف {} ماقدرش لبوت يربطو معا شي ستون ف ويكيداطا"
LOG_SAVE_MSG = "زيادة د دخلة ف لّوحة"

LOCAL_LOG = os.path.dirname(sys.argv[0])+"\\task25.log"
RECENT_LOG_FILE = os.path.dirname(sys.argv[0])+"\\recent_log25.txt"

NOT_LINKED_TO_LOG = set()


def read_json(site,filename):
    batch = pywikibot.Page(site,filename)

    jason = json.loads(batch.text)

    return jason

def get_param_values(jason,page,lang):

    site_wkdt = pywikibot.Site('wikidata','wikidata')

    params = jason[0]["params"]
    new_params = {}

    lang_code = lang+'wiki'

    for param_name, param_code in params.items():
        if ":" in param_code:
            code_parts = param_code.split(':')
            prop_value = getItemPropertyValue(page,code_parts[0])
            print("code_parts[0]: "+str(code_parts[0]))
            print("prop_value "+str(prop_value))
            if prop_value is not None:
                qcode = 'Q'+str(prop_value)
                item = pywikibot.ItemPage(site_wkdt,qcode)
                for i in range(1,len(code_parts)):
                    prop_value_code = getItemPropertyValueFromItem(item,code_parts[i])
                    if prop_value_code is not None:
                        qcode = 'Q'+str(prop_value_code)
                        print("code_parts[0]: "+str(code_parts[0]))
                        print("prop_value "+str(prop_value))
                        item = pywikibot.ItemPage(site_wkdt,qcode)
                    else:
                        break
                if lang_code in item.sitelinks.keys():
                    new_params[param_name] = str(item.sitelinks[lang_code]).strip('[').strip(']')
                else:
                    return None
            else:
               return None
        else:
            prop_value = getItemPropertyValue(page,param_code)
            if prop_value is not None:
                qcode = 'Q'+str(prop_value)
                item = pywikibot.ItemPage(site_wkdt,qcode)
                if lang_code in item.sitelinks.keys():
                    new_params[param_name] = str(item.sitelinks[lang_code]).strip('[').strip(']')
                else:
                    return None
            else:
                return None
    #print("get_param_values")
    #print(new_params)
    return new_params

def get_actual_name(raw_cat,param_values):
    #print("get_actual_name")
    #print(param_values)
    for name, value in param_values.items():
        raw_cat = raw_cat.replace(name, value)

    return raw_cat

def get_category(jason,param_values):
    raw_cat = jason[0]["category"]

    return get_actual_name(raw_cat,param_values)

def get_max_supercat_len(jason):
    length = 0
    for key, value in jason[0].item():
        if "supercategories0" in key and len(key) > length:
            length = len(key)

    return length


def get_hypercats(key,supercat,value,jason):
    hyperkey = key+str(value.index(supercat)+1)
    print(hyperkey)
    if hyperkey in jason[0].keys():
        return jason[0][hyperkey]
    return []

def has_correct_instance(jason, param_value):
    pass
    
def create_cat_tree(jason, cat, param_values,bag_of_cats):
    

    #for i in range(len("supercategories0"),get_max_supercat_len(jason)+1):
    for key, value in jason[0].items():
        if "supercategories0" in key: # and len(key) == i:
            for supercat in value:
                supercat_actual_name = get_actual_name(supercat,param_values)
                if supercat_actual_name not in bag_of_cats:
                    supercat_page = pywikibot.Page(site,supercat_actual_name)
                    
                    tmp_text = ""
                    
                    hypercats = get_hypercats(key,supercat,value,jason)
                    print(hypercats)
                    if len(hypercats)>0:
                        for hypercat in hypercats:
                            tmp_text+='[['+get_actual_name(hypercat,param_values)+']]\n'
                        if len(tmp_text.strip()) > len(supercat_page.text):
                            supercat_page.text = tmp_text.strip()
                            supercat_page.save(SAVE_MESSAGE)
                            bag_of_cats.add(supercat_page.title())

                
    tmp_text = ""

    if len(jason[0]["supercategories0"]) > 0:
        for supercat in jason[0]["supercategories0"]:
            tmp_text+='[['+get_actual_name(supercat,param_values)+']]\n'

        cat_page = pywikibot.Page(site,cat)
            
        if len(tmp_text.strip()) > len(cat_page.text):
            cat_page.text = tmp_text.strip()
            cat_page.save(CREATE_CAT_MESSAGE)
            bag_of_cats.add(supercat_page.title())

    return bag_of_cats

def link_cats(wkdt_jason,jason,page):
    linked = False
    for cat_code_name in wkdt_jason.keys():
        cat_name = get_actual_name(cat_code_name,param_values)
        cat_ary = pywikibot.Page(site,cat_name)
        for lang, cat_lang_code_name in wkdt_jason[cat_code_name].items():
            lang_param_values = get_param_values(jason,page,lang)
            if lang_param_values is not None:
                print(str(type(cat_lang_code_name).__name__))
                if str(type(cat_lang_code_name).__name__) != 'list':
                    cat_lang_code_name = [cat_lang_code_name]
                    
                for code_name in cat_lang_code_name:
                    cat_lang_name = get_actual_name(code_name,lang_param_values)
                    print(cat_lang_name)
                    site_lang = pywikibot.Site(lang,'wikipedia')
                    cat_lang = pywikibot.Page(site_lang,cat_lang_name)

                    print("title for "+lang+" "+cat_lang.title())

                    linked = interlink_page(cat_ary,cat_lang,lang)
                    if linked:
                        break
                if linked:
                        break
                    
        if not linked:
            
            if cat_name not in NOT_LINKED_TO_LOG:
                write_to_interlink_log(INTERLINK_FAILED_MSG.format(cat_name))
                NOT_LINKED_TO_LOG.add(cat_name)
    
def write_to_interlink_log(MSG):
    WIKILOG = pywikibot.Page(site,WIKILOG_PAGE_TITLE)
    WIKILOG.text+="\n*"+MSG
    WIKILOG.save(LOG_SAVE_MSG)


site = pywikibot.Site()

jason = read_json(site,batch_filename)

wkdt_jason = read_json(site,wkdt_filename)

pool = getOnlyArticles(site)

pool_size = len(list(deepcopy(pool)))
print_to_console_and_log('Pool size: '+str(pool_size),LOCAL_LOG)

bag_of_cats = set()
i = 1
pages_in_log = load_pages_in_log(RECENT_LOG_FILE)

with open(RECENT_LOG_FILE,'a',encoding='utf-8') as f:
    
    for page in pool:
        print_to_console_and_log('*********'+str(i)+'/'+str(pool_size),LOCAL_LOG)
        if str(page.title()) not in pages_in_log:
            if jason[0]["instanceof"] in getItemIdentities(page):
                param_values = get_param_values(jason,page,'ary')
                if param_values is not None:
                    cat = get_category(jason,param_values)

                    if '[['+cat+']]' not in page.text:
                        page.text+='\n'+'[['+cat+']]'
                        page.save(SAVE_MESSAGE)
                    bag_of_cats = create_cat_tree(jason, cat, param_values, bag_of_cats)
                    
                    link_cats(wkdt_jason,jason,page)
            f.write(page.title()+'\n')
        i+=1
