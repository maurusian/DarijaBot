# coding=utf-8
from pgvbotLib import *
#import arywikibotlib as awbl
import pywikibot
from copy import deepcopy
#from sys import argv
import re, sys, os
from pywikibot.exceptions import NoPageError
#from arywikibotlib import isHuman, hasPropertyXValue
from datetime import datetime, timezone
from sys import argv
from fuzzywuzzy import fuzz

LAST_RUN_FILE = "last_run.txt"

DATE_FORMAT = "%Y-%m-%d %H:%M"

RECENT_LOG_FILE = "recent_log.txt"

JOB_ID_MSG_PART = "نمرة د دّوزة {}"

LOCAL_LOG = "task24.log"

TALK_NS = "مداكرة:"

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
INFOBOX_TAG_PATTERN = r"{{معلومات[\s\S]*?}}"
DATABOX = "{{Databox}}"

TEMPLATE_NS = "مداكرة"

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
###Tags
OLD_STUB_TAG = "{{بذرة}}"
NEW_STUB_TAG = "{{زريعة}}"
MOR_STUB_TAG = "{{زريعة شخصيات د لمغريب}}"


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



##############################################Source tag treatment##############################################
###Tags
OLD_SOURCE_TAG1 = "{{مراجع}}"
OLD_SOURCE_TAG2 = "<\s*references\s*/>"
NEW_SOURCE_TAG = "{{عيون}}"


##############################################No category tag treatment##############################################
###Tags
NO_CATEGORY_TAG = "{{مقالة ما مصنفاش}}"


##############################################No backlinks tag treatment##############################################
###Tags
ORPHANED_PAGE_TAG = "{{مقالة مقطوعة من شجرة}}"


##############################################Authority Control tag##############################################
###Tags
OLD_AUTHORITY_CONTROL_TAG = "{{ضبط استنادي}}"
NEW_AUTHORITY_CONTROL_TAG = "{{ضبط مخازني}}"


##############################################Deadend tag##############################################
###Tags
CUL_DE_SAC_TAG = "{{مقالة زنقة ماكاتخرجش}}"
OUTLINK_PATTERN = r'\[\[.+?\]\]'

##############################################No sources tag##############################################
###Tags
NO_SOURCES_ON_PAGE_TAG = "{{مقالة ناقصينها عيون لكلام}}"
SOURCE_EXIST_PATTERN = r"ref.+?/ref"
REF_TAG = "<ref"


##############################################Empty paragraph tag##############################################
###Tags
EMPTY_PARAGRAPH_TAG = "{{فقرة مازالا خاوية ولا ناقصة}}"
EMPTY_PARAGRAPH_PATTERN1 = r"==.+==[\n\s]+(?===\s|$)"
EMPTY_PARAGRAPH_PATTERN2 = r"===.+===[\n\s]+(?====\s|$)"


##############################################Transfer category##############################################
###Tags


###Save messages
REDIR_CAT_ADD_MESSAGE = "تصنيف د تّحويلات تزاد"


##############################################Missing pictures tag##########################################
###Tags and search string segmemts
PICTURE_MISSING_TAG         = "{{مقالة ناقصينها تصاور|{parameter}}}"
PICTURE_MISSING_TAG_PATTERN = r"{{مقالة ناقصينها تصاور\|.*?}}"
PICTURE_MISSING_TAG_PART    = "{{مقالة ناقصينها تصاور"
PIC_REGEX                   = r"{{معلومات.+\|صورة=.+\..+}}"
PIC_REGEX2                  = r"{{معلومات.+\|الصورة=.+\..+}}"
PIC_REGEX3                  = r"{{معلومات.+\|تصويرة=.+\..+}}"
PICTURE_PROPERTIES = ["P18","P154","P41","P94","P158","P2176","P8592","P948"]
PIC_EXCEPTION_CAT_LIST = ["تصنيف:نهارات د لعام","تصنيف:عوام د تقويم لميلادي"]
#INFOBOX_TAG_PART = "{{معلومات"

GALLERY_PART_DICT = {'en':'<gallery'
                    ,'fr':'{{Gallery'
                    ,'ar':'<gallery'}
FILE_PART_DICT = {'en':'[[File:'
                 ,'fr':'[[Fichier:'
                 ,'ar':'[[ملف:'}
CITY_INFOBOX_TAG_PART = "{{معلومات مدينة"


##############################################No link to Wikidata cat########################################
###Category
NO_LINK_TO_WIKIDATA_CAT = "[[تصنيف:أرتيكلات مامربوطينش معا ويكيداطا]]"

