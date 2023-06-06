import pywikibot
import random
from copy import deepcopy
from params import MONTHS
from datetime import datetime, timezone
from sys import argv
import os, re
from pgvbotLib import log_error
from pywikibot.exceptions import ArticleExistsConflictError, NoPageError

"""
Links template pages based on identical names from other wikis
"""


LANGS = ['en','fr','ar']

TEMPLATE_LANG = {'en':'Template','fr':'Modèle','ar':'قالب'}

SAVE_LOG_MESSAGE = "دخلة ف لّوحة تزادت"

#TASK_LOG_PAGE = "مستخدم:DarijaBot/عطاشة 17: زّيادة ديال شرح لقوالب بشكل ؤطوماتيكي"

#TASK_LOG_PAGE = 'User:DarijaBot/log'


TEMPLATE_NAMESPACE = 10

#TMP_DOC_LANG = {'en':'/doc','fr':'Documentation','ar':'/شرح'}

if __name__ == '__main__':
    print(len(argv))
    if len(argv)>2:
        local_args = argv[2:]
    else:
        local_args = None

    #local_args = 0 
    if local_args is not None:
        site_ary = pywikibot.Site('ary','wikipedia')
        if local_args[0] == '-l':
            last_run_time = get_last_run_datetime()
            print(last_run_time)
            print("running for last changed pages")
            #load last changed
            last_changes = site_ary.recentchanges(namespace=TEMPLATE_NAMESPACE, reverse=True, top_only=True, start=last_run_time, filterredir=False)
            #create page pool
            #NEXT: check other potential last_change types

            pool = [pywikibot.Page(site_ary, item['title']) for item in last_changes]

        else:
            print("running for all articles")
            #load all pages on the article namespace, default option
            pool = site_ary.allpages(namespace=TEMPLATE_NAMESPACE, filterredir=False)

            #redirect_pool = site.allpages(namespace=TEMPLATE_NAMESPACE,filterredir=True)
        
        pool_size = len(list(deepcopy(pool)))
        print('Pool size: '+str(pool_size))
        i = 1
        for page in pool:
            
            print('*********'+str(i)+'/'+str(pool_size))
            has_interlinks = False
            for link in page.iterlanglinks():
                #print(list(interlinks))
                has_interlinks = True                           
                break
            
            if not has_interlinks:
                #try to add interlink based on name
                for lang_code in LANGS:
                    site_lang  = pywikibot.Site(lang_code,'wikipedia')
                    title_part = TEMPLATE_LANG[lang_code]
                    lang_title = page.title()[len('قالب:'):]
                    page_lang  = pywikibot.Page(site_lang,title_part+':'+lang_title)
                    if page_lang.text is not None and page_lang.text != '':
                        try:
                            item_lang = pywikibot.ItemPage.fromPage(page_lang)
                            print("setSiteLinks for "+page.title())
                            #break
                            item_lang.setSitelink(page, summary=u'Setting sitelink by adding ary template')
                            break
                        except NoPageError:
                            print('NoPageError for Item: '+page_lang.title().replace('قالب',TEMPLATE_LANG[lang_code]))
                            #wiki_log_message = 'NoPageError for Item: '+page_lang.title().replace('قالب',TEMPLATE_LANG[lang_code])
                            #log_error(TASK_LOG_PAGE,wiki_log_message,SAVE_LOG_MESSAGE,site_ary)

            i+=1
