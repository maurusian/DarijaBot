import pywikibot
from arywikibotlib import getItemPropertyValue, getOnlyArticles, getItemIdentities #,hasProperty

site = pywikibot.Site()


pool = getOnlyArticles(site)
#pool = [page for page in site.allpages() if validate_page(page)]

pool_size = len(list(deepcopy(getOnlyArticles(site))))
print('Pool size: '+str(pool_size))
i = 1

