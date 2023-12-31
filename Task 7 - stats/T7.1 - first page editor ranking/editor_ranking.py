#from pgvbotLib import *
import pywikibot
from copy import deepcopy
#from sys import argv
import re, sys, os
from datetime import datetime, timedelta
#import Levenshtein
from fuzzywuzzy import fuzz

#ADMINS = ["Reda benkhadra", "Ideophagous", "Anass Sedrati", "مرشح الإساءة","Mounir Neddi"]
IGNORE_LIST = ["CommonsDelinker","Poulinets"]

MAX_TOP_EDITORS = 5

SAVE_MESSAGE = "أپدييت ل آخر كلاصمة د لكتاتبيا"

NAMESPACES = [0,1,4,5,6,7,10,11,12,13,100,101,118,119,828,829]

SAVE_PAGE = "قالب:تضمين ديال ترتيب د لكتاتبيا ف صفحة لولة"

LOG_FILE = "log.txt"

HEADER = "<noinclude>{{پاج كيعمرها بوت2}}</noinclude>"

FOOTER = """<noinclude>
{{شرح}}
[[تصنيف:قوالب د إحصائيات ويكيپيديا]]
</noinclude>"""

BODY = """{{ترتيب د لكتاتبيا د صفحة لولة
|كتاتبي1={editor1}
|تبديلات1={edits1}
|مقالات1={articles1}
|زيادة1={posneg1}
|كاراكطيرات1={chars1}
|كتاتبي2={editor2}
|تبديلات2={edits2}
|مقالات2={articles2}
|زيادة2={posneg2}
|كاراكطيرات2={chars2}
|كتاتبي3={editor3}
|تبديلات3={edits3}
|مقالات3={articles3}
|زيادة3={posneg3}
|كاراكطيرات3={chars3}
|كتاتبي4={editor4}
|تبديلات4={edits4}
|مقالات4={articles4}
|زيادة4={posneg4}
|كاراكطيرات4={chars4}
|كتاتبي5={editor5}
|تبديلات5={edits5}
|مقالات5={articles5}
|زيادة5={posneg5}
|كاراكطيرات5={chars5}
}}"""


def get_administrators():
    """Return a set of Wikipedia administrator usernames."""
    site = pywikibot.Site()
    
    # Fetch administrators using the allusers API with augroup set to sysop
    return set(user['name'] for user in site.allusers(group='sysop'))

site = pywikibot.Site()

#page = pywikibot.Page(site,title)


#START_TIME = datetime.strptime(START_TIME_STR,DATE_FORMAT)

#print(help(site.recentchanges))


i = 1
editors = {}
last_days = 0
while len(editors) < 5:
    last_days+=30
    difference = timedelta(days=last_days)
    START_TIME = datetime.now() - difference
    last_changes = list(site.recentchanges(reverse=True, bot = False, anon = False, start=START_TIME,changetype="edit",patrolled=True,namespaces=NAMESPACES))
    last_creations = list(site.recentchanges(reverse=True, bot = False, anon = False, start=START_TIME,changetype="new",patrolled=True,namespaces=NAMESPACES))
    admins=get_administrators()
    edit_size = len(list(deepcopy(last_changes)))
    print('Edit size: '+str(edit_size))
    
    for change in last_changes:
        print('*********'+str(i)+'/'+str(edit_size))
        editor = change["user"]
        user_editor = pywikibot.User(site,editor)
        if 'sysop' not in user_editor.groups() and editor not in admins and editor not in IGNORE_LIST and not user_editor.is_blocked():
            if editor not in editors.keys():
                editors[editor] = {"edit_count":0,"size":0,"new_count":0}
            editors[editor]["edit_count"]+=1
            editors[editor]["size"]+=int(change["newlen"])-int(change["oldlen"])
        i+=1
    new_size = len(list(deepcopy(last_creations)))
    i=1
    print("processing new page creations")
    print('New size: '+str(new_size))
    for change in last_creations:
        print('*********'+str(i)+'/'+str(new_size))
        editor = change["user"]
        if editor in editors.keys():
            editors[editor]["new_count"]+=1
        i+=1
            
        

    print("Editors count: "+str(len(editors)))
    editors = dict(sorted(editors.items(), key=lambda item: (item[1]["edit_count"],item[1]["new_count"],item[1]["size"]), reverse=True))
    x = 0
    top_editors = []
    for item in editors.items():
        top_editors.append({"user":item[0],"edit_count":item[1]["edit_count"],"size":item[1]["size"],"new_count":item[1]["new_count"]})
        x+=1
        if x==MAX_TOP_EDITORS:
            break
    #print(editors)

counter = 1
for top_editor in top_editors: 
    BODY = BODY.replace("{editor"+str(counter)+"}",top_editor["user"])
    BODY = BODY.replace("{edits"+str(counter)+"}",str(top_editor["edit_count"]))
    BODY = BODY.replace("{articles"+str(counter)+"}",str(top_editor["new_count"]))
    BODY = BODY.replace("{posneg"+str(counter)+"}",(lambda size:"+" if size>0 else ("-" if size<0 else ""))(top_editor["size"]))
    BODY = BODY.replace("{chars"+str(counter)+"}",str(abs(top_editor["size"])))
    counter+=1



template_page = pywikibot.Page(site,SAVE_PAGE)

template_page.text = HEADER+BODY+"\n\n"+FOOTER

#print(template_page.text)

template_page.save(SAVE_MESSAGE)

#"""
    
