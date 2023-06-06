import pywikibot
import re
#from arywikibotlib import *
from datetime import datetime, timezone
import random
from copy import deepcopy
#from bs4 import BeautifulSoup

IGNORE_LIST = []

USER_TALK_NAMESPACE = 3

IP_PATTERN = r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"

title = "تاريخ د لمغريب"

DOCNAME_1 = "/توثيق"
DOCNAME_2 = "/توتيق"
DOCNAME_3 = "/documentation"
DOCNAME_4 = "/دوكو"
DOCNAME_5 = "/شرح"

NOINC_PATTERN1 = r"<noinclude>.+?</noinclude>"
NOINC_PATTERN2 = r"\<noinclude\>.+?\{\{[dD]ocumentation\}\}.+?\</noinclude\>"
NOINC_PATTERN3 = r"\<noinclude\>.+?\{\{توتيق\}\}.+?\</noinclude\>"


site = pywikibot.Site()

tmp = "قالب:Align"


tmp_page = pywikibot.Page(site,tmp)

print(tmp_page.title()[:-4])

for link in tmp_page.backlinks():
    print(link.title().title()[:-4])

#print(help(site.recentchanges))

#print(dir(site))
'''
page = pywikibot.Page(site,title)

pool = site.allpages(namespace=10,filterredir=False)
pool_size = len(list(deepcopy(site.allpages(namespace=10,filterredir=False))))

print(pool_size)

COUNTER1 = 0
COUNTER2 = 0
COUNTER3 = 0
COUNTER4 = 0
COUNTER5 = 0
COUNTER0 = 0
COUNTER6 = 0

i=1
for page in pool:
    print('*********'+str(i)+'/'+str(pool_size))
    #interlinks = page.iterlanglinks()
    """
    if page.isRedirectPage():
        print(page.title()+" is redirect")
        break
    """
    for link in page.iterlanglinks():
        #print(list(interlinks))
        linkparts = str(link)[2:-2].split(':')
        #print(linkparts)
        if linkparts[0] == 'en':
            print(link)
            item_lang = pywikibot.ItemPage.fromPage(page)
            print(item_lang)
            break
        #break
        COUNTER6+=1
    if DOCNAME_1 in page.title():
        COUNTER1+=1
        print(page.title())
        #new_title = page.title()[:-len(DOCNAME_1)]+DOCNAME_5
        #print(new_title)
    elif DOCNAME_2 in page.title():
        COUNTER2+=1
    elif DOCNAME_3 in page.title():
        COUNTER3+=1
    elif DOCNAME_4 in page.title():
        COUNTER4+=1
    elif DOCNAME_5 in page.title():
        COUNTER5+=1
    else:
        if "/" not in page.title():
            m = re.findall(NOINC_PATTERN1,page.text)
            
            if m is not None and len(m)>0:
                #print(m[0])
                #print(m[0].replace("{{توثيق}}","{{شرح}}"))
                #break
                COUNTER0+=1
    i+=1

print(DOCNAME_1+" count: "+str(COUNTER1))
print(DOCNAME_2+" count: "+str(COUNTER2))
print(DOCNAME_3+" count: "+str(COUNTER3))
print(DOCNAME_4+" count: "+str(COUNTER4))
print(DOCNAME_5+" count: "+str(COUNTER4))
print("Rest count: "+str(COUNTER0))
print("Interlinked count: "+str(COUNTER6))

#'''
