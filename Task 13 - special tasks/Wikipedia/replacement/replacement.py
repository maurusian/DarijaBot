#from pgvbotLib import *
import pywikibot
from copy import deepcopy
#from sys import argv
import re, sys, os, json

def read_json_file(site, json_page_title):
    json_page = pywikibot.Page(site, json_page_title)
    json_content = json_page.get()
    return json.loads(json_content)


if __name__ == '__main__':
    JOBID = 1
    json_page_title = f"ميدياويكي:عطاشة13.خدمة{JOBID}.json"
    site = pywikibot.Site()
    json_data = read_json_file(site, json_page_title)

    status = json_data["STATUS"]

    if status == "ACTIVE":
    

        if json_data["JOBDESC"]["FILTERBYTYPE"] == "cat":
            cat = pywikibot.Category(site,json_data["JOBDESC"]["FILTERBYVALUE"])
            source = json_data["JOBDESC"]["SOURCE"]
            target = json_data["JOBDESC"]["TARGET"]
            SAVE_MESSAGE = json_data["JOBDESC"]["SAVE_MESSAGE"]

            for template in cat.articles():
                tmptext = template.text
                tmptext = tmptext.replace(source, target)
                if tmptext != template.text:
                    template.text = tmptext
                    template.save(SAVE_MESSAGE)

    else:
        print(f"The task is currently inactive with status={status}")

