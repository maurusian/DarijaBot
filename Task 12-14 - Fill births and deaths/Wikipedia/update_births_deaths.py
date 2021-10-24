from openpyxl import Workbook, load_workbook
import re
import pywikibot
from pgvbotLib import *
from urllib.request import urlopen, quote, Request
from urllib.error import URLError
import json, sys, os
#import SPARQLWrapper
import requests

date_pattern = r'[-]{0,1}[0-9]+-[0-9]+-[0-9]+'
#print(re.match(date_pattern,'t2391385487'))

filename = './data/query.sparql'

export = './data/dict_list.json'

BIRTH_PAGE_PART = "قالب:ناس تزادو ف"
DEATH_PAGE_PART = "قالب:ناس توفاو ف"
BOT_NOTICE = "<noinclude>{{پاج كيعمرها بوت}}</noinclude>"
DARIJABOT_CAT = "<noinclude>[[تصنيف:قوالب زادهوم داريجابوت]]</noinclude>"
SAVE_MESSAGE = "لپاج تعمّرات ب معلومات من ويكيداطا"
BC = "ق.م."
NAME_SEPARATOR = " {{•}} "

TIMEQUERY = """
SELECT ?time ?timeprecision
WHERE
{ SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
     { wd:{1}  p:{2}/psv:{2} ?timenode. }
     ?timenode wikibase:timeValue         ?time.
     ?timenode wikibase:timePrecision     ?timeprecision.
     
}
"""

#added to corresponding person page and potentially created
BIRTH_YEAR_CAT_PATTERN = "تصنيف:زيادة {year}{BC}"
DEATH_YEAR_CAT_PATTERN = "تصنيف:وفيات {year}{BC}"

#added to corresponding year cat page and potentially created
MAIN_YEAR_CAT_PATTERN = "تصنيف:{year}{BC}"

#added to all main year cat pages
GENERAL_YEAR_CAT = "تصنيف:لعوام"

#added to all year cat pages of the same type
BIRTHS_BY_YEAR_CAT = "تصنيف:زيادات علا حساب لعام"
DEATHS_BY_YEAR_CAT = "تصنيف:وفيات علا حساب لعام"

#added to corresponding year cat pages of the same type and potentially created (should be calculated)
BIRTH_DECADE_CAT_PATTERN = "تصنيف:زيادة ف عوام {decade}{BC}"
DEATH_DECADE_CAT_PATTERN = "تصنيف:وفيات ف عوام {decade}{BC}"

#added to corresponding decade cat page
MAIN_DECADE_CAT_PATTERN = "تصنيف:عوام {decade}{BC}"

#added to all main decade cat pages
GENERAL_DECADE_CAT = "تصنيف:لعقود"

#added to all decade cat pages of the same type
BIRTHS_BY_DECADE_CAT = "تصنيف:زيادات علا حساب لعقد"
DEATHS_BY_DECADE_CAT = "تصنيف:وفيات علا حساب لعقد"

#added to corresponding decade pages of the same type and potentially created (should be calculated)
BIRTH_CENT_CAT_PATTERN = "تصنيف:زيادة ف لقرن {century}{BC}"
DEATH_CENT_CAT_PATTERN = "تصنيف:وفيات ف لقرن {century}{BC}"

#added to corresponding century cat page
MAIN_CENT_CAT_PATTERN = "تصنيف:لقرن {century}{BC}"

#added to all century cat pages of the same type
BIRTHS_BY_CENT_CAT = "تصنيف:زيادات علا حساب لقرن"
DEATHS_BY_CENT_CAT = "تصنيف:وفيات علا حساب لقرن"

#added to all main century cat pages
GENERAL_CENT_CAT = "تصنيف:لقرون"

#added to corresponding century pages of the same type and potentially created (should be calculated)
BIRTH_MILN_CAT_PATTERN = "تصنيف:زيادات ف لألفية {millennium}{BC}"
DEATH_MILN_CAT_PATTERN = "تصنيف:وفيات ف لألفية {millennium}{BC}"

MAIN_MILN_CAT_PATTERN = "تصنيف:لألفية {millennium}{BC}"


CAT_ADDED_MESSAGE = "تصنيف تزاد"
CAT_PAGE_CREATED_MSG = "پاج د تّصنيف تقادات"
CAT_FIXED_MESSAGE = "تّصنيف تّصلح"

DARIJABOT_CAT_CATEGORY_PAGE = "[[تصنيف:تصنيفات زادهوم داريجابوت]]"

