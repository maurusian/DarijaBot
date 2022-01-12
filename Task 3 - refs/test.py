import pywikibot
import re
from arywikibotlib import *
from bs4 import BeautifulSoup

REF_PATTERN = r"<ref>.+</ref>"
#LINK_PATTERN = r"\[(.+)]\]"
LINK_PATTERN = r"\[(\d+)\]"

title = "تاريخ د لمغريب"

site = pywikibot.Site()

page = pywikibot.Page(site,title)

refs = list(re.findall(REF_PATTERN, page.text))+["[145]"]

#print(refs)

for ref in refs:
    print(ref)
    links = re.search(LINK_PATTERN, ref)
    if links is not None:
        print(links.groups())


