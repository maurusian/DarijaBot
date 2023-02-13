import pywikibot
from copy import deepcopy

TEST_CAT = "تصنيف:لمغريب"

FILENAME_PTRN = ""

TASK_PAGE = ""

ADMINS = []

SAVE_MESSAGE = ""

site = pywikibot.Site()

def get_recur_subcategories(category_name):
    #site = pywikibot.Site("en", "wikipedia")
    category = pywikibot.Category(site, category_name)
    subcategories = set(category.subcategories())
    all_subcategories = subcategories.copy()

    for subcategory in subcategories:
        all_subcategories.update(get_all_subcategories(subcategory.title()))
    
    return all_subcategories


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
    category = pywikibot.Category(site, category_name)
    subcategories = set(category.subcategories())
    temp = deepcopy(subcategories)

    while True:
        for cat in temp:
            subcategories.union(set(cat.subcategories()))
        if len(cats) == len(temp):
            break
        temp = cats


def code_wrap(json_content):
    CODE_TAGS_PTRN = "<syntaxhighlight lang=\"json\">{}</syntaxhighlight>"

    #test prettify option
    
    return CODE_TAGS_PTRN.format(json.dumps(json_content, indent=4))


def save_to_admin_subpage(content,notify_admin=False):
    
    write_to_page_ttl = TASK_PAGE+"/"+FILENAME_PTRN.format(main_jobid)

    write_to_page = pywikibot.Page(site,write_to_page_ttl)

    write_to_page.text = code_wrap(jobs)

    write_to_page.save(SAVE_MESSAGE)
    


#test code for functions
all_subcategories_recur = get_recur_subcategories(TEST_CAT)

subcategories_d2 = get_all_subcategories_by_depth(TEST_CAT, depth=2)

all_subcategories = get_all_subcategories(TEST_CAT)


#actual treatment
#make sure to load json and extract tokens
jobs = []
main_jobid = input("Enter main job ID: ")
i = 1
for cat in all_subcategories:
    for token in tokens:
        actual_src_token = token["FRONT_SEP"]+token["SOURCE_TKN"]+token["BACK_SEP"]
        if actual_src_token in cat.title():
            actual_trgt_token = token["FRONT_SEP"]+token["TARGET_TKN"]+token["BACK_SEP"]
            jobs.append({'jobid':main_jobid+'.'+str(i),'source_cat':cat.title(),'target_cat':cat.title().replace(actual_src_token,actual_trgt_token)})
        i+=1
        break

#save json locally
#see prettify options
with open(FILENAME_PTRN.format(main_jobid),'r') as jsonfile:
    
    jsonfile.write(json.dumps(jobs, indent=4))

#save to subpage of task
save_to_admin_subpage(code_wrap(jobs))
