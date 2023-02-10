import pywikibot
from arywikibotlib import interlink_page
#from copy import deepcopy
#import re
#from openpyxl import Workbook

#langxx_cat_ttl = "Category:Lang-x templates"
langxx_cat_ttl_ary = "تصنيف:موضيلات د لوغة-xx"

tmp_ary_ns = "موضيل:"

SAVE_MESSAGE = "موضيل د لوغة تصاوب"

INTERLINK_ERR_MSG = "الربيط ديال [[{}]] ب ويكيداطا ماصدقش"

WIKILOG_PAGE_TITLE = "خدايمي:DarijaBot/عطاشة 13: عطاشات خاصين"

LOG_SAVE_MSG = "زيادة د دخلة ف لّوحة"

MOVE_SAVE_MESSAGE = "تحويل ديال الصفحة د لقالب"

site = pywikibot.Site()

#site_en = pywikibot.Site("en","wikipedia")

langxx_cat = pywikibot.Category(site,langxx_cat_ttl_ary)

langxx_tmps = langxx_cat.members()

print(len(list(langxx_cat.members())))

def write_to_interlink_log(MSG):
    WIKILOG = pywikibot.Page(site,WIKILOG_PAGE_TITLE)
    WIKILOG.text+="\n*"+MSG
    WIKILOG.save(LOG_SAVE_MSG)

for tmp in langxx_tmps:
    if 'موضيل:Lang-' in tmp.title():
        ary_title = tmp.title().replace("Template:",tmp_ary_ns)
        ary_tmp_page = pywikibot.Page(site,ary_title)
        new_title = ary_title.replace("Lang","لوغة")
        new_page = pywikibot.Page(site,new_title)
        if new_page.text == "":
            ary_tmp_page.move(new_title,MOVE_SAVE_MESSAGE)
        """
        if ary_tmp_page.text.strip() == "":
            ary_tmp_page.text = tmp.text
            ary_tmp_page.save(SAVE_MESSAGE)

            try:
                item = pywikibot.ItemPage.fromPage(tmp)
                if "ary" not in item.sitelinks.keys():
                    interlink_page(ary_tmp_page,tmp,"ary")
            except:
                write_to_interlink_log(INTERLINK_ERR_MSG.format(ary_title))
        
        
        if "[[تصنيف:موضيلات د لوغة-xx]]" not in ary_tmp_page.text:
            ary_tmp_page.text+="<noinclude>[[تصنيف:موضيلات د لوغة-xx]]</noinclude>"

            ary_tmp_page.text = ary_tmp_page.text.replace("</noinclude><noinclude>","")

            ary_tmp_page.save(SAVE_MESSAGE)
        """
        
        
