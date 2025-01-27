#from pgvbotLib import *
import pywikibot
from copy import deepcopy
#from sys import argv
import re, sys, os, json
from datetime import datetime, timedelta
#import Levenshtein
from fuzzywuzzy import fuzz

batch_filename = "ميدياويكي:عطاشة7.1.json"

site = pywikibot.Site()

def read_json(site):
    batch = pywikibot.Page(site,batch_filename)

    jason = json.loads(batch.text)

    return jason

jason = read_json(site)

#ADMINS = ["Reda benkhadra", "Ideophagous", "Anass Sedrati", "مرشح الإساءة","Mounir Neddi"]
IGNORE_LIST = jason["IGNORE_LIST"]

MAX_TOP_EDITORS = jason["MAX_TOP_EDITORS"]

SAVE_MESSAGE = jason["SAVE_MESSAGE"]

NAMESPACES = jason["NAMESPACES"]

SAVE_PAGE = jason["SAVE_PAGE"]

DAYS_PAST = jason["DAYS_PAST"]

LOG_FILE = "log.txt"

HEADER = "<noinclude>{{پاج كيعمرها بوت2}}</noinclude>"

FOOTER = """<noinclude>
{{شرح}}
[[تصنيف:موضيلات د إحصائيات ويكيپيديا]]
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
}}
<div class="ranking-table-first-page">
<center><small>محسوبين غير المساهمات ف 30 يوم اللخرة<br>ديال كتاتبيا ماعندهمش صلاحيات د أمغار</small></center>"""

MAX_INTERVAL_DAYS = 30


def get_administrators(site):
    """Return a set of Wikipedia administrator usernames."""    
    # Fetch administrators using the allusers API with augroup set to sysop
    return set(user['name'] for user in site.allusers(group='sysop'))

def vanished_user(editor):
    """Returns whether a user is a vanished user or not."""
    if "vanished user" in editor.lower() or "renamed user" in editor.lower():
        return True
    return False

#page = pywikibot.Page(site,title)


#START_TIME = datetime.strptime(START_TIME_STR,DATE_FORMAT)

#print(help(site.recentchanges))


editors = {}
END_TIME = datetime.now()
START_TIME = END_TIME - timedelta(days=DAYS_PAST)

print(f"DAYS_PAST: {DAYS_PAST}")

while len(editors) < 5:
    #difference = timedelta(days=DAYS_PAST)
    #print(DAYS_PAST)
    #START_TIME = datetime.now() - difference
    #print(START_TIME)
    admins=get_administrators(site)
    batch_count = DAYS_PAST // MAX_INTERVAL_DAYS
    if DAYS_PAST % MAX_INTERVAL_DAYS != 0:
        batch_count+=1
    for i in range(1, batch_count+1):
        END_TIME = START_TIME + timedelta(days=MAX_INTERVAL_DAYS)
        print(f"START_TIME: {START_TIME}")
        print(f"END_TIME: {END_TIME}")
        interval_last_changes = list(site.recentchanges(reverse=True, bot = False, anon = False, start=START_TIME,end=END_TIME,changetype="edit",patrolled=True,namespaces=NAMESPACES))
        interval_last_creations = list(site.recentchanges(reverse=True, bot = False, anon = False, start=START_TIME,end=END_TIME,changetype="new",patrolled=True,namespaces=NAMESPACES))

        edit_size = len(list(deepcopy(interval_last_changes)))
        print(f"Edit size for edit batch {i} out of {batch_count}: {edit_size}")

        j = 1
        for change in interval_last_changes:
            print('*********'+str(j)+'/'+str(edit_size))
            editor = change["user"]
            user_editor = pywikibot.User(site,editor)
            if ('sysop' not in user_editor.groups() and 'bot' not in user_editor.groups()
                and editor not in admins and editor not in IGNORE_LIST
                and not user_editor.is_blocked() and not vanished_user(editor)):
                if editor not in editors.keys():
                    editors[editor] = {"edit_count":0,"size":0,"new_count":0}
                editors[editor]["edit_count"]+=1
                editors[editor]["size"]+=int(change["newlen"])-int(change["oldlen"])
            j+=1
            
        new_size = len(list(deepcopy(interval_last_creations)))
        j = 1
        print("processing new page creations")
        print('New size: '+str(new_size))
        for change in interval_last_creations:
            print('*********'+str(i)+'/'+str(new_size))
            editor = change["user"]
            if editor in editors.keys():
                editors[editor]["new_count"]+=1
                editors[editor]["edit_count"]+=1
                editors[editor]["size"]+=int(change["newlen"])
            j+=1

        START_TIME = END_TIME
                
        

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


print("Editor ranking update finished at: ", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


#"""
    
