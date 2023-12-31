#from pgvbotLib import *
import pywikibot
from copy import deepcopy
#from sys import argv
import re, sys, os
from datetime import datetime, timedelta
#import Levenshtein
from fuzzywuzzy import fuzz

namespaces = {'article':0
             ,'talk':1
             ,'user':2
             ,'user talk':3
             ,'project':4
             ,'project talk':5
             ,'file':6
             ,'file talk':7
             ,'mediawiki':8
             ,'mediawiki talk':9
             ,'template':10
             ,'template talk':11
             ,'help':12
             ,'help talk':13
             ,'category':14
             ,'category talk':15
             ,'portal':100
             ,'portal talk':101
             ,'draft':118
             ,'draft talk':119
             ,'module':828
             ,'module talk':829
             ,'timedtext':710
             ,'timedtext talk':711
             ,'gadget':2300
             ,'gadget talk':2301
             ,'gadget definition':2302
             ,'gadget def talk':2303
             }

SAVE_MESSAGE = "أپدييت ل إحصائيات لمجالات سّمياتية"

LOG_FILE = "log.txt"

FOOTER = """<noinclude>
{{شرح}}
[[تصنيف:موضيلات د إحصائيات ويكيپيديا]]
[[تصنيف:موضيلات زادهوم داريجابوت]]
</noinclude>"""

HEADER = """<noinclude>{{پاج كيعمرها بوت2}}

باش تزيد تّعرّف على لمجالات سّمياتية، شوف [[ويكيپيديا:مجال سمياتي]].
</noinclude>

{| class="wikitable"
|+ إحصائيات
|-
! مجال سمياتي !! حساب !! صفاحي رئيسيين !! تحويلات
"""

table_footer = """
|}"""
row_pattern = """|-
| {ns} || {count} || {main} || {redir}
"""

template_title = "موضيل:إحصائيات د لمجالات السمياتية"

site = pywikibot.Site()

#page = pywikibot.Page(site,title)


#START_TIME = datetime.strptime(START_TIME_STR,DATE_FORMAT)

#print(help(site.recentchanges))


text = HEADER
#special case for namespace 0
ns_count = len(list(site.allpages(namespace=0)))
redir_count = len(list(site.allpages(namespace=0,filterredir=True)))
text+=row_pattern.replace('{ns}','مقالات').replace('{count}',str(ns_count)).replace('{main}',str(ns_count-redir_count)).replace('{redir}',str(redir_count))

#other namespaces
del namespaces['article']
print(namespaces)
for ns in namespaces.items():
    ns_count = len(list(site.allpages(namespace=ns[1])))
    redir_count = len(list(site.allpages(namespace=ns[1],filterredir=True)))
    text+=row_pattern.replace('{ns}','{{ns:'+str(ns[1])+'}}').replace('{count}',str(ns_count)).replace('{main}',str(ns_count-redir_count)).replace('{redir}',str(redir_count))


text+=table_footer+FOOTER

page = pywikibot.Page(site,template_title)

page.text = text

page.save(SAVE_MESSAGE)


        

