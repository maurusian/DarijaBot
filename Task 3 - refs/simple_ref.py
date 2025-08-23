from pywikibot.exceptions import  OtherPageSaveError
import re, os, requests, pywikibot
from arywikibotlib import getOnlyArticles
from sys import argv
from copy import deepcopy
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse

ARTICLE_NAMESPACE = 0

REF_PATTERN1 = r"<ref>.+?</ref>"
REF_PATTERN2 = r"<ref name\=.+?>.+?</ref>"
REF_PATTERN3 = r"<ref name=.+?/?>"
BRKN_LNK_TAG_PATTERN1 = "\{\{\s*(ليان مهرس|وصلة مكسورة|[dD]ead link)\s*\|\s*date\s*=\s*[^|}]+\|\s*bot\s*=\s*[^|}]+\|\s*fix-attempted\s*=\s*[^|}]+\s*\}\}"

SIMPLE_REF_PATTERN = r">[\n|\s]*\[http.+?\][\n|\s]*<"

ALL_WEB_CITATION_PATTERN_TMP_NAMES = "Lien web|استشهاد بويب|Article|Cite web|Internetquelle|مرجع ويب"
MAIN_WEB_CITATION_TEMPLATE_MATCH_PATTERN = r'\{\{(?:' + ALL_WEB_CITATION_PATTERN_TMP_NAMES + r')(.*)'

CITE_WEB_PATTERN = """{{Cite web
|url={url}
|title={title}
}}
"""


ALL_CITATION_PATTERN_START = "Lien|استشهاد|Article|Ouvrage|Cite|Internetquelle|مرجع"

SIMPLE_BOOK_PATTERN = """<ref{namepart}>{{Cite book
|title={title}
|isbn={isbn}
|url={url}
}}
</ref>"""

SAVE_MESSAGE = "عطاشة 3.1: مقادّة ديال لمصادر ف لمقال"

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
    """
    loads recent log of pages already treated
    """
    if not os.path.exists(RECENT_LOG_FILE):
        return []
    with open(RECENT_LOG_FILE,'r',encoding='utf-8') as f:
        page_name_list = f.read().strip().splitlines()
    
    for i in range(len(page_name_list)):
        page_name_list[i] = page_name_list[i].strip()
    
    return page_name_list

def extract_params(text):
    params = {}
    lines = text.split('\n')
    current_key = None
    current_value = ''
    for line in lines:
        line = line.strip()
        if line.startswith('|'):
            if current_key:
                params[current_key] = current_value
            if '=' in line:
                current_key, current_value = line[1:].split('=', 1)
                current_key = current_key.strip()
                current_value = current_value.strip()
            else:
                current_key = line[1:].strip()
                current_value = ''
        else:
            current_value += ' ' + line
    if current_key:
        params[current_key] = current_value
    return params

def is_simple_reference(ref):
    # Define the regex pattern to match non-simple references
    non_simple_reference_pattern = r'<ref(?:\s+[^>]*)?>\{\{(?:'+ALL_CITATION_PATTERN_START+').*?\}\}<\/ref>'
    
    # Check if the reference matches the non-simple pattern
    if re.search(non_simple_reference_pattern, ref, re.IGNORECASE | re.DOTALL):
        print("has non simple ref")
        return False
    
    # If the reference does not match the non-simple pattern,
    # check if it matches the simple reference pattern
    simple_reference_pattern = r'<ref(?:\s+[^>]*)?>(.*?)<\/ref>'
    match = re.search(simple_reference_pattern, ref, re.DOTALL)
    
    # If a match is found, it's a simple reference
    print(f"has simple ref: {bool(match)}")
    return bool(match)


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


def get_title_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string
        return title
    except Exception as e:
        print(f"An error occurred: {e}")
        return None



