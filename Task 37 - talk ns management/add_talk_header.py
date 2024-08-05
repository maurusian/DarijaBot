import pywikibot, os
from pywikibot import pagegenerators
from copy import deepcopy

# Set up the site
site = pywikibot.Site()

# Template to add
template_name = "راس مداكرة"
template_to_add = f"{{{{{template_name}}}}}\n"
save_summary = f"طاڭ د {template_name} تزاد ل صفحة د لمداكرة"

local_folder = os.path.dirname(__file__) 

def load_pages_in_log():
    if not os.path.exists(RECENT_LOG_FILE):
        return []
    with open(RECENT_LOG_FILE,'r',encoding='utf-8') as f:
        page_name_list = f.read().strip().splitlines()
    
    for i in range(len(page_name_list)):
        page_name_list[i] = page_name_list[i].strip()
    
    return page_name_list

# Function to get all redirect titles for a given template
def get_template_redirects(template_name):
    template_page = pywikibot.Page(site, f"موضيل:{template_name}")
    return [page.title(with_ns=False) for page in template_page.backlinks(filter_redirects=True, namespaces=[10])]

# Function to check if the template or its redirects already exists in the text
def template_exists(text, template_name, redirects):
    template_variations = [f"{{{{{template_name}}}}}"]
    #template_variations += [f"{{{{{redirect}}}}}" for redirect in redirects]
    return any(variation in text for variation in template_variations)

# Get all redirects for the template
redirects = [] #get_template_redirects(template_name)

# Iterate through all talk pages except user talk pages
#print("site help: ",dir(site))
#print("site.namespaces: ",dict(site.namespaces))
for ns in site.namespaces:
    if ns >= 0 and ns % 2 == 1 and ns != 3:  # Talk namespaces have odd IDs, excluding User talk (ID 3)
        print(f"processing pages on the namespace {ns}")
        RECENT_LOG_FILE = local_folder+f"/t37.1_recent_log_{ns}.txt"
        pages_in_log = load_pages_in_log()
        talk_pages = site.allpages(namespace=ns, filterredir=False)
        copy_talk_pages = deepcopy(talk_pages)
        pool_size = len(list(copy_talk_pages))
        print(f"Pool size: {pool_size}")
        i = 1
        with open(RECENT_LOG_FILE,'a',encoding='utf-8') as f:
            for page in talk_pages:
                print(f"*********{i}/{pool_size}")
                try:
                    if str(page.title()) not in pages_in_log:
                        try:
                            text = page.text
                            if not template_exists(text, template_name, redirects):
                                page.text = template_to_add + text
                                page.save(summary=f"{save_summary}")
                        except pywikibot.exceptions.InvalidTitleError:
                            print("Invalid title")
                        f.write(page.title()+'\n')
                except pywikibot.exceptions.InvalidTitleError:
                    print("Invalid page\n")
                    
                i+=1
