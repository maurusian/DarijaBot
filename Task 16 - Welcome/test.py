import pywikibot
import re
from arywikibotlib import *
from datetime import datetime, timezone
import random
from pywikibot import Family
from pywikibot.exceptions import UnknownFamilyError
import time

#from bs4 import BeautifulSoup

IGNORE_LIST = []

USER_TALK_NAMESPACE = 3

IP_PATTERN = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"

title = "تاريخ د لمغريب"

DATE_FORMAT = "%Y-%m-%d %H:%M"

TMS_DATE_FORMAT = "%Y-%m-%d %H:%M"

LAST_DATE_STR = "2022-10-01 00:00"

last_date = datetime.strptime(LAST_DATE_STR,DATE_FORMAT)

site = pywikibot.Site()

#print(dir(site))

page = pywikibot.Page(site,title)

#print(dir(page))

#print(dir(site))
ADMIN_LIST = ["Ideophagous","Reda benkhadra","Anass Sedrati","Mounir Neddi"]
#print(list(site.users(ADMIN_LIST)))

def get_users_oldest_registration_date(username,ary_reg_date):
    reg_date = ary_reg_date
    family = Family.load('wikipedia')
    lang_codes = family.alphabetic_revised

    for lang in lang_codes:
        
        
        site_lang = pywikibot.Site(lang, "wikipedia")
        user_acct = pywikibot.User(site_lang,username)

        if user_acct.registration() < reg_date:
            reg_date = user_acct.registration()

    return reg_date
        

def validate_user(user):
    reg_date = datetime.strptime(user['registration'].replace('T',' ').replace('Z','')[:-3],TMS_DATE_FORMAT)
    #print(reg_date > last_date)
    user_acct = pywikibot.User(site,user['name'])
    user_talk_page = user_acct.getUserTalkPage()
    print(user_talk_page)
    if 'bot' not in user['groups'] and user_talk_page.text == '' and not user_acct.getUserTalkPage().exists():
        return get_users_oldest_registration_date(username,reg_date) > last_date
    return False
"""
print(len(list(site.allusers())))
for user in site.allusers():
    print(user)
    break
    if validate_user(user):
        print(user)
        break
"""
site_meta = pywikibot.Site("meta","meta")

user_acct = pywikibot.User(site_meta,"Jjff1")

print(user_acct.registration())

start_time = time.time()

#get_users_oldest_registration_date("Ideophagous",user_acct.registration())

print(user_acct.getUserTalkPage().exists())

print("--- %s seconds ---" % (time.time() - start_time))

#family = Family.load('wikipedia')

#print(family.alphabetic_revised)


"""
def get_random_admin():
    return ADMIN_LIST[random.randint(0,len(ADMIN_LIST)-1)]

for admin_name in ADMIN_LIST:
    #print(get_random_admin())
    random_admin = pywikibot.User(site,admin_name)
    print(random_admin)
    
    print(random_admin.editCount())
    print(random_admin.gender())
    print(random_admin.rights())
    print(random_admin.registration())
    print(random_admin.properties())


for botuser in site.botusers():
    print(botuser)

for ns in site.namespaces:
    print(site.namespace(ns))


contributors = dict(page.contributors())

print(pywikibot.Timestamp.now(tz=None)-datetime.now(tz=timezone.utc))

for contributor in contributors.keys():
    user_page = pywikibot.Page(site,site.namespace(USER_TALK_NAMESPACE)+":"+contributor)
    user = pywikibot.User(site,contributor)
    #print(dir(user))
    print(user.groups())
    print(user.isAnonymous())
    print(user.isRegistered())
    print(user.getUserTalkPage())
    #break
    if user_page.text == "":
        #print(user_page.text)
        #print(site.namespace(USER_TALK_NAMESPACE)+":"+contributor)
        username = user_page.title()
        aa = re.match(IP_PATTERN,contributor)
        if aa:
            print("is an IP address")
            WELCOME_TEXT = ""
        else:
            print("not an IP address")
            WELCOME_TEXT = ""

"""
