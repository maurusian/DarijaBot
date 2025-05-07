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


TO_ARY_MONTH_TAB = {
    'January': 'يناير', 'February': 'فبراير', 'March': 'مارس', 'April': 'أبريل', 'May': 'ماي',
    'June': 'يونيو', 'July': 'يوليوز', 'August': 'غشت', 'September': 'شتنبر', 'October': 'أكتوبر',
    'November': 'نونبر', 'December': 'دجنبر',

    'january': 'يناير', 'february': 'فبراير', 'march': 'مارس', 'april': 'أبريل', 'may': 'ماي',
    'june': 'يونيو', 'july': 'يوليوز', 'august': 'غشت', 'september': 'شتنبر', 'october': 'أكتوبر',
    'november': 'نونبر', 'december': 'دجنبر',

    'Janvier': 'يناير', 'Février': 'فبراير', 'Mars': 'مارس', 'Avril': 'أبريل', 'Mai': 'ماي',
    'Juin': 'يونيو', 'Juillet': 'يوليوز', 'Août': 'غشت', 'Aout': 'غشت', 'Septembre': 'شتنبر',
    'Octobre': 'أكتوبر', 'Novembre': 'نونبر', 'Decembre': 'دجنبر',

    'janvier': 'يناير', 'février': 'فبراير', 'mars': 'مارس', 'avril': 'أبريل', 'mai': 'ماي',
    'juin': 'يونيو', 'juillet': 'يوليوز', 'août': 'غشت', 'aout': 'غشت', 'septembre': 'شتنبر',
    'octobre': 'أكتوبر', 'novembre': 'نونبر', 'decembre': 'دجنبر',

    # Arabic (Levantine + Egyptian + Standard Arabic variants)
    'كانون الثاني': 'يناير',
    'شباط': 'فبراير',
    'آذار': 'مارس',
    'نيسان': 'أبريل',
    'أيار': 'ماي',
    'حزيران': 'يونيو',
    'تموز': 'يوليوز',
    'آب': 'غشت',
    'أيلول': 'شتنبر',
    'تشرين الأول': 'أكتوبر',
    'تشرين الثاني': 'نونبر',
    'كانون الأول': 'دجنبر',

    # Standard Arabic months
    'يناير':'يناير',
    'فبراير':'فبراير',
    'مارس':'مارس',
    'أبريل':'أبريل',
    'مايو': 'ماي',
    'يونيو': 'يونيو',
    'يوليو': 'يوليوز',
    'أغسطس': 'غشت',
    'سبتمبر': 'شتنبر',
    'أكتوبر': 'أكتوبر',
    'نوفمبر': 'نونبر',
    'ديسمبر': 'دجنبر',
    
}



def get_fixed_dates_ref(ref):
    print("get_fixed_dates_ref")
    ref_adj = ref
    regex_pattern = r"(\|\s*(date|accessdate|access-date|archive-date|archivedate)\s*=\s*\d{1,2}\s+[^\W\d_]+\s+\d{4})"
    matches = re.findall(regex_pattern, ref)
    print(matches)
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
        if 'url' in param_dict:
            url_from_webarchive = param_dict['url']
        else:
            url_from_webarchive = ''

        # Priority handling for archive-date and publication date
        if 'archive-date' in param_dict:
            archive_date = param_dict['archive-date']
        if 'date' in param_dict:
            if 'archive-date' not in param_dict:
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
            '{{Cite web',
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


def is_simple_reference(ref):
    # Define the regex pattern to match non-simple references
    non_simple_reference_pattern = r'<ref(?:\s+[^>]*)?>\{\{(?:Lien|Article|Ouvrage|Cite|Internetquelle|مرجع).*?\}\}<\/ref>'
    
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


