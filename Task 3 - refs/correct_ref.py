import pywikibot
from pywikibot.exceptions import  OtherPageSaveError
import re, os
from arywikibotlib import getOnlyArticles
from sys import argv
from copy import deepcopy
from datetime import datetime

ARTICLE_NAMESPACE = 0

REF_PATTERN1 = r"<ref>.+?</ref>"
REF_PATTERN2 = r"<ref name\=.+?>.+?</ref>"
REF_PATTERN3 = r"<ref name=.+?/?>"

SIMPLE_REF_PATTERN = r">[\n|\s]*\[http.+?\][\n|\s]*<"
CITE_WEB_PATTERN = """{{Cite web
|url={url}
|title={title}
}}
"""

SIMPLE_BOOK_PATTERN = """<ref{namepart}>{{Cite book
|title={title}
|isbn={isbn}
|url={url}
}}
</ref>"""

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
                     }

SAVE_MESSAGE = "إصلاح ديال طّاڭات د لعيون"

LAST_RUN_FILE = "last_run.txt"

DATE_FORMAT = "%Y-%m-%d %H:%M"

RECENT_LOG_FILE = "recent_log.txt"

JOB_ID_MSG_PART = "نمرة د دّوزة {}"

LOCAL_LOG = "task3.log"

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


def get_ref_list(page):
    refs = list(re.findall(REF_PATTERN1, page.text,re.DOTALL))

    repeated_refs = list(re.findall(REF_PATTERN3, page.text,re.DOTALL))
    
    tmp_text = page.text
    for rr in repeated_refs:
        if '/' in rr:
            tmp_text = tmp_text.replace(rr,'')

    named_refs = list(re.findall(REF_PATTERN2, tmp_text,re.DOTALL))
    
    refs.extend(named_refs)

    return refs


def get_simple_ref_part(ref):
    ref_part = list(re.findall(SIMPLE_REF_PATTERN, ref,re.DOTALL))

    if len(ref_part) == 1:
        #print("found*********************")
        #print(ref_part)
        words = ref_part[0].replace('<','').replace('[','').replace('>','').replace(']','').split(' ')
        url = ''
        for word in words:
            if 'http' in word:
                url = word.strip()
                #print('url: '+url)

        if url != '':
            title = ref_part[0].replace('<','').replace('[','').replace('>','').replace(']','').replace(url,'').strip()

            value = ref.replace(ref_part[0],'>'+CITE_WEB_PATTERN.replace('{url}',url).replace('{title}',title)+'<')

            #print(value)
            return value
    return None

def get_simple_book_ref(ref):
    print(ref.split('{{ISBN'))
    raw_isbn = ref.split('{{ISBN')[1].split('}}')[0]
    if 'name=' in ref:
        ref_name_part = ' name='+ref.split('name=')[1].split('>')[0]
    else:
        ref_name_part = ""

    remainder_text = ref.replace('{{ISBN'+raw_isbn+'}}','').replace('</ref>','').strip().strip('.').strip()

    remainder_text = re.sub('<ref.*?>','',remainder_text)

    url = ''
    
    if '[http' in remainder_text:
        words = remainder_text.replace('<','').replace('[','').replace('>','').replace(']','').split(' ')
        
        for word in words:
            if 'http' in word:
                url = word.strip("'").strip('"').strip()
        if url != '':
            remainder_text = remainder_text.replace('[','').replace(']','').replace(url,'').replace('  ',' ').strip()

    return SIMPLE_BOOK_PATTERN.replace('{namepart}',ref_name_part).replace('{title}',remainder_text).replace('{url}',url).replace('{isbn}',raw_isbn.replace('|','').strip())
    

def get_textual_fixed_ref(ref):
    PARAM_VALUE_PATTERN = r'\[\[.+?\|.+?(?=/\n|)' #to fix line feed issue within param value caused by our own replace functions
    fixed_ref = ref.replace('{{!}}','-').replace('\n',' ').replace('  ',' ').replace('\n|','|').replace('|','\n|').replace('\n}}','}}').replace('}}','\n}}').replace('\n</ref>','</ref>').replace('</ref>','\n</ref>')
    fixed_ref = re.sub(r" *= *","=",fixed_ref)
    fixed_ref = re.sub(r" *\| *","|",fixed_ref)

    #param_values = [pv.split('|')[0] for pv in fixed_ref.split('=')]

    """
    for param_value in param_values:
        new_param_value = param_value.replace('\n','')
        fixed_ref = fixed_ref.replace(param_value, new_param_value)
    """
    #fixed_ref = re.sub(r" *\| *","|",fixed_ref)

    ref_parts = fixed_ref.split('=')[1:]

    for ref_part in ref_parts:
        if ']]' in ref_part:
            param_value = ref_part.split(']]')[0]
            new_param_value = param_value.replace('\n','').strip()
            new_param_value = re.sub(r" *\| *","|",new_param_value)
            fixed_ref = fixed_ref.replace(param_value,new_param_value)

    ref_adj_tmp = ""
    for line in fixed_ref.splitlines():
        ref_adj_tmp+=line.strip()+'\n'

    fixed_ref = ref_adj_tmp.strip()

    return fixed_ref

def get_fixed_keywords_ref(ref):
    fixed_keywords_ref = ref
    PIPE = '|'
    EQ = '='
    for key, value in TO_ARY_CONV_TAB.items():
        fixed_keywords_ref = fixed_keywords_ref.replace(PIPE+key+EQ,PIPE+value+EQ)

    return fixed_keywords_ref
    
site = pywikibot.Site()

#page = pywikibot.Page(site,title)

#refs = list(re.findall(REF_PATTERN, page.text,re.DOTALL))

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
    last_changes = site.recentchanges(reverse=True,namespaces=[ARTICLE_NAMESPACE],top_only=True,start=last_run_time) #,filteredir=False)
    #create page pool
    #NEXT: check other potential last_change types

    pool = [pywikibot.Page(site, item['title']) for item in last_changes]

else:

    print_to_console_and_log("Creating working pool")
    pool = getOnlyArticles(site)
    #pool = [page for page in site.allpages() if validate_page(page)]

pool_size = len(list(deepcopy(pool)))
print_to_console_and_log('Pool size: '+str(pool_size))
i = 1
pages_in_log = load_pages_in_log()

with open(RECENT_LOG_FILE,'a',encoding='utf-8') as f:
    
    for page in pool:
        print_to_console_and_log('*********'+str(i)+'/'+str(pool_size))
        #page = pywikibot.Page(site,"كيلوݣرام") #debugging
        if str(page.title()) not in pages_in_log:
        
            refs = get_ref_list(page)

            tmp_text = page.text
            for ref in refs:
                if ref is not None:
                    if '{{ISBN' in ref.upper():
                        print(page.title())
                        new_ref = get_simple_book_ref(ref)
                    else:
                        ref_adj = get_textual_fixed_ref(ref)

                        ref_adj = get_fixed_keywords_ref(ref_adj)
                        
                        
                        tmp_text = tmp_text.replace(ref,ref_adj)

                        new_ref = get_simple_ref_part(ref_adj)

                    if new_ref is not None:
                        
                        tmp_text = tmp_text.replace(ref,new_ref) #to be tested

            if page.text != tmp_text:
                page.text = tmp_text
                try:
                    page.save(SAVE_MESSAGE)
                except OtherPageSaveError:
                    print_to_console_and_log("Page "+page.title()+" caused OtherPageSaveError")

            #write to recent log    
            f.write(page.title()+'\n')

        i+=1
        #break #debugging
write_run_time()
