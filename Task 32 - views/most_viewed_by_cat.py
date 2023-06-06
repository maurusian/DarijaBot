#from pgvbotLib import *
import pywikibot
from copy import deepcopy
#from sys import argv
import re, sys, os
from datetime import datetime, timedelta
#import Levenshtein
from fuzzywuzzy import fuzz

MAX_TOP_EDITORS = 5

SAVE_MESSAGE = ""

SAVE_PAGE = ""

LOG_FILE = "log.txt"


site = pywikibot.Site()

title = ""

