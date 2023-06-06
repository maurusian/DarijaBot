#from pgvbotLib import *
import pywikibot
from copy import deepcopy
#from sys import argv
import re, sys, os, requests
from datetime import datetime, timedelta
#import Levenshtein
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup
from arywikibotlib import get_user_edit_count

MAX_TOP_EDITORS = 5

YES = "أه"

NO = "لا"

SAVE_MESSAGE = "أپدييت ل آخر كلاصمة د لكتاتبيا"

SAVE_PAGE_TITLE = "موضيل:ليستة د لڤوط على لبوتات"

LOG_FILE = "log.txt"

#HEADER = "<noinclude>{{پاج كيعمرها بوت2}}</noinclude>"

FOOTER = """<noinclude>
{{شرح}}
[[تصنيف:قوالب د إحصائيات ويكيپيديا]]
</noinclude>"""

HEADER = """<noinclude>{{پاج كيعمرها بوت2}}

</noinclude>
لأپدييت اللخراني: {last_update}
{| class="wikitable"
|+ ليستة
|-
! كتاتبي !! مجموع التبديلات !! مستوفي لقاعدة د 30 تبديل !! تاريخ د التبديل اللخر !! مبلوكي
"""

table_footer = """
|}"""
row_pattern = """|-
| {username} || {total_count} || {count2} || {last_edit_date_with_link} || {blocked}
"""

def has_edit_in_last_6_months(user):

    if user_acct.last_edit is not None:
        last_edit_timestamp = user_acct.last_edit[2]
        current_date = datetime.now()

        delta = current_date - last_edit_timestamp

        if delta.days <= 180:
            return True
    return False

def validate_page_for_30_edit_rule(page,user):
    USER_PAGE_ARY = user.getUserPage().title() #.replace("User","خدايمي")
    print(dir(user))
    USER_TALK_PAGE_ARY  = user.getUserTalkPage().title() #.replace("UserTalk","")
    if page.title() == USER_PAGE_ARY or page.title() == USER_TALK_PAGE_ARY:
        return False
    if page.title().split(':')[0] in ACCEPTED_ARY_NS_LIST:
        return True
    return False

def satisfies_30_edit_rule(user):
    count = 0
    for contribution in user.contributions():
        #print(help(contribution[0].get))
        if validate_page_for_30_edit_rule(contribution[0],user):
            count+=1
            if count > 29:
                return True
    return False

def build_table(top_users):
    text = HEADER

    for user_info in top_users:
        pass


#request_header = REQUEST_HEADER

site = pywikibot.Site()

user_list = site.allusers()

top_users = []

for user in user_list:
    edit_count = int(user["editcount"])
    user_acct = pywikibot.User(site,"Ideophagous")
    print(user["name"])
    print(user_acct.last_edit)
    print(has_edit_in_last_6_months(user_acct))
    #print(satisfies_30_edit_rule(user_acct))
    if edit_count >= 100 and has_edit_in_last_6_months(user_acct):
        top_users.append((user["name"],edit_count))
    break
    #top_users = sorted(top_users,key=lambda x:-x[1])


#print(top_users)
                         
    
    #user_count = get_user_edit_count(user["name"],site.lang,"wikipedia")
