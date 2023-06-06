import pywikibot


site = pywikibot.Site()
page = pywikibot.Page(site, u"مستخدم:Ideophagous")
text = page.text

page.text = u"DarijaBot kheddam daba"
page.save(u"awwal edit dial DarijaBot")


#print(text)
