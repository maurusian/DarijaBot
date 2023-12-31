import requests
import pywikibot
from urllib.parse import unquote
from fuzzywuzzy import fuzz
from openpyxl import Workbook
import time, ast, os

pywikibot.config.put_throttle = 1

MAX_REQUESTS = 10

site = pywikibot.Site()

api_key = "AIzaSyAkTZCwc6Pihm_IGxiWiPn5DN2r4Pn0cUI"
cx_id = "f401aad12a40e4d66"

ary_base_url = "https://ary.wikipedia.org/wiki/"

ar_base_url = "https://ar.wikipedia.org/wiki/"

print(len(ary_base_url))


def get_page_creation_date(page):
    #page = pywikibot.Page(site, page_title)
    if not page.exists():
        return None
    # Fetch the earliest revision
    earliest_revision = page.oldest_revision
    timestamp = earliest_revision.timestamp
    return timestamp.strftime('%d-%m-%Y')

def string_similarity(str1, str2):
    return fuzz.ratio(str1, str2)

def fetch_google_results(keyword, api_key, cx_id):
    base_url = "https://www.googleapis.com/customsearch/v1"
    results = []

    for i in range(MAX_REQUESTS):  # 10 requests to get 100 results
        params = {
            'key': api_key,
            'cx': cx_id,
            'q': keyword,
            'start': i * 10 + 1
        }

        response = requests.get(base_url, params=params)
        print(response.status_code)
        #print(response.text)
        if response.status_code == 200:
            json_response = response.json()
            results.extend(json_response.get('items', []))
        #break

    return results

def is_same_ary_article(link, keyword):
    if link[:31] == ary_base_url:
        decoded_url = unquote(link)
        article_name = decoded_url.split('/')[-1].replace('_',' ')
        if keyword == article_name:
            return True
    return False


def is_same_ar_article(link, keyword):
    if link[:30] == ar_base_url:
        decoded_url = unquote(link)
        article_name = decoded_url.split('/')[-1].replace('_',' ')
        if keyword == article_name:
            return True
    return False

def get_arwiki_title(ary_page):
    #site_ar = pywikibot.Site("ar","wikipedia")
    for langlink in ary_page.iterlanglinks():
        try:
            if langlink.site.code == 'ar':
                return langlink.title
        except pywikibot.exceptions.UnknownSiteError:
            continue
    return None

def get_result_details(results, ary_page):
    keyword = ary_page.title()
    result_details = {"keyword":keyword}
    result_details["ary_creation_date"] = get_page_creation_date(ary_page)
    arabic_article_title = get_arwiki_title(ary_page)
    ary_flag = False
    ar_flag = False
    i = 1
    for entry in results:
        link = entry.get('link')
        if is_same_ary_article(link, keyword):
            result_details["arywiki-ranking"] = i
            ary_flag =  True
            i+=1
            continue

        if arabic_article_title is not None:
        
            if is_same_ar_article(link, arabic_article_title):
                result_details["arwiki-ranking"] = i
                result_details["similarity"] = string_similarity(keyword, arabic_article_title)
                ar_flag = True
                i+=1
                continue
            
        if ary_flag and ar_flag:
            break
        i+=1

    if "arywiki-ranking" not in result_details.keys():
        result_details["arywiki-ranking"] = ""
    if "arwiki-ranking" not in result_details.keys():
        result_details["arwiki-ranking"] = ""
    if "similarity" not in result_details.keys():
        result_details["similarity"] = ""
    if result_details["arywiki-ranking"] and result_details["arwiki-ranking"]:
        result_details["ar higher than ary"] = str(result_details["arwiki-ranking"] < result_details["arywiki-ranking"])
    elif result_details["arwiki-ranking"]:
        result_details["ar higher than ary"] = str(True)
    elif result_details["arywiki-ranking"] and arabic_article_title is not None:
        result_details["ar higher than ary"] = str(False)
    else:
        result_details["ar higher than ary"] = ""
        
    return result_details

def write_to_excel(data_list, filename):
    wb = Workbook()
    ws = wb.active

    if not data_list:
        return

    headers = list(data_list[0].keys())
    ws.append(headers)

    for row_dict in data_list:
        row = [row_dict[header] for header in headers]
        ws.append(row)

    wb.save(filename)

def check_ary_title(s):
    for char in s:
        if '\u0600' <= char <= '\u06FF' or char in ['پ', 'ڤ', 'ڭ', 'ݣ']:
            return True
    return False

def write_results_to_file(results):
    with open("temp.txt","w",encoding="utf-8") as f:
        f.write(str(results))

def write_exclusive_ary_results_to_file(results):
    with open("temp_excl.txt","w",encoding="utf-8") as f:
        f.write(str(results))

def load_exclusive_ary_dict_from_file():
    filename = "temp_excl.txt"
    if os.path.exists(filename):
        with open(filename, 'r', encoding="utf-8") as f:
            return ast.literal_eval(f.read())
    else:
        return []

def load_dict_from_file():
    filename = "temp.txt"
    if os.path.exists(filename):
        with open(filename, 'r', encoding="utf-8") as f:
            return ast.literal_eval(f.read())
    else:
        return []

def get_keywords(res):
    keywords = []
    for r in res:
        keywords.append(r["keyword"])

    return keywords

if __name__ == "__main__":
    #keyword = "جورج ويا"
    #page = pywikibot.Page(site,keyword)

    #print(get_page_creation_date(page))
    #"""
    all_pages = site.allpages(filterredir=False)
    pool_size = len(list(site.allpages(filterredir=False)))
    print("Pool size: ",pool_size)
    page_count = 1
    api_usage_count = 1
    all_results = load_dict_from_file()
    keywords  = get_keywords(all_results)
    exclusive_ary_results = load_exclusive_ary_dict_from_file()
    ary_keywords = get_keywords(exclusive_ary_results)
    """
    for page in all_pages:
        print(f"{page_count}/{pool_size}")
        title = page.title()
        if check_ary_title(title) and title not in keywords: #make sure the title contains ary characters, and has not been processed
            results = fetch_google_results(title, api_key, cx_id)
            if results is not None:
                all_results.append(get_result_details(results, page))
            api_usage_count+=1
            time.sleep(1)
        page_count+=1
        write_results_to_file(all_results)
        #if api_usage_count == 11:
        #    break
    """
    for i in range(len(all_results)):
        ary_title = all_results[i]["keyword"]
        if ary_title not in ary_keywords:
            ary_page = pywikibot.Page(site,ary_title)
            ar_title = get_arwiki_title(ary_page)
            #print(ar_title.title, type(ar_title))
            #break
            if ar_title is not None:
                #all_results[i]["similarity"] = string_similarity(ary_title, ar_title)
                continue
            else:
                keyword = ary_title
                ary_creation_date = all_results[i]["ary_creation_date"]
                results = fetch_google_results(keyword, api_key, cx_id)
                ary_wiki_ranking = ""
                i = 0
                for entry in results:
                    i+=1
                    link = entry.get('link')
                    if is_same_ary_article(link, keyword):
                        ary_wiki_ranking = i
                        break
                    
                        
                exclusive_ary_results.append({"keyword":keyword,"ary_creation_date":ary_creation_date,"ary_wiki_ranking":ary_wiki_ranking})
                write_exclusive_ary_results_to_file(exclusive_ary_results)
                #break
            
    if all_results is not None:
        write_to_excel(exclusive_ary_results, "exclusive_ary_results.xlsx")
    else:
        print("No results")
    #"""
