from pgvbotLib import *
import pywikibot, re, sys, os
from copy import deepcopy
#from sys import argv 
from pywikibot.exceptions import UnknownSiteError
#from arywikibotlib import getOnlyArticles

SAVE_MESSAGE = "تّصنيفات لي ناقصين تزادو من ويكيپيديا ب {}"

RECENT_LOG_FILE = "recent_log.txt"

LANGUAGE_MAPPING =  {'en':'نّڭليزية'
                    ,'fr':'لفرانساوية'
                    ,'ar':'لعربية'
                    ,'de':'لألمانية'}

CAT_BAN_LIST = ["تصنيف:مقالات مهضورا","تصنيف:صفحة توضيح","تصنيف:زريعة",
                "تصنيف:زريعة شخصيات","تصنيف:زريعات د لارتيكلات كاملين",
                "تصنيف:زريعة د لمغريب","تصنيف:زريعة شخصيات د لمغريب",
                "تصنيف:مدون أترية مفقود","تصنيف:مصطلحات ؤ تعبيرات لاتينية"
                ,"تصنيف:پاجات كيتبعهوم بوت","تصنيف:جميع مقالات البذور"
                ,"تصنيف:تاريخ د لعرب","تصنيف:عرب"]

CAT_LANG_VALUES = {'en':'Category'
                  ,'fr':'Catégorie'
                  ,'ar':'تصنيف'
                  ,'de':'Kategorie'}

PROJ_LANG_VALUES = {'en':'Wikipedia'
                   ,'fr':'Wikipédia'
                   ,'ar':'ويكيبيديا'
                   ,'de':'Wikipedia'}

def load_pages_in_log():
    if not os.path.exists(RECENT_LOG_FILE):
        return []
    with open(RECENT_LOG_FILE,'r',encoding='utf-8') as f:
        page_name_list = f.read().strip().splitlines()
    
    for i in range(len(page_name_list)):
        page_name_list[i] = page_name_list[i].strip()
    
    return page_name_list

namespace = int(input("Enter namespace: "))
lang = input("Enter language code en/fr/ar: ")

site = pywikibot.Site()

site_lang = pywikibot.Site(lang,'wikipedia')

if namespace == 0:
    pool = site.allpages(namespace=0,filterredir=False)
    pool_size = len(list(deepcopy(site.allpages(namespace=0,filterredir=False))))
else:
    pool = site.allpages(namespace=namespace)
    pool_size = len(list(deepcopy(site.allpages(namespace=namespace))))
#pool = [page for page in site.allpages() if validate_page(page)]



print('Pool size: '+str(pool_size))

title_part = ''
if namespace == 14:
    title_part = CAT_LANG_VALUES[lang]+':'
elif namespace == 4:
    title_part = PROJ_LANG_VALUES[lang]+':'


i = 1
pages_in_log = load_pages_in_log()

with open(RECENT_LOG_FILE,'a',encoding='utf-8') as f:
    for page in pool:
        print('*********'+str(i)+'/'+str(pool_size))
        if str(page.title()) not in pages_in_log:
            if (namespace == 0 and validate_page(page)) or (namespace in (4,14)):
                temp = page.text
                try:
                    #print(len(list(page.iterlanglinks())))
                    for link in page.iterlanglinks():
                        linkparts = str(link)[2:-2].split(':')
                        #print(linkparts)
                        if linkparts[0] == lang:
                            print(linkparts)
                            #print(linkparts[1])
                            page_lang = pywikibot.Page(site_lang,title_part+linkparts[-1])
                            #print(page_lang.title())
                            for category in page_lang.categories():                
                                if not category.isHiddenCategory() and 'stub' not in category.title().lower():
                                    #print(category)
                                    cat = pywikibot.Page(site_lang,str(category)[3+len(lang):-2])

                                    for cat_link in cat.iterlanglinks():
                                        cat_linkparts = str(cat_link)[2:-2].split(':')
                                        
                                        if cat_linkparts[0] == 'ary' :
                                            new_cat = '[['+str(cat_link)[3+len('ary'):].replace(CAT_LANG_VALUES[lang]+':',"تصنيف:").replace(PROJ_LANG_VALUES[lang]+':',"ويكيپيديا:")
                                            raw_new_cat = new_cat[2:-2]
                                            if raw_new_cat not in page.text and raw_new_cat not in CAT_BAN_LIST:
                                                page.text += '\n'+new_cat
                                            
                    if temp != page.text:
                        page.save(SAVE_MESSAGE.format(LANGUAGE_MAPPING[lang]))
                except KeyError:
                    print(page_lang.title())
                    print(sys.exc_info())
                except UnknownSiteError:
                    print(page_lang.title())
                    print(sys.exc_info())
            f.write(page.title()+'\n')
        i+=1
