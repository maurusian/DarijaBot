from pgvbotLib import *
import pywikibot
from copy import deepcopy
#from sys import argv
import re, sys, os
from pywikibot.exceptions import NoPageError

RECENT_LOG_FILE = "recent_log.txt"

def load_pages_in_log():
    if not os.path.exists(RECENT_LOG_FILE):
        return []
    with open(RECENT_LOG_FILE,'r',encoding='utf-8') as f:
        page_name_list = f.read().strip().splitlines()
    
    for i in range(len(page_name_list)):
        page_name_list[i] = page_name_list[i].strip()
    
    return page_name_list

def get_final_target(page):
    temp = page
    while temp.isRedirectPage():
        target_title = temp.text.strip().split('[[')[1].strip()[:-2]
        temp = pywikibot.Page(site,target_title)
    return temp
        

#List of subprograms
#Help functions
##Stub tag
##Source header
##Source tag
##No category tag
##No backlinks tag
##Authority Control tag
##Deadend tag
##No sources tag
##Empty paragraph tag
##Good start tag
##Good article tag
##Excellent article tag


##############################################Help functions##############################################
###Tags
INFOBOX_TAG_PATTERN = r"{{معلومات.*}}"
DATABOX = "{{Databox}}"

###Functions
def word_count(text):
    return len(text.split())

def has_infobox_tag(page):
    regexp = re.compile(INFOBOX_TAG_PATTERN)
    if regexp.search(page.text):
        return True

    if DATABOX in page.text:
        return True
    return False

def get_commons_category(page):
    COMMONS_CAT_TAG_PART = "{{Commons category|"

    if COMMONS_CAT_TAG_PART in page.text:
        page_parts = page.text.split(COMMONS_CAT_TAG_PART)
        commons_cat = page_parts[-1].split('}}')[0]
        return commons_cat
    else:
        return None



##############################################Stub tag treatment##############################################
###Tags
OLD_STUB_TAG = "{{بذرة}}"
NEW_STUB_TAG = "{{زريعة}}"

###Save messages
CORRECT_STUB_TAG_MESSAGE = "إصلاح طّاڭ د زريعة."
ADD_STUB_TAG_MESSAGE = "زيادة د طّاڭ د زريعة."
REMOVE_STUB_TAG_MESSAGE = "تحياد طّاڭ د زريعة."

###Functions
def setStubTag(page,text,MESSAGE):
    has_stub_tag = False
    if NEW_STUB_TAG in text:
        has_stub_tag = True
    else:
        temp = text
        text = text.replace(OLD_STUB_TAG,NEW_STUB_TAG)
        if text != temp:
            has_stub_tag = True
            MESSAGE += CORRECT_STUB_TAG_MESSAGE+SPACE
            #print("changing old stub tag with new one")

    if word_count(text) < 250 and not has_stub_tag:
        text += "\n"+NEW_STUB_TAG
        MESSAGE += ADD_STUB_TAG_MESSAGE+SPACE
    elif word_count(text) > 500 and has_stub_tag:
        text = text.replace(NEW_STUB_TAG,"")
        MESSAGE += REMOVE_STUB_TAG_MESSAGE+SPACE

    return text,MESSAGE





##############################################Source header treatment##############################################
###Header patterns
ACCEPTED_SECTION_HEADER_PATTERN = "==\s*عيون\s*لكلام\s*=="
FAULTY_SOURCE_SECTION_HEADERS = ["\\=\\=\s*[ل]{0,1}عيون\s*د\s*لكلام\s*\\=\\="
                                ,"\\=\\=\s*[ل]{0,1}عين\s*[د]{0,1}\s*لكلام\s*\\=\\="
                                ,"\\=\\=\s*[ا]{0,1}[ل]{0,1}مصاد[ي]{0,1}ر\s*\\=\\="
                                ,"\\=\\=\s*[ا]{0,1}[ل]{0,1}م[ا]{0,1}راج[ي]{0,1}ع\s*\\=\\="
                                ,"\\=\\=\s*[ا]{0,1}[ل]{0,1}مصدر\s*\\=\\="
                                ,"\\=\\=\s*[ا]{0,1}[ل]{0,1}مرجع\s*\\=\\="
                                ,"\\=\\=\s*[ل]{0,1}عيون\s*\\=\\="
                                ,ACCEPTED_SECTION_HEADER_PATTERN
                                ]
                                #,"==\s*عيون\s*لكلام\s*=="]
