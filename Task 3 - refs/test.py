import pywikibot
import re
#from arywikibotlib import *
from bs4 import BeautifulSoup

REF_PATTERN1 = r"<ref>.+?</ref>"
REF_PATTERN2 = r"<ref name\=.+?>.+?</ref>"
REF_PATTERN3 = r"<ref name=.+?/?>"
#LINK_PATTERN = r"\[(.+)]\]"
SIMPLE_REF_PATTERN = r">[\n|\s]*\[http.+?\][\n|\s]*<"
LINK_PATTERN = r"\[(\d+)\]"

CITE_WEB_PATTERN = """{{Cite web
|url={url}
|title={title}
}}
"""

#title = "مستخدم:Ideophagous/تيران د رملة"
title='آلبرخت دورر'

PARAM_VALUE_PATTERN = r'\[\[.+?\|.+?(?=/\n|)'
PARAM_VALUE_PATTERN2 = r'\{\{.+?(?=/\n)'

SIMPLE_BOOK_PATTERN = """{{Cite book
|title={title}
|isbn={isbn}
}}
"""

site = pywikibot.Site()

page = pywikibot.Page(site,title)

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
    raw_isbn = ref.split('{{ISBN')[1].split('}}')[0]

    remainder_text = ref.replace('{{ISBN'+raw_isbn+'}}','').replace('</ref>','').strip().strip('.').strip()

    remainder_text = re.sub('<ref.+?>','',remainder_text)

    return SIMPLE_BOOK_PATTERN.replace('{title}',remainder_text).replace('{isbn}',raw_isbn.strip())
    

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

#import re

def fix_webarchive_in_ref(ref_text):
    ref_content = re.search(r'<ref>(.*?)<\/ref>', ref_text, re.DOTALL)
    if not ref_content:
        return ref_text

    ref_inner = ref_content.group(1)

    # Remove the Webarchive template entirely first
    webarchive_match = re.search(r'{{Webarchive(.*?)}}', ref_inner, re.DOTALL)
    archive_url = None
    archive_date = None

    if webarchive_match:
        webarchive_content = webarchive_match.group(1)

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
    result = '<ref>{{Cite web\n'
    for key, value in final_params.items():
        result += f'|{key}={value}\n'
    result += '}}</ref>'

    return result

######import re

def fix_url_and_title_in_ref(ref_text):
    ref_content = re.search(r'<ref>(.*?)<\/ref>', ref_text, re.DOTALL)
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

    if 'url' in params:
        url_value = params['url']
        match_url = re.match(r'\[(https?://[^\s]+)\s([^\]]+)\](.*)', url_value)
        if match_url:
            real_url, link_text, extra_text = match_url.groups()
            params['url'] = real_url.strip()
            combined_title = link_text.strip()
            if extra_text.strip():
                combined_title += ' - ' + extra_text.strip()
            # Always replace or create title
            params['title'] = combined_title

    # Final cleaning: no empty params
    final_params = {}
    for k, v in params.items():
        if v.strip():
            final_params[k] = v.strip()

    # Rebuild the ref
    result = '<ref>{{Cite web\n'
    for key, value in final_params.items():
        result += f'|{key}={value}\n'
    result += '}}</ref>'

    return result

#################import re

def fix_access_date_in_ref(ref_text):
    # Patterns to detect access-date text inside title
    access_date_patterns = [
        r'وصل لهذا المسار في (\d{1,2} [^\s]+ \d{4})',
        r'accessed on (\d{1,2} [^\s]+ \d{4})',
        # Add more patterns if needed
    ]

    ref_content = re.search(r'<ref>(.*?)<\/ref>', ref_text, re.DOTALL)
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
    result = '<ref>{{Cite web\n'
    for key, value in final_params.items():
        result += f'|{key}={value}\n'
    result += '}}</ref>'

    return result

                
