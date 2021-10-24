import pywikibot
from pgvbotLib import log_error
from pywikibot.exceptions import NoPageError



TASK_LOG_PAGE = "مستخدم:DarijaBot/عطاشة 15: زّيادة د تّصنيفات ديال لخاصيات د ويكيداطا"

LANGUAGES = {'fr':'French'
            ,'ar':'Arabic'
            ,'sv':'Swedish'
            ,'de':'German'
            ,'pt':'Portuguese'
            ,'it':'Italian'
            ,'pl':'Polish'
            ,'el':'Greek'
            ,'lij':'Ligurian'
            ,'vec':'Venetian'}

CATEGORY_NAME_TEMPLATES = {'ary':'تصنيف:پاجات كاتخدم خاصية ديال {}'
                          ,'fr':'Catégorie:Page utilisant {}'
                          ,'ar':'تصنيف:صفحات تستخدم خاصية {}'
                          ,'sv':'Kategori:Mallar och moduler som använder Property:{}'
                          ,'de':'Kategorie:Wikipedia:Seite verwendet {}'
                          ,'pt':'Categoria:!Artigos que utilizam {}'
                          ,'it':'Categoria:{} letta da Wikidata'
                          ,'pl':'Kategoria:Strony używające właściwości {}'
                          ,'el':'Κατηγορία:Σελίδα που χρησιμοποιεί δεδομένα των Wikidata/{}'
                          ,'lij':'Categorîa:{} lezûa da Wikidata'
                          ,'vec':'Categoria:{} lexesta da Wikidata'}

SAVE_LOG_MESSAGE = "دخلة ف لّوحة تزادت"

with open('quarry-59138-untitled-run585800.json','r') as f:
    dict_data = eval(f.read())


site_ary = pywikibot.Site('ary','wikipedia')
for elem in dict_data['rows']:
    if 'P' in elem[0]:
        print(elem[0])
        wikidata_property = elem[0]
        title_ary = CATEGORY_NAME_TEMPLATES['ary'].format(wikidata_property)
        page_ary = pywikibot.Page(site_ary, title_ary)

        if page_ary.text != '':
            i = 0
            for lang in LANGUAGES.keys():
                site_lang = pywikibot.Site(lang,'wikipedia')
                title_lang = CATEGORY_NAME_TEMPLATES[lang].format(wikidata_property)
                page_lang = pywikibot.Page(site_lang, title_lang)
                
                if page_lang.text != '':
                    #repo_lang = site_lang.data_repository()
                    try:
                        item_lang = pywikibot.ItemPage.fromPage(page_lang)
                        if 'arywiki' not in item_lang.sitelinks.keys():
                            item_lang.setSitelink(page_ary, summary=u'Setting sitelink by adding ary category')
                            print("Linked ary category for property "+wikidata_property+" with "+LANGUAGES[lang]+" equivalent")
                            
                        else:
                            print("Property "+wikidata_property+" already linked")
                        break
                    except NoPageError:
                        print("Page on "+LANGUAGES[lang]+" Wikipedia for Property "+wikidata_property+" is not linked to Wikidata")
                        
                        wiki_log_message = "لپاج [[:"+lang+":"+title_lang+"]] مامربوطاش معا ويكيداطا"
                        log_error(TASK_LOG_PAGE,wiki_log_message,SAVE_LOG_MESSAGE,site_ary)
                    
                i+=1

            if i == len(LANGUAGES):
                console_log_message = "Property "+wikidata_property+" could not be linked to any page"
                print(console_log_message)
                wiki_log_message = "لپاج [[:"+title_ary+"]] ماتربطاتش معا ويكيداطا"
                log_error(TASK_LOG_PAGE,wiki_log_message,SAVE_LOG_MESSAGE,site_ary)
