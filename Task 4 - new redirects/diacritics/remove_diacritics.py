from arywikibotlib import DIACRITICS, getOnlyArticles
import os, pywikibot
from copy import deepcopy

MOVE_MESSAGE = "لحاراكات تحيّدو من لعنوان"

ADMIN_LIST = ["Ideophagous","Reda benkhadra","Anass Sedrati","سمير تامر"]

BOT_COMMENT_TAG = "{{تعليق بوتي}}"

TALK_PAGE_TITLE_PART = "نقاش:"

NOTIF_SECTION_TITLE = "== دمج ؤلا توضيح =="

NOTIF_TEMPLATE = BOT_COMMENT_TAG+" مرحبا {{جاوب|{إمغارن}}}. عافاكوم شوفو واش هاد لپاج [[{پاج1}]] ؤ هاد لپاج [[{پاج2}]] خاصهوم يتزادو ل پاج ديال تّوضيح ؤلا يتدمجو. --~~~~"

NOTIF_ADMINS_SAVE_MESSAGE = "إعلام ل إمغارن"


DIACRITICS_LIST = list(DIACRITICS)

RECENT_LOG_FILE = os.getcwd()+'/recent_log.txt'


def notify_admins(page,target_page):
    talk_page_title = TALK_PAGE_TITLE_PART+page.title()
    talk_page = pywikibot.Page(pywikibot.Site(),talk_page_title)
    ar_talk_page_title = TALK_PAGE_TITLE_PART+target_page.title()
    ar_talk_page = pywikibot.Page(pywikibot.Site(),ar_talk_page_title)
    
    if (NOTIF_SECTION_TITLE not in talk_page.text and BOT_COMMENT_TAG not in talk_page.text
        and NOTIF_SECTION_TITLE not in ar_talk_page.text and BOT_COMMENT_TAG not in ar_talk_page.text):
        NOTIF_MESSAGE = NOTIF_TEMPLATE.replace("{إمغارن}",'|'.join(ADMIN_LIST)).replace('{پاج1}',page.title()).replace('{پاج2}',target_page.title())
        talk_page.text+=NOTIF_SECTION_TITLE+'\n'+NOTIF_MESSAGE
        talk_page.save(NOTIF_ADMINS_SAVE_MESSAGE)
    else:
        print("Notification already added")
    

def load_pages_in_log():
    if not os.path.exists(RECENT_LOG_FILE):
        return []
    with open(RECENT_LOG_FILE,'r',encoding='utf-8') as f:
        page_name_list = f.read().strip().splitlines()
    
    for i in range(len(page_name_list)):
        page_name_list[i] = page_name_list[i].strip()
    
    return page_name_list

site = pywikibot.Site()
pool = getOnlyArticles(site)

pool_size = len(list(deepcopy(getOnlyArticles(site))))
print('Pool size: '+str(pool_size))
i = 1

pages_in_log = load_pages_in_log()

with open(RECENT_LOG_FILE,'a',encoding='utf-8') as f:
    for page in pool:
        print('*********'+str(i)+'/'+str(pool_size))
        new_title = page.title()
        for diacritic in DIACRITICS_LIST:
            new_title =  new_title.replace(diacritic,'')

        
        if new_title != page.title():
            test_page = pywikibot.Page(site,new_title)
            if test_page.text.strip() == '' or test_page.isRedirectPage():
                pywikibot.output(MOVE_MESSAGE)
                page.move(new_title, reason=MOVE_MESSAGE, movetalk=True, noredirect=False)
            else:
                notify_admins(page,test_page)

        f.write(page.title()+'\n')
        
        i+=1
"""
#debugging
title = "تْوارْخِي"

page = pywikibot.Page(site,title)
new_title = title
for diacritic in DIACRITICS_LIST:
    new_title =  new_title.replace(diacritic,'')

print(list(title))
print(new_title)
"""
