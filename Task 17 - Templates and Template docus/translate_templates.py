import pywikibot
from openpyxl import load_workbook
from copy import deepcopy
from params import MONTHS
from datetime import datetime, timezone
from sys import argv
import os, re, traceback

site = pywikibot.Site()

#TEMPLATE_ARY_NS = "موضيل"

TEMPLATE_NAMESPACE = 10

TASK_LOG_PAGE = "مستخدم:DarijaBot/عطاشة 17: زّيادة ديال شرح لقوالب بشكل ؤطوماتيكي"

LOG_ERROR_COMMENT = "ميساج د ليرور تزاد ف لّوحة"

RECENT_LOG_FILE = "recent_log.txt"

CASCADE_ERROR_MSG = "لپاج [[{}]] ماتقدرش تبدّل حيت محمية ؤلا حيت غادي تأتر ف پاجات خرين"

LAST_RUN_FILE = "last_run.txt"

DATE_FORMAT = "%Y-%m-%d %H:%M"

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

TRANSLATION_FILENAME = "to_translate_templates.xlsx"

SAVE_MESSAGE = "پاج د لموضيل تطرجمات"


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
            pool = site.allpages(namespace=[TEMPLATE_NAMESPACE], filterredir=False)

            #redirect_pool = site.allpages(namespace=TEMPLATE_NAMESPACE,filterredir=True)
        
        pool_size = len(list(deepcopy(pool)))
        print('Pool size: '+str(pool_size))
        i = 1
        pages_in_log = load_pages_in_log()
        wb = load_workbook(TRANSLATION_FILENAME)
        sheet = wb.active
        
        with open(RECENT_LOG_FILE,'a',encoding='utf-8') as f:
            for page in pool:
                
                print('*********'+str(i)+'/'+str(pool_size))
                print(page.title())
                if str(page.title()) not in pages_in_log:
                    tmp_text = page.text
                    for j in range(2,100):
                        source = sheet["A"+str(j)].value
                        target = sheet["C"+str(j)].value
                        if source is not None and source.strip() != "" and target is not None and target.strip() != "":
                            if source in tmp_text:
                                tmp_text = tmp_text.replace(source,target)
                            
                        else:
                            break
                    if page.text != tmp_text:
                        page.text = tmp_text
                        page.save(SAVE_MESSAGE)
                    f.write(page.title()+'\n')
                        
                        
                i+=1
                
            write_run_time()
