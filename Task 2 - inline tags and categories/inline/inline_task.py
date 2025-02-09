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
##Empty paragraph tag


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

##############################################MAIN PROGRAM##############################################

#site = pywikibot.Site()

if __name__=="__main__":

    function_map = {
                   'setEmptyParagraphTag': setEmptyParagraphTag
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

                        new_text,MESSAGE = function_map[func](page,new_text,MESSAGE)

                    if new_text != page.text:
                        page.text = new_text
                        try:
                            if JOB_ID is not None:
                                MESSAGE+=" - "+JOB_ID_MSG_PART.format(JOB_ID)
                            page.save(MESSAGE)
                        except:
                            print(sys.exc_info())
                            continue
              

                f.write(page.title()+'\n')
            i+=1

    write_run_time()
