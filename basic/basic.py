import pywikibot

site = pywikibot.Site("ary","wikipedia")

user = pywikibot.User(site,"Reda benkhadra")

allusers = site.allusers(group="sysop")

print(list(allusers))

for i in range(2):
    print(i)
    print(list(allusers)[i])
    

#print(dir(user))

#print(user.getUserPage())

#print(user.username)
