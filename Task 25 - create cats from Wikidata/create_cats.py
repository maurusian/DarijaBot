import pywikibot
import json, traceback
from arywikibotlib import *
from copy import deepcopy
import os, sys

MAIN_PARAM_PAGE = "ميدياويكي:عطاشة25.خدامي.json"

#batch_filename = "ميدياويكي:عطاشة25.خدمة1.json"
#wkdt_filename = "ميدياويكي:عطاشة25.خدمة1.ويكيداطا.json"

LOCAL_LOG = os.path.dirname(sys.argv[0])+"\\task25.log"
RECENT_LOG_FILE = os.path.dirname(sys.argv[0])+"\\recent_log25.txt"

NOT_LINKED_TO_LOG = set()


def get_main_task_params():
    """
    Load generic parameters from parameter json page on Mediawiki ns.
    These generic paramters are the same for all DarijaBot Task 25 jobs.
    """
    param_page = pywikibot.Page(site,MAIN_PARAM_PAGE)

    pjason = json.loads(param_page.text)

    return pjason


def read_json(site,filename):
    """
    Load job parameters from job json page on Mediawiki ns.
    These parameters are job-specific, and concern the creation
    of categories, adding those categories in articles, and
    linking the categories on Wikidata.
    """
    batch = pywikibot.Page(site,filename)

    jason = json.loads(batch.text)

    return jason

def validate_param_code(qcode,site_wkdt,valid_list):
    qcode_identities = []
    identities = getItemIdentitiesFromItem(pywikibot.ItemPage(site_wkdt,qcode))
    if identities is not None:
        qcode_identities = ['Q'+str(x) for x in identities]
    
    for qcode_identitiy in qcode_identities:
        if qcode_identitiy in valid_list:
            return True
    print("Code lists don't match qcode_identities="+str(qcode_identities)+" and params_instances="+str(valid_list))
    return False

def get_param_values(jason,page,lang):
    """
    Gets the actual values of all params
    """
    site_wkdt = pywikibot.Site('wikidata','wikidata')

    params = jason[0]["params"]
    new_params = {}

    lang_code = lang+'wiki'

    for param_name, param_code in params.items():
        if ":" in param_code:
            code_parts = param_code.split(':')
            prop_value = getItemPropertyValue(page,code_parts[0])
            #print("code_parts[0]: "+str(code_parts[0]))
            #print("prop_value "+str(prop_value))
            if prop_value is not None:
                qcode = 'Q'+str(prop_value)
                item = pywikibot.ItemPage(site_wkdt,qcode)
                for i in range(1,len(code_parts)):
                    prop_value_code = getItemPropertyValueFromItem(item,code_parts[i])
                    if prop_value_code is not None:
                        qcode = 'Q'+str(prop_value_code)
                        #print("code_parts[0]: "+str(code_parts[0]))
                        #print("prop_value "+str(prop_value))
                        #test item of the right type
                        item = pywikibot.ItemPage(site_wkdt,qcode)
                        """
                        qcode_identities = ['Q'+str(x) for x in getItemIdentitiesFromItem(pywikibot.ItemPage(site_wkdt,qcode))]
                        print("Qcode Identities: "+str(qcode_identities))
                        flag = False
                        for qcode_identitiy in qcode_identities:
                            if qcode_identitiy in jason[0]["params_instance"].values():
                                item = pywikibot.ItemPage(site_wkdt,qcode)
                                flag = True
                                break
                        if not flag:
                            print("Code lists don't match qcode_identities="+str(qcode_identities)+" and jason[0][\"params_instance\"]="+str(jason[0]["params_instance"])+" for  of prop "+param_code)
                            return None
                        """
                        
                    else:
                        #shouldn't we return None at this point?
                        print("ttttt")
                        return None
                #print(param_name)

                #TODO: 
                if validate_param_code(qcode,site_wkdt,jason[0]["params_instance"][param_name]):
                    item = pywikibot.ItemPage(site_wkdt,qcode)
                else:
                    #print("11111")
                    return None   
                if lang_code in item.sitelinks.keys():
                    new_params[param_name] = str(item.sitelinks[lang_code]).strip('[').strip(']')
                else:
                    #print("22222")
                    return None
            else:
                #print("33333")
                return None
        else:
            prop_value = getItemPropertyValue(page,param_code)
            if prop_value is not None:
                qcode = 'Q'+str(prop_value)
                #test item of the right type
                if validate_param_code(qcode,site_wkdt,jason[0]["params_instance"][param_name]):
                    item = pywikibot.ItemPage(site_wkdt,qcode)
                else:
                    #print("44444")
                    return None
                """
                qcode_identities = ['Q'+str(x) for x in getItemIdentitiesFromItem(pywikibot.ItemPage(site_wkdt,qcode))]
                print("Qcode Identities: "+str(qcode_identities))
                flag = False
                for qcode_identitiy in qcode_identities:
                    if qcode_identitiy in jason[0]["params_instance"].values():
                        item = pywikibot.ItemPage(site_wkdt,qcode)
                        flag = True
                        break
                if not flag:
                    print("Code lists don't match qcode_identities="+str(qcode_identities)+" and jason[0][\"params_instance\"]="+str(jason[0]["params_instance"])+" for  of prop "+param_code)
                    return None
                """
                if lang_code in item.sitelinks.keys():
                    new_params[param_name] = str(item.sitelinks[lang_code]).strip('[').strip(']')
                else:
                    #print("55555")
                    return None
                
            else:
                #print("66666")
                return None
    #print("get_param_values")
    #print(new_params)
    #print("wiiiiiiin")
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
    #print(hyperkey)
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
                    #print(hypercats)
                    if len(hypercats)>0:
                        for hypercat in hypercats:
                            tmp_text+='[['+get_actual_name(hypercat,param_values)+']]\n'
                        if len(tmp_text.strip()) > len(supercat_page.text):
                            supercat_page.text = tmp_text.strip()
                            supercat_page.save(SAVE_MESSAGE)
                            bag_of_cats.add(supercat_page.title())

                
    tmp_text = ""

    if "supercategories0" in jason[0].keys() and len(jason[0]["supercategories0"]) > 0:
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