SECTION_HEADER = "== عيون لكلام =="

###Save messages
CORRECT_SOURCE_HEADER_MESSAGE = "إصلاح لهادر د عيون لكلام."
ADD_SOURCE_HEADER_MESSAGE = "زيادة د لهادر د عيون لكلام."

###Functions
def setSourceHeaderTag(page,text,MESSAGE):
    has_source_section_header = False
    if SECTION_HEADER in text:
        has_source_section_header = True
    else:
        for header in FAULTY_SOURCE_SECTION_HEADERS:
            text = re.sub(header,SECTION_HEADER,text)
            if text != page.text:
                #print("changing section header")
                has_source_section_header = True
                MESSAGE += CORRECT_SOURCE_HEADER_MESSAGE+SPACE
                """
                with open("temp.txt",'w',encoding="utf-8") as f:
                    f.write(text)
                """
                break

    if NEW_SOURCE_TAG in text and not has_source_section_header:
        text = text.replace(NEW_SOURCE_TAG,SECTION_HEADER+"\n"+NEW_SOURCE_TAG) #"\n\n"+SECTION_HEADER
        MESSAGE += ADD_SOURCE_HEADER_MESSAGE+SPACE
    elif NEW_SOURCE_TAG not in text:
        print("Could not fix source header due to lack of source tag")
    return text,MESSAGE





##############################################Source tag treatment##############################################
###Tags
OLD_SOURCE_TAG1 = "{{مراجع}}"
OLD_SOURCE_TAG2 = "<\s*references\s*/>"
NEW_SOURCE_TAG = "{{عيون}}"

###Save messages
CORRECT_SOURCE_TAG_MESSAGE = "إصلاح طّاڭ د عيون لكلام."
ADD_SOURCE_TAG_MESSAGE ="زيادة د طّاڭ د عيون لكلام."

###Functions
def setSourceTag(page,text,MESSAGE):
    has_source_tag = False
    if NEW_SOURCE_TAG in text:
        has_source_tag = True
            
    else:
        temp = text
        text = text.replace(OLD_SOURCE_TAG1,NEW_SOURCE_TAG)
           
        if text != temp:
            has_source_tag = True
            MESSAGE += CORRECT_SOURCE_TAG_MESSAGE+SPACE
            text = re.sub(OLD_SOURCE_TAG2,"",text) #ensure removal of the other tag, only one is needed
            #print("changing old source tag (1) with new one")

        temp = text
        #new_text = new_text.replace(OLD_SOURCE_TAG2,NEW_SOURCE_TAG)
        text = re.sub(OLD_SOURCE_TAG2,NEW_SOURCE_TAG,text)
            
        if text != temp:
            has_source_tag = True
            MESSAGE += CORRECT_SOURCE_TAG_MESSAGE+SPACE
            text = text.replace(OLD_SOURCE_TAG1,"") #ensure removal of the other tag, only one is needed
            #print("changing old source tag (2) with new one")

    if not has_source_tag:
        text+="\n"+NEW_SOURCE_TAG
        MESSAGE += ADD_SOURCE_TAG_MESSAGE+SPACE

    return text,MESSAGE

##############################################No category tag treatment##############################################
###Tags
NO_CATEGORY_TAG = "{{مقالة ما مصنفاش}}"

