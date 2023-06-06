import pywikibot
import re
#from arywikibotlib import *

OUTLINK_PATTERN = r'\[\[.+?\]\]'

#title = "الأعمدة ديال هيركوليس"
title = "بيرطراند راسل"
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


TEMPLATE_NS = "قالب"
site = pywikibot.Site()
page = pywikibot.Page(site,title)


TALK_RESPONSE_TAG_PART = "{{جاوب|"
def user_call_string(site,page):
    users = get_admins(site) + list(get_nonbot_contributors(page).keys())

    users = list(set(users))

    #r = len(users) // 6
    calls = []
    for i in range(0,len(users),6):
        calls.append(TALK_RESPONSE_TAG_PART+'|'.join(users[i:i+6])+'}}')

    return ' '.join(calls)

def get_admins(site):
    return [user['name'] for user in site.allusers(group='sysop')]

def get_nonbot_contributors(page):
    contributors = dict(page.contributors())
    bots = []
    for contributor in contributors.keys():
        user = pywikibot.User(site,contributor)
        if 'bot' in user.groups():
            bots.append(contributor)

    for user in bots:
        del contributors[user]
    
    return contributors

#admins,contributors = get_admins(site),list(get_nonbot_contributors(page).keys())

print(user_call_string(site,page))
