import pywikibot

MAIN_QUERY_FILENAME = "./data/query_items.sparql"

ITEM_TYPES = {'year':'Q577','decade':'Q39911'}

def get_data(item_type_id):
    with open(MAIN_QUERY_FILENAME,'r') as f:
        query = f.read().replace('{item_type_id}',item_type_id)

    url = "https://darijabot@query.wikidata.org/sparql?query=%s&format=json" % quote(query)
    #headers are necessary, without user-agent the Wikidata server refuses to connect, and without the charset ensues a Unicode error
    headers = {
        'User-Agent': 'DarijaBot/0.1 (Edition Windows 10 Home, Version 20H2, OS build 19042.1165, Windows Feature Experience Pack 120.2212.3530.0) Python3.9.0',
        'Content-Type': 'text/text; charset=utf-8'
    }
    response = requests.get(url, headers=headers)
    res      = response.json()
    if response is not None:
        #res = json.loads(response)
        res      = response.json()
        return res
    else:
        return {}
        


def get_item_id(title,lang):
    pass



for i in range(2,11):
    en_title = "Category:AD"+str(i)
    ary_title = "تصنيف:"+str(i)
    print(get_data(ITEM_TYPES['year']))
    #get item ID, using en_title and fixed query
    break
    item_id = None
    repo = site.data_repository()
    site_en = pywikibot.Site('en','wikipedia')
    page = pywikibot.Page(site_en, en_title)
    print(page.getID())
    #item = pywikibot.ItemPage(repo, item_id)
    site_ary = pywikibot.Site('ary','wikipedia')
    page = pywikibot.Page(site_ary, ary_title)
    item.setSitelink(page, summary=u'Setting sitelink.')
    
    