###Save messages
ADD_NO_CAT_TAG_MESSAGE = 'طاڭ ديال "مقالة مامصنفاش" تزاد.'
REMOVE_NO_CAT_TAG_MESSAGE = 'طاڭ ديال "مقالة مامصنفاش" تحيّد.'

###Functions

def hasExplicitCategory(page):
    len_cat = len(list(page.categories()))
    if len_cat==0:
        #print("page has "+str(len_cat)+" categories")
        return False
    i = 0
    for category in page.categories():
        i+=1
        if str(category.title()).strip() in page.text:
            #print("found "+str(i)+" categories so far")
            return True
    #print("found "+str(i)+" categories (final)")
    return False

def setCategoryTag(page,text,MESSAGE):
    #print("checking category tag")
    if not hasExplicitCategory(page):
        if NO_CATEGORY_TAG not in text:
            #print("Adding NO_CATEGORY_TAG")
            text = NO_CATEGORY_TAG+'\n'+text
            MESSAGE+=ADD_NO_CAT_TAG_MESSAGE+SPACE
    else:
        if NO_CATEGORY_TAG in text:
            #print("Removing NO_CATEGORY_TAG")
            text = text.replace(NO_CATEGORY_TAG,'')
            MESSAGE+=REMOVE_NO_CAT_TAG_MESSAGE+SPACE

    return text,MESSAGE


##############################################No backlinks tag treatment##############################################
###Tags
ORPHANED_PAGE_TAG = "{{مقالة مقطوعة من شجرة}}"

###Save messages
ADD_ORPHAN_TAG_MESSAGE = 'طاڭ ديال "مقطوعة من شجرة" تزاد.'
REMOVE_ORPHAN_TAG_MESSAGE = 'طاڭ ديال "مقطوعة من شجرة" تحيّد.'

###Functions
def setOrphanTag(page,text,MESSAGE):
    should_add_orphan_tag = True
    links =  page.backlinks()
    for link in links:
        if validate_page(link):
            should_add_orphan_tag = False
            break
    if should_add_orphan_tag:
        if ORPHANED_PAGE_TAG not in text:
            text = ORPHANED_PAGE_TAG+'\n'+text
            MESSAGE+=ADD_ORPHAN_TAG_MESSAGE+SPACE
    else:
        if ORPHANED_PAGE_TAG in text:
            text = text.replace(ORPHANED_PAGE_TAG,'')
            MESSAGE+=REMOVE_ORPHAN_TAG_MESSAGE+SPACE
    return text,MESSAGE


##############################################Authority Control tag##############################################
###Tags
OLD_AUTHORITY_CONTROL_TAG = "{{ضبط استنادي}}"
NEW_AUTHORITY_CONTROL_TAG = "{{ضبط مخازني}}"

###Save messages
FIX_AUTHORITY_CONTROL_TAG = "طّاڭ ديال ضبط مخازني تصلح"
ADD_AUTHORITY_CONTROL_TAG = "طّاڭ ديال ضبط مخازني تزاد"

###Functions
def setAuthorityControlTag(page,text,MESSAGE):
    has_authority_control_tag = False
    if NEW_AUTHORITY_CONTROL_TAG in text:
        has_authority_control_tag = True
    else:
        temp = text
        text = text.replace(OLD_AUTHORITY_CONTROL_TAG,NEW_AUTHORITY_CONTROL_TAG)
        if text != temp:
            has_authority_control_tag = True
            MESSAGE += FIX_AUTHORITY_CONTROL_TAG+SPACE
            #print("changing old authority control tag with new one")

    if not has_authority_control_tag:
        text+="\n"+NEW_AUTHORITY_CONTROL_TAG
        MESSAGE += ADD_AUTHORITY_CONTROL_TAG+SPACE
    return text,MESSAGE


##############################################Deadend tag##############################################
###Tags
CUL_DE_SAC_TAG = "{{مقالة زنقة ماكاتخرجش}}"
OUTLINK_PATTERN = r'\[\[.+?\]\]'

