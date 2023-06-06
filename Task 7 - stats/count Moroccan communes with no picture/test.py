import re, pywikibot

ary_file = '[[فيشي:'
en_file = '[[File:'
ar_file = '[[ملف:'

file_symbols = [ary_file,en_file,ar_file]

def extract_images(text):
    images = []
    for sym in file_symbols:
        if sym in page.text:
            parts = page.text.split(sym)
            for part in parts[1:]:
                subpart = part.split(']]')[0]
                images.append(subpart.split('|')[0])

    return ', '.join(images)




title = "أوطوروت 5 (لمغريب)"

site = pywikibot.Site()
page = pywikibot.Page(site,title)


print(extract_images(page.text))
