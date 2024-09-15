#from   pgvbotLib            import *
import pywikibot
from   pywikibot            import textlib
from   pywikibot.exceptions import NoPageError

import re, sys, os, random, json, time
from   copy                 import deepcopy
from   datetime             import datetime, timezone
from   sys                  import argv

print("local path:",os.getcwd())
print("script path:",os.path.dirname(__file__))
print("script name:",os.path.basename(__file__))

local_folder = os.path.dirname(__file__) #os.getcwd()

MAIN_PARAM_PAGE = "ميدياويكي:عطاشة2.1.json"

LAST_RUN_FILE = local_folder+"/last_run.txt"

DATE_FORMAT = "%Y-%m-%d %H:%M"

RECENT_LOG_FILE = local_folder+"/recent_log.txt"

JOB_ID_MSG_PART = "نمرة د دّوزة {}"

LOCAL_LOG = local_folder+"/task2.log"



################## Copied functions for Toolforge ####################
ARTICLE_NAMESPACE = 0
IGNORE_LIST = ['الصفحة اللولا'] #list of pages to be completely ignored by the bot, for all tasks
PAGE_TYPE_IGNORE_LIST = ['موضيل','تصنيف','ويكيپيديا','إدارة','قيسارية','لمداكرة د قيسارية','خدايمي','لمداكرة د لخدايمي','لمداكرة د ويكيپيديا','مداكرة','لمداكرة د تصنيف','لمداكرة د لموضيل'] #list of page types to be completely ignored by the bot, for all tasks
DISAMB_TAG = u"{{توضيح}}" #tag for disambiguation page
SPACE = " "

def validate_page(page):
    """
    Verifies if a page is valid for treatment
    or not. For now, only content pages are
    valid for treatment
    """

    if page.title() in IGNORE_LIST or page.isRedirectPage() or DISAMB_TAG in page.text:
        return False


    page_double_dot_parts = page.title().split(':')
    
    if len(page_double_dot_parts) == 1: #for now only content pages
        return True
    elif len(page_double_dot_parts) > 1 and page_double_dot_parts[0] not in PAGE_TYPE_IGNORE_LIST:
        return True
    return False


################## Get parameters ####################

def get_main_task_params():
    """
    Load parameters for DarijaBot Task 2.1.
    """
    param_page = pywikibot.Page(site,MAIN_PARAM_PAGE)

    pjason = json.loads(param_page.text)

    return pjason

site = pywikibot.Site()

pjason = get_main_task_params()

RECENT_LOG_RETENTION_DAYS = pjason["RECENT_LOG_RETENTION_DAYS"]

################ End get parameters ##################

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


def delete_recent_log_if_old():
    # Get the current time
    current_time = time.time()

    if os.path.exists(RECENT_LOG_FILE):
        # Get the file's last modification time
        file_mod_time = os.path.getmtime(RECENT_LOG_FILE)
        
        # Calculate the file age in days
        file_age_days = (current_time - file_mod_time) / (24 * 3600)
        
        # Check if the file is older than the given number of days
        if file_age_days > RECENT_LOG_RETENTION_DAYS:
            os.remove(RECENT_LOG_FILE)
            print(f"{RECENT_LOG_FILE} deleted.")
        else:
            print(f"{RECENT_LOG_FILE} is not old enough to delete.")

#List of subprograms
##Help functions
##No category tag
##No backlinks tag
##Deadend tag
##No sources tag
##Empty paragraph tag
##Good start tag
##Good article tag
##Excellent article tag


##############################################Help functions##############################################
###Tags
INFOBOX_TAG_PATTERN = r"{{معلومات\s+\w+(?:\s+\w+)*(?:\s*[\n|}]?\s*)"
INFOBOX_TAG_PATTERN2 = r"{{صندوق\s+معلومات\s+\w+(?:\s+\w+)*(?:\s*[\n|}]?\s*)"
#r"{{صندوق\s+معلومات\s*\w+(?:\s+\w+)*(?:\s*[\n|}]?\s*)"
#r"{{صندوق\s+معلومات\s*\w+(?:\s+\w+)*(?:\s*[\n|}]?\s*)"
DATABOX = "{{Databox}}"

