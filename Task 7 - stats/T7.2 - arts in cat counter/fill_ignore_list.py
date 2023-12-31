import pywikibot
import re
from copy import deepcopy

IGNORE_FILE = "ignore.txt"

PATTERNS = [r'تصنيف:\d+',r'تصنيف:وفيات \d+',r'تصنيف:زيادة \d+']

COUNTRY_CAT = "تصنيف:بلدان"

MOROCCO_CAT = "تصنيف:المغريب"


site = pywikibot.Site()

#title = "تصنيف:وفيات 1906"
#title = "تصنيف:1906"

#title = "تصنيف:عوام 1900"

#title = "تصنيف:زيادة 1907"

#print(re.match(PATTERNS[2],title))



pool = site.allpages(namespace=14)


pool_size = len(list(deepcopy(pool)))
print('Pool size: '+str(pool_size))

i=1
for page in pool:
    print('*********'+str(i)+'/'+str(pool_size))
    cats = [cat.title() for cat in page.categories()]
    with open(IGNORE_FILE,'a',encoding="utf-8") as ig:
        for pattern in PATTERNS:
            match = re.match(pattern,page.title())
            
            if match is not None:
                ig.write(page.title()+'\n')
                break

        if match is None and COUNTRY_CAT in cats and page.title() != MOROCCO_CAT:
            ig.write(page.title()+'\n')

    i+=1

