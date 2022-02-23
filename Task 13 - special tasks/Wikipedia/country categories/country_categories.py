import json
import pywikibot

country_items_file = "countries.json"

NSCAT = "تصنيف"

COUNTRIES_CAT = "تصنيف:بلدان"

SAVE_ADD_CNTRY_CAT = "تصنيف د لبلاد تزاد"

def load_country_items():
    with open(country_items_file,'r',encoding='utf-8') as cif:
        country_items_str = cif.read()
        country_items_json = json.loads(country_items_str)

        return list(country_items_json)

def get_qcode(wkd_link):
    return wkd_link.split('/')[-1]

def get_ary_title(entity, site):
    wkd_link = entity["item"] #entity = load_country_items()[i]
    qcode = get_qcode(wkd_link)
    
    repo = site.data_repository()
    item = pywikibot.ItemPage(repo, qcode)
    item.get()

    if "arywiki" in item.sitelinks.keys():
        return str(item.sitelinks["arywiki"]).strip("[]")

    return None

def exist_country_cat(country_name,site):
    page = pywikibot.Page(site,NSCAT+":"+country_name)

    

    
if __name__ == "__main__":
    site = pywikibot.Site()
    
    country_items = load_country_items()

    for entity in country_items:
        country_name = get_ary_title(entity, site)
        if country_name is not None:
            page = pywikibot.Page(site,country_name)
            country_cat_title = NSCAT+":"+country_name
            if '[['+country_cat_title not in page.text:
                page.text+='\n[['+country_cat_title+']]'
                page.save(SAVE_ADD_CNTRY_CAT)

            cat_page = pywikibot.Page(site,country_cat_title)

            if cat_page.text == "" or '[['+COUNTRIES_CAT not in cat_page.text:
                cat_page.text+='\n[['+COUNTRIES_CAT+']]'
                cat_page.save(SAVE_ADD_CNTRY_CAT)
                

            
