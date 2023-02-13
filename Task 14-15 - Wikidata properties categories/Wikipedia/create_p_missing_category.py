import pywikibot, json
from arywikibotlib import getOnlyArticles
from copy import deepcopy

json_param_filename = "ميدياويكي:عطاشة15.2.json"


def read_json(site,json_param_filename):
    """
    Load job parameters from job json page on Mediawiki ns.
    These parameters are job-specific, and concern the creation
    of categories, adding those categories in articles, and
    linking the categories on Wikidata.
    """
    batch = pywikibot.Page(site,json_param_filename)

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

if __name__=='__main__':
    #Prepare parameter values

    #load default site
    site = pywikibot.Site()

    #load parameter json file
    jason = read_json(site,json_param_filename)

    #assign non-parametrized values   
    HIDDEN_TAG = jason["HIDDEN_TAG"]
    CREATE_SAVE_MESSAGE = jason["CREATE_SAVE_MESSAGE"]
    ADD_CAT_SAVE_MESSAGE = jason["ADD_CAT_SAVE_MESSAGE"]
    RECENT_LOG_FILE = jason["LOCAL_RECENT_LOG_FILE"]
    JOBS = jason["JOBS"]

    GENERAL_CAT = "تصنيف:پاجات كاتخدم خاصيات ديال ويكيداطا|{}"
    WIKIDATA_PROP_TAG_PTRN = "{{تصنيف ويكيداطا|{}}}"


    #load pool
    pool = getOnlyArticles(site)

    pool_size = len(list(deepcopy(pool)))
    print_to_console_and_log('Pool size: '+str(pool_size))
    i = 1
    pages_in_log = load_pages_in_log()

    with open(RECENT_LOG_FILE,'a',encoding='utf-8') as f:
        
        for page in pool:
            print_to_console_and_log('*********'+str(i)+'/'+str(pool_size))
            
            #print(pages_in_log[:20])
            
            
            if str(page.title()) not in pages_in_log:
    for elem in dict_data['rows']:
        if 'P' in elem[0]:
            print(elem[0])

            title = CAT_TITLE_PART + elem[0]
            page = pywikibot.Page(site, title)
            WIKIDATA_PROP_ACTUAL_TAG = WIKIDATA_PROP_TAG_PTRN.replace('{}',elem[0])
            if page.text == '':
                page.text = WIKIDATA_PROP_ACTUAL_TAG+'\n'+HIDDEN_TAG+"\n[["+GENERAL_CAT.replace('{}',elem[0].replace('P',''))+"]]"
                page.save(CREATE_SAVE_MESSAGE)
            else:
                temp = page.text
                temp = temp.replace(HIDDEN_TAG_OLD,HIDDEN_TAG)
                temp = temp.replace(HIDDEN,HIDDEN_TAG)
                if GENERAL_CAT.split('|')[0] not in page.text:
                    temp += "\n[["+GENERAL_CAT.replace('{}',elem[0].replace('P',''))+"]]"
                    #page.save(ADD_CAT_SAVE_MESSAGE)
                elif GENERAL_CAT.split('|')[0]+'|' not in page.text:
                    temp = temp.replace(GENERAL_CAT.split('|')[0],GENERAL_CAT.replace('{}',elem[0].replace('P','')))
                if WIKIDATA_PROP_ACTUAL_TAG not in page.text:
                    temp = WIKIDATA_PROP_ACTUAL_TAG+"\n"+temp
                if temp != page.text:
                    page.text = temp
                    page.save(ADD_CAT_SAVE_MESSAGE)
        else:
            print(elem[0]+" not a P property")

