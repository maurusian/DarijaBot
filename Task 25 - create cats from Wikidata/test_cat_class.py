import pywikibot
import json, traceback
from arywikibotlib import interlink_page #getItemPropertyValue, getItemIdentity, getItemPropertyNumericIds, getItemPropertyValueFromItem
import sys, os

site = pywikibot.Site()
#site_wkdt = pywikibot.Site('wikidata','wikidata')

title = "أسفي"
en_title = "Safi, Morocco"

ary_page = pywikibot.Page(site,title)

en_site = pywikibot.Site("en","wikipedia")

en_page = pywikibot.Page(en_site,en_title)

#print(getItemPropertyValue(page,"P17"))


#item = pywikibot.ItemPage(site_wkdt,code)

#print(item.sitelinks['arywiki'])

#print('Q'+str(getItemPropertyValueFromItem(item,"P17")))



#print(os.path.dirname(sys.argv[0]))

interlink_page(ary_page,en_page,"en")
