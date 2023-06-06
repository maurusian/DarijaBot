import pywikibot
from pywikibot.exceptions import OtherPageSaveError, APIError, InvalidTitleError
from urllib.request import urlopen, quote, Request
from urllib.error import URLError
import json, sys, os
#import SPARQLWrapper
import requests
from datetime import datetime


MIN_YEAR = -625
MAX_YEAR = int(datetime.now().year)

BC_PART = " قبل لميلاد"
YEAR_PART = " (عام)"

LOG_PAGE_TITLE = 'User:DarijaBot/log'

SAVE_LOG_MESSAGE = "Added log entry"


def run_for_years():
    print("iterate over years")
    counter = 0
    for year in range(MIN_YEAR,MAX_YEAR+1):
        
        
        if year < 0:
            ary_title = str(abs(year))+BC_PART
            en_title = str(abs(year))+" BC"
        elif year > 0 and year < 32:
            ary_title = str(year)+YEAR_PART
            en_title = 'AD '+str(year)
        elif year > 31 and year < 151:
            ary_title = str(year)
            en_title = 'AD '+str(year)
        elif year > 31:
            ary_title = str(year)
            en_title = str(year)
        
        site = pywikibot.Site()
        repo = site.data_repository()
        
        #year_item = pywikibot.ItemPage(repo,str(year))
        #year_item.get()
        
        site_ary = pywikibot.Site('ary','wikipedia')
        
        page = pywikibot.Page(site_ary, ary_title)
        if page.text != '':
            print("Page "+ary_title+" found")
            site_en = pywikibot.Site('en','wikipedia')
            year_en = pywikibot.Page(site_en, en_title)
            year_item = pywikibot.ItemPage.fromPage(year_en)
            if 'arywiki' not in year_item.sitelinks.keys():
                try:
                    year_item.setSitelink(page, summary=u'Setting sitelink by adding ary category')
                    counter+=1
                except OtherPageSaveError:
                    log_error(LOG_PAGE_TITLE,str(sys.exc_info()),SAVE_LOG_MESSAGE,site)
                    print(sys.exc_info())
                except APIError:
                    log_error(LOG_PAGE_TITLE,str(sys.exc_info()),SAVE_LOG_MESSAGE,site)
                    print(sys.exc_info())
                except InvalidTitleError:
                    log_error(LOG_PAGE_TITLE,str(sys.exc_info()),SAVE_LOG_MESSAGE,site)
                    print(sys.exc_info())
                    
            
    print(str(counter)+" objects linked")


#run for years
run_for_years()