def get_website_name(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc


def get_simple_ref_part(ref):
    match = re.match(r'<ref([^>]*)>(.*?)<\/ref>', ref, re.DOTALL)
    if not match:
        return None

    ref_attrs = match.group(1)  # attributes inside <ref ...>
    ref_content = match.group(2)  # content inside <ref>...</ref>

    url = ''
    full_title = ''
    archive_url = ''
    archive_date = ''
    publication_date = ''

    # Extract the webarchive template if present
    webarchive_match = re.search(r'\{\{[Ww]ebarchive\s*\|\s*(.*?)\}\}', ref_content, re.DOTALL)
    param_dict = {}
    if webarchive_match:
        params = webarchive_match.group(1)
        for param in params.split('|'):
            if '=' in param:
                key, value = param.split('=', 1)
                param_dict[key.strip()] = value.strip()

        # Priority: archive-url > url
        if 'archive-url' in param_dict:
            archive_url = param_dict['archive-url']
        if 'archiveurl' in param_dict:
            archive_url = param_dict['archive-url']
        if 'url' in param_dict:
            url_from_webarchive = param_dict['url']
        else:
            url_from_webarchive = ''

        # Priority handling for archive-date and publication date
        if 'archive-date' in param_dict:
            archive_date = param_dict['archive-date']
        if 'archivedate' in param_dict:
            archive_date = param_dict['archive-date']
        if 'date' in param_dict:
            if 'archive-date' not in param_dict or 'archivedate' not in param_dict:
                archive_date = param_dict['date']
            else:
                publication_date = param_dict['date']

        # Remove the webarchive template from the content
        ref_content = re.sub(r'\{\{[Ww]ebarchive\s*\|.*?\}\}', '', ref_content, flags=re.DOTALL).strip()

    else:
        url_from_webarchive = ''

    link_match = re.search(r'\[(https?://[^\s\]]+)\s+([^\]]+)\]', ref_content)
    if link_match:
        # normal case: [url title]
        url = link_match.group(1).strip()
        title_inside_link = link_match.group(2).strip()

        before_link = ref_content[:link_match.start()].strip()
        after_link = ref_content[link_match.end():].strip()

        parts = []
        if before_link:
            parts.append(before_link)
        parts.append(title_inside_link)
        if after_link:
            parts.append(after_link)

        full_title = ' '.join(parts)

    else:
        # no [url title] inside content
        if 'http' in ref_content:
            url = ref_content.strip()
            title = get_title_from_url(url)
            if not title:
                title = get_website_name(url)
            full_title = title
        elif url_from_webarchive:
            # special case: use Webarchive url and text outside as title
            url = url_from_webarchive
            full_title = ref_content.strip()
        else:
            full_title = ref_content.strip()

    full_title = full_title.replace('|',' - ').replace('\n',' ').replace('  ',' ')
    if url:
        # Build the citation manually
        cite_parts = [
            '{{مرجع ويب',
            f'|url={url}'
        ]
        if archive_url:
            cite_parts.append(f'|archive-url={archive_url}')
        if archive_date:
            cite_parts.append(f'|archive-date={archive_date}')
        if publication_date:
            cite_parts.append(f'|date={publication_date}')
        cite_parts.append(f'|title={full_title.strip()}')
        cite_parts.append('}}')

        new_cite = '\n'.join(cite_parts)

        return f'<ref{ref_attrs}>{new_cite}</ref>'

    return None

def extract_isbn(wiki_reference):
    isbn_pattern = r"isbn\s*\|\s*([\d\-]+)"
    match = re.search(isbn_pattern, wiki_reference, flags=re.IGNORECASE)

    if match:
        return match.group(1)
    else:
        return None

def get_simple_book_ref(ref):
    #print(ref.split('{{ISBN'))
    raw_isbn = extract_isbn(ref)
    if 'name=' in ref:
        ref_name_part = ' name='+ref.split('name=')[1].split('>')[0]
    else:
        ref_name_part = ""

    remainder_text = ref.replace('{{ISBN|'+raw_isbn+'}}','').replace('</ref>','').strip().strip('.').strip()

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

def get_broken_link_tag_list(page):
    broken_link_tags = list(re.findall(BRKN_LNK_TAG_PATTERN1, page.text,re.DOTALL))
    return broken_link_tags

from html import unescape

def get_webpage_title(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; pywikibot/1.0)'
        }
        response = requests.get(url, timeout=10, headers=headers)
        print(f'response.status_code={response.status_code}')
        if response.status_code != 200:
            return None
        html = response.text
        match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if match:
            raw_title = match.group(1)
            clean_title = unescape(raw_title).strip()
            clean_title = re.sub(r'\s+', ' ', clean_title)  # Normalize spaces
            return clean_title
    except Exception:
        return None
    return None

from urllib.parse import urlparse