TEMPLATE_NS = "موضيل"

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

def get_commons_category(text):
    COMMONS_CAT_TAG_PART = "{{Commons category|"

    if COMMONS_CAT_TAG_PART in text:
        text_parts = text.split(COMMONS_CAT_TAG_PART)
        commons_cat = text_parts[-1].split('}}')[0]
        return commons_cat
    else:
        return None

def get_infobox_template_page(text):
    regexp = re.compile(INFOBOX_TAG_PATTERN)
    m = regexp.search(text)
    if m:
        #return m.group(0)
        return TEMPLATE_NS+":"+str(m.group(0)).split("|")[0].replace("{","").replace("}","")
    else:
        regexp = re.compile(INFOBOX_TAG_PATTERN2)
        m = regexp.search(text)
        if m:
            #return m.group(0)
            return TEMPLATE_NS+":"+str(m.group(0)).split("|")[0].replace("{","").replace("}","")

def random_n_digit_integer(n):
    if n <= 0:
        raise ValueError("n must be a positive integer")

    lower_limit = 10 ** (n - 1)
    upper_limit = (10 ** n) - 1

    return random.randint(lower_limit, upper_limit)

def year_based_integer():
    current_year = datetime.now().year

    if current_year < 2023:
        raise ValueError("Year must be greater than or equal to 2023")

    return 5 + (current_year - 2023)


def get_final_redirect_target(page):
    """
    Given a Pywikibot page object, returns the final target of the page's redirect chain,
    or the page itself if it is not a redirect page.
    """
    while page.isRedirectPage():
        page = page.getRedirectTarget()
    return page


##############################################No category tag treatment##############################################
###Tags
NO_CATEGORY_TAG = pjason["JOBS"]["NoCategoryTag"]["TAGCODE"] #"{{مقالة ما مصنفاش}}"
CATEGORY_ISSUE_RGX = "{{مقالة خاصها تقاد\|.+مامصنفاش.+}}"

###Save messages
ADD_NO_CAT_TAG_MESSAGE = pjason["JOBS"]["NoCategoryTag"]["ADD_SAVE_MESSAGE"] #'طاڭ ديال "مقالة مامصنفاش" تزاد.'
REMOVE_NO_CAT_TAG_MESSAGE = pjason["JOBS"]["NoCategoryTag"]["RMV_SAVE_MESSAGE"] #'طاڭ ديال "مقالة مامصنفاش" تحيّد.'

###Functions

def is_category_hidden(category):
    #site = pywikibot.Site()
    #category = pywikibot.Category(site, category_name)

    #print(category.categoryinfo)
    
    if 'hidden' in category.categoryinfo.keys():
        return True
    
    return False

def hasExplicitCategory(page):
    len_cat = len(list(page.categories()))
    if len_cat==0:
        #print("page has "+str(len_cat)+" categories")
        return False
    i = 0
    for category in page.categories():
        i+=1
        if str(category.title()).strip() in page.text and not is_category_hidden(category): # if there's a cat that's explicit and not hidden
            #print("found "+str(i)+" categories so far")
            return True
    #print("found "+str(i)+" categories (final)")
    return False

def setNoCategoryTag(page,text,MESSAGE):
    #print("checking category tag")
    regexp = re.compile(CATEGORY_ISSUE_RGX,flags=re.DOTALL)
    if not hasExplicitCategory(page):
        if NO_CATEGORY_TAG not in text and not regexp.search(text):
            #print("Adding NO_CATEGORY_TAG")
            text = NO_CATEGORY_TAG+'\n'+text
            MESSAGE+=ADD_NO_CAT_TAG_MESSAGE+SPACE
    else:
        if NO_CATEGORY_TAG in text or regexp.search(text):
            #print("Removing NO_CATEGORY_TAG")
            text = text.replace(NO_CATEGORY_TAG,'')
            MESSAGE+=REMOVE_NO_CAT_TAG_MESSAGE+SPACE

    return text,MESSAGE


