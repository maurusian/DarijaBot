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
'''

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
