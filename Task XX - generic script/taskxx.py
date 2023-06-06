"""
This is a generic script for any bot task on arywiki
"""
import sys, json, pywikibot

def read_json_file(site, json_page_title):
    json_page = pywikibot.Page(site, json_page_title)
    json_content = json_page.get()
    return json.loads(json_content)

def taskxx(site, obj):
    return None

def main():

    site = pywikibot.Site()
    JOB_NUMBER = 1
    TASK_NUMBER = 0
    json_page_title = f"ميدياويكي:عطاشة{TASK_NUMBER}.خدمة{JOB_NUMBER}.json"
    site.login()

    json_data = read_json_file(site, json_page_title)
    
    taskxx(site, obj)

if __name__ == "__main__":
    main()