##############################################No backlinks tag treatment##############################################
###Tags
ORPHANED_PAGE_TAG = pjason["JOBS"]["NoBacklinkTag"]["TAGCODE"] #"{{مقالة مقطوعة من شجرة}}"
ORPHANED_ISSUE_RGX = "{{مقالة خاصها تقاد\|.+مقطوعة.+}}"

###Save messages
ADD_ORPHAN_TAG_MESSAGE = pjason["JOBS"]["NoBacklinkTag"]["ADD_SAVE_MESSAGE"] #'طاڭ ديال "مقطوعة من شجرة" تزاد.'
REMOVE_ORPHAN_TAG_MESSAGE = pjason["JOBS"]["NoBacklinkTag"]["RMV_SAVE_MESSAGE"] #'طاڭ ديال "مقطوعة من شجرة" تحيّد.'

###Functions
def setNoBacklinkTag(page,text,MESSAGE):
    should_add_orphan_tag = True
    links =  page.backlinks()
    regexp = re.compile(ORPHANED_ISSUE_RGX,flags=re.DOTALL)
    for link in links:
        if validate_page(link):
            should_add_orphan_tag = False
            break
    if should_add_orphan_tag:
        if ORPHANED_PAGE_TAG not in text and not regexp.search(text):
            text = ORPHANED_PAGE_TAG+'\n'+text
            MESSAGE+=ADD_ORPHAN_TAG_MESSAGE+SPACE
    else:
        if ORPHANED_PAGE_TAG in text or regexp.search(text):
            text = text.replace(ORPHANED_PAGE_TAG,'')
            MESSAGE+=REMOVE_ORPHAN_TAG_MESSAGE+SPACE
    return text,MESSAGE


##############################################Deadend tag##############################################
###Tags
CUL_DE_SAC_TAG = pjason["JOBS"]["setNoOutLinkTag"]["TAGCODE"] #"{{مقالة زنقة ماكاتخرجش}}"
OUTLINK_PATTERN = r'\[\[.+?\]\]'
CUL_DE_SAC_ISSUE_RGX = "{{مقالة خاصها تقاد\|.+ماكاتخرجش.+}}"

###Save messages
ADD_DEADEND_TAG_MESSAGE = pjason["JOBS"]["setNoOutLinkTag"]["ADD_SAVE_MESSAGE"] #"طّاڭ ديال زنقة ماكاتخرجش تزاد"
REMOVE_DEADEND_TAG_MESSAGE = pjason["JOBS"]["setNoOutLinkTag"]["RMV_SAVE_MESSAGE"] #"طّاڭ ديال زنقة ماكاتخرجش تحيد"

###Functions
def setNoOutLinkTag(page,text,MESSAGE):
    has_deadend_tag = False
    should_not_add_tag = False
    regexp = re.compile(CUL_DE_SAC_ISSUE_RGX,flags=re.DOTALL)
    if CUL_DE_SAC_TAG in text:
        has_deadend_tag = True
    else:
        links = re.findall(OUTLINK_PATTERN,text)
        for link in links:
            link_page = pywikibot.Page(site,link[2:-2].split('|')[0])
            link_page = get_final_target(link_page) #make sure the linked page is not a redirect page, but its final target
            if link_page.text != '' and validate_page(link_page):
                should_not_add_tag = True
                break

    if (has_deadend_tag or regexp.search(text)) and should_not_add_tag:
        text = text.replace(CUL_DE_SAC_TAG,'').strip()
        MESSAGE += REMOVE_DEADEND_TAG_MESSAGE+SPACE
    elif not has_deadend_tag and not regexp.search(text) and not should_not_add_tag:
        text = CUL_DE_SAC_TAG + "\n" + text
        MESSAGE += ADD_DEADEND_TAG_MESSAGE+SPACE
    return text,MESSAGE

##############################################Bot Article tag##############################################
###Tags
BOT_ARTICLE_TAG = pjason["JOBS"]["BotArticleTag"]["TAGCODE"]

###Save messages
ADD_BOT_ARTICLE_TAG_MESSAGE = pjason["JOBS"]["BotArticleTag"]["ADD_SAVE_MESSAGE"]
REMOVE_BOT_ARTICLE_TAG_MESSAGE = pjason["JOBS"]["BotArticleTag"]["RMV_SAVE_MESSAGE"]

