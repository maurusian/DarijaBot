import pywikibot
#import random
#from copy import deepcopy
#from params import MONTHS
#from datetime import datetime, timezone
#from sys import argv
import requests, json
from pgvbotLib import log_error
#from pywikibot.exceptions import ArticleExistsConflictError, NoPageError

COMPARE_LINK_PATTERN = "https://www.wikidata.org/w/api.php?format=json&action=compare&prop=diff&torelative=prev&fromrev={}"

LOG_PAGE_TITLE = 'User:DarijaBot/log'

SAVE_LOG_MESSAGE = "Added log entries"

def log_error(LOG_PAGE_TITLE,log_message,save_log_message,site):
    log_page = pywikibot.Page(site, LOG_PAGE_TITLE)
    if log_page.text != '':
        log_page.text += '\n* '+log_message
    else:
        log_page.text = '* '+log_message

    log_page.save(save_log_message)


site = pywikibot.Site()

user = pywikibot.User(site, "DarijaBot")

#print(user.contributions())
print(help(user.contributions))
log_message = ""
for c in user.contributions():
    #print(help(c))
    #print(c.keys())
    revision_id = c[1]
    print(revision_id)

    COMPARE_LINK = COMPARE_LINK_PATTERN.format(revision_id)

    json_data = requests.get(COMPARE_LINK).json()
    
    if "</del>" in str(json_data):
        print(c[0])
        #print(json_data)
        
        log_message+="*Interwiki link replacement error: Bot replaced linked page for arywiki in object "+str(c[0]).replace("wikidata:",'')+" (revision ID: "+str(revision_id)+"). Please check potential duplicates on arywiki.\n"
#print(log_message) #dry run
log_error(LOG_PAGE_TITLE,log_message,SAVE_LOG_MESSAGE,site)
    
#print(dir(user))
