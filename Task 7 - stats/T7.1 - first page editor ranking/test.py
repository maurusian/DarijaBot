#from pgvbotLib import *
import pywikibot
from copy import deepcopy
#from sys import argv
import re, sys, os, requests
from datetime import datetime, timedelta
#import Levenshtein
from fuzzywuzzy import fuzz
from collections import defaultdict
from pywikibot import pagegenerators

ADMINS = ["Reda benkhadra", "Ideophagous", "Anass Sedrati", "مرشح الإساءة","Mounir Neddi"]
IGNORE_LIST = ["CommonsDelinker"]

MAX_TOP_EDITORS = 5

NAMESPACES = [0,1,4,5,6,7,10,11,12,13,100,101,118,119,828,829]

SAVE_MESSAGE = "أپدييت ل آخر كلاصمة د لكتاتبيا"

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

def fetch_recent_edits(admins):
    """Fetch recent edits in the last 30 days, ignoring administrators, bots, and IGNORE_LIST."""
    site = pywikibot.Site()
    now = datetime.utcnow()
    start_date = now  # The more recent date
    end_date = now - timedelta(days=30)  # The older date

    contributions = defaultdict(lambda: {"edits": 0, "new": 0, "bytes": 0})

    for entry in site.recentchanges(reverse=True, bot = False, anon = False, start=start_date, user="Siaahmed",excludeuser=list(admins).extend(IGNORE_LIST),changetype="edit"):
        user = entry["user"]

        contributions[user]["edits"] += 1
        if entry["type"] == "new":
            contributions[user]["new"] += 1
        contributions[user]["bytes"] += entry["newlen"] - entry["oldlen"]

    return contributions


site = pywikibot.Site()

"""
admins = get_administrators()
print(admins)

now = datetime.utcnow()
start_date = now - timedelta(days=1)  # The more recent date
end_date = now   # The older date
print()
"""

username = "TohaomgBot"

user = pywikibot.User(site,username)

print(user.groups())