BOT_LIST = ['AmgharBot', 'DarijaBot', 'InternetArchiveBot','MediaWiki default'
            ,'MediaWiki message delivery','MenoBot','PGVBot','Sa7bot','TohaomgBot'
            ,'BotFunast']

###Functions    

# Helper function to check if a user is a bot based on the "bot" flag or the bot_list
def is_bot(user):
    user_obj = pywikibot.User(site, user)
    print(user)
    return 'bot' in user_obj.groups() or user in BOT_LIST

# Helper function to check if an article was created by a bot
def is_created_by_bot(page):
    first_revision = list(page.revisions())[-1]
    return is_bot(first_revision.user)

# Helper function to calculate the sum of bytes added by human users (non-bot)
def is_human_edits_sum_exceed_1000_bytes(page):
    total_bytes = 0
    for revision in page.revisions():
        if not is_bot(revision.user):
            total_bytes += revision.size
        if total_bytes > 1000:
            return True  # Early exit if it exceeds 1000 bytes
    return False

# Helper function to calculate the sum of pure text added by human users
def is_human_pure_text_sum_exceed_1000_bytes(page):
    total_text_bytes = 0
    for revision in page.revisions():
        if not is_bot(revision.user):
            prev_revision = page.getOldVersion(revision.parentid) if revision.parentid else ''
            curr_revision = page.getOldVersion(revision.revid)
            prev_text = pywikibot.textlib.removeDisabledParts(prev_revision)
            curr_text = pywikibot.textlib.removeDisabledParts(curr_revision)
            diff_bytes = len(curr_text) - len(prev_text)
            total_text_bytes += max(0, diff_bytes)  # Only consider positive increases
        if total_text_bytes > 1000:
            return True  # Early exit if it exceeds 1000 bytes
    return False

# Main function to check if an article is a bot article
def isBotArticle(page):
    # Step 1: Check if the article was created by a bot
    if not is_created_by_bot(page):
        return False

    # Step 2: Check if no human has edited the article
    human_edits_count = sum(1 for rev in page.revisions() if not is_bot(rev.user))
    if human_edits_count > 0:
        # Step 3: Check if the sum of human edits (in bytes) exceeds 1000 bytes
        if is_human_edits_sum_exceed_1000_bytes(page):
            # Step 4: Check if the sum of pure text added by humans exceeds 1000 bytes
            if is_human_pure_text_sum_exceed_1000_bytes(page):
                return False

        # If none of the above conditions disqualify it, it's a bot article
    return True

def setBotArticleTag(page,text,MESSAGE):

    if BOT_ARTICLE_TAG in text and not isBotArticle(page):
        text = text.replace(BOT_ARTICLE_TAG,"").strip()
        MESSAGE += REMOVE_BOT_ARTICLE_TAG_MESSAGE+SPACE
    elif not BOT_ARTICLE_TAG in text and isBotArticle(page):
        text = BOT_ARTICLE_TAG+'\n'+text
        MESSAGE += ADD_BOT_ARTICLE_TAG_MESSAGE+SPACE
    
    return text,MESSAGE

##############################################No sources tag##############################################
###Tags
json_source_proc = pjason["JOBS"]["NoSourceTag"]["TAGCODE"]
func = pjason["JOBS"]["NoSourceTag"]["SETFUNC"] #json_source_proc["SETFUNC"]
NO_SOURCES_ON_PAGE_TAG = pjason["JOBS"]["NoSourceTag"]["TAGCODE"] #json_source_proc["TAGCODE"]
SOURCE_TAG_EXCEPTION_CAT = pjason["JOBS"]["NoSourceTag"]["TAG_EXCEPTION_CAT"] #json_source_proc["TAG_EXCEPTION_CAT"]

###Save messages
ADD_NO_SOURCE_TAG_MESSAGE = pjason["JOBS"]["NoSourceTag"]["ADD_SAVE_MESSAGE"] #json_source_proc["ADD_SAVE_MESSAGE"]
REMOVE_NO_SOURCE_TAG_MESSAGE = pjason["JOBS"]["NoSourceTag"]["RMV_SAVE_MESSAGE"] #json_source_proc["RMV_SAVE_MESSAGE"]

