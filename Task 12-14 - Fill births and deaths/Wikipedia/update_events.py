import pywikibot, os
from arywikibotlib import isHuman, getItemPropertyValue, getOnlyArticles, extractYearDay, getMonthName, getItemIdentities
from copy import deepcopy


export = './data/event_dict.json'

INS_FILE = "instance_values.txt"

NEW_INS_FILE = "new_instance_values.txt"

CAT_IGNORE_LIST = ["[[تصنيف:عوام د تقويم لميلادي]]","[[تصنيف:لقرون]]"]

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
FOOTER = "<noinclude>{{شرح}}[[تصنيف:قوالب زادهوم داريجابوت]][[تصنيف:قوالب د توارخ]]</noinclude>"

EVENT_NAME_PREFIX = {'P585':''
                    ,'P571':'بدية/تأسيس ديال '
                    ,'P580':'بدية/تأسيس ديال '
                    ,'P576':'لمسالية/لإلغاء ديال '
                    ,'P582':'لمسالية/لإلغاء ديال '
                    ,'P577':'نشر ديال '
                    }

def get_event_name_prefix(page,property_code):
    instance_value = getItemIdentity(page)
    pass

def load_property_entries_by_date(page,property_code,dict_events_by_date):
    """
    Fills event dictionary using Wikidata properties
    """
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
                event = EVENT_NAME_PREFIX[property_code]+'[['+page.title()+']]'
                if event not in dict_events_by_date[daymonth][year]:
                    flag = False
                    for ev in dict_events_by_date[daymonth][year]:
                        if page.title() in ev:
                            flag = True
                            break
                    if not flag:
                        dict_events_by_date[daymonth][year].append(EVENT_NAME_PREFIX[property_code]+'[['+page.title()+']]')
    return dict_events_by_date

def reverse_dict_events(dict_events_by_date):
    """
    Converts dictionary with daymonth keys first,
    then year keys second, to a dictionary with
    year keys first and daymonth keys second.
    This is necessary to fill year based event
    template pages. 
    """
    dict_events_by_year = {}

    for daymonth, value in dict_events_by_date.items():
        for year, events in value.items():
            if year not in dict_events_by_year.keys():
                dict_events_by_year[year] = {}
            #else:
            #if daymonth not in dict_events_by_year[year].keys():
            dict_events_by_year[year][daymonth] = events


    return dict_events_by_year

def load_instance_values():
    

    if os.path.exists(INS_FILE):
        with open(INS_FILE,'r') as ins:
            return set(ins.read().splitlines())

    return set()

def update_instance_values(instance_values):
    with open(INS_FILE,'a') as new:
        for value in instance_values:
            new.write(value+'\n')

def create_new_instance_value_file(new_instance_values):
    with open(NEW_INS_FILE,'w') as new:
        for value in new_instance_values:
            new.write(value+'\n')
    

def create_and_save_dict_by_date(site):

    dict_events_by_date = {}

    print("Creating working pool")
    pool = getOnlyArticles(site)
    #pool = [page for page in site.allpages() if validate_page(page)]

    pool_size = len(list(deepcopy(getOnlyArticles(site))))
    print('Pool size: '+str(pool_size))
    i = 1
    
    #to collect values of "instance of" for further treatment
    total_instance_values = load_instance_values()
    new_instance_values = set()

    
    print("Running through pages to create event dictionary")
    for page in pool:
        print('*********'+str(i)+'/'+str(pool_size))

        #item = pywikibot.ItemPage.fromPage(page)
        #print(list(item.get()["claims"]['P31']))
        instance_values = getItemIdentities(page)
        instance_values = set(instance_values)

        for value in instance_values:
            if value not in total_instance_values:
                total_instance_values.add(value)
                new_instance_values.add(value)
                
        ignore_flag = False
        for cat in CAT_IGNORE_LIST:
            if cat in page.text:
                i+=1
                ignore_flag = True
        
        if ignore_flag:
            continue
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

    save_dict(dict_events_by_date)

    return dict_events_by_date, total_instance_values, new_instance_values

def save_dict(dict_obj):
    with open(export,'w',encoding='utf-8') as f:
        f.write(str(dict_obj))

def load_dict():
    with open(export,'r',encoding='utf-8') as f:
        dict_obj = eval(f.read())
    return dict_obj

if __name__ == '__main__':

    site = pywikibot.Site()
    #check if data has been saved form previous run
    if os.path.exists(export):
        dict_events_by_date = load_dict()
        new_instance_values = set()
        total_instance_values = load_instance_values()
    else:
        print("creating dictionary")
        dict_events_by_date, total_instance_values, new_instance_values = create_and_save_dict_by_date(site)
        save_dict(dict_events_by_date)
    print("Data loaded")
    
    
    for daymonth, value in dict_events_by_date.items():
        
        title = EVENT_PAGE_PART+str(int(daymonth[:2]))+" "+getMonthName(int(daymonth[2:]))

        page = pywikibot.Page(site,title)

        orig_text = page.text
        
        years = list(value.keys())

        years.sort()

        page.text = STANDARD_BOT_NOTIF

        for year in years:
            if year > 0:
                page.text+="\n* '''"+str(year)+":''' "
            else:
                year = year
                page.text+="\n* '''"+str(abs(year-1))+" "+BC+":''' " #fixed year issue
            page.text+=SEPARATOR.join(value[year])

        page.text+="\n\n"+FOOTER
        if orig_text != page.text:
            page.save(UPDATED_EVENT_LIST_MESSAGE)


    dict_events_by_year = reverse_dict_events(dict_events_by_date)

    print(dict_events_by_year)

    for year, value in dict_events_by_year.items():
        if year < 0:
            year = year -1
            title = EVENT_PAGE_PART+str(abs(year))+" "+BC
        else:
            title = EVENT_PAGE_PART+str(year)

        page = pywikibot.Page(site,title)

        orig_text = page.text
        
        daymonths = sorted(list(value.keys()),key = lambda v:(v[2:],v[:2]))


        page.text = STANDARD_BOT_NOTIF+'\n'+"== حوايج وقعو ==\n"

        for daymonth in daymonths:
            page.text+="\n* '''"+str(int(daymonth[:2]))+" "+getMonthName(int(daymonth[2:]))+":''' "
            page.text+=SEPARATOR.join(value[daymonth])

        page.text+="\n\n"+FOOTER
        if orig_text != page.text:
            page.save(UPDATED_EVENT_LIST_MESSAGE)


    update_instance_values(total_instance_values)
    create_new_instance_value_file(new_instance_values)
        