###Save messages
ADD_DEADEND_TAG_MESSAGE = "طّاڭ ديال زنقة ماكاتخرجش تزاد"
REMOVE_DEADEND_TAG_MESSAGE = "طّاڭ ديال زنقة ماكاتخرجش تحيد"

###Functions
def setDeadendTag(page,text,MESSAGE,site):
    has_deadend_tag = False
    should_not_add_tag = False
    if CUL_DE_SAC_TAG in text:
        has_deadend_tag = True
    else:
        links = re.findall(OUTLINK_PATTERN,page.text)
        for link in links:
            link_page = pywikibot.Page(site,link[2:-2].split('|')[0])
            link_page = get_final_target(link_page) #make sure the linked page is not a redirect page, but its final target
            if link_page.text != '' and validate_page(link_page):
                should_not_add_tag = True
                break

    if has_deadend_tag and should_not_add_tag:
        text = text.replace(CUL_DE_SAC_TAG,'').strip()
        MESSAGE += REMOVE_DEADEND_TAG_MESSAGE+SPACE
    elif not has_deadend_tag and not should_not_add_tag:
        text = CUL_DE_SAC_TAG + "\n" + text
        MESSAGE += ADD_DEADEND_TAG_MESSAGE+SPACE
    return text,MESSAGE

##############################################No sources tag##############################################
###Tags
NO_SOURCES_ON_PAGE_TAG = "{{مقالة ناقصينها عيون لكلام}}"
SOURCE_EXIST_PATTERN = r"ref.+?/ref"
REF_TAG = "<ref"

###Save messages
ADD_NO_SOURCE_TAG_MESSAGE = "طّاڭ ديال ناقصين عيون لكلام تزاد"
REMOVE_NO_SOURCE_TAG_MESSAGE = "طّاڭ ديال ناقصين عيون لكلام تحيد"

###Functions
def setNoSourceTag(page,text,MESSAGE):
    has_no_source_tag = False
    if NO_SOURCES_ON_PAGE_TAG in text:
        has_no_source_tag = True
    
    sources = re.findall(SOURCE_EXIST_PATTERN,page.text)

    if REF_TAG not in page.text and not has_no_source_tag:
        text = NO_SOURCES_ON_PAGE_TAG + '\n' + text
        MESSAGE += ADD_NO_SOURCE_TAG_MESSAGE+SPACE
    elif REF_TAG in page.text and has_no_source_tag:
        text = text.replace(NO_SOURCES_ON_PAGE_TAG,'').strip()
        MESSAGE += REMOVE_NO_SOURCE_TAG_MESSAGE+SPACE
    return text,MESSAGE


##############################################Empty paragraph tag##############################################
###Tags
EMPTY_PARAGRAPH_TAG = "{{فقرة مازالا خاوية ولا ناقصة}}"
EMPTY_PARAGRAPH_PATTERN1 = r"==.+==[\n\s]+(?===\s|$)"
EMPTY_PARAGRAPH_PATTERN2 = r"===.+===[\n\s]+(?====\s|$)"

###Save messages
ADD_EMPTY_PARAGRAPH_TAG_MESSAGE = "طّاڭ ديال فقرة خاوية تزاد"

###Functions
def setEmptyParagraphTag(page,text,MESSAGE):
    #print("checking empty paragraph tag")
    #treating case 1
    titles = re.findall(EMPTY_PARAGRAPH_PATTERN1,text)
    #print("found "+str(len(titles))+" empty paragraphs")
    temp = text
    for title in titles:
        temp = re.sub(title.strip(),title.strip()+'\n'+EMPTY_PARAGRAPH_TAG,temp)
    #treating case 2
    titles = re.findall(EMPTY_PARAGRAPH_PATTERN2,temp)
    #print("found "+str(len(titles))+" empty paragraphs")
    for title in titles:
        temp = re.sub(title.strip(),title.strip()+'\n'+EMPTY_PARAGRAPH_TAG,temp)
        
    if temp != text:
        text = temp
        MESSAGE += ADD_EMPTY_PARAGRAPH_TAG_MESSAGE+SPACE
    return text,MESSAGE