BC = " قبل لميلاد"

CENTURY_NUM_NAMES = {1:'لول'
                    ,2:'تاني'
                    ,3:'تالت'
                    ,4:'رابع'
                    ,5:'لخامس'
                    ,6:'سات'
                    ,7:'سابع'
                    ,8:'تامن'
                    ,9:'تاسع'
                    ,10:'لعاشر'
                    ,11:'لحاضش'
                    ,12:'طناش'
                    ,13:'تلطاش'
                    ,14:'ربعطاش'
                    ,15:'خمسطاش'
                    ,16:'سطاش'
                    ,17:'سبعطاش'
                    ,18:'تمنطاش'
                    ,19:'تسعطاش'
                    ,20:'لعشرين'
                    ,21:'لواحد ؤ عشرين'
                    ,22:'تنين ؤ عشرين'
                    ,23:'تلاتة ؤ عشرين'
                    ,24:'ربعة عشرين'
                    ,25:'خمسة ؤ عشرين'
                    ,26:'ستة ؤ عشرين'
                    ,27:'سبعة ؤ عشرين'
                    ,28:'تمنية ؤ عشرين'
                    ,29:'تسعود ؤ عشرين'
                    ,30:'تلاتين'
                    }

MILLENIUM_NUM_NAMES = {1:'لولة'
                      ,2:'تانية'
                      ,3:'تالتة'
                      ,4:'رابعة'}


def BC_value(year):
    if year < 0:
        return BC
    else:
        return ""

def get_decade_value(year):
    return year - year%10

def get_century_value(year):
    
    century_num = year//100
    if year%100 != 0:
        century_num += 1
    return CENTURY_NUM_NAMES[century_num]

def get_millennium_value(year):
    millennium_num = year//1000
    if year%1000 != 0:
        millennium_num += 1
    return MILLENIUM_NUM_NAMES[millennium_num]

def get_precision(objectCode,date_type,date):
    #print(objectCode)
    #print(date_type)
    #print(date)
    query = TIMEQUERY.replace('{1}',objectCode).replace('{2}',date_type)
    #print(query)
    url = "https://darijabot@query.wikidata.org/sparql?query=%s&format=json" % quote(query)
    #headers are necessary, without user-agent the Wikidata server refuses to connect, and without the charset ensues a Unicode error
    headers = {
        'User-Agent': 'DarijaBot/0.1 (Edition Windows 10 Home, Version 20H2, OS build 19042.1165, Windows Feature Experience Pack 120.2212.3530.0) Python3.9.0',
        'Content-Type': 'text/text; charset=utf-8'
    }
    response = requests.get(url, headers=headers)
    res      = response.json()
    
    if response is not None:
        #res = json.loads(response)
        res      = response.json()
        #print(res)
        values = []
        for i in range(len(res['results']['bindings'])):
            if res['results']['bindings'][i]['time']['value'] == date:

                values.append(int(res['results']['bindings'][i]['timeprecision']['value']))
        if len(values)>0:
            return max(values)
    
    return 0

def simplify_json(jason):
    """
    Converts json response from Wikidata server into a simpler dictionary list,
    that only has the required values.
    """
    dict_list = []
    
    for i in range(len(jason['results']['bindings'])):
        #print(i)
        #print(jason['results']['bindings'][i]['personLabel']['value'])
        dict_list.append({})
        dict_list[i]['personLabel']    = jason['results']['bindings'][i]['personLabel']['value']
        try:
            dict_list[i]['dateOfBirth']    = jason['results']['bindings'][i]['dateOfBirth']['value']
            
        except KeyError:
            #print('Date of Birth not available for '+jason['results']['bindings'][i]['personLabel']['value'])
            #print(sys.exc_info())
            pass
        if 'dateOfBirth' in dict_list[i].keys():
            objectCode = jason['results']['bindings'][i]['person']['value'].split('/')[-1]
            date_type  = 'P569'
            date       = dict_list[i]['dateOfBirth']
            try:
                dict_list[i]['birthPrecision'] = get_precision(objectCode,date_type,date)
            except:
                dict_list[i]['birthPrecision'] = 0
        try:
            if 'dateOfDeath' in jason['results']['bindings'][i].keys():
                dict_list[i]['dateOfDeath']    = jason['results']['bindings'][i]['dateOfDeath']['value']
            
        except KeyError:
            #print('Date of Death not available for '+jason['results']['bindings'][i]['personLabel']['value'])
            #print(sys.exc_info())
            pass
        if 'dateOfDeath' in dict_list[i].keys():
            objectCode = jason['results']['bindings'][i]['person']['value'].split('/')[-1]
            date_type  = 'P570'
            date       = dict_list[i]['dateOfDeath']
            try:
                dict_list[i]['deathPrecision'] = get_precision(objectCode,date_type,date)
            except:
                dict_list[i]['deathPrecision'] = 0
    return dict_list


