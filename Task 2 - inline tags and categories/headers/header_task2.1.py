from   pgvbotLib            import *
import arywikibotlib        as awbl
from   arywikibotlib        import isHuman, hasPropertyXValue

import pywikibot
from pywikibot import textlib
from   pywikibot.exceptions import NoPageError

import re, sys, os, random
from   copy                 import deepcopy
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
        return TEMPLATE_NS+":"+str(m.group(0)).split("|")[0].replace("{","").replace("}","")
    else:
        regexp = re.compile(INFOBOX_TAG_PATTERN2)
        m = regexp.search(page.text)
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
NO_CATEGORY_TAG = "{{مقالة ما مصنفاش}}"
CATEGORY_ISSUE_RGX = "{{مقالة خاصها تقاد\|.+مامصنفاش.+}}"

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
ORPHANED_PAGE_TAG = "{{مقالة مقطوعة من شجرة}}"
ORPHANED_ISSUE_RGX = "{{مقالة خاصها تقاد\|.+مقطوعة.+}}"

###Save messages
ADD_ORPHAN_TAG_MESSAGE = 'طاڭ ديال "مقطوعة من شجرة" تزاد.'
REMOVE_ORPHAN_TAG_MESSAGE = 'طاڭ ديال "مقطوعة من شجرة" تحيّد.'

###Functions
def setOrphanTag(page,text,MESSAGE):
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
CUL_DE_SAC_TAG = "{{مقالة زنقة ماكاتخرجش}}"
OUTLINK_PATTERN = r'\[\[.+?\]\]'
CUL_DE_SAC_ISSUE_RGX = "{{مقالة خاصها تقاد\|.+ماكاتخرجش.+}}"

###Save messages
ADD_DEADEND_TAG_MESSAGE = "طّاڭ ديال زنقة ماكاتخرجش تزاد"
REMOVE_DEADEND_TAG_MESSAGE = "طّاڭ ديال زنقة ماكاتخرجش تحيد"

###Functions
def setDeadendTag(page,text,MESSAGE,site):
    has_deadend_tag = False
    should_not_add_tag = False
    regexp = re.compile(CUL_DE_SAC_ISSUE_RGX,flags=re.DOTALL)
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

    if (has_deadend_tag or regexp.search(text)) and should_not_add_tag:
        text = text.replace(CUL_DE_SAC_TAG,'').strip()
        MESSAGE += REMOVE_DEADEND_TAG_MESSAGE+SPACE
    elif not has_deadend_tag and not regexp.search(text) and not should_not_add_tag:
        text = CUL_DE_SAC_TAG + "\n" + text
        MESSAGE += ADD_DEADEND_TAG_MESSAGE+SPACE
    return text,MESSAGE

##############################################No sources tag##############################################
###Tags
NO_SOURCES_ON_PAGE_TAG = "{{مقالة ناقصينها عيون لكلام}}"
SOURCE_EXIST_PATTERN = r"ref.+?/ref"
REF_TAG = "<ref"
NO_SOURCES_ISSUE_RGX = "{{مقالة خاصها تقاد\|.+عيون لكلام.+}}"

###Save messages
ADD_NO_SOURCE_TAG_MESSAGE = "طّاڭ ديال ناقصين عيون لكلام تزاد"
REMOVE_NO_SOURCE_TAG_MESSAGE = "طّاڭ ديال ناقصين عيون لكلام تحيد"

def has_sources(text):
    source_patterns = [r"<ref[^>]*>"] #, r"{{\s*cite", r"{{\s*cite"]
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