##############################################Transfer category##############################################
###Tags


###Save messages
REDIR_CAT_ADD_MESSAGE = "تصنيف د تّحويلات تزاد"

###Functions
def add_redirect_cat(page,text,MESSAGE):
    if REDIRECT_PAGE_CAT_CODE not in page.text:
        text+='\n\n'+REDIRECT_PAGE_CAT_CODE
        MESSAGE +=REDIR_CAT_ADD_MESSAGE+SPACE
    return text,MESSAGE

##############################################Missing pictures tag##########################################
###Tags and search string segmemts
PICTURE_MISSING_TAG = "{{مقالة ناقصينها تصاور|{parameter}}}"
PICTURE_MISSING_TAG_PATTERN = r"{{مقالة ناقصينها تصاور\|.*?}}"
PICTURE_MISSING_TAG_PART = "{{مقالة ناقصينها تصاور"
#INFOBOX_TAG_PART = "{{معلومات"

GALLERY_PART_DICT = {'en':'<gallery'
                    ,'fr':'{{Gallery'
                    ,'ar':'<gallery'}
FILE_PART_DICT = {'en':'[[File:'
                 ,'fr':'[[Fichier:'
                 ,'ar':'[[ملف:'}
CITY_INFOBOX_TAG_PART = "{{معلومات مدينة"

###Save messages
ADD_PICTURE_MISSING_TAG = "طّاڭ ديال ناقصين تصاور تزاد"
RMV_PICTURE_MISSING_TAG = "طّاڭ ديال ناقصين تصاور تحيّد"

###Functions
def add_missing_picture_tag(page,text,MESSAGE):
    #print("checking picture tag")
    has_picture = False
    has_picture_missing_tag = False
    add_picture_tag = False
    picture = ""
    commons_cat = get_commons_category(page)
    if FILE_PART_DICT['en'] in text or FILE_PART_DICT['ar'] in text or GALLERY_PART_DICT['en'] in text:
        #print(FILE_PART_DICT['en'] in text)
        
        has_picture = True
        #print("found article to have a picture "+str(page.title())+" flag has_picture="+str(has_picture))
    
    if PICTURE_MISSING_TAG_PART in text:
        has_picture_missing_tag = True


    if not has_picture:
        
        #print("treating article that has no picture "+str(page.title()))
        if CITY_INFOBOX_TAG_PART in text:
            add_picture_tag = True
        
        try:
            item = pywikibot.ItemPage.fromPage(page)

            item_dict = item.get()

            if "claims" in item_dict.keys():

                item_claims = item_dict["claims"]

                #check image property
                if 'P18' in item_claims.keys():
                    picture = str(item_claims['P18'][0].getTarget())[10:-2].replace(' ','_')
                    add_picture_tag = True
                    if has_infobox_tag(page):
                        has_picture = True
                            

                #check image logo property
                if 'P154' in item_claims.keys():
                    picture = str(item_claims['P154'][0].getTarget())[10:-2].replace(' ','_')
                    add_picture_tag = True
                    if has_infobox_tag(page):
                        has_picture = True
                        
            if not add_picture_tag:
                        #check EN article
                lang = 'en'
                if lang+'wiki' in item.sitelinks.keys():
                    site_lang = pywikibot.Site(lang,'wikipedia')
                    title_lang = str(item.sitelinks[lang+'wiki'])[2:-2]
                    page_lang = pywikibot.Page(site_lang, title_lang)

                    if FILE_PART_DICT[lang] in page_lang.text or GALLERY_PART_DICT[lang] in page_lang.text:
                        add_picture_tag = True
                            
                        
                #check AR article
                lang = 'ar'
                if lang+'wiki' in item.sitelinks.keys():
                    site_lang = pywikibot.Site(lang,'wikipedia')
                    title_lang = str(item.sitelinks[lang+'wiki'])[2:-2]
                    page_lang = pywikibot.Page(site_lang, title_lang)

                    if FILE_PART_DICT[lang] in page_lang.text or GALLERY_PART_DICT[lang] in page_lang.text:
                        add_picture_tag = True

                #check FR article
                lang = 'fr'
                if lang+'wiki' in item.sitelinks.keys():
                    site_lang = pywikibot.Site(lang,'wikipedia')
                    title_lang = str(item.sitelinks[lang+'wiki'])[2:-2]
                    page_lang = pywikibot.Page(site_lang, title_lang)

                    if FILE_PART_DICT[lang] in page_lang.text or GALLERY_PART_DICT[lang] in page_lang.text:
                        add_picture_tag = True
                        
        except NoPageError:
            add_picture_tag = False

        #check commons catagory tag
        if commons_cat is not None:
            add_picture_tag = True
            picture = "Category:"+commons_cat.replace(' ','_')

    if (has_picture or not add_picture_tag) and has_picture_missing_tag:
        text = re.sub(PICTURE_MISSING_TAG_PATTERN,'',text).strip()
        MESSAGE +=RMV_PICTURE_MISSING_TAG+SPACE
    elif not has_picture and not has_picture_missing_tag and add_picture_tag:
        #print(not has_picture)
        text = PICTURE_MISSING_TAG.replace('{parameter}',picture)+'\n'+text
        MESSAGE +=ADD_PICTURE_MISSING_TAG+SPACE

    return text,MESSAGE