def get_website_name(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain:
            return domain.replace("www.","")
    except Exception:
        pass
    return None


def fix_empty_title(ref_text):
    ref_content = re.search(r'<ref(?:\s+[^>]*)?>(.*?)<\/ref>', ref_text, re.DOTALL)
    if not ref_content:
        return ref_text

    ref_inner = ref_content.group(1)

    # Remove any leftover closing }}
    ref_inner = re.sub(r'}}\s*', '', ref_inner)

    # Find main Cite web template
    main_template_match = re.search(MAIN_WEB_CITATION_TEMPLATE_MATCH_PATTERN, ref_inner, re.DOTALL)
    if not main_template_match:
        return ref_text

    main_template_content = main_template_match.group(1)

    def extract_params(text):
        params = {}
        lines = text.split('\n')
        current_key = None
        current_value = ''
        for line in lines:
            line = line.strip()
            if line.startswith('|'):
                if current_key:
                    params[current_key] = current_value
                if '=' in line:
                    current_key, current_value = line[1:].split('=', 1)
                    current_key = current_key.strip()
                    current_value = current_value.strip()
                else:
                    current_key = line[1:].strip()
                    current_value = ''
            else:
                current_value += ' ' + line
        if current_key:
            params[current_key] = current_value
        return params

    params = extract_params(main_template_content)

    if 'title' not in params or not params['title'].strip():
        if 'url' in params and params['url'].strip():
            url_link = params['url'].strip()
            page_title = get_webpage_title(url_link)
            print(f'page_title={page_title}')
            if page_title:
                params['title'] = page_title
            else:
                params['title'] = get_website_name(url_link)

    #cleanup
    params['title'] = params['title'].replace('|','-')
    # Final cleaning: no empty params
    final_params = {}
    for k, v in params.items():
        if v.strip():
            final_params[k] = v.strip()

    # Rebuild the ref
    # Find the <ref> opening tag (with possible attributes)
    ref_open_match = re.match(r'<ref([^>]*)>', ref_text)
    ref_open = ref_open_match.group(0) if ref_open_match else '<ref>'

    # Replace the Cite web content
    new_cite_web = '{{مرجع ويب\n'
    for key, value in final_params.items():
        new_cite_web += f'|{key}={value}\n'
    new_cite_web += '}}'

    # Replace the old Cite web template inside
    ref_inner_replaced = re.sub(MAIN_WEB_CITATION_TEMPLATE_MATCH_PATTERN, new_cite_web, ref_inner, flags=re.DOTALL)

    # Rebuild the full <ref> tag
    result = f'{ref_open}{ref_inner_replaced}</ref>'

    return result

if __name__ =="__main__":

    site = pywikibot.Site()
    site.throttle.maxdelay = 0
    site.login()

    #page = pywikibot.Page(site,title)

    #refs = list(re.findall(REF_PATTERN, page.text,re.DOTALL))

    test_title = "جاسمين دمراوي" #"لمتحف ليهودي لمغريبي"
    load_from_cat_name = "تصنيف:أرتيكلات فيهوم موشكيل بسباب عطاشة 3.1"
    if test_title is not None and test_title.strip() != "":
        test_page = pywikibot.Page(site,test_title)
        pool = [test_page]

    
    elif load_from_cat_name is not None and load_from_cat_name.strip() != "":
        category = pywikibot.Category(site, load_from_cat_name)
        test_articles = list(category.articles())
        if test_articles is not None and len(test_articles)>0:
            pool = test_articles

    else:
        print_to_console_and_log('Number of passed arguments: '+str(len(argv)))
        local_args = None
        if len(argv)>3:
            if len(argv) > 4:
                local_args = argv[4:]

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
        archives = load_archive_log()
        #print(archives)
        for page in pool:
            print_to_console_and_log('*********'+str(i)+'/'+str(pool_size))
            #page = pywikibot.Page(site,"كيلوݣرام") #debugging
            if str(page.title()) not in pages_in_log:
                
                refs = get_ref_list(page)

                tmp_text = page.text
                for ref in refs:
                    if ref is not None:
                        #print(ref)
                        """
                        if '{{ISBN' in ref.upper():
                            print(page.title())
                            new_ref = get_simple_book_ref(ref)
                        """
                        #else:
                        print(ref)
                        if is_simple_reference(ref):
                            print("is simple ref")
                            new_ref = get_simple_ref_part(ref)
                            if new_ref is not None:
                                #fix issues introduced by naive implementation of get_simple_ref_part, due to "webarchive" template
                            
                                #fix url and title
                                new_ref = fix_empty_title(new_ref)

                                #fix dates
                                #fix issues introduced by naive implementation of get_simple_ref_part, due to "webarchive" template
                                #new_ref = fix_url_and_title_in_ref(new_ref)
                                #new_ref = fix_empty_title(new_ref)
                                #new_ref = get_fixed_dates_ref(new_ref)

                                new_ref = new_ref.replace("}}\n</ref>","}}</ref>") #bug fix
                                tmp_text = tmp_text.replace(ref,new_ref) #to be tested

                            else:
                                print(f"Reference {ref} should be parsed as a simple ref but is not.")

                                
                                
                        else:
                            continue

                            

                broken_link_tags = get_broken_link_tag_list(page)
                for broken_link_tag in broken_link_tags:
                    tmp_text = tmp_text.replace(broken_link_tag,fix_broken_link_tag(broken_link_tag))

                        
                #break        
                if page.text != tmp_text:
                    page.text = tmp_text
                    try:
                        page.save(SAVE_MESSAGE)
                    except OtherPageSaveError:
                        print_to_console_and_log("Page "+page.title()+" caused OtherPageSaveError")
                    except pywikibot.exceptions.SpamblacklistError:
                        print_to_console_and_log("Page "+page.title()+" caused SpamblacklistError")

                #write to recent log    
                f.write(page.title()+'\n')

            i+=1
            #break #debugging
    write_run_time()
    write_to_archives_log(archives)
    #"""
