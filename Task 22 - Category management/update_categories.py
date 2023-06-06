import pywikibot
import re
from datetime import datetime, timezone

CAT_NS = 14

site = pywikibot.Site()

pool = site.allpages(namespace = CAT_NS)

HIDDEN_CODE = "__HIDDENCAT__"
HIDDEN_TMPL = "{{تصنيف مخفي}}"

HID_REPLACE_MSG = "تعويض لكوض د مخفي ب لقالب لمناسب"
UPDATED_REDIRECT_TMP_MSG = "لقالب ديال تحويل د تصنيف تزاد"

REDIRECT_CAT_TMP_PATTERN = "{{تحويل د تصنيف|{target}}}"

REDIRECT_CAT_TMP_PART = "{{تحويل د تصنيف"

def get_cat_redir_target(text):
    target = text.split("[[")[1].split("]]")[0][6:]

    return target

pool_size = len(list(site.allpages(namespace = CAT_NS)))

print(pool_size)

i=1

for page in pool:
    print('*********'+str(i)+'/'+str(pool_size))

    if page.isRedirectPage():
        if REDIRECT_CAT_TMP_PART not in page.text:
            page.text = REDIRECT_CAT_TMP_PATTERN.replace("{target}",get_cat_redir_target(page.text))
            page.save(UPDATED_REDIRECT_TMP_MSG)
    """
    #deactivated for now
    else:
        text = page.text.replace(HIDDEN_CODE,HIDDEN_TMPL)

        if text != page.text:
            page.text = text
            page.save(HID_REPLACE_MSG)
    """
    i+=1
