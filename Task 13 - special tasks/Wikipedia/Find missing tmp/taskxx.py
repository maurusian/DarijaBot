import pywikibot

anchor = "{{لعمالات ولأقاليم دلمغريب"

site = pywikibot.Site()

cat = "تصنيف:أقاليم لمغريب"

SAVE_MESSAGE = "عطاشة 13: زيادة ديال لموضيل د لأقاليم ل لمقالات"

provinces = pywikibot.Category(site,cat).articles()

#print(len(list(provinces)))

for province in provinces:
    tmp_tag = "{{"+province.title()+"}}"
    if tmp_tag not in province.text:
        province.text = province.text.replace(anchor,tmp_tag+"\n"+anchor)
        province.save(SAVE_MESSAGE)