def wikidata_rest_query(filename):
    with open(filename,'r',encoding='utf8') as f:
        query = f.read()
    #headers are necessary, without user-agent the Wikidata server refuses to connect, and without the charset ensues a Unicode error
    headers = {
        'User-Agent': 'DarijaBot/0.1 (Edition Windows 10 Home, Version 20H2, OS build 19042.1165, Windows Feature Experience Pack 120.2212.3530.0) Python3.9.0',
        'Content-Type': 'text/text; charset=utf-8'
    }
    url = "https://query.wikidata.org/sparql?query=%s&format=json" % quote(query)
    response = requests.get(url, headers=headers)
    return response.json()

def get_dict_by_new_key(key_index,value_index,raw_dict,min_prec):
    """
    Transforms raw_dict into a new dictionary with one of
    the elements of the value in raw_dict as the new key.
    The old key and the rest of the value elements form
    a list of tuples that are the value of new_dict.

    Input:
    - key_index
    - value_index
    - raw_dict
    - min_prec
    """
    new_dict = {}
    for key,value in raw_dict.items():
        if len(value)== 1:
            #make sure the precision is at least equal to min_prec, for daymonth values if it is different from 1 January, the precision doesn't matter
            if (key_index == 0 and value[0][2] >= min_prec) or (key_index == 1 and (value[0][key_index]!='0101' or value[0][2] >= min_prec)):
                if value[0][key_index] not in new_dict.keys():
                    new_dict[value[0][key_index]] = []
                new_dict[value[0][key_index]].append((key,value[0][value_index]))
        elif len(value)>1:
            for v in value:
                #make sure the precision is at least equal to min_prec, for daymonth values if it is different from 1 January, the precision doesn't matter
                if (key_index == 0 and v[2] >= min_prec) or (key_index == 1 and (v[key_index]!='0101' or v[2] >= min_prec)):
                    if v[key_index] not in new_dict.keys():
                         new_dict[v[key_index]] = []
                    new_dict[v[key_index]].append((key,v[value_index]))
                    
    return new_dict

def get_daymonth(key):
    """
    """
    day_number = key[2:]
    if day_number[0] == '0':
        day_number = day_number[-1]
    month_number = int(key[:2])
    month = MONTHS[month_number-1]['ary_name']

    return day_number+' '+month
    
def save_dict_list(dict_list):
    with open(export,'w',encoding='utf-8') as f:
        f.write(str(dict_list))

def load_dict_list():
    with open(export,'r',encoding='utf-8') as f:
        dict_list = eval(f.read())
    return dict_list


