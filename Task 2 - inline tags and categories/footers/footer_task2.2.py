from   pgvbotLib            import *
import arywikibotlib        as awbl
import pywikibot
from   copy                 import deepcopy
import re, sys, os
from   pywikibot.exceptions import NoPageError
from   arywikibotlib        import isHuman, hasPropertyXValue
from   datetime             import datetime, timezone
from   sys                  import argv

LAST_RUN_FILE = "last_run.txt"

DATE_FORMAT = "%Y-%m-%d %H:%M"

RECENT_LOG_FILE = "recent_log.txt"

JOB_ID_MSG_PART = "نمرة د دّوزة {}"

LOCAL_LOG = "task2.log"

def print_to_console_and_log(MSG):
    MESSAGE = MSG+'\n'
    with open(LOCAL_LOG,'a',encoding="utf-8") as log:
        log.write(MESSAGE)
    print(MSG)

def get_last_run_datetime():
    if not os.path.exists(LAST_RUN_FILE):
        with open(LAST_RUN_FILE,'w') as f:
            return None

    with open(LAST_RUN_FILE,'r') as f:
        datetime_str = f.read().strip()

    return datetime.strptime(datetime_str,DATE_FORMAT)

def write_run_time():
    with open(LAST_RUN_FILE,'w') as f:
        f.write(pywikibot.Timestamp.now().strftime(DATE_FORMAT))

def get_time_string():
    raw_time = pywikibot.Timestamp.now(tz=timezone.utc)
    #utc_time = datetime.now(tz=timezone.utc)
    raw_time_parts = str(raw_time).split('T')
    date_parts = raw_time_parts[0].split('-')
    return " "+raw_time_parts[1][:-4]+"، "+date_parts[2]+" "+MONTHS[int(date_parts[1])-1]["ary_name"]+" "+date_parts[0]+" (UTC)"

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
        try:
            target_title = temp.text.strip().split('[[')[1].strip()[:-2]
            temp = pywikibot.Page(site,target_title)
        except:
            with open(LOCAL_LOG,'a') as log:
                log.write("Error: "+str(sys.exc_info())+'\n')
    return temp
        

#List of subprograms
##Help functions
##Stub tag
##Source header
##Source tag
##Authority Control tag
##Empty paragraph tag


##############################################Help functions##############################################
###Tags
INFOBOX_TAG_PATTERN = r"{{معلومات[\s\S]*?}}"
DATABOX = "{{Databox}}"

TEMPLATE_NS = "قالب"

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

def get_infobox_template_page(page):
    regexp = re.compile(INFOBOX_TAG_PATTERN)
    m = regexp.search(page.text)
    if m:
        #return m.group(0)
        return TEMPLATE_NS+":"+str(m.group(0)).split("|")[0].replace("{{","").replace("}}","")



##############################################Stub tag treatment##############################################
"""
###Tags
OLD_STUB_TAG = "{{بذرة}}"
NEW_STUB_TAG = "{{زريعة}}"
MOR_STUB_TAG = "{{زريعة شخصيات د لمغريب}}"

###Save messages
CORRECT_STUB_TAG_MESSAGE = "إصلاح طّاڭ د زريعة."
ADD_STUB_TAG_MESSAGE = "زيادة د طّاڭ د زريعة."
REMOVE_STUB_TAG_MESSAGE = "تحياد طّاڭ د زريعة."

###Functions
def setStubTag(page,text,MESSAGE):
    has_stub_tag = False
    if NEW_STUB_TAG in text or MOR_STUB_TAG in text:
        if isHuman(page) and hasPropertyXValue(page,"P27",1028):
            temp = text
            text = text.replace(NEW_STUB_TAG,MOR_STUB_TAG)
            if text != temp:
                MESSAGE += CORRECT_STUB_TAG_MESSAGE+SPACE
        has_stub_tag = True
    else:
        temp = text
        text = text.replace(OLD_STUB_TAG,NEW_STUB_TAG)
        if isHuman(page) and hasPropertyXValue(page,"P27",1028):
            text = text.replace(NEW_STUB_TAG,MOR_STUB_TAG)
        if text != temp:
            has_stub_tag = True
            MESSAGE += CORRECT_STUB_TAG_MESSAGE+SPACE
            #print("changing old stub tag with new one")

    if word_count(text) < 250 and not has_stub_tag:
        if isHuman(page) and hasPropertyXValue(page,"P27",1028):
            text += "\n"+MOR_STUB_TAG
        else:
            text += "\n"+NEW_STUB_TAG
        MESSAGE += ADD_STUB_TAG_MESSAGE+SPACE
    elif word_count(text) > 500 and has_stub_tag:
        text = text.replace(NEW_STUB_TAG,"")
        text = text.replace(MOR_STUB_TAG,"")
        MESSAGE += REMOVE_STUB_TAG_MESSAGE+SPACE

    return text,MESSAGE



"""

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


