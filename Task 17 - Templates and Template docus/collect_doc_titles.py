import pywikibot
from openpyxl import Workbook
import re

TMP_NS = 10

DOC_SUBTITLE = "/شرح"

TITLE_PATTERN = r"=\s*.+?\s*="

site = pywikibot.Site()

pool = site.allpages(namespace=TMP_NS)

pool_size = len(list(site.allpages(namespace=TMP_NS)))

print(pool_size)

def clean_title_part(s):
    return s.replace("=","").strip()

title_parts = {}
i = 1

for page in pool:
    print('*********'+str(i)+'/'+str(pool_size))
    
    if page.title()[-4:] == DOC_SUBTITLE:
        ms = re.findall(TITLE_PATTERN,page.text)
        #print(ms)
        for s in ms:
            cleaned_s = clean_title_part(s)
            print(cleaned_s)
            if len(cleaned_s.split()) <= 3:
                if cleaned_s in title_parts.keys():
                    title_parts[cleaned_s]+=1
                else:
                    title_parts[cleaned_s] = 1
                    
        #print(page.text)
        #break

    i+=1

print(title_parts)

wb = Workbook()

sheet = wb.active

sheet['A1'] = "title"
sheet['B1'] = "count"
sheet['C1'] = "translation"

j = 2
for key,value in title_parts.items():
    if value > 1:
        sheet['A'+str(j)] = key
        sheet['B'+str(j)] = str(value)
        j+=1


wb.save("to_translate2.xlsx")
    
