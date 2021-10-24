from lib.pgvbotLib import *
import pywikibot
from copy import deepcopy
#from sys import argv
import re

OLD_STUB_TAG = "{{بذرة}}"
NEW_STUB_TAB = "{{زريعة}}"
FAULTY_SOURCE_SECTION_HEADERS = ["\\=\\=\s*[ل]{0,1}عيون\s*د\s*لكلام\s*\\=\\="
                                ,"\\=\\=\s*[ل]{0,1}عين\s*[د]{0,1}\s*لكلام\s*\\=\\="
                                ,"\\=\\=\s*[ل]{0,1}مصاد[ي]{0,1}ر\s*\\=\\="
                                ,"\\=\\=\s*[ل]{0,1}مراج[ي]{0,1}ع\s*\\=\\="
                                ,"\\=\\=\s*[ل]{0,1}مصدر\s*\\=\\="
                                ,"\\=\\=\s*[ل]{0,1}مرجع\s*\\=\\="
                                ]
                                #,"==\s*عيون\s*لكلام\s*=="]
SECTION_HEADER = "==عيون لكلام=="
OLD_SOURCE_TAG1 = "{{مراجع}}"
OLD_SOURCE_TAG2 = "<\s*references\s*/>"
NEW_SOURCE_TAG = "{{عيون}}"

TEST_STRING1 = "=== عيون دلكلام==      "


#print(re.sub(FAULTY_SOURCE_SECTION_HEADERS[0],SECTION_HEADER,TEST_STRING1))


site = pywikibot.Site()

#pool = site.allpages()

print("Creating working pool")
pool = site.allpages()
#pool = [page for page in site.allpages() if validate_page(page)]

"""
pool_size = len(list(deepcopy(pool)))
print('Pool size: '+str(pool_size))
"""
i = 1

pool = [pywikibot.Page(site, '1Q84 (رواية)')]

for page in pool:
    #print('*********'+str(i)+'/'+str(pool_size))
    if validate_page(page):
        new_text = page.text
        print(len(new_text))
        for header in FAULTY_SOURCE_SECTION_HEADERS:
            new_text = re.sub(header,SECTION_HEADER,new_text)
            if new_text != page.text:
                print("changing section header")
                with open("temp.txt",'w',encoding="utf-8") as f:
                    f.write(new_text)
                break
        
            
        temp = new_text
        print(OLD_STUB_TAG in new_text)
        new_text = new_text.replace(OLD_STUB_TAG,NEW_STUB_TAB)
        print(len(new_text))
        if new_text != page.text:
            print("changing old stub tag with new one")
        
        temp = new_text
        new_text = new_text.replace(OLD_SOURCE_TAG1,NEW_SOURCE_TAG)
        print(len(new_text))
        if new_text != page.text:
            print("changing old stub source (1) with new one")

        temp = new_text
        #new_text = new_text.replace(OLD_SOURCE_TAG2,NEW_SOURCE_TAG)
        new_text = re.sub(OLD_SOURCE_TAG2,NEW_SOURCE_TAG,new_text)
        print(len(new_text))
        if new_text != page.text:
            print("changing old stub source (2) with new one")

        if new_text != page.text:
            MESSAGE = "داريجابوت قاد عيون لكلام ؤلا طّاڭ د زريعة"
            page.save(MESSAGE)
            
            cha = input("continue to next page?\n")
    i+=1
