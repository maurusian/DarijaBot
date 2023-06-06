import pywikibot, traceback
from arywikibotlib import getItemIdentities
from copy import deepcopy
#import re
from openpyxl import Workbook

MAIN_NS = 0

def write_to_interlink_log(MSG):
    WIKILOG = pywikibot.Page(site,WIKILOG_PAGE_TITLE)
    WIKILOG.text+="\n*"+MSG
    WIKILOG.save(LOG_SAVE_MSG)

if __name__=="__main__":
    """
    site = pywikibot.Site()

    pool = site.allpages(namespace=MAIN_NS, filterredir=False)

    pool_size = len(list(deepcopy(pool)))
    print('Pool size: '+str(pool_size))
    i = 1
    #pages_in_log = load_pages_in_log()
    qcodes = {}
    for article in pool:
        print('*********'+str(i)+'/'+str(pool_size))
        identities = []
        try:
            identities = getItemIdentities(article)
        except:
            continue
        for identity in identities:
            if identity in qcodes.keys():
                qcodes[identity]+=1
            else:
                qcodes[identity] = 1
        i+=1
    #"""
    with open("temp.txt","r") as t:
        #t.write(str(qcodes))
        qcodes = dict(eval((t.read())))
    

    
    wb = Workbook()
    sheet = wb.active

    sheet['A1'] = 'Qcode'
    sheet['B1'] = 'Frequency'

    j=2
    for qcode, freq in qcodes.items():
        sheet['A'+str(j)] = qcode
        sheet['B'+str(j)] = freq
        j+=1

    wb.save('qcodes.xlsx')
    