###Functions
def setNoSourceTag(page,text,MESSAGE):
    has_no_source_tag = False
    regexp = re.compile(NO_SOURCES_ISSUE_RGX,flags=re.DOTALL)
    if NO_SOURCES_ON_PAGE_TAG in text or regexp.search(page.text):
        has_no_source_tag = True
    
    sources = re.findall(SOURCE_EXIST_PATTERN,page.text)

    if (REF_TAG not in page.text and not find_template_sources(text)) and not has_no_source_tag:
        text = NO_SOURCES_ON_PAGE_TAG + '\n' + text
        MESSAGE += ADD_NO_SOURCE_TAG_MESSAGE+SPACE
    elif (REF_TAG in page.text or find_template_sources(text)) and has_no_source_tag:
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
PICTURE_MISSING_TAG         = "{{مقالة ناقصينها تصاور|{parameter}}}"
PICTURE_MISSING_TAG_PATTERN = r"{{مقالة ناقصينها تصاور\|.*?}}"
PICTURE_MISSING_TAG_PART    = "{{مقالة ناقصينها تصاور"
PIC_REGEX                   = r"{{معلومات.+\|صورة=.+\..+}}"
PIC_REGEX2                  = r"{{معلومات.+\|الصورة=.+\..+}}"
PIC_REGEX3                  = r"{{معلومات.+\|تصويرة=.+\..+}}"
PICTURE_PROPERTIES = ["P18","P154","P41","P94","P158","P2176","P8592","P948","P8224","P1846"]
PIC_EXCEPTION_CAT_LIST = ["تصنيف:نهارات د لعام","تصنيف:عوام د تقويم لميلادي","تصنيف:ستيتناء من طاݣ ناقصين تصاور"]
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
ADD_PICTURE_MISSING_TAG = "طّاڭ ديال ناقصين تصاور تزاد"
RMV_PICTURE_MISSING_TAG = "طّاڭ ديال ناقصين تصاور تحيّد"

###Functions

def has_pictures_or_videos(page):
    return bool(page.imagelinks())

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

def is_image_property_used_in_infobox(page, image_properties):
    #print("is_image_property_used_in_infobox")
    infobox_template_page = get_infobox_template_page(page)

    #print(infobox_template_page)
    
    if infobox_template_page:
        infobox_template = get_final_redirect_target(pywikibot.Page(site, infobox_template_page))

        #print(infobox_template)

        for image_property in image_properties:
            if image_property in infobox_template.text:
                #print(image_property)
                return True

    return False

def add_missing_picture_tag(page,text,MESSAGE):
    #print("checking picture tag")
    has_picture = False
    has_picture_missing_tag = False
    add_picture_tag = False
    picture = ""
    commons_cat = get_commons_category(page)
    regexp = re.compile(PIC_REGEX,flags=re.DOTALL)
    regexp2 = re.compile(PIC_REGEX2,flags=re.DOTALL)
    regexp3 = re.compile(PIC_REGEX3,flags=re.DOTALL)
    if has_pictures_or_videos(page) or FILE_PART_DICT['ary'] in text or FILE_PART_DICT['en'] in text or FILE_PART_DICT['ar'] in text or GALLERY_PART_DICT['en'] in text or regexp.search(text) or regexp2.search(text) or regexp3.search(text):
        #print(FILE_PART_DICT['en'] in text)
        #print("has a picture in text")
        has_picture = True
        #print("found article to have a picture "+str(page.title())+" flag has_picture="+str(has_picture))
    
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
            if len(image_properties)>0 and is_image_property_used_in_infobox(page, image_properties):
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
        commons_cat = get_commons_category(page)
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
site = pywikibot.Site()



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

                #Calling "No category tag treatment" subprogram
                new_text,MESSAGE = setCategoryTag(page,new_text,MESSAGE)
                   
                #checking back links
                new_text,MESSAGE = setOrphanTag(page,new_text,MESSAGE)
                  
                #handling no source tag
                new_text,MESSAGE = setNoSourceTag(page,new_text,MESSAGE)

                #handling empty paragraphs
                new_text,MESSAGE = setEmptyParagraphTag(page,new_text,MESSAGE)

                #handling missing picture tag
                new_text,MESSAGE = add_missing_picture_tag(page,new_text,MESSAGE)

                #handling too many problems at once
                new_text,MESSAGE = add_smth_not_right_tag(page,new_text,MESSAGE)

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
                        print_to_console_and_log(str(sys.exc_info()))

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
