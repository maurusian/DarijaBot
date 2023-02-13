import pywikibot
import json, traceback

batch_filename_ptrn = "ميدياويكي:عطاشة6.خدمة{}.json"

BATCH_NUMBER = int(input("Batch number: "))

batch_filename = batch_filename_ptrn.format(BATCH_NUMBER)

TASK_NAME = batch_filename.split(':')[1][:-5]

MOVE_MESSAGE = '[['+batch_filename+'|'+TASK_NAME+']]: '+"تحويل تصنيف"
SAVE_MESSAGE = '[['+batch_filename+'|'+TASK_NAME+']]: '+"تعويض سمية د تصنيف"


def read_json(site):
    batch = pywikibot.Page(site,batch_filename)

    jason = json.loads(batch.text)

    return jason

def to_move(source_cat, target_cat):
    """
    Checks if the category source_cat should be moved or not.
    The two conditions
    1- source_cat should not be a redirect page
    2- target_cat should not already exist
    """
    if source_cat.isCategoryRedirect(): #do not move a category redirect
        return False
    if len(list(target_cat.members())) == 0 or target_cat != "": #do not move to a category that has members or that has content
        return True
    return False


site = pywikibot.Site()

jason = read_json(site)

for i in range(len(jason)):

    source_cat_title = jason[i]["source_cat"]
    target_cat_title = jason[i]["target_cat"]




    source_cat = pywikibot.Page(site,source_cat_title)

    if to_move(source_cat, pywikibot.Category(site,target_cat_title)):

        try:
            source_cat.move(target_cat_title,MOVE_MESSAGE)
            
        except:
            print("could not transfer cat "+source_cat.title())
            print(traceback.format_exc())

    source_cat = pywikibot.Category(site,source_cat_title)

           
    print(len(list(source_cat.backlinks())))
    for page in source_cat.backlinks():
        page.text = page.text.replace(source_cat_title,target_cat_title)
        page.save(SAVE_MESSAGE)


    print(len(list(source_cat.members())))
    for page in source_cat.members():
        page.text = page.text.replace(source_cat_title,target_cat_title)
        page.save(SAVE_MESSAGE)
