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

TO_ARY_MONTH_TAB = {'January':'يناير'
                   ,'February':'فبراير'
                   ,'March':'مارس'
                   ,'April':'أبريل'
                   ,'May':'ماي'
                   ,'June':'يونيو'
                   ,'July':'يوليوز'
                   ,'August':'غشت'
                   ,'September':'شتنبر'
                   ,'October':'أكتوبر'
                   ,'November':'نونبر'
                   ,'December':'دجنبر'
                   ,'january':'يناير'
                   ,'february':'فبراير'
                   ,'march':'مارس'
                   ,'april':'أبريل'
                   ,'may':'ماي'
                   ,'june':'يونيو'
                   ,'july':'يوليوز'
                   ,'august':'غشت'
                   ,'september':'شتنبر'
                   ,'october':'أكتوبر'
                   ,'november':'نونبر'
                   ,'december':'دجنبر'
                   ,'Janvier':'يناير'
                   ,'Février':'فبراير'
                   ,'Mars':'مارس'
                   ,'Avril':'أبريل'
                   ,'Mai':'ماي'
                   ,'Juin':'يونيو'
                   ,'Juillet':'يوليوز'
                   ,'Août':'غشت'
                   ,'Aout':'غشت'
                   ,'Septembre':'شتنبر'
                   ,'Octobre':'أكتوبر'
                   ,'Novembre':'نونبر'
                   ,'Decembre':'دجنبر'
                   ,'janvier':'يناير'
                   ,'février':'فبراير'
                   ,'mars':'مارس'
                   ,'avril':'أبريل'
                   ,'mai':'ماي'
                   ,'juin':'يونيو'
                   ,'juillet':'يوليوز'
                   ,'août':'غشت'
                   ,'aout':'غشت'
                   ,'septembre':'شتنبر'
                   ,'octobre':'أكتوبر'
                   ,'novembre':'نونبر'
                   ,'decembre':'دجنبر'
                   ,'كانون الثاني':''
                   ,'شباط':'فبراير'
                   ,'آذار':'مارس'
                   ,'نيسان':'أبريل'
                   ,'أيار':'ماي'
                   ,'تموز':'يونيو'
                   ,'آب':'يوليوز'
                   ,'حزيران':'غشت'
                   ,'أيلول':'شتنبر'
                   ,'تشرين الأول':'أكتوبر'
                   ,'تشرين الثاني':'نونبر'
                   ,'كانون الأول':'دجنبر'
                   ,'مايو':'ماي'
                   ,'يوليو':'يوليوز'
                   ,'أغسطس':'غشت'
                   ,'سبتمبر':'شتنبر'
                   ,'نوفمبر':'نونبر'
                   ,'ديسمبر':'دجنبر'
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
    non_simple_reference_pattern = r'<ref>\{\{(?:Lien|Article|Ouvrage|Cite|Internetquelle|مرجع).*?\}\}<\/ref>'
    
    # Check if the reference matches the non-simple pattern
    if re.search(non_simple_reference_pattern, ref, re.IGNORECASE):
        return False
    
    # If the reference does not match the non-simple pattern,
    # check if it matches the simple reference pattern
    simple_reference_pattern = r'<ref>(.*?)<\/ref>'
    match = re.search(simple_reference_pattern, ref)
    
    # If a match is found, it's a simple reference
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

        if url:
            title = ref_part[0].replace('<','').replace('[','').replace('>','').replace(']','').replace(url,'').strip()

            value = ref.replace(ref_part[0],'>'+CITE_WEB_PATTERN.replace('{url}',url).replace('{title}',title)+'<')

            #print(value)
            return value
    else:
        if 'http' in ref:
            url = ref.replace('<ref>','').replace('</ref>','').strip()
            title = get_title_from_url(url)
            if not title:
                title = get_website_name(url)
                
            return '<ref>'+CITE_WEB_PATTERN.replace('{url}',url).replace('{title}',title)+'</ref>'
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


def get_fixed_dates_ref(ref):
    print("get_fixed_dates_ref")
    ref_adj = ref
    regex_pattern = r"(\|\s*(date|accessdate|access-date|archive-date|archivedate)\s*=\s*\d{1,2}\s+[a-zA-Z]+\s+\d{4})"
    matches = re.findall(regex_pattern, ref)
    for match in matches:
        #print(match) #for debugging
        date = match[0] #.group(1)
        month_name = re.sub(r"[0-9\s]", "", date.split('=')[-1])
        #print(month_name) #for debugging
        if month_name in TO_ARY_MONTH_TAB.keys():
            ary_date = date.replace(month_name,TO_ARY_MONTH_TAB[month_name])
            ref_adj = ref_adj.replace(date,ary_date)
        #ref_adj = re.sub(regex_pattern, replace_month, ref_adj)
    return ref_adj


def extract_last_archive_url(html_text,url):
    # The regular expression pattern to find archive URLs in the HTML content
    pattern = re.compile(r"https://web\.archive\.org/web/\d+/http[s]?://[^\s\"'<]+")
    
    # Find all archive URLs
    archive_urls = re.findall(pattern, html_text)
    
    # Get the last archive URL
    last_archive_url = None
    for archive_url in archive_urls:
        if url in archive_url:
            last_archive_url = archive_url
            break
        
    
    return last_archive_url


def get_date_from_archive_timestamp(timestamp):
    timestamp_str = timestamp[:8]  # Take only the YYYYMMDD part
    archive_date = datetime.strptime(timestamp_str, "%Y%m%d").strftime("%d %B %Y").lstrip("0")

    month = archive_date.split(' ')[1]

    archive_date = archive_date.replace(month,TO_ARY_MONTH_TAB[month])

    return archive_date

def get_date_from_archive_url(archive_url):
    pattern = re.compile(r"/web/(\d{14})/")
    #print(archive_url)
    match = re.search(pattern, str(archive_url))
    if match:
        timestamp_str = match.group(1)
        return get_date_from_archive_timestamp(timestamp_str)
    
    else:
        return None

def fetch_from_archive(url):
    archive_url = f"https://web.archive.org/web/{url}"
    try:
        response = requests.get(archive_url)
        
        if response.status_code == 200:
            archiving_date = response.headers.get('X-Archive-Orig-date', 'Unknown date')
            archive_url = extract_last_archive_url(response.text,url)
            if archive_url:
                archiving_date = get_date_from_archive_url(archive_url)
                return archive_url, archiving_date
    except requests.exceptions.TooManyRedirects:
        print("Error retrieving response for archive url")
    return None, None

def fetch_from_archive2(url):
    try:
        # Construct the URL for the Wayback Machine API
        api_url = f"http://archive.org/wayback/available?url={url}"

        # Send a GET request to the API
        response = requests.get(api_url)
        data = response.json()

        # Check if the response contains archived URLs
        if 'archived_snapshots' in data:
            archived_snapshots = data['archived_snapshots']
            if 'closest' in archived_snapshots:
                closest_snapshot = archived_snapshots['closest']
                archive_url = closest_snapshot['url']
                archiving_date = get_date_from_archive_timestamp(closest_snapshot['timestamp'])
                return archive_url, archiving_date

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving data from the Wayback Machine API: {str(e)}")

    return None, None

def has_archive_url(ref):
    pattern = re.compile(r'archive-url\s*=\s*(https?://[^\s"\']+|www\.[^\s"\']+)')
    pattern2 = re.compile(r'archiveurl\s*=\s*(https?://[^\s"\']+|www\.[^\s"\']+)')
    return bool(re.search(pattern, ref)) or bool(re.search(pattern2, ref))

def extract_url_from_wiki_ref(ref):
    pattern = re.compile(r'\|\s*url\s*=\s*(https?://[^\s"\']+|www\.[^\s"\']+)')
    match = re.search(pattern, ref)
    return match.group(1) if match else None

def extract_archive_url_from_wiki_ref(ref):
    pattern = re.compile(r'\|\s*archive-url\s*=\s*(https?://[^\s"\']+|www\.[^\s"\']+)')
    match = re.search(pattern, ref)
    if match:
        return match.group(1)
    else:
        pattern = re.compile(r'\|\s*archiveurl\s*=\s*(https?://[^\s"\']+|www\.[^\s"\']+)')
        match = re.search(pattern, ref)
        if match:
            return match.group(1)
    return None

def get_ref_with_archive(ref, archives):
    print("get_ref_with_archive")
    ref_adj = ref
    #print("extract_url_from_wiki_ref") #for debugging
    url = extract_url_from_wiki_ref(ref_adj)
    if url is not None:
        #print("url is not None")
        if not has_archive_url(ref_adj):
            if url in archives.keys():
                archive_url = archives[url]
                archiving_date =  get_date_from_archive_url(archive_url)
            else:
                #print("does not have archive url")
                archive_url, archiving_date = fetch_from_archive2(url)
                archives[url] = archive_url
            if archive_url is not None and archiving_date is not None:
                ref_adj = ref_adj.replace('}}','|archive-url='+archive_url+'\n'+'|archive-date='+archiving_date+'}}')
        else:
            #print("has archive url")
            if url not in archives.keys():
                archive_url = extract_archive_url_from_wiki_ref(ref)
                if archive_url:
                    archives[url] = archive_url
    return ref_adj, archives


def fix_ref_archive_location(ref,archives):
    ref_adj = ref
    url_match = extract_url_from_wiki_ref(ref_adj)
    print("fix_ref_archive_location")
    if url_match and not has_archive_url(ref):
        url_pattern = r'(\|\s*url\s*=\s*)(https?://(?:web\.archive\.org/web/|www\.web\.archive\.org/web/)(\d+)/)([^|\n]+)'
        archive_url = None
        def replacer(match):
            url_label, archive_prefix, archive_date, original_url = match.groups()
            #print(get_date_from_archive_url(url_match))
            if archive_date:
                archive_url=f"{archive_prefix}{archive_date}/{original_url}"
            return f"{url_label}{original_url}\n|archive-url={archive_prefix}{archive_date}/{original_url}\n|archive-date={get_date_from_archive_url(url_match)}"
        
        ref_adj = re.sub(url_pattern, replacer, ref_adj)
        if archive_url:
            archives = update_archive(archives,url_match,archive_url)
    return ref_adj,archives

def update_archive(archives,url,archive_url):
    archives[url]=archive_url
    return archives

def write_to_archives_log(archives):
    filename = "archive_log.txt"
    with open(filename,"w",encoding="utf-8") as arc:
        for url, archive_url in archives.items():
            arc.write(f"{url};{archive_url}\n")

def load_archive_log():
    filename = "archive_log.txt"
    archives = {}
    with open(filename,"r",encoding="utf-8") as arc:
        for i,line in enumerate(arc):
            spliline = line.strip().split(';')
            archives[spliline[0]]=spliline[1]
    return archives

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

def fix_broken_link_tag(broken_link_tag):
    fixed_broken_link_tag = broken_link_tag
    regex_pattern = r"(\|\s*(date)\s*=\s*[a-zA-Z]+\s+\d{4})"
    match = re.search(regex_pattern, ref)  # This returns a Match object for the first match or None if no match is found

    if match:
        date = match[0]  # or match.group(1) if 'match' captures the date in a group
        month_name = re.sub(r"[0-9\s]", "", date.split('=')[-1]).strip()
        if month_name in TO_ARY_MONTH_TAB.keys():
            ary_date = date.replace(month_name, TO_ARY_MONTH_TAB[month_name])
            fixed_broken_link_tag = fixed_broken_link_tag.replace(date, ary_date)
    return fixed_broken_link_tag


#import re
###############Fixing webarchive template issue

def fix_webarchive_in_ref(ref_text):
    ref_content = re.search(r'<ref(?:\s+[^>]*)?>(.*?)<\/ref>', ref_text, re.DOTALL)
    if not ref_content:
        return ref_text

    ref_inner = ref_content.group(1)

    # Remove the Webarchive template entirely first
    webarchive_match = re.search(r'{{Webarchive(.*?)}}', ref_inner, re.DOTALL)
    archive_url = None
    archive_date = None

    if webarchive_match:
        webarchive_content = webarchive_match.group(1)

        archive_params = extract_params(webarchive_content)
        archive_url = archive_params.get('url')
        archive_date = archive_params.get('date')

        # Now remove the full Webarchive template including its braces
        ref_inner = re.sub(r'{{Webarchive.*?}}', '', ref_inner, flags=re.DOTALL)

    # Remove any leftover closing }}
    ref_inner = re.sub(r'}}\s*', '', ref_inner)

    # Now process the main Cite web template
    main_template_match = re.search(r'{{Cite web(.*)', ref_inner, re.DOTALL)
    if not main_template_match:
        return ref_text

    main_template_content = main_template_match.group(1)

    params = extract_params(main_template_content)

    # Inject archive-url and archive-date if found
    if archive_url:
        params['archive-url'] = archive_url
    if archive_date:
        params['archive-date'] = archive_date

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
    new_cite_web = '{{Cite web\n'
    for key, value in final_params.items():
        new_cite_web += f'|{key}={value}\n'
    new_cite_web += '}}'

    # Replace the old Cite web template inside
    ref_inner_replaced = re.sub(r'{{Cite web.*', new_cite_web, ref_inner, flags=re.DOTALL)

    # Rebuild the full <ref> tag
    result = f'{ref_open}{ref_inner_replaced}</ref>'

    return result

######import re

def fix_url_and_title_in_ref(ref_text):
    ref_content = re.search(r'<ref(?:\s+[^>]*)?>(.*?)<\/ref>', ref_text, re.DOTALL)
    if not ref_content:
        return ref_text

    ref_inner = ref_content.group(1)

    # Remove any leftover closing }}
    ref_inner = re.sub(r'}}\s*', '', ref_inner)

    # Find main Cite web template
    main_template_match = re.search(r'{{Cite web(.*)', ref_inner, re.DOTALL)
    if not main_template_match:
        return ref_text

    main_template_content = main_template_match.group(1)

    params = extract_params(main_template_content)

    if 'url' in params:
        url_value = params['url']
        match_url = re.match(r'(.*)?\[(https?://[^\s]+)\s([^\]]+)\](.*)', url_value)
    if match_url:
        pre_text, real_url, link_text, post_text = match_url.groups()
        params['url'] = real_url.strip()
        combined_title = ''
        if pre_text and pre_text.strip():
            combined_title += pre_text.strip() + ' - '
        combined_title += link_text.strip()
        if post_text and post_text.strip():
            combined_title += ' - ' + post_text.strip()
        # Always replace or create title
        params['title'] = combined_title

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
    new_cite_web = '{{Cite web\n'
    for key, value in final_params.items():
        new_cite_web += f'|{key}={value}\n'
    new_cite_web += '}}'

    # Replace the old Cite web template inside
    ref_inner_replaced = re.sub(r'{{Cite web.*', new_cite_web, ref_inner, flags=re.DOTALL)

    # Rebuild the full <ref> tag
    result = f'{ref_open}{ref_inner_replaced}</ref>'

    return result

#################import re

def fix_access_date_in_ref(ref_text):
    # Patterns to detect access-date text inside title
    access_date_patterns = [
        r'وصل لهذا المسار في (\d{1,2} [^\s]+ \d{4})',
        r'accessed on (\d{1,2} [^\s]+ \d{4})',
        # Add more patterns if needed
    ]

    ref_content = re.search(r'<ref(?:\s+[^>]*)?>(.*?)<\/ref>', ref_text, re.DOTALL)
    if not ref_content:
        return ref_text

    ref_inner = ref_content.group(1)

    # Remove any leftover closing }}
    ref_inner = re.sub(r'}}\s*', '', ref_inner)

    # Find main Cite web template
    main_template_match = re.search(r'{{Cite web(.*)', ref_inner, re.DOTALL)
    if not main_template_match:
        return ref_text

    main_template_content = main_template_match.group(1)

    params = extract_params(main_template_content)

    # Only operate if there is a title
    if 'title' in params and params['title']:
        title = params['title']

        for pattern in access_date_patterns:
            match = re.search(pattern, title)
            if match:
                found_date = match.group(1)
                # Remove the matched text from title
                title = re.sub(pattern, '', title).strip()
                # Update title
                params['title'] = title
                # Only add access-date if not already present
                if 'access-date' not in params:
                    params['access-date'] = found_date
                break  # Only apply the first matching pattern

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
    new_cite_web = '{{Cite web\n'
    for key, value in final_params.items():
        new_cite_web += f'|{key}={value}\n'
    new_cite_web += '}}'

    # Replace the old Cite web template inside
    ref_inner_replaced = re.sub(r'{{Cite web.*', new_cite_web, ref_inner, flags=re.DOTALL)

    # Rebuild the full <ref> tag
    result = f'{ref_open}{ref_inner_replaced}</ref>'

    return result

#import re
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
    main_template_match = re.search(r'{{Cite web(.*)', ref_inner, re.DOTALL)
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
    new_cite_web = '{{Cite web\n'
    for key, value in final_params.items():
        new_cite_web += f'|{key}={value}\n'
    new_cite_web += '}}'

    # Replace the old Cite web template inside
    ref_inner_replaced = re.sub(r'{{Cite web.*', new_cite_web, ref_inner, flags=re.DOTALL)

    # Rebuild the full <ref> tag
    result = f'{ref_open}{ref_inner_replaced}</ref>'

    return result

if __name__ =="__main__":

    site = pywikibot.Site()
    site.throttle.maxdelay = 0
    site.login()

    #page = pywikibot.Page(site,title)

    #refs = list(re.findall(REF_PATTERN, page.text,re.DOTALL))

    test_title = "هواية د راديو" #"لمتحف ليهودي لمغريبي"
    load_from_cat_name = "" #"تصنيف:أرتيكلات فيهوم موشكيل بسباب عطاشة 3.1"
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
                        
                        if is_simple_reference(ref):
                            new_ref = get_simple_ref_part(ref)

                            
                            if new_ref is not None:
                                #fix issues introduced by naive implementation of get_simple_ref_part, due to "webarchive" template
                                new_ref = fix_webarchive_in_ref(new_ref)
                                new_ref = fix_url_and_title_in_ref(new_ref)
                                new_ref = fix_access_date_in_ref(new_ref)
                                new_ref = fix_empty_title(new_ref)
                                
                                tmp_text = tmp_text.replace(ref,new_ref) #to be tested

                                
                                
                        else:
                            new_ref = get_textual_fixed_ref(ref)

                            new_ref = get_fixed_keywords_ref(new_ref)
                                
                            new_ref = get_fixed_dates_ref(new_ref)

                            #fix issues introduced by naive implementation of get_simple_ref_part, due to "webarchive" template
                            new_ref = fix_webarchive_in_ref(new_ref)
                            new_ref = fix_url_and_title_in_ref(new_ref)
                            new_ref = fix_access_date_in_ref(new_ref)
                            new_ref = fix_empty_title(new_ref)
                            

                            #new_ref, archives = fix_ref_archive_location(new_ref,archives)

                            #print("fixed dates", new_ref)

                            #new_ref, archives = get_ref_with_archive(new_ref,archives)

                            #print("added archive url", new_ref)
                            new_ref = new_ref.replace("}}\n</ref>","}}</ref>") #bug fix
                            tmp_text = tmp_text.replace(ref,new_ref)

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
