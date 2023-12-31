#from pgvbotLib import *
import pywikibot
from copy import deepcopy
#from sys import argv
import re, sys, os
from datetime import datetime, timedelta
#import Levenshtein
from fuzzywuzzy import fuzz

SAVE_MESSAGE = "أپدييت ل آخر كلاصمة د لكتاتبيا"

SAVE_PAGE = "موضيل:شحال د التشابه معا لعربية"

LOG_FILE = "log.txt"

HEADER = "<noinclude>{{پاج كيعمرها بوت2}}</noinclude>"

FOOTER = """<noinclude>
{{شرح}}
[[تصنيف:قوالب د إحصائيات ويكيپيديا]]
</noinclude>"""

site = pywikibot.Site()

#page = pywikibot.Page(site,title)


#START_TIME = datetime.strptime(START_TIME_STR,DATE_FORMAT)

#print(help(site.recentchanges))

def clean_text(text):
    template_usage_ptrn = r"\{\{.+?\}\}"
    ref_usage_pattern = r"<ref>.+?</ref>"

    tmp = re.sub(template_usage_ptrn,"",text)
    tmp = re.sub(ref_usage_pattern,"",tmp)WW


def get_perc_for_single_page(ary_text,ar_text):
    cleaned_ar_text = clean_text(ar_text)
    cleaned_ary_text = clean_text(ary_text)

    return 
    

def get_ar_text(page):
    pass


pool = site.allpages(namespace=0,filterredir=False)

pool_size = len(list(deepcopy(site.allpages(namespace=0,filterredir=False))))

print('Pool size: '+str(pool_size))

i = 1
percs = []
for page in pool:
    print('*********'+str(i)+'/'+str(pool_size))

    ar_text = get_ar_text(page)

    if ar_text is not None:
        percs.append(get_perc_for_single_page(ary_text,ar_text))


average = round(sum(percs)/len(percs),2)

template_page = pywikibot.Page(site,SAVE_PAGE)

template_page.text = HEADER+BODY+"\n\n"+FOOTER

#print(template_page.text)

template_page.save(SAVE_MESSAGE)

#"""
    
