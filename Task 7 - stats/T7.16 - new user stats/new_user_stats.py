import pywikibot
from datetime import datetime
import os

print("local path:",os.getcwd())
print("script path:",os.path.dirname(__file__))
print("script name:",os.path.basename(__file__))

local_folder = os.path.dirname(__file__) #os.getcwd()

current_year = datetime.now().year
#print(current_year)

IGNORE_LIST_FILE = local_folder+"/ignore_list.txt"
PAGE_TO_UPDATE = "موضيل:مساهمات ديال لكتاتبيا الجداد "+str(current_year)
EDIT_SUMMARY = "أپدييت ديال لإحصائيات"
HEADER = "<noinclude>{{پاج كيعمرها بوت2}}</noinclude>"
FOOTER = "<noinclude>{{شرح}}</noinclude>"

def load_ignore_list():
    """Load the ignore list from file or create an empty one if the file doesn't exist."""
    if not os.path.exists(IGNORE_LIST_FILE):
        return set()
    with open(IGNORE_LIST_FILE, 'r', encoding="utf-8") as file:
        return set(line.strip() for line in file)

def save_ignore_list(ignore_list):
    """Save the updated ignore list to the file."""
    with open(IGNORE_LIST_FILE, 'w', encoding="utf-8") as file:
        for user in ignore_list:
            file.write(f"{user}\n")

def get_new_user_contributions(site, ignore_list):
    """Get the number of contributions by users registered in the current year."""
    current_year = str(datetime.now().year)
    new_user_contributions = 0
    ignore_list_updated = False

    for user in site.allusers(total=None):
        username = user['name']
        if username not in ignore_list:
            groups = user.get('groups', [])

            # Ignore bots, regardless of other roles they might have
            registration_date = user.get('registration')

            registration_year = registration_date[:4]

            if registration_year == current_year and 'bot' not in groups and username[-3:].lower() != 'bot':
                # Always count contributions for new users
                contributions_count = len(list(site.usercontribs(user=username)))
                if contributions_count > 0:
                    print(username,': ',contributions_count)
                new_user_contributions += contributions_count
            else:
                # Add users who registered in previous years to the ignore list
                if username not in ignore_list:
                    ignore_list.add(username)
                    ignore_list_updated = True

    if ignore_list_updated:
        save_ignore_list(ignore_list)

    return new_user_contributions

def update_wiki_page(site, page_title, total_contributions):
    """Update the wiki page with the total contributions count."""
    page = pywikibot.Page(site, page_title)
    page.text = HEADER+str(total_contributions)+FOOTER
    page.save(summary=EDIT_SUMMARY)

if __name__=="__main__":
    # Load ignore list
    ignore_list = load_ignore_list()

    # Connect to the wiki
    site = pywikibot.Site()

    # Get the total contributions by new users
    new_user_contributions = get_new_user_contributions(site, ignore_list)

    # Update the wiki page
    update_wiki_page(site, PAGE_TO_UPDATE, new_user_contributions)
