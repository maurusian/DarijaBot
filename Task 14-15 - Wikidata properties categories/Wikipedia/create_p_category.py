import pywikibot

CAT_TITLE_PART = "تصنيف:پاجات كاتخدم خاصية ديال "
HIDDEN = "__HIDDENCAT__"

GENERAL_CAT = "تصنيف:پاجات كاتخدم خاصيات ديال ويكيداطا"

CREATE_SAVE_MESSAGE = "پاج د تّصنيف ديال خاصية د ويكيداطا تقادات"

ADD_CAT_SAVE_MESSAGE = "تصنيف ديال تّصنيفات تزاد"

site = pywikibot.Site()

with open('quarry-59138-untitled-run585800.json','r') as f:
    dict_data = eval(f.read())


for elem in dict_data['rows']:
    if 'P' in elem[0]:
        print(elem[0])

        title = CAT_TITLE_PART + elem[0]
        page = pywikibot.Page(site, title)
        if page.text == '':
            page.text = "[["+GENERAL_CAT+"]]"+"\n"+HIDDEN
            page.save(CREATE_SAVE_MESSAGE)
        else:
            if GENERAL_CAT not in page.text:
                page.text += "\n[["+GENERAL_CAT+"]]"
                page.save(ADD_CAT_SAVE_MESSAGE)
    else:
        print(elem[0]+" not a P property")