###Regex and regex-like
#SOURCE_EXIST_PATTERN = r"ref.+?/ref" #probably not needed
#REF_TAG = "<ref" #probably not needed
NO_SOURCES_ISSUE_RGX = "{{"+pjason["JOBS"]["NoSourceTag"]["GENERIC_FIX_ART_TAG_NAME"]+"\|.+"+pjason["JOBS"]["NoSourceTag"]["RELATED_ARY_NAME_STR"]+".+}}"
SOURCE_PATTERN = r"<ref[^>]*>"
SRC_SFN_PATTERN = r"\{\{[Ss]fn\|([^}|]+)(\|[^}|]+)*\}\}" #matches {{sfn}} tag with parameters


######Functions
def has_sources(text):
    source_patterns = [SOURCE_PATTERN, SRC_SFN_PATTERN] #, r"{{\s*cite", r"{{\s*cite"]
    for pattern in source_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def find_template_sources(text):
    templates = textlib.extract_templates_and_params(text)
    
    for template_name, params in templates:
        template_page = pywikibot.Page(site, f"Template:{template_name}")
        
        try:
            template_text = template_page.get()
        except pywikibot.exceptions.NoPageError:
            continue
        except pywikibot.exceptions.IsRedirectPageError:
            template_text =  template_page.getRedirectTarget().get()
        
        if has_sources(template_text):
            return True

    return False

def setNoSourceTag(page,text,MESSAGE):
    #print(setNoSourceTag)
    has_no_source_tag = False
    regexp = re.compile(NO_SOURCES_ISSUE_RGX,flags=re.DOTALL)
    if NO_SOURCES_ON_PAGE_TAG in text or regexp.search(text):
        has_no_source_tag = True
    
    cats = page.categories()
    is_source_exp_page = False
    for cat in cats:
        if cat.title() in SOURCE_TAG_EXCEPTION_CAT:
            is_source_exp_page = True
            break
    
    #sources = re.findall(SOURCE_EXIST_PATTERN,page.text) #probably not needed

    if (not has_sources(text) and not find_template_sources(text) and not is_source_exp_page) and not has_no_source_tag:
        text = NO_SOURCES_ON_PAGE_TAG + '\n' + text
        MESSAGE += ADD_NO_SOURCE_TAG_MESSAGE+SPACE
    elif (has_sources(text) or find_template_sources(text) or is_source_exp_page) and has_no_source_tag:
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
    if REDIRECT_PAGE_CAT_CODE not in text:
        text+='\n\n'+REDIRECT_PAGE_CAT_CODE
        MESSAGE +=REDIR_CAT_ADD_MESSAGE+SPACE
    return text,MESSAGE

##############################################Missing pictures tag##########################################
###Tags and search string segmemts
picture_json_source_proc = pjason["JOBS"]["NoPicturetag"]["TAGCODE"]
PICTURE_MISSING_TAG         = "{{مقالة ناقصينها تصاور|{parameter}}}"
PICTURE_MISSING_TAG_PATTERN = r"{{مقالة ناقصينها تصاور\|.*?}}"
PICTURE_MISSING_TAG_PART    = "{{مقالة ناقصينها تصاور"
PIC_REGEX                   = r"{{معلومات.+\|صورة=.+\..+}}"
PIC_REGEX2                  = r"{{معلومات.+\|الصورة=.+\..+}}"
PIC_REGEX3                  = r"{{معلومات.+\|تصويرة=.+\..+}}"
PICTURE_PROPERTIES = ["P15","P18","P154","P41","P94","P158","P2176","P8592","P948","P8224","P1846"]
PIC_EXCEPTION_CAT_LIST = pjason["JOBS"]["NoPicturetag"]["TAG_EXCEPTION_CAT"] #picture_json_source_proc["TAG_EXCEPTION_CAT"]
#INFOBOX_TAG_PART = "{{معلومات"

GALLERY_PART_DICT = {'en':'<gallery'
                    ,'fr':'{{Gallery'
                    ,'ar':'<gallery'}
