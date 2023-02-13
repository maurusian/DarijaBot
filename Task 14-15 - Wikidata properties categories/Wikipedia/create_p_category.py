import pywikibot

CAT_TITLE_PART = "تصنيف:پاجات كاتخدم خاصية ديال "
HIDDEN = "__HIDDENCAT__"

HIDDEN_TAG_OLD = "{{تصنيف مخفي}}"

HIDDEN_TAG = "{{تصنيف مخبي}}"

GENERAL_CAT = "تصنيف:پاجات كاتخدم خاصيات ديال ويكيداطا|{}"

CREATE_SAVE_MESSAGE = "عطاشة15: پاج د تّصنيف ديال خاصية د ويكيداطا تقادات"

ADD_CAT_SAVE_MESSAGE = "عطاشة15: أپدييت ل تصنيف ديال خاصية د ويكيداطا"

FILEMAME = "quarry-70843-untitled-run702727.json"

WIKIDATA_PROP_TAG = "{{تصنيف ويكيداطا|{}}}"

site = pywikibot.Site()

with open(FILEMAME,'r') as f:
    dict_data = eval(f.read())


for elem in dict_data['rows']:
    if 'P' in elem[0]:
        print(elem[0])

        title = CAT_TITLE_PART + elem[0]
        page = pywikibot.Page(site, title)
        WIKIDATA_PROP_ACTUAL_TAG = WIKIDATA_PROP_TAG.replace('{}',elem[0])
        if page.text == '':
            page.text = WIKIDATA_PROP_ACTUAL_TAG+'\n'+HIDDEN_TAG+"\n[["+GENERAL_CAT.replace('{}',elem[0].replace('P',''))+"]]"
            page.save(CREATE_SAVE_MESSAGE)
        else:
            temp = page.text
            temp = temp.replace(HIDDEN_TAG_OLD,HIDDEN_TAG)
            temp = temp.replace(HIDDEN,HIDDEN_TAG)
            if GENERAL_CAT.split('|')[0] not in page.text:
                temp += "\n[["+GENERAL_CAT.replace('{}',elem[0].replace('P',''))+"]]"
                #page.save(ADD_CAT_SAVE_MESSAGE)
            elif GENERAL_CAT.split('|')[0]+'|' not in page.text:
                temp = temp.replace(GENERAL_CAT.split('|')[0],GENERAL_CAT.replace('{}',elem[0].replace('P','')))
            if WIKIDATA_PROP_ACTUAL_TAG not in page.text:
                temp = WIKIDATA_PROP_ACTUAL_TAG+"\n"+temp
            if temp != page.text:
                page.text = temp
                page.save(ADD_CAT_SAVE_MESSAGE)
    else:
        print(elem[0]+" not a P property")

