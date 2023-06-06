import pywikibot
import re
from arywikibotlib import *

OUTLINK_PATTERN = r'\[\[.+?\]\]'

#title = "الأعمدة ديال هيركوليس"
title = "لمهدي بن بركة"
title2 = "ويكيپيديا:زريعة"
INFOBOX_TAG_PATTERN = r"{{معلومات.*}}"
TITLE_PATTERN = r"==.+==[\n\s]+(?===\s|$)"
EMPTY_PARAGRAPH_TAG = "{{فقرة مازالا خاوية ولا ناقصة}}"
CATEGORY = "تصنيف:عنصر كيميائي"
CATEGORY = "تصنيف:17"

TEST_STRINGS = ["{{معلومات مدينة|صورة=سفسف.سد}}"
               ,"{{معلومات مدينة|صورة=سفسف.}}"
               ,"{{معلومات مدينة|صورة=سفسف}}"
               ,"{{معلومات مدينة|صورة=.سفسف}}"
               ,"{{معلومات مدينة|صورة=}}"
               ,"{{معلومات مدينة|صورة=}}}}"
               ,"{{معلومات مدينة|صورة=}}فسفسف}}"
               ,"{{معلومات مدينة|صورة=}}  فسفسف}}"
               ,"""{{معلومات مدينة|صورة=}} 

{{فسفسف|صورة=}}"""
               ,"""{{معلومات مدينة|صورة=}} 

{{فسفسف|صورة=ففدفف.ڢسفڢف}}"""]
PIC_REGEX = r"{{معلومات.+\|صورة=.+\..+}}"

FILE = '[[File:'
MILF = '[[ملف:'

FILE_PART_DICT = {'en':'[[File:'
                 ,'fr':'[[Fichier:'
                 ,'ar':'[[ملف:'}

#PICTURE_MISSING_TAG_PATTERN = r"{{مقالة ناقصينها تصاور\|.+?}}"
#text = "{{مقالة ناقصينها تصاور|1351vdvfd551}}\nevbdb464vt}}\n"

#print(re.findall(PICTURE_MISSING_TAG_PATTERN, text))
#text = re.sub(PICTURE_MISSING_TAG_PATTERN,'',text)

#print(text)

def get_disambig_pages(page):
    disambig_pages = []

    for link in page.backlinks():
        if link.isDisambig():
            disambig_pages.append(link)
        elif link.isRedirectPage():
            disambig_pages+=get_disambig_pages(link)
    return disambig_pages


def has_infobox_tag(page):
    regexp = re.compile(INFOBOX_TAG_PATTERN,flags=re.DOTALL)
    if regexp.search(page.text):
        return True
    return False

def get_infobox_template_page(page):
    regexp = re.compile(INFOBOX_TAG_PATTERN)
    m = regexp.search(page.text)
    if m:
        #return m.group(0)
        return TEMPLATE_NS+":"+str(m.group(0)).split("|")[0].replace("{{","").replace("}}","")

#TEMPLATE_NS = "قالب"
title = "إبليس ف لإسلام"
site = pywikibot.Site()
page = pywikibot.Page(site,title)
#print(get_infobox_template_page(page))

CATEGORY_ISSUE_RGX = "{{مقالة خاصها تقاد\|.+عيون لكلام.+}}"


print(site.deadendpages())
"""
regexp = re.compile(CATEGORY_ISSUE_RGX,flags=re.DOTALL)
if regexp.search(page.text):
    print(True)
else:
    print(False)


regexp = re.compile(PIC_REGEX,flags=re.DOTALL)
for TEST_STRING in TEST_STRINGS:
    if regexp.search(TEST_STRING):
        print(True)
    else:
        print(False)


"""
"""
site = pywikibot.Site()

page = pywikibot.Page(site,title)
page2 = pywikibot.Page(site,title2)

item = pywikibot.ItemPage.fromPage(page)

print(getItemIdentity(page))
print(getItemPropertyNumericId(page,"P27"))
print(isHuman(page))
print(hasPropertyXValue(page,"P27",1028))


for link in page.iterlanglinks():
    linkparts = str(link)[2:-2].split(':')
    print(linkparts)

#print(dir(page))

print(get_disambig_pages(page))

if page2 in page.linkedPages():
    print(True)

for linkedPage in page.linkedPages():
    if page2 == linkedPage:
        print(linkedPage.title())


if FILE_PART_DICT['en'] in page.text or FILE_PART_DICT['ar'] in page.text:
    print("yes file/milf")

if FILE_PART_DICT['ar'] in page.text:
    print("yes milf")


print(dir(page))
"""
#item = pywikibot.ItemPage.fromPage(page)

#print([key for key in item.sitelinks.keys()])
#print(str(item.sitelinks['shiwiki'])[2:-2])

#item_dict = item.get()
#print(item_dict.keys())
#print(item_dict['labels']['fr'])
"""
if "claims" in item_dict.keys():
    item_claims = item_dict["claims"]
    print(str(item_claims['P18'][0].getTarget())[10:-2])


pool = site.allpages(namespace=0)

print(site.allpages.__code__.co_varnames)
#print(len(list(pool)))
def get_final_target(page):
    temp = page
    while temp.isRedirectPage():
        target_title = temp.text.strip().split('[[')[-1][:-2]
        temp = pywikibot.Page(site,target_title)
    return temp

page = pywikibot.Page(site,CATEGORY)
for p in page.backlinks():
    print(p.title())
print(type(page.title()))
print(dir(page))
print(has_infobox_tag(page))
#print(get_final_target(page).title())

titles = re.findall(TITLE_PATTERN,page.text)
text = 'nothing'
print(len(titles))
text = page.text
for title in titles:
    text = re.sub(title.strip(),title.strip()+'\n'+EMPTY_PARAGRAPH_TAG,text)
    
print(text)
'''
OUTLINK_PATTERN = r'\[\[.+?\]\]'
links = re.findall(OUTLINK_PATTERN,page.text)
for link in links:
    page_link = pywikibot.Page(site,link[2:-2].split('|')[0])
    print(get_final_target(page_link).title())
#print(dir(page))

for link in page.linkedPages():
    print(link)
    print(link.title())


outlinks = re.findall(OUTLINK_PATTERN,page.text)
for link in outlinks:
    link_page = pywikibot.Page(site,link[2:-2])
    print(link_page.title())
'''
SOURCE_EXIST_PATTERN = "ref.+?/ref"

sources = re.findall(SOURCE_EXIST_PATTERN,page.text)
print(len(sources))

for source in sources:
    print(source)
'''
pool = site.allpages()

for page in pool:
    page =  pywikibot.Page(site, title)
    if not page.isRedirectPage():
        print(dir(page))
        print(page.title())
        linkedPages = page.linkedPages()
        for lpage in linkedPages:
            print(lpage.title())
        categories = page.categories()
        print(len(list(categories)))
        for category in categories:
            print(category.title())
        for category in page.categories():
            if '[['+str(category.title()).strip()+']]' in page.text:
                print("found explicit category "+str(category))
                
        contrs = page.contributors()
        for contr in contrs:
            print(str(contr))

        links =  page.backlinks()
        for link in links:
            print(type(link))
            print(str(link))
        print(page.isRedirectPage())
            
        break
'''
"""
