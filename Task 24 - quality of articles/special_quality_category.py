import pywikibot, os, re
from copy import deepcopy

ARTICLE_NAMESPACE = 0

WIKI_LOG = "خدايمي:DarijaBot/عطاشة 24: معايير لجودة"

LOCAL_LOG = "task24.2.log"

RECENT_LOG_FILE = "recent_log.txt"

SPECIAL_CAT = "[[تصنيف:مقالة ب جودة مابيهاش (تصنيف د إحصائيات لمينحة د 2023)]]"

ADD_CAT_SAVE_MESSAGE = "تصنيف خاص د لجودة تزاد"
RMV_CAT_SAVE_MESSAGE = "تصنيف خاص د لجودة تحيد"

NEEDS_PICTURE_TAG_PART = "{{مقالة ناقصينها تصاور"

NO_SOURCES_ON_PAGE_TAG = "{{مقالة ناقصينها عيون لكلام}}"

NO_CATEGORY_TAG = "{{مقالة ما مصنفاش}}"

need_more_work_tag_part = "{{مقالة خاصها تقاد"


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

site = pywikibot.Site()

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
                try:
                    if len(page.text.encode('utf-8')) > 3000 and NEEDS_PICTURE_TAG_PART not in page.text \
                       and NO_SOURCES_ON_PAGE_TAG not in page.text and NO_CATEGORY_TAG not in page.text \
                       and need_more_work_tag_part not in page.text:
                        if SPECIAL_CAT not in page.text:
                            page.text+="\n"+SPECIAL_CAT
                            page.save(ADD_CAT_SAVE_MESSAGE)
                    else:
                        if SPECIAL_CAT in page.text:
                            page.text+=page.text.replace(SPECIAL_CAT,"").strip()
                            page.save(RMV_CAT_SAVE_MESSAGE)
                except pywikibot.exceptions.OtherPageSaveError:
                    wiki_log_page = pywikibot.Page(site,WIKI_LOG)
                    wiki_log_page.text += "صّفحة [["+page.title()+"]] ماقدراتش تّصوڤا ب زيادة د تصنيف ديال لمينحة د 2023."
                f.write(page.title()+'\n')
            i+=1
