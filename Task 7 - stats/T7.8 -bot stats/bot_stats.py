import pywikibot
from pywikibot import pagegenerators

# Replace 'YourUsername' with the specific user's username
username = 'DarijaBot'
# Replace 'YourCategory' with the category name you want to check
category_name = 'تصنيف:مقالات زادهوم داريجابوت'

# Connect to the Arywiki site
site = pywikibot.Site('ary', 'wikipedia')
site.login()

# Generate a set of all articles in Arywiki
all_pages = set(page.title() for page in site.allpages(filterredir=False))

# Generate a set of articles under the specified category
category = pywikibot.Category(site, category_name)
category_pages = set(page.title() for page in pagegenerators.CategorizedPageGenerator(category))

# Exclude the articles that are in the specified category from the set of all articles
remaining_articles = all_pages - category_pages

# Loop through the remaining articles and add the category if they were created by the specified user
i=1
pool_size = len(remaining_articles)
for article_title in remaining_articles:
    print(f"**********{i}/{pool_size}")
    page = pywikibot.Page(site, article_title)
    # Check the creator of the page
    creator = page.oldest_revision.user
    if creator == username:
        text = page.text
        #if '[[Category:' + category_name + ']]' not in text:
        page.text = text + '\n[[' + category_name + ']]'
        page.save(summary=f'[[{category_name}]] تزاد')
    i+=1