##############################################No link to Wikidata cat########################################
###Category
NO_LINK_TO_WIKIDATA_CAT = "[[تصنيف:أرتيكلات مامربوطينش معا ويكيداطا]]"


###Save messages
ADD_NO_LINK_TO_WIKIDATA_MESSAGE = "تزاد تّصنيف ديال [[تصنيف:أرتيكلات مامربوطينش معا ويكيداطا]]"
RMV_NO_LINK_TO_WIKIDATA_MESSAGE = "تحيّد تّصنيف ديال [[تصنيف:أرتيكلات مامربوطينش معا ويكيداطا]]"

###Functions
def add_no_link_to_wikidata_cat(page,text,MESSAGE):
    #print("checking wikidata tag")
    has_no_wikidata_cat = False
    if NO_LINK_TO_WIKIDATA_CAT in text:
        has_no_wikidata_cat = True
    try:
        item = pywikibot.ItemPage.fromPage(page)
        has_wikidata_item_page = True
    except NoPageError:
        has_wikidata_item_page = False

    if has_no_wikidata_cat and has_wikidata_item_page:
        text = text.replace(NO_LINK_TO_WIKIDATA_CAT,'').strip()
        MESSAGE +=RMV_NO_LINK_TO_WIKIDATA_MESSAGE+SPACE
    elif not has_no_wikidata_cat and not has_wikidata_item_page:
        text+='\n\n'+NO_LINK_TO_WIKIDATA_CAT
        MESSAGE +=ADD_NO_LINK_TO_WIKIDATA_MESSAGE+SPACE
    return text,MESSAGE

##############################################Somethings not right##############################################
###Tags
SOMETHINGS_NOT_RIGHT_TAG = "{{مقالة خاصها تقاد}}"
WIKIBIDIAS = {"ويكيبيديا","ويكبيديا","ويكبديا","ويكيبديا"}

###Save messages
SMTH_NOT_RIGHT_ADD_MSG = "طّاڭ ديال مقالة خاصها تقاد تزاد"
#SMTH_NOT_RIGHT_RMV_MSG = ""

