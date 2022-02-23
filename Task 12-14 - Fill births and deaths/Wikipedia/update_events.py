import pywikibot
from arywikibotlib import isHuman, getItemPropertyValue, getOnlyArticles, extractYearDay, getMonthName
from copy import deepcopy

EVENT_PAGE_PART = "قالب:حوايج وقعو ف "
ARTICLE_NAMESPACE = 0
KEEP_REDIRECTS = False
POINT_IN_TIME_PROP_CODE = 'P585'
INCEPTION_PROP_CODE = 'P571'
ABOLISHED_PROP_CODE = 'P576'
PUBLICATION_PROP_CODE = 'P577'
START_TIME_PROP_CODE = 'P580'
END_TIME_PROP_CODE = 'P582'
#POINT_IN_TIME_PROP_CODE = 'P31'
SEPARATOR = " {{•}} "
BC = "ق.م."
STANDARD_BOT_NOTIF = "<noinclude>{{پاج كيعمرها بوت}}</noinclude>"
UPDATED_EVENT_LIST_MESSAGE = "أپدييت ديال لأحدات"
DATE_TEMPLATES_CAT = "[[تصنيف:قوالب د توارخ]]"

EVENT_NAME_PREFIX = {'P585':''
                    ,'P571':'بدية/تأسيس ديال '
                    ,'P580':'بدية/تأسيس ديال '
                    ,'P576':'لمسالية/لإلغاء ديال '
                    ,'P582':'لمسالية/لإلغاء ديال '
                    ,'P577':'نشر ديال '
                    }

def load_property_entries_by_date(page,property_code,dict_events_by_date):
    prop = getItemPropertyValue(page,property_code)
    if prop is not None:
        time, prec = prop
        print(prop)
        if prec >= 11:
            year, daymonth = extractYearDay(time)

            if daymonth not in dict_events_by_date.keys():
                dict_events_by_date[daymonth] = {}
                dict_events_by_date[daymonth][year] = [EVENT_NAME_PREFIX[property_code]+'[['+page.title()+']]']
            elif year not in dict_events_by_date[daymonth].keys():
                dict_events_by_date[daymonth][year] = [EVENT_NAME_PREFIX[property_code]+'[['+page.title()+']]']
            else:
                dict_events_by_date[daymonth][year].append(EVENT_NAME_PREFIX[property_code]+'[['+page.title()+']]')
    return dict_events_by_date


dict_events_by_date = {}

site = pywikibot.Site()

print("Creating working pool")
pool = getOnlyArticles(site)
#pool = [page for page in site.allpages() if validate_page(page)]

pool_size = len(list(deepcopy(getOnlyArticles(site))))
print('Pool size: '+str(pool_size))
i = 1

print("Running through pages to create event dictionary")
for page in pool:
    print('*********'+str(i)+'/'+str(pool_size))

    #load for property P585 = Point in Time
    load_property_entries_by_date(page,POINT_IN_TIME_PROP_CODE,dict_events_by_date)

    #load for property P571 = Inception Time
    load_property_entries_by_date(page,INCEPTION_PROP_CODE,dict_events_by_date)

    #load for property P576 = Abolishing Time
    load_property_entries_by_date(page,ABOLISHED_PROP_CODE,dict_events_by_date)

    #load for property P577 = Publication Time
    load_property_entries_by_date(page,PUBLICATION_PROP_CODE,dict_events_by_date)

    #load for property P580= Start Time
    load_property_entries_by_date(page,START_TIME_PROP_CODE,dict_events_by_date)

    #load for property P582= End Time
    load_property_entries_by_date(page,END_TIME_PROP_CODE,dict_events_by_date)

    """
    p585 = getItemPropertyValue(page,POINT_IN_TIME_PROP_CODE)
    if p585 is not None:
        time, prec = p585
        print(p585)
        if prec >= 11:
            year, daymonth = extractYearDay(time)

            if daymonth not in dict_events_by_date.keys():
                dict_events_by_date[daymonth] = {}
                dict_events_by_date[daymonth][year] = [page.title()]
            elif year not in dict_events_by_date[daymonth].keys():
                dict_events_by_date[daymonth][year] = [page.title()]
            else:
                dict_events_by_date[daymonth][year].append(page.title())
    """
    
    i+=1

print(dict_events_by_date)
for daymonth, value in dict_events_by_date.items():
    
    title = EVENT_PAGE_PART+str(int(daymonth[:2]))+" "+getMonthName(int(daymonth[2:]))

    page = pywikibot.Page(site,title)
    
    years = list(value.keys())

    years.sort()

    page.text = STANDARD_BOT_NOTIF

    for year in years:
        if year > 0:
            page.text+="\n* '''"+str(year)+":''' "
        else:
            page.text+="\n* '''"+str(abs(year))+" "+BC+":''' "
        page.text+=SEPARATOR.join(value[year])

    page.text+="\n\n"+DATE_TEMPLATES_CAT
    page.save(UPDATED_EVENT_LIST_MESSAGE)
