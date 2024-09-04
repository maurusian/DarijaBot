import pywikibot
from datetime import datetime, timedelta

site = pywikibot.Site()

DAYS_PAST = 30

END_TIME = datetime.now()
START_TIME = END_TIME - timedelta(days=DAYS_PAST)

NAMESPACES = [0,1]

user_name = 'Mr.Kenzo1'  # replace with the target user's name
#last_changes = site.recentchanges(reverse=True, bot=False)
last_changes = list(site.recentchanges(reverse=True, bot = False, anon = False, start=START_TIME,end=END_TIME,changetype="new",patrolled=True,namespaces=NAMESPACES)) #

# Filter changes by the user
user_changes = [change for change in last_changes if change['user'] == user_name]

print(len(user_changes))
