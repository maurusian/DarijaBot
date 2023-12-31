"""
This is a generic script for any bot task
"""

import sys, pywikibot

def main():

    site = pywikibot.Site() #invoke default site
    site_en = pywikibot.Site("en", "wikipedia") #invoke English Wikipedia
    site.login() #not needed if you only to read from Wiki

    
    title = "Marrakesh"

    page = pywikibot.Page(site_en, title) #invoke the article for Marrakech on the English Wikipedia

    text = page.text #invoke the wiki text of the page

    category_title = "Category:Marrakesh"

    cat = pywikibot.Category(site_en, category_title) #invoke the category for Marrakech on the English Wikipedia

    members = cat.members() #invoke all members of the category, including subcategories and content pages

    subcats = cat.subcategories() #invoke subcategories only

    content_pages = cat.articles() #invoke content pages only, such as articles, templates, etc.
    

if __name__ == "__main__":
    main()
