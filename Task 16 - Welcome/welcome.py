import pywikibot
import random
from copy import deepcopy
from params import MONTHS
from datetime import datetime, timezone
from sys import argv
import os
#from arywikibotlib import getOnlyArticles


ADMIN_LIST = ["Ideophagous","Reda benkhadra","Anass Sedrati"]

ACCT_WELCOME_TAG = "{{ترحيب جديد|{admin}|sign=[[مستخدم:{admin}|{admin}]] ([[نقاش المستخدم:{admin}|نقاش]]){time}}}"
IP_WELCOME_TAG = "{{ترحيب أي پي|{admin}|sign=[[مستخدم:{admin}|{admin}]] ([[نقاش المستخدم:{admin}|نقاش]]){time}}}"

ACCT_SAVE_MESSAGE = "ترحيب ب خدايمي"
IP_SAVE_MESSAGE = "ترحيب ب أيپي"

ARTICLE_NAMESPACE = 0

LAST_RUN_FILE = "last_run.txt"

DATE_FORMAT = "%Y-%m-%d %H:%M"

#EARLIEST_TIME = datetime.strptime("2000-01-01 00:00",DATE_FORMAT)

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
    

def get_random_admin():
    seed = int(datetime.now().strftime("%H%M%S%f"))
    random.seed(seed)
    return ADMIN_LIST[random.randint(0,len(ADMIN_LIST)-1)]


def get_time_string():
    raw_time = pywikibot.Timestamp.now(tz=timezone.utc)
    #utc_time = datetime.now(tz=timezone.utc)
    raw_time_parts = str(raw_time).split('T')
    date_parts = raw_time_parts[0].split('-')
    return " "+raw_time_parts[1][:-4]+"، "+date_parts[2]+" "+MONTHS[int(date_parts[1])-1]["ary_name"]+" "+date_parts[0]+" (UTC)"

    
if __name__ == '__main__':
    print(len(argv))
    if len(argv)>2:
        if len(argv) > 3:
            local_args = argv[3:]
    else:
        local_args = None

    #local_args = 0 
    if local_args is not None:
        site = pywikibot.Site()
        namespaces = []
        pools = []
        if local_args[0] == '-l':
            last_run_time = get_last_run_datetime()
            print(last_run_time)
            print("running for last changed pages")
            #load last changed
            last_changes = site.recentchanges(reverse=True,bot=False,top_only=True,start=last_run_time)
            #create page pool
            #NEXT: check other potential last_change types

            pools = [[pywikibot.Page(site, item['title']) for item in last_changes]]
            namespaces = ['any']

        elif len(local_args) > 1 and local_args[0] == '-a':
            print([int(ns) for ns in local_args[1:]])
            #print(EARLIEST_TIME)
            
            for ns in [int(ns) for ns in local_args[1:]]:
                pools.append(site.allpages(namespace=ns))
                namespaces.append(ns)
            
        else:
            print("running for all articles")
            #load all pages on the article namespace, default option
            pools = [site.allpages(namespace=ARTICLE_NAMESPACE)]
            namespaces = [0]
        
        for pool in pools:
            print("Runnng for namespaces: "+NAMESPACES[namespaces[pools.index(pool)]])
            pool_size = len(list(deepcopy(pool)))
            print('Pool size: '+str(pool_size))
            i = 1
            for page in pool:
                print('*********'+str(i)+'/'+str(pool_size))
                
                contributors = dict(page.contributors())

                for contributor in contributors.keys():
                    user = pywikibot.User(site,contributor)
                    user_talk_page = user.getUserTalkPage()
                    if user_talk_page.text == "":
                        #now = datetime.now()
                        time = get_time_string()
                        admin = get_random_admin()
                        if user.isRegistered():
                            WELCOME = ACCT_WELCOME_TAG.replace("{admin}",admin).replace("{time}",time)
                            SAVE_MESSAGE = ACCT_SAVE_MESSAGE
                        else:
                            WELCOME = IP_WELCOME_TAG.replace("{admin}",admin).replace("{time}",time)
                            SAVE_MESSAGE = IP_SAVE_MESSAGE
                        user_talk_page.text = WELCOME
                        user_talk_page.save(SAVE_MESSAGE)
                    else:
                        talk_page_contributors = dict(user_talk_page.contributors())
                        #print(page.title())
                        #print(talk_page_contributors)
                        if len(talk_page_contributors.keys()) == 1 and list(talk_page_contributors.keys())[0] == 'MenoBot':
                            
                            time = get_time_string()
                            admin = get_random_admin()
                            if user.isRegistered():
                                WELCOME = ACCT_WELCOME_TAG.replace("{admin}",admin).replace("{time}",time)
                                SAVE_MESSAGE = ACCT_SAVE_MESSAGE
                            else:
                                WELCOME = IP_WELCOME_TAG.replace("{admin}",admin).replace("{time}",time)
                                SAVE_MESSAGE = IP_SAVE_MESSAGE
                            user_talk_page.text = WELCOME
                            user_talk_page.save(SAVE_MESSAGE)
                i+=1
                
    write_run_time()