##############################################Needs more work tag##############################################
###Tags
NEED_MORE_WORK_TAG = "{{مقالة خاصها تقاد}}"
need_more_work_tag_part = "{{مقالة خاصها تقاد"
TAG_PROBLEM_NAME_DICT = {EMPTY_PARAGRAPH_TAG:"فقرة خاوية ؤلا ناقصة"
                        ,NO_SOURCES_ON_PAGE_TAG:"ناقصين عيون لكلام"
                        ,CUL_DE_SAC_TAG:"زنقة ماكاتخرّجش"
                        ,ORPHANED_PAGE_TAG:"مقطوعة من شجرة"
                        ,NO_CATEGORY_TAG:"ناقصين تصنيفات"
                        }
#WIKIBIDIAS = {"ويكيبيديا","ويكبيديا","ويكبديا","ويكيبديا"}

##############################################Article of the day suggestion##############################################
###Params
SUG_TEXT_TITLE = "قتيراح د لمقال ل صّفحة لّولة"
SUGGESTION_TEXT = u"""== قتيراح د لمقال ل صّفحة لّولة ==
{{تعليق بوتي}} سلام. طاڭ ل لكتاتبيا لمعنيين {كتاتبيا}. كانرشّح هاد لمقال باش يتزاد ل فقرة [[قالب:مقالة الصفحة اللولا لمزيانة|لأرتيكل لمزيانة ديال ليوم]]. ناقشو عافاكوم واش لمقال كيستاحق، ؤلا واش خاصو مازال شوية د لخدمة باش يولي كيستوفي شّروط. تقدرو تقراو لحكام ديال لأرتيكل لمزيانة ديال ليوم [[ويكيپيديا:لأرتيكل لمزيانة ديال ليوم|هنا]].--~~~~"""

SUGGESTION_MAX_LIMIT = 3

TAG_PROBLEM_DICT = {EMPTY_PARAGRAPH_TAG:"فقرة مازالا خاوية ولا ناقصة"
                   ,NO_SOURCES_ON_PAGE_TAG:"مقالة ناقصينها عيون لكلام"
                   ,CUL_DE_SAC_TAG:"مقالة زنقة ماكاتخرجش"
                   ,ORPHANED_PAGE_TAG:"مقالة مقطوعة من شجرة"
                   ,NO_CATEGORY_TAG:"مقالة ما مصنفاش"
                   ,NEED_MORE_WORK_TAG:"مقالة خاصها تقاد"
                   ,'NOTABILITY_TAG':"ملحوضية"
                   ,'NOT_CLEAR_IN_TEXT_TAG':"ماواضحش"
                   ,'IMAGE_MISSING_TAG':"مقالة ناقصينها تصاور"
                   ,'MORE_SOURCES_NEEDED':"عيون ماكافيينش"
                   ,'INLINE_SOURCE_NEEDED':"خاص شي مصدر لهادشي"
                   ,'DELETE_TAG':"حدف"
                   ,'FUSION_TAG':"دمج"
                   ,'SENSITIVE_TOPIC':"موضوع حساس"
                   ,'NO_OR_TAG':"بلا فيخرات"
                   }

CATEGORY_BAN_LIST = []

PAGE_BAN_LIST = []

###Save messages
ADD_SUGGESTION_SAVE_MESSAGE = "قتيراح د لمقال ل فقرة لأرتيكل لمزيانة د ليوم"
TALK_RESPONSE_TAG_PART = "{{جاوب|"
FIND_CAT = "تصنيف:المغريب"

###Functions
def get_admins(site):
    return [user['name'] for user in site.allusers(group='sysop')]

def get_nonbot_contributors(page):
    contributors = dict(page.contributors())
    bots = []
    for contributor in contributors.keys():
        user = pywikibot.User(site,contributor)
        if 'bot' in user.groups():
            bots.append(contributor)

    for user in bots:
        del contributors[user]
    
    return contributors

def user_call_string(site,page):
    users = get_admins(site) + list(get_nonbot_contributors(page).keys())

    users = list(set(users))

    #r = len(users) // 6
    calls = []
    for i in range(0,len(users),6):
        calls.append(TALK_RESPONSE_TAG_PART+'|'.join(users[i:i+6])+'}}')

    return ' '.join(calls)

def has_no_problems(page):
    """
    """
    for tag_name in TAG_PROBLEM_DICT.values():
        if '{{'+tag_name in page.text:
            return False

    return True

def get_raw_paragraphs(text):
    """
    Removes all content that's not a paragraph
    """
    REF_PATTERN = r"<ref>.\n+?</ref>"
    TMP_PATTERN = r"\{\{.\n+?\}\}"
    TBL_PATTERN = r"\{\|.\n+?\|\}"

    
    

def has_non_trivial_sections(page):
    TITLE_PATTERN = r"==.+=="
    titles = re.findall(TITLE_PATTERN,page.text)
    #check page has sections
    if titles is None or len(titles) == 0:
        return False
    #check page has sections other than "references"
    
    if len(titles)<2:
        return False

    #check sections actually contain text paragraphs, not lists or tables
    

    return True

