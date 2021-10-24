import pywikibot
from openpyxl import load_workbook


site = pywikibot.Site()
'''
page = pywikibot.Page(site, u"Project:Sandbox")
text = page.text


#page.text = u"DarijaBot kheddam daba"
page.save(page.text+u"\n\nawwal edit dial DarijaBot")
'''

sandbox = pywikibot.Page(site, 'User:' + site.user() + '/Project:Sandbox')

sandbox.text = page.text+u"\n\nawwal edit dial DarijaBot"

sandbox.save()
