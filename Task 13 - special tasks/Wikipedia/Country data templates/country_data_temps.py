import pywikibot
import re
from arywikibotlib import *
from datetime import datetime, timezone
import random
from copy import deepcopy
#from bs4 import BeautifulSoup

IGNORE_LIST = []

TEMPLATE_NAMESPACE = 10 

site = pywikibot.Site()

site_en = pywikibot.Site("en","wikipedia")

START_PAGE = "Country data"
#END_PAGE = "Template:CP"

pool_en = site_en.allpages(namespace=TEMPLATE_NAMESPACE, start = START_PAGE, total = 2000, filterredir = True)

#pool = site.allpages(namespace=TEMPLATE_NAMESPACE)

pool_size = len(list(deepcopy(pool_en)))

print("Pool size: "+str(pool_size))

#print(help(site.allpages))

for page in pool_en:
    print(page.title())

#print(page.title())
