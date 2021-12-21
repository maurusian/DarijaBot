import pywikibot
from pgvbotLib import *
from copy import deepcopy

DEATH_CAT_PART = "تصنيف:وفيات"
BIRTH_CAT = "[[تصنيف:زيادات علا حساب لعام]]"

CATEGORY_NAMESPACE = 14

SAVE_MESSAGE = "تّصنيف لفوقاني د زّيادات تحيّد"


           
site = pywikibot.Site()
pool = site.allpages(namespace = CATEGORY_NAMESPACE)
pool_size = len(list(deepcopy(site.allpages(namespace=CATEGORY_NAMESPACE))))
print('Pool size: '+str(pool_size))
i = 1
for page in pool:
    print('*********'+str(i)+'/'+str(pool_size))
    if DEATH_CAT_PART in page.title():
        text = page.text.replace(BIRTH_CAT,'').strip()
        
        if text != page.text:
            page.text = text
            save_page(page,SAVE_MESSAGE)
    i+=1
