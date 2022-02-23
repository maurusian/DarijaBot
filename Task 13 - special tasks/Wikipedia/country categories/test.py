import pywikibot
import re
from arywikibotlib import *
from datetime import datetime, timezone
import random
#from bs4 import BeautifulSoup

IGNORE_LIST = []

USER_TALK_NAMESPACE = 3

IP_PATTERN = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"

title = "تاريخ د لمغريب"

site = pywikibot.Site()

#print(dir(site))

page = pywikibot.Page(site,title)

#print(dir(page))

#print(dir(site))
ADMIN_LIST = ["Ideophagous","Reda benkhadra","Anass Sedrati"]
print(list(site.users(ADMIN_LIST)))



def get_random_admin():
    return ADMIN_LIST[random.randint(0,len(ADMIN_LIST)-1)]

while(True):
    #print(get_random_admin())
    random_admin = pywikibot.User(site,get_random_admin())
    print(random_admin)
    
    print(random_admin.editCount())
    print(random_admin.gender())
    print(random_admin.rights())
    print(random_admin.registration)
    print(random_admin.properties)
    #print(random_admin.data_item())
    print(random_admin.coordinates())
    print(random_admin._getInternals())
    print(dir(random_admin))
    input()

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
for botuser in site.botusers():
    print(botuser)

for ns in site.namespaces:
    print(site.namespace(ns))

"""
