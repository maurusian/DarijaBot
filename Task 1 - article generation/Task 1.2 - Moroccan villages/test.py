import pywikibot
from arywikibotlib import has_wikipedia_article


site = pywikibot.Site()

qid1 = "Q28879664"

print(has_wikipedia_article(qid1,site.lang)) #True

qid2 = "Q2"

print(has_wikipedia_article(qid2,site.lang)) #True

qid3 = "Q4967771"

print(has_wikipedia_article(qid3,site.lang)) #False

qid4 = "Q28878914"

print(has_wikipedia_article(qid4,site.lang)) #False ?? Not for long anyway
