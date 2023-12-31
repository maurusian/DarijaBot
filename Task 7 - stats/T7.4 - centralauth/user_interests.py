from collections import Counter
import pywikibot

def get_super_categories(site, category, super_cat_cache):
    if category in super_cat_cache:
        return super_cat_cache[category]
    
    super_categories = []
    cat_page = pywikibot.Page(site, f"Category:{category}")
    
    for parent_cat in cat_page.categories():
        super_category = parent_cat.title().split(":", 1)[1]
        super_categories.append(super_category)
        
    super_cat_cache[category] = super_categories
    return super_categories

def get_top_keywords(site, username, super_cat_cache):
    keyword_weights = Counter()
    
    user_contribs = site.usercontribs(user=username)
    for contrib in user_contribs:
        title = contrib['title']
        page = pywikibot.Page(site, title)
        
        try:
            for cat in page.categories():
                direct_category = cat.title().split(":", 1)[1]
                keyword_weights[direct_category] += 1
                
                # Level 1 super categories
                level1_supers = get_super_categories(site, direct_category, super_cat_cache)
                for super_cat in level1_supers:
                    keyword_weights[super_cat] += 0.5
                    
                    # Level 2 super categories
                    level2_supers = get_super_categories(site, super_cat, super_cat_cache)
                    for super_cat_2 in level2_supers:
                        keyword_weights[super_cat_2] += 0.25
        except Exception as e:
            print(f"An exception occurred while processing page {title}: {e}")

    return keyword_weights.most_common()

# Setup site and user namespace
lang = 'en'  # Replace with the desired language code
site = pywikibot.Site(lang)

# Cache for super categories
super_cat_cache = {}

# Extract top keywords
username = 'Ideophagous'  # Replace with the actual username
top_keywords = get_top_keywords(site, username, super_cat_cache)
print(top_keywords)
