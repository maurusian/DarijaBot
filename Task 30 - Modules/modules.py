import pywikibot, traceback
from arywikibotlib import interlink_page
from copy import deepcopy
#import re
#from openpyxl import Workbook

MODULE_NS = 828

mdl_ary_ns = "مودول:"
mdl_en_ns = "Module:"

SAVE_MESSAGE = "شرح د لمودول تزاد"

INTERLINK_ERR_MSG = "الربيط ديال [[{}]] ب ويكيداطا ماصدقش"

WIKILOG_PAGE_TITLE = "خدايمي:DarijaBot/عطاشة 30: صفاحي د الشرح ديال لمودولات"

LOG_SAVE_MSG = "زيادة د دخلة ف لّوحة"

LANGS = ["en", "fr", "ar"]
MDL_NS = {"en":"Module:","fr":"Module:","ar":"وحدة:"}

TMP_DOC_LANG = {'en':'/doc','fr':'/Documentation','ar':'/شرح','ary':'/شرح'}

IGNORE_SIDE_PAGE_PARTS = ["/شرح","/styles.css","/ملعب","/تيران","Portal/images/"]

def validate_mdl_page(mdl_title):
    for ttl_part in IGNORE_SIDE_PAGE_PARTS:
        if ttl_part in mdl_title:
            return False
    return True

def write_to_interlink_log(MSG):
    WIKILOG = pywikibot.Page(site,WIKILOG_PAGE_TITLE)
    WIKILOG.text+="\n*"+MSG
    WIKILOG.save(LOG_SAVE_MSG)

def create_mdl_doc_page(lang,site,site_lang,mdl_page,lang_mdl_page):
    """
    Creates Module doc page, by copying from another language,
    if the doc page doesn't in arywiki
    """
    mdl_doc_page_title = mdl_page.title()+TMP_DOC_LANG["ary"]
    mdl_doc_page = pywikibot.Page(site,mdl_doc_page_title)
    if mdl_doc_page.text == "":
        lang_mdl_doc_page_title = lang_mdl_page.title()+TMP_DOC_LANG[lang]
        lang_mdl_doc_page = pywikibot.Page(site_lang,lang_mdl_doc_page_title)
        mdl_doc_page.text = lang_mdl_doc_page.text
        mdl_doc_page.save(SAVE_MESSAGE)
    

if __name__=="__main__":
    site = pywikibot.Site()

    pool = site.allpages(namespace=MODULE_NS, filterredir=False)

    pool_size = len(list(deepcopy(pool)))
    print('Pool size: '+str(pool_size))
    i = 1
    #pages_in_log = load_pages_in_log()

    for mdl_page in pool:
        print('*********'+str(i)+'/'+str(pool_size))
        if validate_mdl_page(mdl_page.title()): # "/شرح" not in mdl_page.title() and "/styles.css" not in mdl_page.title():
            for lang in LANGS:
                mdl_lang_ns = MDL_NS[lang]
                lang_mdl_name = mdl_page.title().replace(mdl_ary_ns,mdl_lang_ns)
                site_lang = pywikibot.Site(lang,"wikipedia")
                lang_mdl_page = pywikibot.Page(site_lang,lang_mdl_name)
                if lang_mdl_page.text != "":
                    try:
                        item = pywikibot.ItemPage.fromPage(lang_mdl_page)
                        if 'arywiki' not in item.sitelinks.keys():
                            interlink_page(mdl_page,lang_mdl_page,lang)
                            create_mdl_doc_page(lang,site,site_lang,mdl_page,lang_mdl_page)
                        break
                    except:
                        print(traceback.format_exc())
                        write_to_interlink_log(INTERLINK_ERR_MSG.format(mdl_page.title()))
            try:
                print("checking Wikidata item for Module page")
                item = pywikibot.ItemPage.fromPage(mdl_page)
                for lang in LANGS:
                    if lang in item.sitelinks.keys():
                        print("--------******************-------")
                        print(item.sitelinks[lang])
                        site_lang = pywikibot.Site(lang,"wikipedia")
                        create_mdl_doc_page(lang,site,site_lang,mdl_page,item.sitelinks[lang])
                        break
            except:
                print(traceback.format_exc())
        i+=1
                        
