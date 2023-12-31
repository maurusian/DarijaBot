import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_article_titles(lang):
    search_url = "https://"+lang+".wikipedia.org/w/index.php?title=Special:search&limit=500&ns0=1&offset=0&profile=default&search=-insource%3A%3Cref%3E"
    #search_url = base_url + search_title

    response = requests.get(search_url)

    if response.status_code != 200:
        print(f"Failed to get page: {search_url}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    divs = soup.find_all('div', class_='mw-search-result-heading')

    titles = [div.find('a').get('title') for div in divs]

    return titles

def save_to_excel(titles, file_name):
    df = pd.DataFrame(titles, columns=["Article Titles"])
    df.to_excel(file_name, index=False)
    print(f"Titles saved to {file_name}")

#search_title = "Search_page_title"  # replace with your actual search page title
lang = "kn"
file_name = "article_titles"+lang+".xlsx"  # replace with your desired file name

titles = get_article_titles(lang)
if titles is not None:
    save_to_excel(titles, file_name)
