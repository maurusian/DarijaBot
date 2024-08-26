import pywikibot
import re, json, os
from datetime import datetime
import traceback

batch_filename = "ميدياويكي:Currentcontest.json"

site = pywikibot.Site()

local_folder = os.path.dirname(__file__)

QIDS_FILE = local_folder+"/qids.txt"

def read_json(site):
    batch = pywikibot.Page(site,batch_filename)

    jason = json.loads(batch.text)

    return jason

jason = read_json(site)

IGNORE_LIST_PAGE_TITLE = jason["IGNORE_LIST_PAGE_TITLE"] #"ويكيپيديا:مسابقة ويكيپيديا ب الداريجة يوليوز 2024/كتاتبيا مامشاركينش"
start_date = jason["START_DATE"] #'2024-07-20T00:00:00Z'
end_date = jason["END_DATE"] #'2024-07-27T23:59:59Z'
ARTICLE_CAT = jason["ARTICLE_CAT"]
GENERAL_CAT = jason["GENERAL_CAT"]
quality_points = {}

if "QUALITY_POINTS" in jason.keys():
    quality_points = jason["QUALITY_POINTS"]

def load_user_list_from_ignore_page(site):
    # Set up the site and the page
    #site = pywikibot.Site('ary', 'wikipedia')
    page = pywikibot.Page(site, IGNORE_LIST_PAGE_TITLE)

    # Get the page content
    text = page.get()

    # Remove category for processing
    text = text.replace(f"[[{GENERAL_CAT}]]","")

    # Find list items and extract usernames, removing the leading *
    user_list_pattern = r'\* *(.+)'
    user_list = re.findall(user_list_pattern, text)

    # Return the list of users
    return user_list

def load_qids_from_file():
    filename = QIDS_FILE
    qids = []
    try:
        with open(filename, 'r') as file:
            qids = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"The file {filename} was not found.")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
    return qids

def get_recent_changes(site,start_date, end_date):
    # Set up the site
    #site = pywikibot.Site('ary', 'wikipedia')
    
    # Load the ignore list
    ignore_users = load_user_list_from_ignore_page(site)
    
    # Convert dates to Pywikibot Timestamp format
    start = pywikibot.Timestamp.fromISOformat(start_date)
    end = pywikibot.Timestamp.fromISOformat(end_date)
    
    # Retrieve recent changes
    recent_changes = site.recentchanges(start=start, end=end, bot=False,reverse=True)

    # Filter out edits by users in the ignore list
    filtered_changes = [
        change for change in recent_changes 
        if change['user'] not in ignore_users
        and 'vanished user' not in str(change['user']).lower()
        and 'renamed user' not in str(change['user']).lower()
        and not pywikibot.User(site, change['user']).isAnonymous()
        and 'mw-reverted' not in change['tags']
        and 'mw-manual-revert' not in change['tags']
        and not pywikibot.User(site, change['user']).is_blocked()
    ]
    
    return filtered_changes

def get_target_page_title(site,page_title):
    """
    Retrieve the target page title if the input title is a redirect.
    Check the move log if the original redirect page has been deleted.
    
    :param site: The Pywikibot site object.
    :param page_title: The title of the page to check.
    :return: The target page title if the input title is a redirect, else the input title.
    """
    
    i = 0
    while i<10:
        page = pywikibot.Page(site, page_title)

        # Check the move log if the page has been deleted
        if not page.exists():
            log_entries = site.logevents(logtype='move', page=page_title, total=1)
            for entry in log_entries:
                page = pywikibot.Page(site, entry.target_title)

        if page.isRedirectPage():
            target_page = page.getRedirectTarget()
            page = pywikibot.Page(site, target_page.title())

        if page.exists() and not page.isRedirectPage():
            return page.title()

        i+=1
    
    return None

def process_filtered_changes(site,filtered_changes):
    # Set up the site and repository
    
    repo = site.data_repository()  # Wikidata repository
    
    user_stats = {}

    for change in filtered_changes:
        user = change['user']
        title = change['title']
        #print(title)
        #tags = change['tags']
        #print(tags)
        namespace = change['ns']
        size = change['newlen'] - change['oldlen']
        
        if user not in user_stats.keys():
            user_stats[user] = {'articles': set(), 'total_edit_count': 0, 'total_edit_size': 0}
        
        user_stats[user]['total_edit_count'] += 1

        if namespace == 0:  # Only consider changes in the main namespace for articles and edit size
            try:
                page = pywikibot.Page(site, get_target_page_title(site,title)) 
                if page is not None:
                    #page = pywikibot.Page(site, get_target_page_title(site,title))
                    item = pywikibot.ItemPage.fromPage(page)
                    qid = item.id
                    #print(qid)
                else:
                    qid = None
            except Exception as e:
                print(f"Error processing page {title}: {e}")
                traceback.print_exc()
                
            user_stats[user]['articles'].add(qid)
            user_stats[user]['total_edit_size'] += size

    # Convert sets to lists and prepare final dictionary
    for user in user_stats:
        user_stats[user]['articles'] = list(user_stats[user]['articles'])
    
    return user_stats


