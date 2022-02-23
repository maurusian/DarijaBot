import pywikibot

site = pywikibot.Site()

cat = pywikibot.Category(site,"تصنيف:تاريخ على حساب لمدينة ؤ لبلاد")

new_title = "تصنيف:تاريخ على حساب لمدينة و لبلاد"

reason = "test"

print(len(list(cat.subcategories())))

cat.move(new_title,reason=reason,movetalk=True)
