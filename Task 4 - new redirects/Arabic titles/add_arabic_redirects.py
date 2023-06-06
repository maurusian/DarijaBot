from pgvbotLib import *
from params import *
import pywikibot
from copy import deepcopy
import re, os

RECENT_LOG_FILE = "recent_log.txt"

ADMIN_LIST = ["Ideophagous","Reda benkhadra","Anass Sedrati","سمير تامر"]

BOT_COMMENT_TAG = "{{تعليق بوتي}}"

TALK_PAGE_TITLE_PART = "نقاش:"

NOTIF_SECTION_TITLE = "== دمج ؤلا توضيح =="

NOTIF_TEMPLATE = BOT_COMMENT_TAG+" مرحبا {{جاوب|{إمغارن}}}. عافاكوم شوفو واش هاد لپاج [[{پاج1}]] ؤ هاد لپاج [[{پاج2}]] خاصهوم يتزادو ل پاج ديال تّوضيح ؤلا يتدمجو. --~~~~"

NOTIF_ADMINS_SAVE_MESSAGE = "إعلام ل إمغارن"

def load_pages_in_log():
    if not os.path.exists(RECENT_LOG_FILE):
        return []
    with open(RECENT_LOG_FILE,'r',encoding='utf-8') as f:
        page_name_list = f.read().strip().splitlines()
    
    for i in range(len(page_name_list)):
        page_name_list[i] = page_name_list[i].strip()
    
    return page_name_list

def get_final_target(page):
    temp = page
    while temp.isRedirectPage():
        target_title = temp.text.strip().split('[[')[1].strip()[:-2]
        temp = pywikibot.Page(site,target_title)
    return temp

def get_disambig_pages(page):
    disambig_pages = []

    for link in page.backlinks():
        if link.isDisambig():
            disambig_pages.append(link)
        elif link.isRedirectPage():
            disambig_pages+=get_disambig_pages(link)
    return disambig_pages


def has_disambig_cross_ref(page1,page2):
    """
    Returns True if the disambiguation page
    linked to page1 or page2 refers to the
    other. False otherwise.
    """
    page1_disambig = get_disambig_pages(page1)
    page2_disambig = get_disambig_pages(page2)

    for disam_page in page1_disambig:
        if page2 in disam_page.linkedPages():
            return True

    for disam_page in page2_disambig:
        if page1 in disam_page.linkedPages():
            return True

    return False

def get_admins(site):
    """
    Retrieves a list of human administrators on the given wiki site.

    Args:
        site (str): The URL of the wiki site to retrieve admins from.

    Returns:
        list: A list of usernames of all the human administrators on the given wiki site.
    """
    # Get the Site object for the wiki site
    site = pywikibot.Site(site)

    # Get the User object for the "Administrators" group
    admins_group = pywikibot.Group(site, 'sysop')

    # Get a list of User objects for all members of the "Administrators" group
    admins_list = list(admins_group.members())

    # Extract the usernames from the User objects and exclude adminbots
    usernames = [admin.username for admin in admins_list if not admin.isBot()]

    # Return the list of usernames
    return usernames

def notify_admins(page,ar_page):
    talk_page_title = TALK_PAGE_TITLE_PART+page.title()
    talk_page = pywikibot.Page(pywikibot.Site(),talk_page_title)
    ar_talk_page_title = TALK_PAGE_TITLE_PART+ar_page.title()
    ar_talk_page = pywikibot.Page(pywikibot.Site(),ar_talk_page_title)
    if (NOTIF_SECTION_TITLE not in talk_page.text and BOT_COMMENT_TAG not in talk_page.text
        and NOTIF_SECTION_TITLE not in ar_talk_page.text and BOT_COMMENT_TAG not in ar_talk_page.text):
        NOTIF_MESSAGE = NOTIF_TEMPLATE.replace("{إمغارن}",'|'.join(get_admins(site))).replace('{پاج1}',page.title()).replace('{پاج2}',ar_page.title())
        talk_page.text+=NOTIF_SECTION_TITLE+'\n'+NOTIF_MESSAGE
        talk_page.save(NOTIF_ADMINS_SAVE_MESSAGE)
    else:
        print("Notification already added")
    
    



    
site = pywikibot.Site()

"""

site = pywikibot.Site()

cat = pywikibot.Category(site,"تصنيف:تاريخ على حساب لمدينة ؤ لبلاد")

new_title = "تصنيف:تاريخ على حساب لمدينة و لبلاد"

reason = "test"

print(len(list(cat.subcategories())))

cat.move(new_title,reason=reason,movetalk=True)
"""

NAMESPACE = input("Enter namespace code (only default and project for now): ")

ar_title_part = ''
if NAMESPACE == 14:
    ar_title_part = 'تصنيف:'
elif NAMESPACE == 4:
    ar_title_part = 'ويكيبيديا:'

TRANSFER_CODE = "#تحويل [[{}]]"

ADD_TRANSFER_SAVE_MESSAGE = "دّخلة لموقابيلة ب لعربية تزادت كا تحويل"

print("Creating working pool")
pool = site.allpages(namespace=NAMESPACE)
#pool = [page for page in site.allpages() if validate_page(page)]

pool_size = len(list(deepcopy(site.allpages(namespace=ARTICLE_NAMESPACE))))
print('Pool size: '+str(pool_size))
i = 1
pages_in_log = load_pages_in_log()

with open(RECENT_LOG_FILE,'a',encoding='utf-8') as f:
    for page in pool:
        print('*********'+str(i)+'/'+str(pool_size))
        
        #print(pages_in_log[:20])
        
        
        if str(page.title()) not in pages_in_log:
                
            MESSAGE = ""

            #avoiding redirects and disambiguation pages
            if not page.isRedirectPage() and not page.isDisambig():
                try:
                    for link in page.iterlanglinks():
                        linkparts = str(link)[2:-2].split(':')
                        #print(linkparts)
                        if linkparts[0] == 'ar':
                            ar_title = ar_title_part+linkparts[-1]
                            if ar_title != page.title():
                                ar_page = pywikibot.Page(site,ar_title)
                                if ar_page.text == "":
                                    ar_page.text = TRANSFER_CODE.format(page.title())+'\n\n'+REDIRECT_PAGE_CAT_CODE
                                    ar_page.save(ADD_TRANSFER_SAVE_MESSAGE)
                                elif ar_page.isRedirectPage():
                                    final_target = get_final_target(ar_page)
                                    if final_target.title() == page.title():
                                        print("all is good (case 1)")
                                        break #all is good
                                    else:
                                        #check disambigs, eventually notify_admins(page,ar_page)
                                        if has_disambig_cross_ref(page,final_target):
                                            print("all is good (case 2)")
                                            break #all is good
                                        else:
                                            print("notifying admins on talk page")
                                            notify_admins(page,ar_page)
                                elif ar_page.isDisambig():
                                    if page in ar_page.linkedPages():
                                        print("all is good (case 3)")
                                        break #all is good
                                    else:
                                        print("notifying admins on talk page")
                                        notify_admins(page,ar_page)
                                        
                                else:
                                    if has_disambig_cross_ref(page,ar_page):
                                        print("all is good (case 4)")
                                        break #all is good
                                    else:
                                        print("notifying admins on talk page")
                                        notify_admins(page,ar_page)
                            else:
                                print("identical titles")


                            break #only ar interlanglink is checked
                except KeyError:
                    print(page.title())
                    print(sys.exc_info())
                except pywikibot.exceptions.UnknownSiteError:
                    print(page.title())
                    print(sys.exc_info())
                        

            f.write(page.title()+'\n')
        i+=1