##############################################MAIN PROGRAM##############################################
site = pywikibot.Site()

print_to_console_and_log('Number of passed arguments: '+str(len(argv)))
local_args = None
if len(argv)>2:
    if len(argv) > 3:
        local_args = argv[3:]

JOB_ID = None
if local_args is not None and len(local_args)>2:
    JOB_ID = local_args[-1]
    print_to_console_and_log('Job ID '+str(JOB_ID))

if local_args is not None and local_args[0] == '-l':
    last_run_time = get_last_run_datetime()
    print_to_console_and_log('Last run time '+str(last_run_time))
    print_to_console_and_log("running for last changed pages")
    #load last changed
    last_changes = site.recentchanges(reverse=True,bot=False,namespaces=[ARTICLE_NAMESPACE],top_only=True,start=last_run_time)
    #create page pool
    #NEXT: check other potential last_change types

    pool = [pywikibot.Page(site, item['title']) for item in last_changes]

else:

    print_to_console_and_log("Creating working pool")
    pool = site.allpages(namespace=ARTICLE_NAMESPACE, filterredir=False)
    #pool = [page for page in site.allpages() if validate_page(page)]

pool_size = len(list(deepcopy(pool)))
print_to_console_and_log('Pool size: '+str(pool_size))
i = 1
pages_in_log = load_pages_in_log()

with open(RECENT_LOG_FILE,'a',encoding='utf-8') as f:
    
    for page in pool:
        print_to_console_and_log('*********'+str(i)+'/'+str(pool_size))
        
        #print(pages_in_log[:20])
        
        
        if str(page.title()) not in pages_in_log:
                
            MESSAGE = ""
                
            if validate_page(page) and awbl.validate_page(page,0,"article",2,"GEN"):
                #print("checking page "+str(i))
                    
                new_text = page.text

                
                #Set source tag
                new_text,MESSAGE = setSourceTag(page,new_text,MESSAGE)
                    
                #Set source header flag
                new_text,MESSAGE = setSourceHeaderTag(page,new_text,MESSAGE)

                #handling Authority Control tag
                new_text,MESSAGE = setAuthorityControlTag(page,new_text,MESSAGE)

                #handling stub tag
                #new_text,MESSAGE = setStubTag(page,new_text,MESSAGE)

                #handling empty paragraphs
                new_text,MESSAGE = setEmptyParagraphTag(page,new_text,MESSAGE)

                #handling wikidata link
                new_text,MESSAGE = add_no_link_to_wikidata_cat(page,new_text,MESSAGE)

                
                if new_text != page.text:
                        
                    page.text = new_text
                    try:
                        page.save(MESSAGE)
                    except:
                        #LOG_PAGE_TITLE = 
                        #log_error(LOG_PAGE_TITLE,log_message,save_log_message,site)
                        continue
                        
                    #cha = input("continue to next page?\n")
            """
            elif page.isRedirectPage():
                #handling transfer category for redirect pages
                new_text = page.text
                new_text,MESSAGE = add_redirect_cat(page,new_text,MESSAGE)

                if new_text != page.text:
                        
                    page.text = new_text
                    try:
                        if JOB_ID is not None:
                            MESSAGE+=" - "+JOB_ID_MSG_PART.format(JOB_ID)
                        page.save(MESSAGE)
                    except:
                        #log_error(LOG_PAGE_TITLE,log_message,save_log_message,site)
                        continue
            """
            f.write(page.title()+'\n')
        i+=1

write_run_time()
