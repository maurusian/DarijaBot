import pywikibot, os, re, json
from copy import deepcopy

ARTICLE_NAMESPACE = 0
batch_filename = "ميدياويكي:عطاشة24.2.json"
LOCAL_LOG = "task24.2.log"
RECENT_LOG_FILE = "recent_log.txt"


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


def load_pages_in_log():
    if not os.path.exists(RECENT_LOG_FILE):
        return []
    with open(RECENT_LOG_FILE,'r',encoding='utf-8') as f:
        page_name_list = f.read().strip().splitlines()
    
    for i in range(len(page_name_list)):
        page_name_list[i] = page_name_list[i].strip()
    
    return page_name_list

def print_to_console_and_log(MSG):
    MESSAGE = MSG+'\n'
    with open(LOCAL_LOG,'a',encoding="utf-8") as log:
        log.write(MESSAGE)
    print(MSG)


def validate_page(page,addcat_entry):
    no_hascats = addcat_entry["NO_HASCATS"]
    hascats = addcat_entry["HASCATS"]
    minsize = addcat_entry["MIN_SIZE"]
    maxsize = addcat_entry["MAX_SIZE"]
    page_size = len(page.text.encode('utf-8'))
    ADDCAT = addcat_entry["ADDCAT"]
    
    if page_size >= minsize and (maxsize == 0 or page_size < maxsize):
        for cat in page.categories():
            if cat.title() in no_hascats:
                return "RMV"
        for hascat in hascats:
            hascat_page = pywikibot.Category(site,hascat)
            if hascat_page not in page.categories():
                return "RMV"
        if "[["+ADDCAT+"]]" not in page.text:
            return "ADD"
    else:
        return "RMV"

    return None

if __name__ == "__main__":

    site = pywikibot.Site()
    jason = read_json(site,batch_filename)

    WIKI_LOG = jason["WIKI_LOG"]

    #SPECIAL_CAT = "[[تصنيف:مقالات فيها مصدر و 3000 بايت]]"

    ADD_CAT_SAVE_MESSAGE = jason["ADD_CAT_SAVE_MESSAGE"]
    RMV_CAT_SAVE_MESSAGE = jason["RMV_CAT_SAVE_MESSAGE"]

    ADDCATS = jason["ADDCATS"]
    
    pool = site.allpages(namespace=ARTICLE_NAMESPACE, filterredir=False)

    pool_size = len(list(deepcopy(pool)))
    print_to_console_and_log('Pool size: '+str(pool_size))

    i = 1
    pages_in_log = load_pages_in_log()

    with open(RECENT_LOG_FILE,'a',encoding='utf-8') as f:
        with open("suggestion_list.txt","w",encoding='utf-8') as sug:
            for page in pool:
                print_to_console_and_log('*********'+str(i)+'/'+str(pool_size))
                
                if str(page.title()) not in pages_in_log:
                    #print(dir(page))
                    for addcat_entry in ADDCATS:
                        addcat = addcat_entry["ADDCAT"]
                        
                        try:
                            action = validate_page(page,addcat_entry)
                            print(action)
                            
                            if action is not None:
                                if action == "RMV":
                                    if "[["+addcat+"]]" in page.text:
                                        page.text=page.text.replace("[["+addcat+"]]","").strip()
                                        page.save(RMV_CAT_SAVE_MESSAGE)
                                elif action == "ADD":
                                    page.text+="\n[["+addcat+"]]"
                                    page.save(ADD_CAT_SAVE_MESSAGE)
                                    
                        except pywikibot.exceptions.OtherPageSaveError:
                            wiki_log_page = pywikibot.Page(site,WIKI_LOG)
                            wiki_log_page.text += jason["ERROR_MSG"].replace("{title}",page.title())
                        
                        f.write(page.title()+'\n')
                        
                i+=1
