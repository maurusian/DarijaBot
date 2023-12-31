"""
This is a generic script for any bot task on arywiki
"""
import sys, json, pywikibot
from arywikibotlib import interlink_page

def read_json_file(site, json_page_title):
    json_page = pywikibot.Page(site, json_page_title)
    json_content = json_page.get()
    return json.loads(json_content)

def taskxx(site, obj):
    return None

def main():

    site = pywikibot.Site()
    #JOB_NUMBER = 1
    #TASK_NUMBER = 0
    json_page_title = f"ميدياويكي:عطاشة23.خدمة3.json"
    site.login()

    json_data = read_json_file(site, json_page_title)

    #setup
    save_message = json_data["SAVE_MESSAGE"]
    save_redir_msg = json_data["SAVE_REDIR_MSG"]
    link_to_lang = json_data["LINK_TO_LANG"]
    site_lang = pywikibot.Site(link_to_lang,"wikipedia")

    for i in range(201, -1, -1):

        #initialize values
        variables = {
            "deca": i,
            "decade": i*10,
            "century": i // 10 + 1,
            "end_decade": i*10 + 9,
            "millennium": i // 100 + 1,
            "formatted_year_list":"{{hlist|"+" | ".join(["[["+str(x)+"]]" for x in range(i*10,i*10+10)])+"}}"
        }

        #(re)set texts
        text = '\n\n'.join(json_data["TEXT_STRUCT"])+"\n\n"+json_data["FOOTER"]
        page_ttl = json_data["TITLE"]
        redir_ttl = json_data["REDIRECT_TITLE"]
        redir_text = json_data["REDIR_TEXT"]
        link_to_ttl = json_data["LINK_TO_TTL"]
        

        for key, value in variables.items():
            key_str = "{"+key+"}"
            text = text.replace(key_str,str(value))
            page_ttl = page_ttl.replace(key_str,str(value))
            redir_ttl = redir_ttl.replace(key_str,str(value))
            redir_text = redir_text.replace(key_str,str(value))
            link_to_ttl = link_to_ttl.replace(key_str,str(value))
        print(page_ttl)

        page = pywikibot.Page(site, page_ttl)
        TO_ADD =  False
        if page.text.strip() == "":
            page.text = text
            page.save(save_message)
            TO_ADD =  True

        redir = pywikibot.Page(site, redir_ttl)

        if redir.text.strip() == "":
            redir.text = redir_text
            redir.save(save_redir_msg)

        item = None
        if TO_ADD:
            try:
                link_to_page = pywikibot.Page(site_lang, link_to_ttl)
                item = pywikibot.ItemPage.fromPage(link_to_page)
                #print(list(item.sitelinks.keys()))
                #break
                if "arywiki" in item.sitelinks.keys():
                    TO_ADD = False
                    
            except:
                print(traceback.format_exc())
                print("no Wikidata item")
                #TO_ADD = True

            if item is not None:
                interlink_page(page,link_to_page,"ary","main namespace")

        #break

if __name__ == "__main__":
    main()
