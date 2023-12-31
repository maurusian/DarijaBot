import pywikibot
import json, traceback
from pywikibot.exceptions import CascadeLockedPageError, ArticleExistsConflictError

site = pywikibot.Site()
site.login()

def read_json(filename):
    batch = pywikibot.Page(site,filename)

    jason = json.loads(batch.text)

    return jason

main_param_filename = "Mediawiki:Task6.json"

main_param_json = read_json(main_param_filename)

batch_filename_ptrn = main_param_json["BATCH_FILENAME_PATTERN"]

BATCH_NUMBER = int(input("Batch number: "))

batch_filename = batch_filename_ptrn.format(BATCH_NUMBER)

TASK_NAME = batch_filename.split(':')[1][:-5]

MOVE_MESSAGE = '[['+batch_filename+'|'+TASK_NAME+']]: '+main_param_json["MOVE_MESSAGE_PART"]
SAVE_MESSAGE = '[['+batch_filename+'|'+TASK_NAME+']]: '+main_param_json["SAVE_MESSAGE_PART"]

CASCADE_LOG_MSG = main_param_json["CASCADE_ERROR_LOG_MSG"]
LOG_PAGE_TTL = main_param_json["LOG_PAGE_TTL"]
LOG_SAVE_MSG = main_param_json["LOG_SAVE_MSG"]

def write_to_log(LOG_MSG):
    WIKILOG = pywikibot.Page(site,LOG_PAGE_TTL)
    WIKILOG.text+="\n*"+LOG_MSG
    WIKILOG.save(LOG_SAVE_MSG)


def to_move(source_cat, target_cat):
    """
    Checks if the category source_cat should be moved or not.
    The two conditions
    1- source_cat should not be a redirect page
    2- target_cat should not already exist
    """
    if source_cat.isCategoryRedirect() or source_cat.isRedirectPage(): #do not move a category redirect
        return False
    if len(list(target_cat.members())) == 0 or target_cat != "": #do not move to a category that has members or that has content
        return True
    return False




jason = read_json(batch_filename)

for i in range(len(jason)):

    source_cat_title = jason[i]["source_cat"]
    target_cat_title = jason[i]["target_cat"]

    source_cat = pywikibot.Page(site,source_cat_title)

    
    if to_move(source_cat, pywikibot.Category(site,target_cat_title)):

        try:
            source_cat.move(target_cat_title,MOVE_MESSAGE)
            
        except ArticleExistsConflictError:
            print("could not transfer cat "+source_cat.title()+" due to ArticleExistsConflictError")
            #print(traceback.format_exc())
    
    source_cat = pywikibot.Category(site,source_cat_title)

    #print(len(list(source_cat.backlinks())))
    for page in source_cat.backlinks():
        tmp_text = page.text
        tmp_text = page.text.replace(source_cat_title,target_cat_title)
        if tmp_text != page.text:
            try:
                page.text = tmp_text
                page.save(SAVE_MESSAGE)
            except CascadeLockedPageError:
                write_to_log(CASCADE_LOG_MSG)


    #print(len(list(source_cat.members())))
    for page in source_cat.members():
        tmp_text = page.text
        tmp_text = page.text.replace(source_cat_title,target_cat_title)
        if tmp_text != page.text:
            try:
                page.text = tmp_text
                page.save(SAVE_MESSAGE)
            except CascadeLockedPageError:
                write_to_log(CASCADE_LOG_MSG)
