import pywikibot
from lib.pgvbotLib import *

NEW_STUB_TAB = "{{زريعة}}"
ADJUST_STUB_TAG_MESSAGE = "تقاد طّاڭ د زريعة."

site = pywikibot.Site()

pool = site.allpages()

i=1
for page in pool:
    
    temp = page.text
    if NEW_STUB_TAB in page.text:
        page.text = page.text.replace(NEW_STUB_TAB,'')

        if validate_page(page):
            page.text += '\n'+NEW_STUB_TAB

        if temp != page.text:
            page.save(ADJUST_STUB_TAG_MESSAGE)
            print("page number "+str(i)+" saved")
    i+=1