FILE_PART_DICT = {'en':'[[File:'
                 ,'fr':'[[Fichier:'
                 ,'ar':'[[ملف:'
                 ,'ary':'[[فيشي:'}
CITY_INFOBOX_TAG_PART = "{{معلومات مدينة"

###Save messages
ADD_PICTURE_MISSING_TAG = pjason["JOBS"]["NoPicturetag"]["ADD_SAVE_MESSAGE"] #picture_json_source_proc["ADD_SAVE_MESSAGE"]
RMV_PICTURE_MISSING_TAG = pjason["JOBS"]["NoPicturetag"]["RMV_SAVE_MESSAGE"] #picture_json_source_proc["RMV_SAVE_MESSAGE"]

###Functions

def has_pictures_or_videos(page):
    return bool(page.imagelinks())

def remove_comments(text):
    """Remove commented-out sections from wiki text."""
    return re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)

def has_pictures(text):
    #text = remove_comments(page.text)
    if any(ext in text.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg','.webp']):
        return True
    if '<gallery>' in text.lower():
        return True
    
    return False

def is_in_exception_list(page,text):
    #rudimentary method for now
    for cat in PIC_EXCEPTION_CAT_LIST:
        if cat in text:
            return True

    return False


def get_image_properties_from_wikidata(item):
    #print("getting image properties")
    image_properties = []

    item_dict = item.get()

    if "claims" in item_dict.keys():
        item_claims = item_dict["claims"]
        #print(item_claims)
        for image_property in PICTURE_PROPERTIES:
            if image_property in item_claims.keys():
                #print(image_property)
                image_properties.append(image_property)

    return image_properties

def is_image_property_used_in_infobox(text, image_properties):
    #print("is_image_property_used_in_infobox")
    infobox_template_page = get_infobox_template_page(text)

    #print(infobox_template_page)
    
    if infobox_template_page:
        infobox_template = get_final_redirect_target(pywikibot.Page(site, infobox_template_page))

        #print(infobox_template)

        for image_property in image_properties:
            if image_property in infobox_template.text:
                #print(image_property)
                return True

    return False

def setNoPicturetag(page,text,MESSAGE):
    #print("checking picture tag")
    has_picture = False
    has_picture_missing_tag = False
    add_picture_tag = False
    picture = ""
    commons_cat = get_commons_category(text)
    #regexp = re.compile(PIC_REGEX,flags=re.DOTALL)
    #regexp2 = re.compile(PIC_REGEX2,flags=re.DOTALL)
    #regexp3 = re.compile(PIC_REGEX3,flags=re.DOTALL)

    
    has_picture = has_pictures(text)
    
    if PICTURE_MISSING_TAG_PART in text:
        #print("Has picture missing tag")
        has_picture_missing_tag = True


    if not has_picture:
        
        #print("treating article that has no picture "+str(page.title()))
        try:
            item = pywikibot.ItemPage.fromPage(page)
            image_properties = get_image_properties_from_wikidata(item)

            #print((len(image_properties)>0))
            #print((is_image_property_used_in_infobox(page, image_properties)))
            if len(image_properties)>0 and is_image_property_used_in_infobox(text, image_properties):
                #print("has a picture in infobox")
                has_picture = True
                #add_picture_tag = False
            else:
                if CITY_INFOBOX_TAG_PART in text:
                    add_picture_tag = True
                
                for lang in ['en', 'ar', 'fr']:
                    if lang + 'wiki' in item.sitelinks.keys():
                        site_lang = pywikibot.Site(lang, 'wikipedia')
                        title_lang = str(item.sitelinks[lang + 'wiki'])[2:-2]
                        page_lang = pywikibot.Page(site_lang, title_lang)

                        if FILE_PART_DICT[lang] in page_lang.text or GALLERY_PART_DICT[lang] in page_lang.text:
                            add_picture_tag = True
                            break


        except NoPageError:
            add_picture_tag = False

        #check commons catagory tag
        commons_cat = get_commons_category(text)
        if commons_cat is not None:
            add_picture_tag = True
            picture = "Category:"+commons_cat.replace(' ','_')
    
    if is_in_exception_list(page,text):
        add_picture_tag = False
    
    if has_picture and has_picture_missing_tag:
        #print("removing tag")
        text = re.sub(PICTURE_MISSING_TAG_PATTERN,'',text).strip()
        MESSAGE +=RMV_PICTURE_MISSING_TAG+SPACE
    elif not has_picture and not has_picture_missing_tag and add_picture_tag:
        #print("add tag")
        text = PICTURE_MISSING_TAG.replace('{parameter}',picture)+'\n'+text
        MESSAGE +=ADD_PICTURE_MISSING_TAG+SPACE
    """
    else:
        print("no change")
    """
    return text,MESSAGE


##############################################Needs more work tag##############################################
###Tags
NEED_MORE_WORK_TAG = "{{مقالة خاصها تقاد}}"
need_more_work_tag_part = "{{مقالة خاصها تقاد"
TAG_PROBLEM_NAME_DICT = {EMPTY_PARAGRAPH_TAG:"فقرة خاوية ؤلا ناقصة"
                        ,NO_SOURCES_ON_PAGE_TAG:"ناقصين عيون لكلام"
                        ,CUL_DE_SAC_TAG:"زنقة ماكاتخرجش"
                        ,ORPHANED_PAGE_TAG:"مقطوعة من شجرة"
                        ,NO_CATEGORY_TAG:"ناقصين تصنيفات"
                        }
#WIKIBIDIAS = {"ويكيبيديا","ويكبيديا","ويكبديا","ويكيبديا"}

###Save messages
NEED_MORE_WORK_ADD_MSG = "طّاڭ ديال مقالة خاصها تقاد تزاد"
#NEED_MORE_WORK_RMV_MSG = ""

def get_problems(text):
    """
    Returns the list of problems in a page text,
    e.g. missing sources, deadend page, etc.
    """

    problems = []

    """
    if EMPTY_PARAGRAPH_TAG in text:
        problems.append(EMPTY_PARAGRAPH_TAG)
    """
    
    if NO_SOURCES_ON_PAGE_TAG in text:
        problems.append(NO_SOURCES_ON_PAGE_TAG)

    if CUL_DE_SAC_TAG in text:
        problems.append(CUL_DE_SAC_TAG)

    if ORPHANED_PAGE_TAG in text:
        problems.append(ORPHANED_PAGE_TAG)

    if NO_CATEGORY_TAG in text:
        problems.append(NO_CATEGORY_TAG)

    return problems

###Functions
def add_smth_not_right_tag(page,text,MESSAGE):
    #print("checking wikidata tag")
    has_need_more_work_tag = False
    add_need_more_work_tag = False
    problems = get_problems(text)
    if NEED_MORE_WORK_TAG in text:
        if len(problems)>1:
            problem_statements = [TAG_PROBLEM_NAME_DICT[x] for x in problems]
            text = text.replace(NEED_MORE_WORK_TAG,need_more_work_tag_part+"|problems="+'، '.join(problem_statements)+"}}")
            for problem in problems:
                text = text.replace(problem,"")
            MESSAGE+=NEED_MORE_WORK_ADD_MSG
    else:
        if len(problems)>2:
            problem_statements = [TAG_PROBLEM_NAME_DICT[x] for x in problems]
            text = need_more_work_tag_part+"|problems="+'، '.join(problem_statements)+"}}\n"+text
            for problem in problems:
                text = text.replace(problem,"")
            MESSAGE+=NEED_MORE_WORK_ADD_MSG

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

#site = pywikibot.Site()

if __name__=="__main__":

    function_map = {
                    'setNoSourceTag': setNoSourceTag
                   ,'setNoCategoryTag': setNoCategoryTag
                   ,'setNoBacklinkTag': setNoBacklinkTag
                   #,'setEmptyParagraphTag': setEmptyParagraphTag
                   ,'setNoOutLinkTag': setNoOutLinkTag
                   ,'setNoPicturetag': setNoPicturetag
                   ,'setBotArticleTag': setBotArticleTag
    }

    print_to_console_and_log('Number of passed arguments: '+str(len(argv)))
    local_args = None
    if len(argv)>2:
        if len(argv) > 3:
            local_args = argv[3:]


    JOB_ID = random_n_digit_integer(year_based_integer())
    print_to_console_and_log('Job ID '+str(JOB_ID))

    if local_args is not None and local_args[0] == '-l':
        last_run_time = get_last_run_datetime()
        print_to_console_and_log('Last run time '+str(last_run_time))
        print_to_console_and_log("running for last changed pages")
        #load last changed
        last_changes = site.recentchanges(reverse=True,bot=False,namespaces=[ARTICLE_NAMESPACE],top_only=True,start=last_run_time)
        #create page pool
        #NEXT: check other potential last_change tyfpes

        pool = [pywikibot.Page(site, item['title']) for item in last_changes]

    else:

        print_to_console_and_log("Creating working pool")
        pool = site.allpages(namespace=ARTICLE_NAMESPACE, filterredir=False)
        #pool = [page for page in site.allpages() if validate_page(page)]
    #"""

    #pool = [pywikibot.Page(site, 'جن')]
    #pool = list(pywikibot.Category(site,'تصنيف:مقالات ناقصينهوم تصاور').articles())
    #pool = list(pywikibot.Category(site,'تصنيف:مقالات بلا عيون لكلام').articles())
    #pool = list(pywikibot.Category(site,'تصنيف:أرتيكلات مامربوطينش معا ويكيداطا').articles())
    #pool = list(pywikibot.Category(site,'تصنيف:مقالات زناقي ماكايخرّجوش').articles())
    #pool = list(pywikibot.Category(site,'تصنيف:مقالات مقطوعين من شجرة').articles())

    pool_size = len(list(deepcopy(pool)))
    print_to_console_and_log('Pool size: '+str(pool_size))
    i = 1
    delete_recent_log_if_old()
    pages_in_log = load_pages_in_log()

    with open(RECENT_LOG_FILE,'a',encoding='utf-8') as f:
        
        for page in pool:
            print_to_console_and_log('*********'+str(i)+'/'+str(pool_size))
            
            #print(pages_in_log[:20])
            
            
            if str(page.title()) not in pages_in_log:
                    
                MESSAGE = ""
                    
                if validate_page(page):
                    #print("checking page "+str(i))
                        
                    new_text = page.text

                    for func in function_map.keys():

                        #Calling "No category tag treatment" subprogram
                        #new_text,MESSAGE = setNoCategoryTag(page,new_text,MESSAGE)
                           
                        #checking back links
                        #new_text,MESSAGE = setOrphanTag(page,new_text,MESSAGE)
                          
                        #handling no source tag
                        
                        new_text,MESSAGE = function_map[func](page,new_text,MESSAGE)

                        #handling empty paragraphs
                        #new_text,MESSAGE = setEmptyParagraphTag(page,new_text,MESSAGE)

                        #handling missing picture tag
                        #new_text,MESSAGE = add_missing_picture_tag(page,new_text,MESSAGE)

                        #handling too many problems at once
                        #new_text,MESSAGE = add_smth_not_right_tag(page,new_text,MESSAGE)

                        """
                        Deactivated for now
                        #handling Wikipidia with SOMETHINGS_NOT_RIGHT_TAG
                        new_text,MESSAGE = add_smth_not_right_tag(page,new_text,MESSAGE)
                        """
                        #handling deadend tag
                        """
                        try:
                            new_text,MESSAGE = setDeadendTag(page,new_text,MESSAGE,site)
                        except Exception:
                            with open('error_log.txt','w',encoding='utf-8') as er:
                                er.write(str(page.title())+'\n'+str(sys.exc_info()))
                                print_to_console_and_log(str(sys.exc_info()))
                        """
                        #print("testing page text changed")    
                    if new_text != page.text:
                        #print("page text has been changed")
                        page.text = new_text
                        try:
                            if JOB_ID is not None:
                                MESSAGE+=" - "+JOB_ID_MSG_PART.format(JOB_ID)
                            page.save(MESSAGE)
                        except:
                            #LOG_PAGE_TITLE = 
                            #log_error(LOG_PAGE_TITLE,log_message,save_log_message,site)
                            print(sys.exc_info())
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
