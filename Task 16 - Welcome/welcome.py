import pywikibot
from pywikibot import Family
import random
from copy import deepcopy
from params import MONTHS
from datetime import datetime, timezone
from sys import argv
import os
import traceback
#from arywikibotlib import getOnlyArticles


ADMIN_LIST = ["Ideophagous","Reda benkhadra","Anass Sedrati","Mounir Neddi","Mico2022"]

ACCT_WELCOME_TAG = "{{ترحيب جديد|{admin}|sign=[[مستخدم:{admin}|{admin}]] ([[نقاش المستخدم:{admin}|نقاش]]){time}}}"
IP_WELCOME_TAG = "{{ترحيب أي پي|{admin}|sign=[[مستخدم:{admin}|{admin}]] ([[نقاش المستخدم:{admin}|نقاش]]){time}}}"

ACCT_SAVE_MESSAGE = "ترحيب ب خدايمي"
IP_SAVE_MESSAGE = "ترحيب ب أيپي"

ARTICLE_NAMESPACE = 0

LAST_RUN_FILE = "last_run.txt"

DATE_FORMAT = "%Y-%m-%d %H:%M"

TMS_DATE_FORMAT = "%Y-%m-%d %H:%M"

ARY_CRE_DATE_STR = "2020-07-10 00:00"

OLD_DATE_STR = "2001-01-01 00:00"

OLD_DATE = datetime.strptime(OLD_DATE_STR,DATE_FORMAT)

PROBABLE_LANGS_FOR_MOROCCAN_USERS = ["shi","en","simple","fr","ar","de","nl","ja","zh","it","es","pt","sv","ru","pl"]

IGNORE_LIST = ["Mirji"]

NEWUSER_COUNT_LIMIT = 500

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

def validate_user(user):
    username = user.username
    if username in IGNORE_LIST:
        return False
    time = ARY_CRE_DATE_STR
    #time = get_last_run_datetime()
    last_date = datetime.strptime(ARY_CRE_DATE_STR,DATE_FORMAT)
    #reg_date = datetime.strptime(user['registration'].replace('T',' ').replace('Z','')[:-3],TMS_DATE_FORMAT)
    reg_date = get_users_oldest_registration_date(username,datetime.strptime(user['registration'].replace('T',' ').replace('Z','')[:-3],TMS_DATE_FORMAT))
    #print(reg_date > last_date)
    user_acct = pywikibot.User(site,username)
    user_talk_page = user_acct.getUserTalkPage()
    #print(user_talk_page)
    if 'bot' not in user.groups() and user_talk_page.text == '' and not user_acct.getUserTalkPage().exists():
        return reg_date > last_date
    return False

from pywikibot import pagegenerators as pg

def get_new_users(site, limit):
    """
    Get a list of new users who created their accounts on the specified wiki site.

    :param site: The wiki site to get new users from
    :type site: pywikibot.site.BaseSite
    :param limit: The maximum number of new users to retrieve (default is 100)
    :type limit: int
    :return: A list of new users
    :rtype: list[pywikibot.User]
    """
    new_users = []

    # Retrieve new users using a logevent generator
    generator = pg.LogeventsPageGenerator(site=site, logtype='newusers', total=limit)
    for entry in generator:
        #print(entry)
        #user = entry.user()
        new_users.append(entry)

    return new_users

def get_users_oldest_registration_date(username,ary_reg_date):
    reg_date = ary_reg_date
    #family = Family.load('wikipedia')
    #lang_codes = family.alphabetic_revised

    found = False
    for lang in PROBABLE_LANGS_FOR_MOROCCAN_USERS:        
        
        site_lang = pywikibot.Site(lang, "wikipedia")
        try:
            user_acct = pywikibot.User(site_lang,username)
            if user_acct.exists() and user_acct.registration() is not None:
                if user_acct.registration() < reg_date:
                    reg_date = user_acct.registration()
                    found = True
        except AttributeError:
            print("AttributeError: "+traceback.format_exc())

    if not found:
        return OLD_DATE
    return reg_date



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
                    if user_talk_page.text == "" and not user_talk_page.exists():
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

    
    with open("save_users.txt","r",encoding="utf-8") as sv:
        treated_users = sv.read().split()

    new_users = get_new_users(site, limit=NEWUSER_COUNT_LIMIT)
    with open("save_users.txt","a",encoding="utf-8") as sv:
        user_count = len(list(new_users))
        print("User count: "+str(user_count))
        i=1
        for user in new_users:
            print('*********'+str(i)+'/'+str(user_count))
            username = user.username
            #print(username)
            #break
            if username not in treated_users and 'bot' not in user.groups(): #validate_user(user) and ,, not needed anymore
                time = get_time_string()
                admin = get_random_admin()
                WELCOME = ACCT_WELCOME_TAG.replace("{admin}",admin).replace("{time}",time)
                SAVE_MESSAGE = ACCT_SAVE_MESSAGE
                user_acct = pywikibot.User(site,username)
                user_talk_page = user_acct.getUserTalkPage()
                if user_talk_page.text == "":
                    user_talk_page.text = WELCOME
                    user_talk_page.save(SAVE_MESSAGE)
                #break
            i+=1
            sv.write(username+"\n")
    
#'''
