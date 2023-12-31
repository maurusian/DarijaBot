import pywikibot, urllib, requests
from bs4 import BeautifulSoup
import json, traceback
from copy import deepcopy

TEST_CAT = "تصنيف:لمغريب"

TASK_PAGE = "خدايمي:DarijaBot/عطاشة 6: تحويل تصنيفات"

ADMINS = ["Ideophagous"]

SAVE_MESSAGE = "عطاشة 6.1، لكوض دجيسون تصاوب"

site = pywikibot.Site()

JOB_PAGE_TITLE_PTRN = "ميدياويكي:عطاشة6.1.خدمة{}.json"

FILENAME_PTRN  = "عطاشة6.خدمة{}"
#JOB_ID = 1

site = pywikibot.Site()

def read_json(site):
    batch = pywikibot.Page(site,batch_filename)

    print(batch_filename)

    jason = json.loads(batch.text)

    return jason

"""
if __name__ == "__main__":
    jason = read_json(site)
    ROOT_CAT_NAME = jason["ROOT_CAT"]

    root_cat = pywikibot.Category(site,ROOT_CAT_NAME)
    
"""

def get_all_subcategories_by_depth(category_name, depth=None):
    #site = pywikibot.Site("en", "wikipedia")
    category = pywikibot.Category(site, category_name)
    subcategories = set(category.subcategories())
    if depth == None:
        return subcategories
    else:
        while depth > 1:
            new_subcategories = set()
            for subcat in subcategories:
                new_subcategories.update(set(subcat.subcategories()))
            subcategories.update(new_subcategories)
            depth -= 1
    return subcategories

def get_all_subcategories(category_name):
    print(category_name)
    category = pywikibot.Category(site, category_name)
    subcategories = set(category.subcategories())
    print(subcategories)
    temp = deepcopy(subcategories)

    while True:
        for cat in temp:
            subcategories = subcategories.union(set(cat.subcategories()))
            print(set(cat.subcategories()))
        if len(subcategories) == len(temp):
            break
        temp = deepcopy(subcategories)

    return subcategories

def get_all_search_results(search_token,search_limit,lang):
    search_url = "https://"+lang+".wikipedia.org/w/index.php?title=Special:search&limit="+search_limit+"&ns0=1&offset=0&profile=default&search="+urllib.parse.quote(search_token)
    #search_url = base_url + search_title

    response = requests.get(search_url)

    if response.status_code != 200:
        print(f"Failed to get page: {search_url}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    divs = soup.find_all('div', class_='mw-search-result-heading')

    titles = [div.find('a').get('title') for div in divs]

    return titles

def get_all_search_result_cats(jason):
    search_token = jason["MAIN_SEARCH_TOKEN"]
    search_limit = str(jason["MAX_DATA_POOL_SIZE"])
    lang = jason["lang"]

    titles = get_all_search_results(search_token,search_limit,lang)
    
    tokens = jason["TOKENS"]

    all_cats = set()

    for title in titles:
        for token in tokens:
            if token["SOURCE_TKN"] in title:
                all_cats.add(pywikibot.Category(site,title))
                break

    return all_cats

def code_wrap(json_content):
    CODE_TAGS_PTRN = "<syntaxhighlight lang=\"json\">{}</syntaxhighlight>"

    #test prettify option
    
    return CODE_TAGS_PTRN.format(json.dumps(json_content, indent=4, ensure_ascii=False))
    #return CODE_TAGS_PTRN.format(str(json_content))


def save_to_subpage(content,notify_admin=False):
    
    write_to_page_ttl = TASK_PAGE+"/"+FILENAME_PTRN.format(main_jobid)

    write_to_page = pywikibot.Page(site,write_to_page_ttl)

    write_to_page.text = code_wrap(jobs)

    write_to_page.save(SAVE_MESSAGE)
    


#test code for functions



#actual treatment
#make sure to load json and extract tokens
jobs = []
main_jobid = input("Enter main job ID: ")
i = 1

batch_filename = JOB_PAGE_TITLE_PTRN.format(main_jobid)
jason = read_json(site)
tokens = jason["TOKENS"]

if "ROOT_CAT" in jason.keys():
    all_cats = get_all_subcategories(jason["ROOT_CAT"])
elif "MAIN_SEARCH_TOKEN" in jason.keys():
    all_cats = get_all_search_result_cats(jason)
for cat in all_cats:
    for token in tokens:
        actual_src_token = token["FRONT_SEP"]+token["SOURCE_TKN"]+token["BACK_SEP"]
        if actual_src_token in cat.title():
            actual_trgt_token = token["FRONT_SEP"]+token["TARGET_TKN"]+token["BACK_SEP"]
            jobs.append({'jobid':main_jobid+'.'+str(i),'source_cat':cat.title(),'target_cat':cat.title().replace(actual_src_token,actual_trgt_token)})
            i+=1
            break

print("All cats loaded and ready to meow")
#save json locally
#see prettify options
with open(FILENAME_PTRN.format(main_jobid),'w',encoding="utf-8") as jsonfile:
    
    #jsonfile.write(str(jobs))
    jsonfile.write(json.dumps(jobs, indent=4, ensure_ascii=False))
    

#save to subpage of task
save_to_subpage(code_wrap(jobs))