#jason = read_json(site,pjson["TASK_MAIN_FILE_PTRN"].replace("{task_number}","2"))

#wkdt_jason = read_json(site,pjson["TASK_INTERLINK_FILE_PTRN"].replace("{task_number}","2"))

site = pywikibot.Site()

pjson = get_main_task_params()

WIKILOG_PAGE_TITLE = pjson["WIKILOG_PAGE_TITLE"] #"خدايمي:DarijaBot/عطاشة 25: لمصاوبة د تصنيفات من ويكيداطا"


INTERLINK_FAILED_MSG = pjson["INTERLINK_FAILED_MESSAGE_PTRN"] #"تّصنيف {} ماقدرش لبوت يربطو معا شي ستون ف ويكيداطا"
LOG_SAVE_MSG = pjson["LOG_ENTRY_SAVE_MSG"] #"زيادة د دخلة ف لّوحة"
pool = getOnlyArticles(site)

pool_size = len(list(deepcopy(pool)))
print_to_console_and_log('Pool size: '+str(pool_size),LOCAL_LOG)

bag_of_cats = set()
i = 1
pages_in_log = load_pages_in_log(RECENT_LOG_FILE)

#test
"""
title = "عائشة الشنا"
test_page = pywikibot.Page(site,title)
pool = [test_page]
"""

with open(RECENT_LOG_FILE,'a',encoding='utf-8') as f:
    job_pool = pjson["launch_tasks"]
    for task_number in job_pool:
        #loading job json files (from Mediawiki ns)
        batch_filename = pjson["TASK_MAIN_FILE_PTRN"].replace("{task_number}",str(task_number))
        wkdt_filename = pjson["TASK_INTERLINK_FILE_PTRN"].replace("{task_number}",str(task_number))
        jason = read_json(site,batch_filename)
        wkdt_jason = read_json(site,wkdt_filename)
        CREATE_CAT_MESSAGE = batch_filename[10:-5]+':'+pjson["CREATE_CAT_MESSAGE_PART"] #" تصنيف جديد تصاوب"
        SAVE_MESSAGE = batch_filename[10:-5]+':'+pjson["ADD_CAT_TO_PAGE_PART"] #" زيادة د تصنيف"
        for page in pool:
            print_to_console_and_log('*********'+str(i)+'/'+str(pool_size),LOCAL_LOG)
            if str(page.title()) not in pages_in_log:
                #adding this cat only to pages where it was previously missing
                check_cat = '[['+jason[0]["category"].split("{")[0].strip()
                #print(check_cat)
                if True: #if check_cat not in page.text:
                    if jason[0]["instanceof"] in getItemIdentities(page):
                        param_values = get_param_values(jason,page,'ary')
                        print("param values: "+str(param_values))
                        if param_values is not None:
                            cat = get_category(jason,param_values)

                            if '[['+cat+']]' not in page.text:
                                page.text+='\n'+'[['+cat+']]'
                                page.save(SAVE_MESSAGE)
                            bag_of_cats = create_cat_tree(jason, cat, param_values, bag_of_cats)
                            
                            link_cats(wkdt_jason,jason,page)
                f.write(page.title()+'\n')
            i+=1
