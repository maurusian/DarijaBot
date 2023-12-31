import pywikibot
from pywikibot.exceptions import NoPageError
#from pywikibot import pagegenerators

# main topic template
TEMPLATE_NAME = "مقالة تصنيف"

def add_main_topic_to_cat(cat_page, target_item):
    target_article = target_item.sitelinks['arywiki']
    if target_article == cat_page.title(with_ns=False):
        new_text = f"{{{{{TEMPLATE_NAME}}}}}\n" + cat_page.text
    else:
        new_text = f"{{{{{TEMPLATE_NAME}|{str(target_article).strip(']').strip('[')}}}}}\n" + cat_page.text

    return new_text

def main():
    site = pywikibot.Site("ary", "wikipedia")
    cat_namespace = 14
    pool = site.allpages(namespace=cat_namespace)
    pool_size = len(list(site.allpages(namespace=cat_namespace)))

    print("Pool size: ",pool_size)
    i = 0

    for page in pool:
        i+=1
        print("****** processing cat: ",f"{str(i)}/{str(pool_size)}")
        if page.isRedirectPage():
            continue
        try:
            item = pywikibot.ItemPage.fromPage(page)
            if not item.exists():
                continue
        except NoPageError:
            print("Wikidata page doesn't exist")
            continue

        # Check if the template is used
        if page.text.find("{{"+TEMPLATE_NAME) != -1:
            continue

        # Check if the property P301 is present
        if 'P301' not in item.claims:
            continue

        # Check if the target of P301 has an article on arywiki
        target_item = item.claims['P301'][0].getTarget()
        if target_item.sitelinks.get('arywiki') is None:
            continue

        # Add the template to the category page
        page.text = add_main_topic_to_cat(page, target_item)
        page.save(summary=f"زيد لموضيل {TEMPLATE_NAME}")
        
        

if __name__ == "__main__":
    main()
