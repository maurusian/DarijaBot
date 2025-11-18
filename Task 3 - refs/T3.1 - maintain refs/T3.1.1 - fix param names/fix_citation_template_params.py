import pywikibot
import re, os
from sys import argv
from copy import deepcopy
from datetime import datetime
from pywikibot.exceptions import OtherPageSaveError, SpamblacklistError

ALL_WEB_CITATION_PATTERN_TMP_NAMES = "Lien web|استشهاد ويب|استشهاد بخبر|استشهاد بويب|Article|Cite web|Internetquelle|مرجع ويب|ouvrage|cite magazine|مرجع مجلة|مرجع موسوعة|مرجع پاطونط|cite patent|cite book|مرجع كتاب|مرجع تيز|cite thesis|cite encyclopedia|cite journal|مرجع جورنال|cite report|cite conference|مرجع خبار|cite tweet|cite episode|cite dictionary"
MAIN_WEB_CITATION_TEMPLATE_MATCH_PATTERN = r"\{\{(" + ALL_WEB_CITATION_PATTERN_TMP_NAMES + r")((?:\|[^{}]*)*)\}\}"

TO_ARY_CONV_TAB = {'الأخير':'last'
                   ,'الأول':'first'
                   ,'سنة':'year'
                   ,'عنوان':'title'
                   ,'إصدار':'issue'
                   ,'ناشر':'publisher'
                   ,'طبعة':'publication-date'
                   ,'لغة':'language'
                   ,'مسار':'url'
                   ,'تاريخ':'date'
                   ,'مؤلف1':'author1'
                   ,'مؤلف2':'author2'
                   ,'مؤلف':'author'
                   ,'تاريخ الوصول':'access-date'
                   ,'تاريخ لوصول':'access-date'
                   ,'مسار أرشيف':'archive-url'
                   ,'تاريخ أرشيف':'archive-date'
                   ,'مكان':'location'
                   ,'صفحات':'pages'
                   ,'عنوان مترجم':'trans-title'
                   ,'الأول1':'first1'
                   ,'أول1':'first1'
                   ,'أول2':'first2'
                   ,'الأخير1':'last1'
                   ,'الأخير2':'last2'
                   ,'الأول2':'first2'
                   ,'صفحة':'page'
                   ,'المجلد':'volume'
                   ,'صحيفة':'journal'
                   ,'عمل':'work'
                   ,'موقع':'website'
                   ,'وصلة مكسورة':'dead-url'
                   ,'وصلة مؤلف':'author-link'
                   ,'مؤلفون مشاركون':'authors'
                   ,'حالة المسار':'url-status'
                   ,'titre':'title'
                   ,'langue':'language'
                   ,'consulté le':'access-date'
                   ,'site':'website'
                   ,'الصفحات':'pages'
                   ,'nom':'last'
                   ,'prénom':'first'
                   ,'nom1':'last1'
                   ,'prénom1':'first1'
                   ,'nom2':'last2'
                   ,'prénom2':'first2'
                   ,'nom3':'last3'
                   ,'prénom3':'first3'
                   ,'nom4':'last4'
                   ,'prénom4':'first4'
                   ,'lire en ligne':'url'
                   ,'numéro':'issue'
                   ,'périodique':'journal'
                   ,'auteur':'author'
                   ,'année':'year'
                   ,'éditeur':'editor'
                   ,'autor':'author'
                   ,'zugriff':'access-date'
                   ,'titel':'title'
                   ,'werk':'work'
                   ,'datum':'date'
                   ,'abruf':'access-date'
                   ,'archiv-url':'archive-url'
                   ,'archiv-datum':'archive-date'
                   ,'sprache':'language'
                   ,'hrsg':'website'
                   }


SAVE_MESSAGE = "عطاشة 3.1.1: مقادّة ديال السميات د لپاراميطرات ف لمراجع د لمقال"

LAST_RUN_FILE = "last_run.txt"

DATE_FORMAT = "%Y-%m-%d %H:%M"

RECENT_LOG_FILE = "recent_log.txt"

JOB_ID_MSG_PART = "نمرة د دّوزة {}"

LOCAL_LOG = "task3.1.1.log"

