import pywikibot
from pywikibot import pagegenerators
from datetime import datetime

# Configuration
current_year = "2025" #datetime.now().year
site = pywikibot.Site('ary', 'wikipedia')
site.login()
target_page_title = f"موضيل:حساب د لمقالات لي تصاوبو ب ليد ف {current_year}"

# Helpers
def is_human(editor):
    return not editor.lower().endswith('bot')

def is_not_from_draft(title):
    draft_title = f'واساخ:{title}'
    return not pywikibot.Page(site, draft_title).exists()

# Main logic
def count_human_articles_created_this_year():
    count = 0
    gen = site.allpages(namespace=0, filterredir=False)

    pool_size = len(list(site.allpages(namespace=0, filterredir=False)))
    i=1
    for page in gen:
        print(f"****************** {i}/{pool_size}")
        try:
            hist = list(page.revisions(total=1, reverse=True))  # First revision only
            if not hist:
                continue
            rev = hist[0]
            created = rev.timestamp
            year_str = created.strftime('%Y')
            if year_str == str(current_year) and is_human(rev.user) and is_not_from_draft(page.title()):
                count += 1
            i+=1
        except Exception as e:
            i+=1
            continue

    return count

# Update target page
def update_target_page(count):
    header = '<noinclude>{{پاج كيعمرها بوت}}</noinclude>\n'
    footer = '\n<noinclude>{{شرح}}[[تصنيف:موضيلات د إحصائيات ويكيپيديا]]</noinclude>'
    content = f"{header}{count}{footer}"

    page = pywikibot.Page(site, target_page_title)
    page.text = content
    page.save(summary=f'أپدييت د عدد المقالات لي تكتبات ب ليد ف {current_year}')

if __name__ == "__main__":
    article_count = count_human_articles_created_this_year()
    print(article_count)
    update_target_page(article_count)
