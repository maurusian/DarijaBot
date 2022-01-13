import pywikibot
import random
from copy import deepcopy
from params import MONTHS
from datetime import datetime, timezone
from arywikibotlib import getOnlyArticles


ADMIN_LIST = ["Ideophagous","Reda benkhadra","Anass Sedrati"]

ACCT_WELCOME_TAG = "{{ترحيب جديد|{admin}|sign=[[مستخدم:{admin}|{admin}]] ([[نقاش المستخدم:{admin}|نقاش]]){time}}}"
IP_WELCOME_TAG = "{{ترحيب أي پي|{admin}|sign=[[مستخدم:{admin}|{admin}]] ([[نقاش المستخدم:{admin}|نقاش]]){time}}}"

ACCT_SAVE_MESSAGE = "ترحيب ب خدايمي"
IP_SAVE_MESSAGE = "ترحيب ب أيپي"

ARTICLE_NAMESPACE = 0

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

    
"""
if len(argv)>3:
    local_args = argv[3:]
else:
    local_args = None
"""
local_args = 0 
if local_args is not None:
    site = pywikibot.Site()
    """
    if LAST_PAGES_OPTION in option_string:
                
        #load last changed
        last_changes = site.recentchanges(reverse=True,bot=False,top_only=True)
        #create page pool
        #NEXT: check other potential last_change types

        pool = [pywikibot.Page(site, item['title']) for item in last_changes]

                
    else:

        #load all pages on the article namespace, default option
        pool = site.allpages(namespace=ARTICLE_NAMESPACE)
    """
    pool = site.allpages(namespace=ARTICLE_NAMESPACE) #getOnlyArticles(site) #
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
                now = datetime.now()
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
