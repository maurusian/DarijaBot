import pywikibot
import random
from copy import deepcopy
from params import MONTHS
from datetime import datetime, timezone
from sys import argv
import os, re
from pywikibot.exceptions import ArticleExistsConflictError, NoPageError, CascadeLockedPageError
#from arywikibotlib import getOnlyArticles



TEMPLATE_NAMESPACE = 10

TASK_LOG_PAGE = "مستخدم:DarijaBot/عطاشة 17: زّيادة ديال شرح لقوالب بشكل ؤطوماتيكي"

LOG_ERROR_COMMENT = "ميساج د ليرور تزاد ف لّوحة"

RECENT_LOG_FILE = "recent_log.txt"

CASCADE_ERROR_MSG = "لپاج [[{}]] ماتقدرش تبدّل حيت محمية ؤلا حيت غادي تأتر ف پاجات خرين"

LAST_RUN_FILE = "last_run.txt"

DATE_FORMAT = "%Y-%m-%d %H:%M"

TMPL_REDIRECT_PAGE_STRUCT = """#تحويل [[{}]]
<noinclude>
[[تصنيف:تحويلات قوالب]]
</noinclude>"""

TEMPLATE_DOC_MOVE_MSG = "تحويل لپاج د شّرح"
REDIR_UPDATE_MESSAGE = "إصلاح تحويلات لقوالب"
UPDATE_TMP_DOC_CALL_MSG = "إصلاح سّمية د لقالب د شّرح"
FIX_TMP_CALL_MSG = "إصلاح سّمية د لقالب ؤلا تحياد يلا كان معاود"
CREATE_NEW_DOC_PAGE_MSG = "پاج د شّرح تصاوبات"
ADD_MISSING_DOC_FOOTER = "لفوتر تزاد ف صّفحة د لقالب"

DOC_FOOTER = "<noinclude>{{شرح}}</noinclude>"

EXISTING_LIST = "existinglist.txt"

#EARLIEST_TIME = datetime.strptime("2000-01-01 00:00",DATE_FORMAT)

DOCNAME_1 = "/توثيق"
DOCNAME_2 = "/توتيق"
DOCNAME_3 = "/documentation"
DOCNAME_4 = "/دوكو"
DOCNAME_5 = "/شرح"
DOCNAME_6 = "/doc"

DOCNAMES = [DOCNAME_1, DOCNAME_2, DOCNAME_5]

NOINC_PATTERN = r"<noinclude>.+?</noinclude>"
DOC_TMP_1 = "{{توثيق}}"
DOC_TMP_2 = "{{توتيق}}"
DOC_TMP_3 = "{{documentation}}"
DOC_TMP_3_bis = "{{Documentation}}"
#DOC_TMP_4 = "/دوكو"
DOC_TMP_4 = "{{شرح}}"

NAMESPACES = {0:'Articles'
             ,1:'Article discussions'
             ,2:'Users'
             ,3:'User discussions'
             ,4:'Project'
             ,5:'Project discussion'
             ,6:'File'
             ,7:'File discussion'
             ,8:'Mediawiki'
             ,9:'Mediawiki discussion'
             ,10:'Template'
             ,11:'Template discussion'
             ,12:'Help'
             ,13:'Help discussion'
             ,14:'Categories'
             ,15:'Category discussion'
             ,828:'Module'
             ,829:'Module discussion'
             ,'any':'any'
             }

LOG_PAGE_TITLE = 'User:DarijaBot/log'

SAVE_LOG_MESSAGE = "Added log entry"

LANGS = ['en','fr','ar']

TEMPLATE_LANG = {'en':'Template','fr':'Modèle','ar':'قالب'}

TMP_DOC_LANG = {'en':'/doc','fr':'Documentation','ar':'/شرح'}

DOC_HEADER = """{{طرجامة}}\n<noinclude>{{صفحات فرعية د شرح}}</noinclude>"""

def save_template(page,message):

    try:
        page.save(message)
    except pywikibot.exceptions.LockedPageError:
        print("page "+page.title()+"is locked")
        with open("local.log", "a", encoding="utf-8") as log:
            log.write("page "+page.title()+"is locked\n")

def log_error(LOG_PAGE_TITLE,log_message,save_log_message,site):
    log_page = pywikibot.Page(site, LOG_PAGE_TITLE)
    if log_page.text != '':
        log_page.text += '\n* '+log_message
    else:
        log_page.text = '* '+log_message

    log_page.save(save_log_message)
    