def create_add_all_categories(site,_type,year,title):
    abs_year = abs(year)
    #print('Year: '+str(abs(year)))
    #print('BC: '+BC_value(year))
    MAIN_YEAR_CAT = MAIN_YEAR_CAT_PATTERN.replace('{year}',str(abs_year)).replace('{BC}',BC_value(year))
    MAIN_DECADE_CAT = MAIN_DECADE_CAT_PATTERN.replace('{decade}',str(get_decade_value(abs_year))).replace('{BC}',BC_value(year))
    MAIN_CENT_CAT = MAIN_CENT_CAT_PATTERN.replace('{century}',str(get_century_value(abs_year))).replace('{BC}',BC_value(year))
    MAIN_MILN_CAT = MAIN_MILN_CAT_PATTERN.replace('{millennium}',str(get_millennium_value(abs_year))).replace('{BC}',BC_value(year))

    if _type == 'b':
        YEAR_CAT = BIRTH_YEAR_CAT_PATTERN.replace('{year}',str(abs_year)).replace('{BC}',BC_value(year))
        
        DECADE_CAT = BIRTH_DECADE_CAT_PATTERN.replace('{decade}',str(get_decade_value(abs_year))).replace('{BC}',BC_value(year))
        
        CENT_CAT = BIRTH_CENT_CAT_PATTERN.replace('{century}',str(get_century_value(abs_year))).replace('{BC}',BC_value(year))
        
        MILN_CAT = BIRTH_MILN_CAT_PATTERN.replace('{millennium}',str(get_millennium_value(abs_year))).replace('{BC}',BC_value(year))

        BY_YEAR_CAT = BIRTHS_BY_YEAR_CAT

        BY_DECADE_CAT = BIRTHS_BY_DECADE_CAT

        BY_CENT_CAT = BIRTHS_BY_CENT_CAT
        
        
    elif _type == 'd':
        YEAR_CAT = DEATH_YEAR_CAT_PATTERN.replace('{year}',str(abs_year)).replace('{BC}',BC_value(year))
        
        DECADE_CAT = DEATH_DECADE_CAT_PATTERN.replace('{decade}',str(get_decade_value(abs_year))).replace('{BC}',BC_value(year))
        
        CENT_CAT = DEATH_CENT_CAT_PATTERN.replace('{century}',str(get_century_value(abs_year))).replace('{BC}',BC_value(year))
        
        MILN_CAT = DEATH_MILN_CAT_PATTERN.replace('{millennium}',str(get_millennium_value(abs_year))).replace('{BC}',BC_value(year))

        BY_YEAR_CAT = DEATHS_BY_YEAR_CAT

        BY_DECADE_CAT = DEATHS_BY_DECADE_CAT

        BY_CENT_CAT = DEATHS_BY_CENT_CAT
        
    else:
        print("Unknown type value in function create_add_all_categories")
        return None

    #update person page
    page = pywikibot.Page(site,title)
    if page.text != '':
        if '[['+YEAR_CAT+']]' not in page.text:
            page.text+='\n[['+YEAR_CAT+']]'
            save_page(page,CAT_ADDED_MESSAGE)
    else:
        print('Page '+title+' not found!') #replace with log line

    #create or update birth/death year category page
    page = pywikibot.Page(site,YEAR_CAT)

    if page.text == '':
        page.text = '[['+BY_YEAR_CAT+']]\n'+'[['+DECADE_CAT+']]\n'+'[['+MAIN_YEAR_CAT+']]\n'+DARIJABOT_CAT_CATEGORY_PAGE
        save_page(page,CAT_PAGE_CREATED_MSG)
    else:
        temp = page.text
        if BY_YEAR_CAT not in page.text:
            page.text += '\n[['+BY_YEAR_CAT+']]'
        if DECADE_CAT not in page.text:
            page.text += '\n[['+DECADE_CAT+']]'
        if MAIN_YEAR_CAT not in page.text:
            page.text += '\n[['+MAIN_YEAR_CAT+']]'
        if temp != page.text:
            save_page(page,CAT_ADDED_MESSAGE)

    #create or update main year category page
    page = pywikibot.Page(site,MAIN_YEAR_CAT)

    if page.text == '':
        page.text = '[['+GENERAL_YEAR_CAT+']]\n'+'[['+MAIN_DECADE_CAT+']]\n'+DARIJABOT_CAT_CATEGORY_PAGE
        save_page(page,CAT_PAGE_CREATED_MSG)
    
    #create or update birth/death decade category page
    page = pywikibot.Page(site,DECADE_CAT)

    if page.text == '':
        page.text = '[['+BY_DECADE_CAT+']]\n'+'[['+CENT_CAT+']]\n'+'[['+MAIN_DECADE_CAT+']]\n'+DARIJABOT_CAT_CATEGORY_PAGE
        save_page(page,CAT_PAGE_CREATED_MSG)

    #create or update main decade category page
    page = pywikibot.Page(site,MAIN_DECADE_CAT)

    if page.text == '':
        page.text = '[['+GENERAL_DECADE_CAT+']]\n'+'[['+MAIN_CENT_CAT+']]\n'+DARIJABOT_CAT_CATEGORY_PAGE
        save_page(page,CAT_PAGE_CREATED_MSG)

    #create or update birth/death century category page
    page = pywikibot.Page(site,CENT_CAT)

    if page.text == '':
        page.text = '[['+BY_CENT_CAT+']]\n'+'[['+MILN_CAT+']]\n'+'[['+MAIN_CENT_CAT+']]\n'+DARIJABOT_CAT_CATEGORY_PAGE
        save_page(page,CAT_PAGE_CREATED_MSG)

    #create or update main century category page
    page = pywikibot.Page(site,MAIN_CENT_CAT)

    if page.text == '':
        page.text = '[['+GENERAL_CENT_CAT+']]\n'+'[['+MAIN_MILN_CAT+']]\n'+DARIJABOT_CAT_CATEGORY_PAGE
        save_page(page,CAT_PAGE_CREATED_MSG)

