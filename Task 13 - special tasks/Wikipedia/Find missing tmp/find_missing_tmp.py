import requests
import pywikibot

def get_templates_starting_with(s):
    base_url = "https://ary.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "allpages",
        "apprefix": s,
        "apnamespace": 10,  # This is the namespace for templates
        "aplimit": 500,  # Maximum number of pages to return
        "apfilterredir": "nonredirects",  # Exclude redirects
    }

    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        print(f"Failed to get data from API")
        return None

    data = response.json()

    template_titles = [page["title"] for page in data["query"]["allpages"]]

    return template_titles

s = "إقليم"  # replace with your actual prefix
template_titles = set(get_templates_starting_with(s))

site = pywikibot.Site()

cat = "تصنيف:موضيلات أقاليم لمغريب"

compare_to_tmp_titles = set([page.title() for page in pywikibot.Category(site,cat).articles()])

sym_diff = template_titles.symmetric_difference(compare_to_tmp_titles)

print(len(sym_diff))

for title in sym_diff:
    print(title)