def getOnlyArticles(site):
    """
    Returns a generator that contains only articles (with no redirects)
    """
    return site.allpages(namespace=0,filterredir=False)


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

def extract_params(param_text):
    params = {}
    current = ""
    depth = 0
    parts = []

    for char in param_text.strip():
        if char == '|' and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += char
            if char in ['{', '[']:
                depth += 1
            elif char in ['}', ']']:
                depth -= 1

    if current:
        parts.append(current)

    for part in parts:
        if '=' in part:
            key, value = part.split('=', 1)
            params[key.strip()] = value.strip()

    return params


def correct_param_keys(params):
    corrected = {}
    for k, v in params.items():
        new_key = TO_ARY_CONV_TAB.get(k.strip(), k.strip())
        corrected[new_key] = v
    return corrected

def rebuild_template(name, params_dict):
    template_lines = [f"{{{{{name}"]
    for key, value in params_dict.items():
        template_lines.append(f"|{key}={value}")
    template_lines.append("}}")
    return "\n".join(template_lines)

def fix_single_citation_match(match):
    template_name = match.group(1).strip()
    param_text = match.group(2) or ""
    try:
        return fix_single_template(template_name, param_text)
    except Exception:
        return match.group(0)


def fix_single_template(template_name, raw_param_text):
    param_dict = extract_params(raw_param_text)
    corrected_params = correct_param_keys(param_dict)
    return rebuild_template(template_name, corrected_params)


def fix_citation_templates_in_text(text):
    pattern = re.compile(MAIN_WEB_CITATION_TEMPLATE_MATCH_PATTERN, flags=re.DOTALL | re.IGNORECASE)
    return pattern.sub(fix_single_citation_match, text)


if __name__ == "__main__":
    site = pywikibot.Site()
    site.throttle.maxdelay = 0
    site.login()

    test_title = "دم" #"جاسمين دمراوي"  # Optional manual page title for testing
    load_from_cat_name = "" #"تصنيف:أرتيكلات فيهوم موشكيل بسباب عطاشة 3.1"

    if test_title.strip():
        test_page = pywikibot.Page(site, test_title)
        pool = [test_page]

    elif load_from_cat_name.strip():
        category = pywikibot.Category(site, load_from_cat_name)
        test_articles = list(category.articles())
        pool = test_articles if test_articles else []

    else:
        print_to_console_and_log('Number of passed arguments: ' + str(len(argv)))
        local_args = argv[4:] if len(argv) > 4 else None

        JOB_ID = local_args[-1] if local_args and len(local_args) > 2 else None
        if JOB_ID:
            print_to_console_and_log('Job ID ' + str(JOB_ID))

        if local_args and local_args[0] == '-l':
            last_run_time = get_last_run_datetime()
            print_to_console_and_log('Last run time ' + str(last_run_time))
            print_to_console_and_log("running for last changed pages")
            last_changes = site.recentchanges(
                reverse=True, namespaces=[0], top_only=True, start=last_run_time
            )
            pool = [pywikibot.Page(site, item['title']) for item in last_changes]
        else:
            print_to_console_and_log("Creating working pool")
            pool = getOnlyArticles(site)

    pool_size = len(list(deepcopy(pool)))
    print_to_console_and_log('Pool size: ' + str(pool_size))
    pages_in_log = load_pages_in_log()
    i = 1

    with open(RECENT_LOG_FILE, 'a', encoding='utf-8') as f:
        for page in pool:
            print_to_console_and_log('********* ' + str(i) + '/' + str(pool_size))
            if str(page.title()) not in pages_in_log:
                #print(page.title())
                try:
                    original_text = page.text
                    fixed_text = fix_citation_templates_in_text(original_text)

                    if original_text != fixed_text:
                        page.text = fixed_text
                        try:
                            page.save(SAVE_MESSAGE)
                        except OtherPageSaveError:
                            print_to_console_and_log("Page " + page.title() + " caused OtherPageSaveError")
                        except SpamblacklistError:
                            print_to_console_and_log("Page " + page.title() + " caused SpamblacklistError")

                        f.write(page.title() + '\n')
                except Exception as e:
                    print_to_console_and_log(f"Error processing page {page.title()}: {e}")
                
                f.write(page.title()+'\n')
            i += 1

    write_run_time()
