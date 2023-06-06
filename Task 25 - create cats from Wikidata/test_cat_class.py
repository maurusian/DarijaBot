import pywikibot
import json, traceback
from arywikibotlib import interlink_page #getItemPropertyValue, getItemIdentity, getItemPropertyNumericIds, getItemPropertyValueFromItem
import sys, os
from wikibase_api import Wikibase
import requests

site = pywikibot.Site()
#site_wkdt = pywikibot.Site('wikidata','wikidata')

title = "أسفي"
en_title = "Safi, Morocco"

ary_page = pywikibot.Page(site,title)

en_site = pywikibot.Site("en","wikipedia")

en_page = pywikibot.Page(en_site,en_title)

username = "User:Ideophagous"

user = pywikibot.User(en_site,username)

#print(dir(site))

print(site.lang)

wb = Wikibase()

print(help(wb.entity.get))

headers = {
        'User-Agent': 'DarijaBot/0.1 (Edition Windows 10 Home, Version 20H2, OS build 19042.1165, Windows Feature Experience Pack 120.2212.3530.0) Python3.9.0',
        'Content-Type': 'application/json; charset=utf-8'
    }

req_url = "https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q5&languages=ary"


r = requests.get(req_url,headers=headers)

print(r.content)

#print(dir(user))

#contributions = user.contributions()

#print(dir(user.contributions()))

#print(len(list(contributions)))

#print(getItemPropertyValue(page,"P17"))


#item = pywikibot.ItemPage(site_wkdt,code)

#print(item.sitelinks['arywiki'])

#print('Q'+str(getItemPropertyValueFromItem(item,"P17")))



#print(os.path.dirname(sys.argv[0]))

#interlink_page(ary_page,en_page,"en")