def get_fixed_dates_ref(ref):
    print("get_fixed_dates_ref")
    ref_adj = ref

    # Find all date-like fields inside templates
    field_pattern = r"(\|\s*(date|accessdate|access-date|archive-date|archivedate)\s*=\s*[^|\n]*)"
    fields = re.findall(field_pattern, ref, re.DOTALL)

    for field in fields:
        full_match = field[0]  # the full "|param= value"
        #print(f"full_match: {full_match}")
        field_name = field[1]  # the param name like "date"
        #print(f"field_name: {field_name}")
        
        value = full_match.split('=', 1)[-1].strip()
        #print(f"value: {value}")

        # Try normal "day month year" first
        match_normal = re.match(r'^(\d{1,2})\s+([^\d\s,،]+)\s+(\d{4})$', value)
        #print(f"match_normal: {match_normal}")
        match_reverse = re.match(r'^([^\d\s,،]+)\s+(\d{1,2})[,،]?\s+(\d{4})$', value)
        #print(f"match_reverse: {match_reverse}")

        if match_normal:
            day_part = str(int(match_normal.group(1)))
            #print(f"day_part: {day_part}")
            month_part = match_normal.group(2)
            year_part = match_normal.group(3)

            if month_part in TO_ARY_MONTH_TAB.keys():
                new_value = f"{day_part} {TO_ARY_MONTH_TAB[month_part]} {year_part}"
                fixed_line = f"|{field_name}={new_value}"
                ref_adj = ref_adj.replace(full_match, fixed_line)

        elif match_reverse:
            month_part = match_reverse.group(1)
            day_part = str(int(match_reverse.group(2)))
            year_part = match_reverse.group(3)

            if month_part in TO_ARY_MONTH_TAB.keys():
                new_value = f"{day_part} {TO_ARY_MONTH_TAB[month_part]} {year_part}"
                fixed_line = f"|{field_name}={new_value}"
                ref_adj = ref_adj.replace(full_match, fixed_line)

    return ref_adj

#import re
#from urllib.parse import urlparse

def fix_website_field(ref):
    print("fix_website_field")
    ref_adj = ref

    website_pattern = r"(\|\s*website\s*=\s*[^|\n]*)"
    websites = re.findall(website_pattern, ref, re.DOTALL)

    for full_match in websites:
        value = full_match.split('=', 1)[-1].strip()

        # If the value looks like a full URL
        if value.startswith('http://') or value.startswith('https://'):
            parsed_url = urlparse(value)
            domain = parsed_url.netloc

            # Safety cleanup: remove "www." if present
            if domain.startswith('www.'):
                domain = domain[4:]

            fixed_line = f"|website={domain}"
            ref_adj = ref_adj.replace(full_match, fixed_line)

    return ref_adj


test_input = """<ref>{{مرجع ويب
|url=https://www.lesinrocks.com/cinema/gad-elmaleh-in-gad-we-trust-90970-30-01-2001/
|title=Gad Elmaleh - In Gad we trust - Les Inrocks
|website=https://www.lesinrocks.com/
|language=fr-FR
|accessdate=2023-06-06
|archive-url=https://web.archive.org/web/20230606104403/https://www.lesinrocks.com/cinema/gad-elmaleh-in-gad-we-trust-90970-30-01-2001/
|archive-date=2023-06-06
|url-status=live
}}</ref> """

'''
test_input="""<ref>, Charles W. Furlong ,1911 ,September , The French Conquest Of Morocco: The Real Meaning Of The International Trouble, World's Work
|The World's Work: A History of Our Time, المجلد XXII, صفحات=14988–14999, تاريخ الوصول: 2009-07-10 {{Webarchive
|url=https://books.google.com/books?id=rHAAAAAAYAAJ&pg=RA1-PA14988
|archive-url=https://web.archive.org/web/20170106064208/20170106064208/https://books.google.com/books?id=rHAAAAAAYAAJ&pg=RA1-PA14988
|archive-date=6 يناير 2017
|date=06 يناير 2017
}}</ref>"""
'''

from pprint import pprint

# Assume the previous function fix_wiki_ref_tag is already defined
#fixed_output = fix_access_date_in_ref(fix_url_and_title_in_ref(fix_webarchive_in_ref(test_input)))

fixed_output = fix_website_field(test_input)

print("Original Input:")
print(test_input)
print("\nFixed Output:")
print(fixed_output)

