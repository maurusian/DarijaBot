from lib.pgvbotLib import *
import pywikibot
from copy import deepcopy
import re
from openpyxl import Workbook



site = pywikibot.Site()

#page = pywikibot.Page(site,title)

pool = site.allpages()
pool_size = len(list(deepcopy(pool)))
print(pool_size)
wb = Workbook()
sheet = wb.active
sheet['A1'] = 'Page'
sheet['B1'] = 'existing redirects'
sheet['C1'] = 'new redirects'
i = 2
c = 1
for page in pool:
    
    if validate_page(page):
        
        
        redirects = []
        links =  page.backlinks()
        for link in links:
            if link.isRedirectPage():
                redirects.append(link.title())
        if len(redirects) < 3:
            sheet['A'+str(i)] = page.title()
            if len(redirects)>0:
                sheet['B'+str(i)] = ' ..  '.join(redirects)
        
            
            i+=1
    print(str(c)+'/'+str(pool_size))
    c+=1
    if i == 101:
        break

wb.save('./export/page_redirects.xlsx')
