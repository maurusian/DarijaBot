#from pgvbotLib import *
import pywikibot
from copy import deepcopy
#from sys import argv
import re, sys, os
from datetime import datetime, timedelta
#import Levenshtein
from fuzzywuzzy import fuzz

SAVE_MESSAGE = "أپدييت ل إحصائيات لمجالات سّمياتية"

LOG_FILE = "log.txt"

site = pywikibot.Site()

articles = list(site.allpages(namespace=0,filterredir=False))


print(len(articles))