#load data from Wikidata
print("Loading data from Wikidata")
if os.path.exists(export):
    dict_list = load_dict_list()
else:
    dict_list = simplify_json(wikidata_rest_query(filename))
    save_dict_list(dict_list)
print("Data loaded")



dict_by_person_birth = {}
dict_by_person_death = {}

for i in range(len(dict_list)):
    if ('dateOfBirth' in dict_list[i].keys() and dict_list[i]['dateOfBirth'] != ''):
        if dict_list[i]['personLabel'] not in dict_by_person_birth.keys():
            dict_by_person_birth[dict_list[i]['personLabel']] = []
        fulldob = dict_list[i]['dateOfBirth'].split('T')[0]
        #print(dict_list[i]['dateOfBirth'])
        #print(fulldob)
        if re.match(date_pattern,fulldob):
            if 'birthPrecision' in dict_list[i].keys():
                print("adding birth date precision")
                prec = dict_list[i]['birthPrecision']
            else:
                prec = 0
            
            if fulldob[0] == '-':
                year = 0-int(fulldob.split('-')[1])
                #print((year,fulldob[-5:].replace('-','')))
            else:
                year = int(fulldob.split('-')[0])
            tupl = (year,fulldob[-5:].replace('-',''),prec)
            if tupl not in dict_by_person_birth[dict_list[i]['personLabel']]:
                dict_by_person_birth[dict_list[i]['personLabel']].append(tupl)
        


    if ('dateOfDeath' in dict_list[i].keys() and dict_list[i]['dateOfDeath'] != ''):
        if dict_list[i]['personLabel'] not in dict_by_person_death.keys():
            dict_by_person_death[dict_list[i]['personLabel']] = []

        fulldod = dict_list[i]['dateOfDeath'].split('T')[0]
        if re.match(date_pattern,fulldod):
            if 'deathPrecision' in dict_list[i].keys():
                print("adding death date precision")
                prec = dict_list[i]['deathPrecision']
            else:
                prec = 0
            if fulldod[0] == '-':
                year = 0-int(fulldod.split('-')[1])
                #print((year,fulldod[-5:].replace('-','')))
            else:
                year = int(fulldod.split('-')[0])
        
            tupl = (year,fulldod[-5:].replace('-',''),prec)
            if tupl not in dict_by_person_death[dict_list[i]['personLabel']]:
                dict_by_person_death[dict_list[i]['personLabel']].append(tupl)

#print(dict_by_person_birth['لويس أنطوان دو بوݣانڤيل'])

    
dict_by_day_birth = get_dict_by_new_key(1,0,dict_by_person_birth,11)
#print(dict_by_day_birth)

for key, value in dict_by_day_birth.items():
    dict_by_day_birth[key] = sorted(value,key=lambda x:x[1])

dict_by_day_death = get_dict_by_new_key(1,0,dict_by_person_death,11)
#print(dict_by_day_death)

for key, value in dict_by_day_death.items():
    dict_by_day_death[key] = sorted(value,key=lambda x:x[1])

dict_by_year_birth = get_dict_by_new_key(0,1,dict_by_person_birth,9)
#print(dict_by_year_birth)

for key, value in dict_by_year_birth.items():
    dict_by_year_birth[key] = sorted(value,key=lambda x:x[1])

print(dict_by_year_birth)

dict_by_year_death = get_dict_by_new_key(0,1,dict_by_person_death,9)
#print(dict_by_year_death)

for key, value in dict_by_year_death.items():
    dict_by_year_death[key] = sorted(value,key=lambda x:x[1])


site = pywikibot.Site()

current_year = None
for key, value in dict_by_day_birth.items():
    if len(key) == 4:
        #print(key)
        daymonth = get_daymonth(key)
        title = BIRTH_PAGE_PART+' '+daymonth
        page = pywikibot.Page(site,title)
        temp = page.text #temporary variable to compare
        text = BOT_NOTICE+'\n\n'
        name_list = []
        current_year = value[0][1]
        for v in value:
            
            if current_year != v[1]:
                
                #print(current_year)
                text+= '\n* '
                if current_year < 0:
                    text+="'''"+str(0-current_year)+" "+BC+":''' "
                    print(str(0-current_year))
                else:
                    text+="'''"+str(current_year)+":''' "
                #print('namelist: '+str(name_list))
                if len(name_list)>0:
                    text+=NAME_SEPARATOR.join(["[["+name+"]]" for name in name_list])
                name_list = []
                current_year = v[1]
            name_list.append(v[0])   
            
            #text+= '* [['+v[0]+']]\n'
        text+= '\n* '
        if current_year < 0:
            text+="'''"+str(0-current_year)+" "+BC+":''' "
            print(str(0-current_year))
        else:
            text+="'''"+str(current_year)+":''' "
        if len(name_list)>0:
            text+=NAME_SEPARATOR.join(["[["+name+"]]" for name in name_list])
        if temp != text:
            #text+='\n'+DARIJABOT_CAT
            page.text = text
            #print(text)
            save_page(page,SAVE_MESSAGE)

    else:
        print("Invalid key: "+key+" for record "+str(value))

    