'''
refs = get_ref_list(page)
#print(len(refs))

#print(refs)

for ref in refs:
    #print(ref)
    #print(get_simple_ref_part(ref))
    """
    fixed_ref = ref.replace('\n',' ').replace('  ',' ').replace('\n|','|').replace('|','\n|').replace('\n}}','}}').replace('}}','\n}}').replace('\n</ref>','</ref>').replace('</ref>','\n</ref>')
    fixed_ref = re.sub(r" *= *","=",fixed_ref)
    fixed_ref = re.sub(r" *\| *","|",fixed_ref)
    new_ref = fixed_ref
    ref_parts = fixed_ref.split('=')[1:] #[pv.split('|')[0] for pv in fixed_ref.split('=')]
    
    #param_values = []
    #print(param_values)
    for ref_part in ref_parts:
        if ']]' in ref_part:
            param_value = ref_part.split(']]')[0]
            new_param_value = param_value.replace('\n','').strip()
            new_param_value = re.sub(r" *\| *","|",new_param_value)
            new_ref = new_ref.replace(param_value,new_param_value)
    """

    
    #print(ref)
    if '{{ISBN' in ref.upper():
        ref_parts = ref.split('{{ISBN')
        print(get_simple_book_ref(ref))
    #print(ref.replace('\n|','|'))
    #print(ref.replace('|','\n|'))
    #break
    """
    links = re.search(LINK_PATTERN, ref)
    if links is not None:
        print(links.groups())

    """


def is_simple_reference(reference_text):
    # Define the regex pattern to match non-simple references
    non_simple_reference_pattern = r'<ref>\{\{(?:Cite|مرجع).*?\}\}<\/ref>'
    
    # Check if the reference matches the non-simple pattern
    if re.search(non_simple_reference_pattern, reference_text, re.IGNORECASE):
        return False
    
    # If the reference does not match the non-simple pattern,
    # check if it matches the simple reference pattern
    simple_reference_pattern = r'<ref>(.*?)<\/ref>'
    match = re.search(simple_reference_pattern, reference_text)
    
    # If a match is found, it's a simple reference
    return bool(match)


# Test the function with sample reference texts
reference1 = "<ref>Simple reference</ref>"
reference2 = "{{Cite book|title=Book Title|author=Author}} Some text"
reference3 = "{{مرجع|عنوان=عنوان الكتاب|مؤلف=المؤلف}} بعض النص"
reference4 = "<ref>Another simple reference</ref>"
reference5 = "{{Cite journal|title=Journal Title|author=Author}} Some text"

print(is_simple_reference(reference1))  # True
print(is_simple_reference(reference2))  # False
print(is_simple_reference(reference3))  # False
print(is_simple_reference(reference4))  # True
print(is_simple_reference(reference5))  # False
'''

import requests
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


test_input = """<ref>{{Cite web
|url=[https://www.hespress.com/%d8%a7%d9%84%d9%85%d8%aa%d8%ad%d9%81-%d8%a7%d9%84%d9%8a%d9%87%d9%88%d8%af%d9%8a-%d8%a8%d8%a7%d9%84%d8%a8%d9%8a%d8%b6%d8%a7%d8%a1-%d8%b0%d8%a7%d9%83%d8%b1%d8%a9-%d8%a7%d9%84%d8%aa%d8%b3%d8%a7%d9%85-225537.html المتحف اليهودي بالبيضاء .. ذاكرة التسامح الديني بالمغرب] صحيفة هسبريس. وصل لهذا المسار في 18 مايو 2016 {{Webarchive
|url=https://web.archive.org/web/20230605094803/https://www.hespress.com/%D8%A7%D9%84%D9%85%D8%AA%D8%AD%D9%81-%D8%A7%D9%84%D9%8A%D9%87%D9%88%D8%AF%D9%8A-%D8%A8%D8%A7%D9%84%D8%A8%D9%8A%D8%B6%D8%A7%D8%A1-%D8%B0%D8%A7%D9%83%D8%B1%D8%A9-%D8%A7%D9%84%D8%AA%D8%B3%D8%A7%D9%85-225537.html
|date=2023-06-05
}}
|title=
}}</ref>"""

test_input="""<ref name="صحيفة الشرق الأوسط">[http://archive.aawsat.com/details.asp?section=54&issueno=12764&article=749494#.VzxzVDUrJdg المتحف اليهودي في الدار البيضاء.. الوحيد في العالم العربي ومحافظته مسلمة] صحيفة الشرق الأوسط، 8 نوفمبر 2013. وصل لهذا المسار في 18 مايو 2016 {{Webarchive
|url=https://archive.aawsat.com/details.asp?section=54&issueno=12764&article=749494
|archive-url=https://web.archive.org/web/20191204155725/20191204155725/https://archive.aawsat.com/details.asp?section=54&issueno=12764&article=749494
|archive-date=4 دجنبر 2019
|date=4 ديسمبر 2019
}}</ref>"""

test_input="""<ref name="laselki.net">{{Cite web
|url=http://laselki.net/aboutus.html
|accessdate=2020-07-23
|archive-date=2020-01-16
|archive-url=https://web.archive.org/web/20200116014137/http://www.laselki.net/aboutus.html
|url-status=
}}</ref>"""

from pprint import pprint

# Assume the previous function fix_wiki_ref_tag is already defined
#fixed_output = fix_access_date_in_ref(fix_url_and_title_in_ref(fix_webarchive_in_ref(test_input)))

fixed_output = fix_empty_title(test_input)

print("Original Input:")
print(test_input)
print("\nFixed Output:")
print(fixed_output)

