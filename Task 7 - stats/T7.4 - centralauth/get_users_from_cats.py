import pywikibot
import pandas as pd

lis = [('ar','تصنيف:مستخدمون مغاربة','مستخدم')
      ,('fr','Catégorie:Utilisateur origine Maroc','Utilisateur')
      ,('en','Category:Moroccan Wikipedians','User')]

def extract_usernames(site, category, user_ns):
    cat = pywikibot.Category(site, f"{category}")
    usernames = set()

    for page in cat.articles(namespaces=site.namespaces.USER):
        username = page.title().split(":", 1)[1]
        if '/' in username:
            username = username.split('/')[0]
        usernames.add(username)

    return usernames

def save_to_excel(usernames, filename):
    df = pd.DataFrame(usernames, columns=['Username'])
    df.to_excel(filename, index=False)

if __name__ == '__main__':
    usernames = set()
    for lang, category, user_ns in lis:
        site = pywikibot.Site(lang,'wikipedia')
        usernames.update(extract_usernames(site, category, user_ns))
    
    save_to_excel(usernames, "usernames.xlsx")