###Functions
def add_smth_not_right_tag(page,text,MESSAGE):
    #print("checking wikidata tag")
    has_smth_not_right_tag = False
    add_smth_not_right_tag = False
    if SOMETHINGS_NOT_RIGHT_TAG in text:
        has_smth_not_right_tag = True
    """
    #not useful
    if ':' in page.title() and page.title().split(':')[0] in WIKIBIDIAS:
        add_smth_not_right_tag = True

    """
    if not has_smth_not_right_tag and add_smth_not_right_tag:
        text = SOMETHINGS_NOT_RIGHT_TAG+'\n'+text
        MESSAGE +=SMTH_NOT_RIGHT_ADD_MSG+SPACE

    return text,MESSAGE
    

##############################################Good start tag##############################################
###Tags


###Save messages


###Functions


##############################################Suggest Good article tag##############################################
###Tags


###Save messages


###Functions


##############################################Suggest Excellent article tag##############################################
###Tags


###Save messages


###Functions





##############################################MAIN PROGRAM##############################################
site = pywikibot.Site()

print("Creating working pool")
pool = site.allpages(namespace=ARTICLE_NAMESPACE)
#pool = [page for page in site.allpages() if validate_page(page)]

pool_size = len(list(deepcopy(site.allpages(namespace=ARTICLE_NAMESPACE))))
print('Pool size: '+str(pool_size))
i = 1
for page in pool:
    print('*********'+str(i)+'/'+str(pool_size))
    pages_in_log = load_pages_in_log()
    #print(pages_in_log[:20])
    
    with open(RECENT_LOG_FILE,'a',encoding='utf-8') as f:
        if str(page.title()) not in pages_in_log:
            
            MESSAGE = ""
            
            if validate_page(page):
                #print("checking page "+str(i))
                
                new_text = page.text

                #Calling "No category tag treatment" subprogram
                new_text,MESSAGE = setCategoryTag(page,new_text,MESSAGE)
               
                #checking back links
                new_text,MESSAGE = setOrphanTag(page,new_text,MESSAGE)
               
                #Set source tag
                new_text,MESSAGE = setSourceTag(page,new_text,MESSAGE)
                
                #Set source header flag
                new_text,MESSAGE = setSourceHeaderTag(page,new_text,MESSAGE)

                #handling Authority Control tag
                new_text,MESSAGE = setAuthorityControlTag(page,new_text,MESSAGE)

                #handling stub tag
                new_text,MESSAGE = setStubTag(page,new_text,MESSAGE)

                #handling no source tag
                new_text,MESSAGE = setNoSourceTag(page,new_text,MESSAGE)

                #handling empty paragraphs
                new_text,MESSAGE = setEmptyParagraphTag(page,new_text,MESSAGE)

                #handling wikidata link
                new_text,MESSAGE = add_no_link_to_wikidata_cat(page,new_text,MESSAGE)

                #handling missing picture tag
                new_text,MESSAGE = add_missing_picture_tag(page,new_text,MESSAGE)

                """
                Deactivated for now
                #handling Wikibidia with SOMETHINGS_NOT_RIGHT_TAG
                new_text,MESSAGE = add_smth_not_right_tag(page,new_text,MESSAGE)
                """
                #handling deadend tag
                try:
                    new_text,MESSAGE = setDeadendTag(page,new_text,MESSAGE,site)
                except Exception:
                    with open('error_log.txt','w',encoding='utf-8') as er:
                        er.write(str(page.title())+'\n'+str(sys.exc_info()))
                        print(sys.exc_info())

                if new_text != page.text:
                    
                    page.text = new_text
                    page.save(MESSAGE)
                    
                    #cha = input("continue to next page?\n")
            elif page.isRedirectPage():
                #handling transfer category for redirect pages
                new_text = page.text
                new_text,MESSAGE = add_redirect_cat(page,new_text,MESSAGE)

                if new_text != page.text:
                    
                    page.text = new_text
                    page.save(MESSAGE)

            f.write(page.title()+'\n')
    i+=1