def calculate_user_points(user_stats, qids):
    """
    Calculate the points obtained by each user based on the given rules.
    
    :param user_stats: A dictionary containing user statistics.
    :param qids: A list of QIDs loaded from qids.txt.
    :return: None. Updates the user_stats dictionary with the total points for each user.
    """
    for user, stats in user_stats.items():
        points = 0
        
        # 1 point for each edit
        points += stats['total_edit_count']
        
        # 5 points if an article has a qid in the list of qids
        points += 5 * sum(1 for qid in stats['articles'] if qid in qids)
        
        # 10 points for each 1000 bytes of total edit size (rounded down)
        points += 10 * (max(stats['total_edit_size'], 0) // 1000)

        if user in quality_points.keys():
            points += quality_points[user]
        
        # Update the user_stats dictionary with the calculated points
        user_stats[user]['points'] = points
    
    return user_stats

def write_user_statistics_to_page(site, page_title, user_stats):
    """
    Write user statistics to a specified page on the site.
    
    :param site: The Pywikibot site object.
    :param page_title: The title of the page to write to.
    :param user_stats: A dictionary containing user statistics.
    :param user_points: A dictionary containing user points.
    """
    # Headers (can be translated)
    header_count = "نمرة"
    header_user = "مشارك(ة)"
    header_edit_count = "شحال د التبديلات"
    header_edit_size = "مقدار د التبديلات (بايت)"
    header_points = "نقاط"

    # Sort users by points in descending order
    sorted_users = sorted(
    user_stats.keys(),
    key=lambda user: (
        user_stats[user].get('points', 0), 
        user_stats[user].get('total_edit_size', 0), 
        user_stats[user].get('total_edit_count', 0),
        user
    ),
    reverse=True
    )


    # Start creating the table
    table_content = (
        f'<div style="text-align: center;">\n'
        f'{{| class="wikitable sortable" style="margin: auto;"\n'
        f'|-\n'
        f'! {header_count}\n'
        f'! {header_user}\n'
        f'! {header_edit_count}\n'
        f'! {header_edit_size}\n'
        f'! {header_points}\n'
    )

    # Add the user statistics to the table
    i=1
    for user in sorted_users:
        stats = user_stats[user]
        edit_count = stats['total_edit_count']
        edit_size = stats['total_edit_size']
        points = stats['points']
        
        table_content += '|-\n'
        table_content += f'| {i}\n'
        table_content += '| {{خ|{user}|separator=pipe}}\n'.replace("{user}",user)
        table_content += (
            f'| {edit_count}\n'
            f'| {edit_size}\n'
            f'| {points}\n'
        )
        i+=1

    # Close the table and div
    table_content += '\n|}\n</div>\n[['+GENERAL_CAT+']]'

    # Write the content to the specified page
    page = pywikibot.Page(site, page_title)
    page.text = table_content
    page.save(f"أپدييت ل لإحصائيات")
    
def update_category(user_stats):
    category_name = ARTICLE_CAT
    qid_list = set()
    for user in user_stats.keys():
        qid_list = qid_list.union(user_stats[user]['articles'])
    print("qid_list: ", qid_list) #debugging
    site = pywikibot.Site()  # This will automatically use the language set in user-config.py
    repo = site.data_repository()
    category = pywikibot.Category(site, f'{category_name}')

    # Create a set of current members of the category
    current_members = set(page.title() for page in category.articles())

    # Create a set of titles for the QIDs in the list
    new_members = set()

    for qid in qid_list:
        item = pywikibot.ItemPage(repo, qid)
        item.get()  # Fetch the item details from Wikidata

        # Get the Wikipedia page linked to this QID
        langwiki = site.lang+'wiki'  # Use the language code from the user's site configuration
        print("langwiki: ",langwiki)
        print("item.sitelinks: ",list(item.sitelinks))
        if langwiki in item.sitelinks:
            print(item.sitelinks[langwiki].title)
            page = pywikibot.Page(site, item.sitelinks[langwiki].title)
            new_members.add(page.title())
            print("adding cat to ",page.title())
            # Add category to this page if not already present
            if category not in page.categories():
                page.text += f'\n[[{category_name}]]'
                page.save(summary=f'تزاد تصنيف: {category_name}')

    # Remove category from pages not in the QID list
    for member_title in current_members - new_members:
        page = pywikibot.Page(site, member_title)
        text = page.text
        if f'[[{category_name}]]' in text:
            page.text = text.replace(f'[[{category_name}]]', '')
            page.save(summary=f'تحيّد تصنيف: {category_name}')

if __name__=="__main__":
    qids = load_qids_from_file()
    
    #site = pywikibot.Site('ary', 'wikipedia')
    #print(qids)
    #users = load_user_list_from_ignore_page()
    #print(users)
    filtered_changes = get_recent_changes(site,start_date, end_date)
    user_stats = process_filtered_changes(site,filtered_changes)

    #print(user_stats)
    user_stats = calculate_user_points(user_stats, qids)
    #print(user_points)

    page_title = jason["STATS_PAGE_TITLE"] #"ويكيپيديا:مسابقة ويكيپيديا ب الداريجة يوليوز 2024/طابلو د لإحصائيات"
    write_user_statistics_to_page(site, page_title, user_stats)

    # Update article category for tracking
    update_category(user_stats)
    """
    site = pywikibot.Site('ary', 'wikipedia')
    print(load_user_list_from_ignore_page(site))
    """