for key, value in dict_by_day_death.items():
    if len(key) == 4:
        #print(key)
        daymonth = get_daymonth(key)
        title = DEATH_PAGE_PART+' '+daymonth
        page = pywikibot.Page(site,title)
        temp = page.text #temporary variable to compare
        text = BOT_NOTICE+'\n\n'
        name_list = []
        current_year = value[0][1]
        for v in value:
            
            if current_year != v[1]:
                
                #print(current_year)
                text+= '\n* '
                if current_year < 0:
                    text+="'''"+str(0-current_year)+" "+BC+":''' "
                    print(str(0-current_year))
                else:
                    text+="'''"+str(current_year)+":''' "
                #print('namelist: '+str(name_list))
                if len(name_list)>0:
                    text+=NAME_SEPARATOR.join(["[["+name+"]]" for name in name_list])
                name_list = []
                current_year = v[1]
            name_list.append(v[0])
                
            
            #text+= '* [['+v[0]+']]\n'
        text+= '\n* '
        if current_year < 0:
            text+="'''"+str(0-current_year)+" "+BC+":''' "
            print(str(0-current_year))
        else:
            text+="'''"+str(current_year)+":''' "
        if len(name_list)>0:
            text+=NAME_SEPARATOR.join(["[["+name+"]]" for name in name_list])
        if temp != text:
            #text+='\n'+DARIJABOT_CAT
            page.text = text
            #print(text)
            save_page(page,SAVE_MESSAGE)

    else:
        print("Invalid key: "+key+" for record "+str(value))


for key, value in dict_by_year_birth.items():
    year = key
    for v in value:
        name = v[0]
        create_add_all_categories(site=site,_type='b',year=year,title=name)
        


for key, value in dict_by_year_death.items():
    year = key
    for v in value:
        name = v[0]
        create_add_all_categories(site=site,_type='d',year=year,title=name)
"""

for i in range(-600,2022):
    abs_year = abs(i)
    year = i
    title = DEATH_YEAR_CAT_PATTERN.replace('{year}',str(abs_year)).replace('{BC}',BC_value(year))
    page = pywikibot.Page(site,title)
    temp = page.text
    if page.text != '':
        page.text = page.text.replace(BIRTHS_BY_YEAR_CAT,DEATHS_BY_YEAR_CAT)
        if temp != page.text:
            save_page(page,CAT_FIXED_MESSAGE)

for i in range(-600,2022,10):
    abs_decade = abs(i)
    year = i
    title = DEATH_DECADE_CAT_PATTERN.replace('{decade}',str(abs_decade)).replace('{BC}',BC_value(year))
    page = pywikibot.Page(site,title)
    temp = page.text
    if page.text != '':
        page.text = page.text.replace(BIRTHS_BY_DECADE_CAT,DEATHS_BY_DECADE_CAT)
        if temp != page.text:
            save_page(page,CAT_FIXED_MESSAGE)
    
for century in CENTURY_NUM_NAMES.values():
    title = DEATH_CENT_CAT_PATTERN.replace('{century}',century).replace('{BC}',"")
    page = pywikibot.Page(site,title)
    temp = page.text
    if page.text != '':
        page.text = page.text.replace(BIRTHS_BY_CENT_CAT,DEATHS_BY_CENT_CAT)
        if temp != page.text:
            save_page(page,CAT_FIXED_MESSAGE)

    title = DEATH_CENT_CAT_PATTERN.replace('{century}',century).replace('{BC}',BC)
    page = pywikibot.Page(site,title)
    temp = page.text
    if page.text != '':
        page.text = page.text.replace(BIRTHS_BY_CENT_CAT,DEATHS_BY_CENT_CAT)
        if temp != page.text:
            save_page(page,CAT_FIXED_MESSAGE)
"""
