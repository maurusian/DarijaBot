import pywikibot
from openpyxl import load_workbook

MONUMENT_TAG = "{{معلومات معلمة}}"
STUB_TAG = "{{بذرة}}"
SOURCE_TAG = "==عيون لكلام==\n{{مراجع}}"
CATEGORY_CODE = "[[تصنيف:المغريب]]"
SAVE_MESSAGE = "تاني تجريبة ديال داريجابوت"

def build_article(title,body):
    return MONUMENT_TAG+"\n'''"+title+"''' "+body+"\n\n"+STUB_TAG+"\n\n"+SOURCE_TAG+"\n\n"+CATEGORY_CODE
    


site = pywikibot.Site()

wb = load_workbook('./export/monuments_no_ary.xlsx')

sheet = wb.active

articles = {}
for i in range(50):
    title = sheet['C'+str(i+2)].value
    body = sheet['D'+str(i+2)].value

    if title is not None and body is not None:
        #articles[title]=body
        page = pywikibot.Page(site, title)
        page.text = build_article(title,body)
        page.save(SAVE_MESSAGE)
        break
        