def get_last_run_datetime():
    if not os.path.exists(LAST_RUN_FILE):
        with open(LAST_RUN_FILE,'w') as f:
            return None

    with open(LAST_RUN_FILE,'r') as f:
        datetime_str = f.read().strip()

    return datetime.strptime(datetime_str,DATE_FORMAT)

def write_run_time():
    with open(LAST_RUN_FILE,'w') as f:
        f.write(pywikibot.Timestamp.now().strftime(DATE_FORMAT))
    

def get_time_string():
    raw_time = pywikibot.Timestamp.now(tz=timezone.utc)
    #utc_time = datetime.now(tz=timezone.utc)
    raw_time_parts = str(raw_time).split('T')
    date_parts = raw_time_parts[0].split('-')
    return " "+raw_time_parts[1][:-4]+"، "+date_parts[2]+" "+MONTHS[int(date_parts[1])-1]["ary_name"]+" "+date_parts[0]+" (UTC)"

def get_final_target(page):
    temp = page
    while temp.isRedirectPage():
        target_title = temp.text.strip().split('[[')[1].split(']]')[0].strip()
        temp = pywikibot.Page(site,target_title)
    return temp

def move_template(page,new_title):
    try:
        page.move(new_title, reason=TEMPLATE_DOC_MOVE_MSG, movetalk=True, noredirect=False)
    except ArticleExistsConflictError:
        with open(EXISTING_LIST,'a',encoding="utf-8") as f:
            f.write(page.title()+' ** '+new_title+'\n')


def load_pages_in_log():
    if not os.path.exists(RECENT_LOG_FILE):
        return []
    with open(RECENT_LOG_FILE,'r',encoding='utf-8') as f:
        page_name_list = f.read().strip().splitlines()
    
    for i in range(len(page_name_list)):
        page_name_list[i] = page_name_list[i].strip()
    
    return page_name_list

            
