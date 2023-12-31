import pywikibot
from pywikibot import pagegenerators

replacements = {"ايت ":"أيت "
               ,"آيت ":"أيت "
               ,"نأيت ":"نايت "
               ,"اكادير":"أݣادير"
               ,"أكادير":"أݣادير"
               ,"بود جعفر":"بوجعفر"
               ,"ث":"ت"
               }


SAVE_MESSAGE = "إصلاح لعنوان"

VILLAGE_CAT = "تصنيف:دوار ف لمغريب"

def placeholder_same_article():
    # Placeholder: Logic when the new title is a redirect to the same article
    pass

def placeholder_different_article(old_title):
    # Placeholder: Logic when the new title is another article
    print("not moving ",old_title)

def placeholder_redirect_to_different_article():
    # Placeholder: Logic when the new title is a redirect to another article
    pass

def main():
    site = pywikibot.Site()  # Adjust the site
    site.login()
    cat = pywikibot.Category(site, VILLAGE_CAT)  # Adjust the category
    gen = pagegenerators.CategorizedPageGenerator(cat)

    for page in gen:
        old_title = page.title()
        new_title = old_title
        for oldvalue, newvalue in replacements.items():
            new_title = new_title.replace(oldvalue, newvalue)  # Adjust the words

        if old_title != new_title:
            new_page = pywikibot.Page(site, new_title)

            if new_page.exists():
                # Check if the new title is a redirect
                if new_page.isRedirectPage():
                    target_page = new_page.getRedirectTarget()

                    # Resolve to the final target
                    while target_page.isRedirectPage():
                        target_page = target_page.getRedirectTarget()

                    if target_page.title() == old_title:
                        page.move(new_title, reason=SAVE_MESSAGE)
                    else:
                        print("not moving ",old_title)
                else:
                    print("not moving ",old_title)

            else:
                # Move the page
                page.move(new_title, reason=SAVE_MESSAGE)

if __name__ == "__main__":
    main()
