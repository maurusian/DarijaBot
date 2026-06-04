import pywikibot
import re
from pywikibot import pagegenerators
from copy import deepcopy

import traceback

site = pywikibot.Site()
site.throttle.maxdelay = 0
site.login()
repo = site.data_repository()

def get_actual_template_name(title):
    """Return the final target if the موضيل is a redirect, else return the same name."""
    try:
        template_page = pywikibot.Page(site, f"موضيل:{title}")
        if template_page.isRedirectPage():
            #print("this is a redirect")
            return template_page.getRedirectTarget().title().replace("موضيل:", "")
        return title
    except Exception:
        print(f"Error while checking موضيل:{title}")
        traceback.print_exc()
        return title

def replace_template_redirects(text):
    #print(text)
    def replacer(match):
        full_match = match.group(0)
        #print(full_match)
        template_name = match.group(1).strip()
        actual_name = get_actual_template_name(template_name)
        #print(f"actual_name: {actual_name}")
        if template_name != actual_name:
            return full_match.replace("{{" + template_name, "{{" + actual_name, 1)
        return full_match

    # This regex matches {{Template name}} or {{Template name|...}}
    return re.sub(r"\{\{\s*([^\|\}\n]+)", replacer, text)

def main():
    
    gen = site.allpages(namespace=0, filterredir=False)
    i = 0
    pool_size = len(list(site.allpages(namespace=0, filterredir=False)))
    #title = "داكا (مدينة)"
    #gen = [pywikibot.Page(site,title)]
    for page in gen:
        i+=1
        #print(page.title())
        print(f"******** {i}/{pool_size}")
        try:
            text = page.text
            new_text = replace_template_redirects(text)
            if new_text != text:
                page.text = new_text
                page.save(summary="تبديل سميات الموضيلات باش تولي لي فالأصل ماشي لي كدير تحويلة", minor=False)
        except Exception as e:
            print(f"Error processing {page.title()}: {e}")
        
if __name__ == "__main__":
    main()
