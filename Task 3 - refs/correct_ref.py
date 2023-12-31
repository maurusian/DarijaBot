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

def is_simple_reference(ref):
    # Define the regex pattern to match non-simple references
    non_simple_reference_pattern = r'<ref>\{\{(?:Cite|مرجع).*?\}\}<\/ref>'
    
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

if __name__ =="__main__":

    site = pywikibot.Site()

    #page = pywikibot.Page(site,title)

    #refs = list(re.findall(REF_PATTERN, page.text,re.DOTALL))

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
        print(archives)
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
                            new_ref = get_simple_ref_part(ref_adj)

                            
                            if new_ref is not None:
                            
                                tmp_text = tmp_text.replace(ref,new_ref) #to be tested
                        else:
                            ref_adj = get_textual_fixed_ref(ref)

                            ref_adj = get_fixed_keywords_ref(ref_adj)
                                
                            ref_adj = get_fixed_dates_ref(ref_adj)

                            ref_adj, archives = fix_ref_archive_location(ref_adj,archives)

                            #print("fixed dates", ref_adj)

                            ref_adj, archives = get_ref_with_archive(ref_adj,archives)

                            #print("added archive url", ref_adj)
                            ref_adj = ref_adj.replace("}}\n</ref>","}}</ref>") #bug fix
                            tmp_text = tmp_text.replace(ref,ref_adj)

                        
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
