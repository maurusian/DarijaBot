import pywikibot
from pgvbotLib import *
from copy import deepcopy

TEMPLATE_CATEGORY_CODE = "<noinclude>[[تصنيف:قوالب زادهوم داريجابوت]]</noinclude>"

MONTHS = [{"en_name":"January","ary_name":u"يناير","day_count":31,"alt_name":""}
         ,{"en_name":"February","ary_name":u"فبراير","day_count":29,"alt_name":u"يبراير"}
         ,{"en_name":"March","ary_name":u"مارس","day_count":31,"alt_name":""}
         ,{"en_name":"April","ary_name":u"أبريل","day_count":30,"alt_name":""}
         ,{"en_name":"May","ary_name":u"ماي","day_count":31,"alt_name":""}
         ,{"en_name":"June","ary_name":u"يونيو","day_count":30,"alt_name":""}
         ,{"en_name":"July","ary_name":u"يوليوز","day_count":31,"alt_name":""}
         ,{"en_name":"August","ary_name":u"غشت","day_count":31,"alt_name":""}
         ,{"en_name":"September","ary_name":u"شتنبر","day_count":30,"alt_name":""}
         ,{"en_name":"October","ary_name":u"أكتوبر","day_count":31,"alt_name":u"كتوبر"}
         ,{"en_name":"November","ary_name":u"نونبر","day_count":30,"alt_name":""}
         ,{"en_name":"December","ary_name":u"دجنبر","day_count":31,"alt_name":""}]


BOT_TEMPLATE = "{{پاج كيعمرها بوت}}"

BIRTH_TEMPLATE_PART = "قالب:ناس تزادو ف "
DEATH_TEMPLATE_PART = "قالب:ناس توفاو ف "

SAVE_MESSAGE = "تّصنيف د لقالب تزاد"
          
site = pywikibot.Site()

for month in MONTHS:
    for i in range(1,month['day_count']):
        title = BIRTH_TEMPLATE_PART+str(i)+" "+month['ary_name']
        page = pywikibot.Page(site,title)
        if BOT_TEMPLATE in page.text and TEMPLATE_CATEGORY_CODE not in page.text:
            page.text += '\n'+TEMPLATE_CATEGORY_CODE
            page.save(SAVE_MESSAGE)

        
        title = DEATH_TEMPLATE_PART+str(i)+" "+month['ary_name']
        page = pywikibot.Page(site,title)
        if BOT_TEMPLATE in page.text and TEMPLATE_CATEGORY_CODE not in page.text:
            page.text += '\n'+TEMPLATE_CATEGORY_CODE
            page.save(SAVE_MESSAGE)