if __name__ == '__main__':
    print(len(argv))
    if len(argv)>2:
        local_args = argv[2:]
    else:
        local_args = None

    #local_args = 0 
    if local_args is not None:
        site = pywikibot.Site()
        if local_args[-1] == '-l':
            last_run_time = get_last_run_datetime()
            print(last_run_time)
            print("running for last changed pages")
            #load last changed
            last_changes = site.recentchanges(namespaces=[TEMPLATE_NAMESPACE], reverse=True, top_only=True, start=last_run_time, redirect = False)
            #create page pool
            #NEXT: check other potential last_change types

            pool = [pywikibot.Page(site, item['title']) for item in last_changes]

        else:
            print("running for all templates")
            #load all pages on the article namespace, default option
            pool = site.allpages(namespaces=[TEMPLATE_NAMESPACE], filterredir=False)

            #redirect_pool = site.allpages(namespace=TEMPLATE_NAMESPACE,filterredir=True)
        
        pool_size = len(list(deepcopy(pool)))
        print('Pool size: '+str(pool_size))
        i = 1
        pages_in_log = load_pages_in_log()
        with open(RECENT_LOG_FILE,'a',encoding='utf-8') as f:
            for page in pool:
                
                print('*********'+str(i)+'/'+str(pool_size))

                if str(page.title()) not in pages_in_log:
                
                    if page.title()[-len(DOCNAME_1):] == DOCNAME_1:
                        new_title = page.title()[:-len(DOCNAME_1)]+DOCNAME_5
                        move_template(page,new_title)
                        #page.move(new_title, reason=TEMPLATE_DOC_MOVE_MSG, movetalk=True, noredirect=False)
                        
                    elif page.title()[-len(DOCNAME_2):] == DOCNAME_2:
                        new_title = page.title()[:-len(DOCNAME_2)]+DOCNAME_5
                        move_template(page,new_title)

                    elif page.title()[-len(DOCNAME_5):] == DOCNAME_5:
                        text_changed = False
                        if "{{صفحات فرعية د شرح}}" in page.text:
                            text = page.text.replace("{{صفحة توثيق فرعية}}",'')
                            if text != page.text:
                                page.text = text
                                text_changed = True
                        else:
                            text = page.text.replace("{{صفحة توثيق فرعية}}",'{{صفحات فرعية د شرح}}')
                            if text != page.text:
                                page.text = text
                                text_changed = True
                        text = page.text.replace("{{Documentation subpage}}",'').replace("{{documentation subpage}}",'')
                        if text != page.text:
                            page.text = text
                            text_changed = True
                        if text_changed:
                            save_template(page,FIX_TMP_CALL_MSG)

                    elif "/" not in page.title():
                        
                        m = re.findall(NOINC_PATTERN,page.text)
                    
                        if m is not None and len(m)>0:
                            #print(m[0])
                            text_changed = False
                            doc_tag_exists = False
                            for j in range(len(m)):
                                new_m = m[j].replace(DOC_TMP_1,DOC_TMP_4).replace(DOC_TMP_2,DOC_TMP_4).replace(DOC_TMP_3,DOC_TMP_4).replace(DOC_TMP_3_bis,DOC_TMP_4)
                                if new_m != m[j]:
                                    page.text = page.text.replace(m[j],new_m)
                                    #doc_tag_exists = True
                                    text_changed = True
                            if DOC_TMP_1 not in page.text and DOC_TMP_2 not in page.text and DOC_TMP_3 not in page.text and DOC_TMP_3_bis not in page.text and DOC_TMP_4 not in page.text:
                                page.text+=DOC_FOOTER
                                text_changed = True
                            if text_changed:
                                save_template(page,UPDATE_TMP_DOC_CALL_MSG)
                        elif DOC_TMP_1 not in page.text and DOC_TMP_2 not in page.text and DOC_TMP_3 not in page.text and DOC_TMP_3_bis not in page.text and DOC_TMP_4 not in page.text:
                            page.text+=DOC_FOOTER
                            try:
                                save_template(page,ADD_MISSING_DOC_FOOTER)
                            except CascadeLockedPageError:
                                log_message = CASCADE_ERROR_MSG.format(page.title())
                                save_log_message = LOG_ERROR_COMMENT
                                log_error(TASK_LOG_PAGE,log_message,save_log_message,site)
                        
                        doc_available = False
                        for DOCNAME in DOCNAMES:
                            doc_page = pywikibot.Page(site, page.title()+DOCNAME)
                            if doc_page is not None and doc_page.text != "" and not doc_page.isRedirectPage():
                                doc_available = True
                                break

                        lang = None
                        has_interlinks = False
                        documentation = ""
                        if not doc_available:
                            try:
                                for link in page.iterlanglinks():
                                    #print(list(interlinks))
                                    has_interlinks = True
                                    linkparts = str(link)[2:-2].split(':')
                                    #print(linkparts)
                                    if linkparts[0] in LANGS:
                                        lang = linkparts[0]
                                        site_lang  = pywikibot.Site(lang,'wikipedia')
                                        title_part = TEMPLATE_LANG[lang]
                                        doc_page_lang  = pywikibot.Page(site_lang,title_part+':'+linkparts[-1]+TMP_DOC_LANG[lang])
                                        if doc_page_lang.text is not None and doc_page_lang.text != '':
                                            documentation = doc_page_lang.text
                                            #lang = 'en'                              
                                            break
                            except pywikibot.exceptions.UnknownSiteError:
                                log_message = "UnknownSiteError for "+str(page.title())
                                log_error(LOG_PAGE_TITLE,log_message,LOG_ERROR_COMMENT,site)


                        if documentation != '':
                            new_doc_page = pywikibot.Page(site,page.title()+DOCNAME_5)
                            new_doc_page.text = DOC_HEADER + '\n' + documentation
                            save_template(new_doc_page,CREATE_NEW_DOC_PAGE_MSG)

                    f.write(page.title()+'\n')
                                            
                i+=1
                
                

            if local_args[-1] == '-l':
                last_run_time = get_last_run_datetime()
                print(last_run_time)
                print("running for last changed redirect pages")
                
                last_changes = site.recentchanges(namespaces=[TEMPLATE_NAMESPACE], reverse=True, top_only=True, start=last_run_time, redirect = True)

                redirect_pool = [pywikibot.Page(site, item['title']) for item in last_changes]

            else:
                print("running for all redirects")

                redirect_pool = site.allpages(namespaces=[TEMPLATE_NAMESPACE],filterredir=True)

            pool_size = len(list(deepcopy(redirect_pool)))
            print('Pool size: '+str(pool_size))
            i = 1
            with open(RECENT_LOG_FILE,'a',encoding='utf-8') as f:
                for redir in redirect_pool:
                    print('*********'+str(i)+'/'+str(pool_size))
                    if str(page.title()) not in pages_in_log:
                        target = get_final_target(redir).title()

                        text = TMPL_REDIRECT_PAGE_STRUCT.format(target)

                        if text != redir.text:
                            redir.text = text

                            save_template(redir,REDIR_UPDATE_MESSAGE)

                        f.write(page.title()+'\n')
                        
                        
                    i+=1
                
        write_run_time()