def has_good_size(page):
    tag_pattern = "\{\{.+\}\}" #needs improvement
    ref_pattern = "<ref.*>.+</ref>"

    if len(page.text) < 5000:
        return False
    
    tags = re.findall(tag_pattern,page.text)
    
    text = page.text
    for tag in tags:
        text = text.replace(tag,"")

    refs = re.findall(ref_pattern,page.text)
    for ref in refs:
        text = text.replace(ref,"")

    text_parts = text.split("==")

    intro_words = text_parts[0].split()

    if len(intro_words) < 50:
        return False

    for section in text_parts[1:]:
        if len(section.split()) > len(intro_words):
            return True

    return False

def not_in_skip_lists(page):
    USED_LIST_FILE = "already_displayed.txt"
    IGNORE_LIST_FILE = "ignore_list.txt"
    IGNORE_CATS = "ignore_cat_list.txt"

    with open(USED_LIST_FILE, 'r') as used:
        for i,line in enumerate(used):
            if page.title() == line.strip():
                return False

    with open(IGNORE_LIST_FILE, 'r') as ign:
        for i,line in enumerate(ign):
            if page.title() == line.strip():
                return False

    with open(IGNORE_CAT_LIST_FILE, 'r') as cats:
        for i,line in enumerate(cats):
            if '[['+line.strip()+']]' in page.text:
                return False

    return True

def isUnderCat(page, target_cat, cat_list):
    isUnderCat.count = 0
    def _isUnderCat(page, target_cat, cat_list, c):
        isUnderCat.count+=1
        if isUnderCat.count > 15:
            return False
        cats = list(page.categories())
        if len(cats) == 0:
            print_to_console_and_log("no categories found for page :"+page.title())
            return False
        if target_cat in cats:
            return True

        temp_cat_list = deepcopy(cat_list) #assignment alone creates a shallow copy

        cat_list += cats

        cat_list = list(set(cat_list))

        print_to_console_and_log('length temp_cat_list '+str(len(temp_cat_list)))
        print_to_console_and_log('length cat_list '+str(len(cat_list)))

        if len(temp_cat_list) == len(cat_list):
            print_to_console_and_log("no new categories discovered for page :"+page.title())
            return False
        
        cats = sorted(cats,key = lambda x:fuzz.partial_ratio(FIND_CAT[6:],x.title()[6:]),reverse=True)
        for category in cats:
            if not category.isHiddenCategory() and category.title() not in IGNORE_LIST:
                print_to_console_and_log("going through categories of page "+page.title())
                if _isUnderCat(category, target_cat, cat_list,isUnderCat.count):
                    return True
                
        print_to_console_and_log("Page "+page.title()+" is not under category "+target_cat.title())
        return False
    return _isUnderCat(page, target_cat, cat_list, isUnderCat.count)


def has_not_been_suggested(site,page):
    """
    This is a terrible implementation of this functionality
    """
    talk_page = pywikibot.Page(site,TALK_NS+page.title())
    if SUG_TEXT_TITLE in talk_page.text:
        return False
    
    return True


def is_suggestable(page):
    if has_no_problems(page) and has_non_trivial_sections(page) and has_good_size(page):
        return True
    
    return False

    

def suggest_page(site,page):
    
    talk_page = pywikibot.Page(site,TALK_NS+page.title())

    sugg_text = SUGGESTION_TEXT.replace("{كتاتبيا}",user_call_string(site,page))

    talk_page.text+=sugg_text

    print_to_console_and_log(user_call_string(site,page))

    print_to_console_and_log(sugg_text)

    talk_page.save(ADD_SUGGESTION_SAVE_MESSAGE)
    

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
    last_changes = site.recentchanges(reverse=True,bot=False,namespaces=[ARTICLE_NAMESPACE],top_only=True,start=last_run_time, redirect=False)
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

target_cat = pywikibot.Category(site,FIND_CAT)

mar_suggestion_counter = 0
non_suggestion_counter = 0

moroccan_pages = []
non_moroccan_pages = []

with open(RECENT_LOG_FILE,'a',encoding='utf-8') as f:
    with open("suggestion_list.txt","w",encoding='utf-8') as sug:
        for page in pool:
            print_to_console_and_log('*********'+str(i)+'/'+str(pool_size))
            
            #print(pages_in_log[:20])
            
            
            if str(page.title()) not in pages_in_log:
                
                MESSAGE = ""

                
                if validate_page(page) and is_suggestable(page) and has_not_been_suggested(site,page): # and awbl.validate_page(page,0,"article",2,"GEN"):
                    #print(user_call_string(site,page))
                    
                    if isUnderCat(page, target_cat, []):
                        moroccan_pages.append(page)
                        mar_suggestion_counter+=1
                        if mar_suggestion_counter >= 3:
                            break
                    elif non_suggestion_counter == 0:
                        non_moroccan_pages.append(page)
                        non_suggestion_counter+=1

                    sug.write(page.title()+"\n")
                    

                f.write(page.title()+'\n')
            i+=1


for page in moroccan_pages+non_moroccan_pages:
    suggest_page(site,page)


    
