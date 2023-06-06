import pywikibot, math
from datetime import datetime

MIN_YEAR = -625
MAX_YEAR = int(datetime.now().year)+5


BIRTH_PAGE_PART = "قالب:ناس تزادو ف"
DEATH_PAGE_PART = "قالب:ناس توفاو ف"
EVENT_PAGE_PART = "قالب:حوايج وقعو ف"
EXPCT_PAGE_PART = "قالب:أحدات مبرمجة ؤلا متوقعة ف"
BC = " قبل لميلاد"
BC_REDUCED = "ق.م"
BH_REDUCED = "ق.هـ"
BCH_REDUCED = "ق.ش"

YEAR_NAV_PTRN = "{{Year nav|{raw_year}}}"
CENT_TEMPLATE_TAG = "{{C{century} year in topic}}"

YEAR = "[[عام]]"
LEAP_YEAR = "[[عام مكبس]]"

CENTURY = "قرن "
DECADE_PART = "عوام "

EN_ARY_DAYS = {"Sunday":"لحد"
              ,"Monday":"تنين"
              ,"Tuesday":"تلات"
              ,"Wednesday":"لاربع"
              ,"Thursday":"لخميس"
              ,"Friday":"جمعة"
              ,"Saturday":"سبت"
              }

ROMAN_PART = "، ؤ {روماني} ف [[تقويم روماني|تّقويم رّوماني]]"

SOURCE = "<ref>{{Cite web|url=https://www.timeanddate.com/calendar/?year={عام}&country=106|title={عام}|language=en}}</ref>"


list_page_parts = [BIRTH_PAGE_PART, DEATH_PAGE_PART, EVENT_PAGE_PART, EXPCT_PAGE_PART]

YEAR_PART = "(عام)"

MAIN_TEXT = """{{Year nav|yy}}
{{C{cent} year in topic}}
'''{عام}''' هوّا {نوع} ف [[تقويم ڭريڭوري|تّقويم لڭريڭوري]] [[عوام ميلاديين بداو نهار {نهار1}|بدا نهار {نهار1}]] ؤ {مسالية} نهار {نهار2}. هوّا لعام نمرة {عام} ف [[إيرا عامة|لإيرا لعامة]] ؤ لفترة د [[بعد لميلاد]]، نمرة {فلقرن} ف [[لقرن {قرن}]]، ؤ نمرة {فلعقد} ف ل[[عقد]] ديال [[عوام {بدية}]].{source}

{عام} كيوافق {إسلامي} ف [[تقويم إسلامي|تّقويم لهيجري]] ؤ {أمازيغي} ف [[تقويم أمازيغي|تّقويم لأمازيغي]] ؤ {هولوسيني} ف [[تقويم هولوسيني|تّقويم لهولوسيني]].

{{ناس تزادو ف {عام}}}

{{ناس توفاو ف {عام}}}

{{حوايج وقعو ف {عام}}}

{{قالب:أحدات مبرمجة ؤلا متوقعة ف {موستقبال}}}

== عيون لكلام ==
{{عيون}}
{{ضبط مخازني}}

[[تصنيف:{عام}]]
[[تصنيف:عوام د تقويم لميلادي]]
[[تصنيف:مقالات زادهوم داريجابوت]]
"""

MAIN_TEXT_BC = """{{Year nav|yy}}
{{CX year in topic}}
'''{عام}''' هوّا عام ف [[تقويم يولياني|تّقويم ليولياني]] ف لفترة د [[قبل لميلاد]]، نمرة {فلقرن} ف [[لقرن {قرن}]]، ؤ نمرة {فلعقد} ف ل[[عقد]] ديال [[عوام {بدية}]].<ref>{{Cite web|url=https://keisan.casio.com/exec/system/1247132711|title=Day of Week Calculator|language=en}}</ref>

{عام} كيوافق {إسلامي} ف [[تقويم إسلامي|تّقويم لهيجري]] ؤ {أمازيغي} ف [[تقويم أمازيغي|تّقويم لأمازيغي]]، ؤ {روماني} ف [[تقويم روماني|تّقويم رّوماني]]، ؤ {هولوسيني} ف [[تقويم هولوسيني|تّقويم لهولوسيني]].

{{ناس تزادو ف {عام}}}

{{ناس توفاو ف {عام}}}

{{حوايج وقعو ف {عام}}}

== عيون لكلام ==
{{عيون}}
{{ضبط مخازني}}

[[تصنيف:{عام}]]
[[تصنيف:عوام د تقويم لميلادي]]
[[تصنيف:مقالات زادهوم داريجابوت]]"""


TMP_PAGE_SAVE_MESSAGE = "پاج ديال لقالب تقادّات خاوية"

PAGE_SAVE_MESSAGE = "پاج د لعام تقادّات"

def get_year_text(year):
    if year > 0:
        return str(year)
    else:
        return str(abs(year))+BC

def is_year_templates_available(site, year):
    
    year_text = get_year_text(year)
    for page_part in list_page_parts:
        title = page_part+" "+year_text
        page = pywikibot.Page(site,title)
        #print(page.title())
        if page.text != "":
            #print(page.title())
            return True

    return False

"""
def get_islamic_year_range(year):
    islamicMult = 1.030684 # the factor to multiply by
    islamicSub = 621.5643 # the factor to subtract by
    if (year - 621) > 0:
	#year1 = math.floor(islamicMult*(year-islamicSub ))
	year1 = math.floor(islamicMult*(year-islamicSub))
	#year2 = math.floor( islamicMult * ( year - islamicSub + 1 ) )
	year2 = math.floor(islamicMult*(year-islamicSub+1))
	return str(year1)+'-'+str(year2)
    else:
	year1 = math.ceil( -islamicMult * ( year - islamicSub ) )
	year2 = math.ceil( -islamicMult * ( year - islamicSub + 1 ) )
	return str(year1)+" "+BH_REDUCED+'-'+str(year2)+" "+BH_REDUCED
"""
def get_islamic_year_range(year):
    mult = 1.030684
    sub = 621.5643
    if year > 621:
        year1 = math.floor(mult * (year - sub))
        year2 = math.floor(mult * (year - sub + 1))
        return str(year1)+'-'+str(year2)
    else:
        year1 = math.ceil(-mult * (year - sub))
        year2 = math.ceil(-mult * (year - sub + 1))
        return str(year1)+" "+BH_REDUCED+'-'+str(year2)+" "+BH_REDUCED

def get_year_type(year):
    if year < 0:
        return YEAR
    elif year % 400 == 0:
        return LEAP_YEAR
    elif year % 100 == 0:
        return YEAR
    elif year % 4 == 0:
        return LEAP_YEAR
    
    return YEAR

def get_start_end_of_year_day_name(year):
    start_year = datetime.strptime('Jan 1 '+str(year).rjust(4,'0'), '%b %d %Y')
    end_year = datetime.strptime('Dec 31 '+str(year).rjust(4,'0'), '%b %d %Y')

    start, end = start_year.strftime("%A"),end_year.strftime("%A")

    return EN_ARY_DAYS[start],EN_ARY_DAYS[end]
    
def get_number_in_century(year):
    if year > 0:
        r = year%100
        return (lambda r:100 if r == 0 else r)(r)
    else:
        return 10 - (year + 1)%10

def get_number_in_decade(year):
    """
    Returns the year number within the decade.
    """
    if year > 9:
        return year%10+1
    elif year > -10:
        return year%10 
    else:
        if year%10 == 0:
            return 10
        else:
            return year%10

def get_decade(year):
    decade_number = abs(year)//10*10
    if year > 0:
        return str(decade_number)
    else:
        return str(decade_number)+BC
    

def get_century(year):
    century_number = abs(year)//100+1
    return (lambda year:str(century_number) if year > 0 else str(century_number)+BC)(year)
    
def get_amazigh_year(year):
    K = 950
    if year > 0:
        return year + K
    elif year < - K:
        return str(year+K+1)+" "+BCH_REDUCED
    else:
        return year + K + 1

def get_holocene_year(year):
    K = 10000
    if year > 0:
        return year + K
    else:
        return year + K + 1

def get_roman_year(year):
    K = 753
    if year > 0:
        return year + K
    elif year < - K:
        return None
    else:
        return year + K + 1

def get_full_text(year):
    if year > 0:
        text = MAIN_TEXT.replace("yy",str(year))
        year_text = str(year)
        start, end = get_start_end_of_year_day_name(year)
        if year >= datetime.now().year:
            end_verb = "غادي يسالي"
            text = text.replace("{موستقبال}",year_text)
        else:
            end_verb = "سالا"
            text = text.replace("{{قالب:أحدات مبرمجة ؤلا متوقعة ف {موستقبال}}}","")
            
        century = int(get_century(year))
        if century > 17:
            cent = str(century)
        else:
            cent = "X"
        text = text.replace("{source}",SOURCE).replace("{عام}",year_text).replace("{نوع}",get_year_type(year)).replace("{نهار1}",start).replace("{مسالية}",end_verb).replace("{نهار2}",end) \
               .replace("{فلقرن}",str(get_number_in_century(year))).replace("{قرن}",str(get_century(year))).replace("{فلعقد}",str(get_number_in_decade(year))) \
               .replace("{بدية}",str(get_decade(year))).replace("{إسلامي}",get_islamic_year_range(year)).replace("{أمازيغي}",str(get_amazigh_year(year))) \
               .replace("{هولوسيني}",str(get_holocene_year(year))).replace("{cent}",cent)
    else:
        text = MAIN_TEXT_BC.replace("yy",str(year))
        year_text = str(abs(year))+BC
        text = text.replace("{عام}",year_text).replace("{نوع}",get_year_type(year)).replace("{فلقرن}",str(get_number_in_century(year))) \
               .replace("{قرن}",str(get_century(year))).replace("{فلعقد}",str(get_number_in_decade(year))) \
               .replace("{بدية}",str(get_decade(year))).replace("{إسلامي}",get_islamic_year_range(year)).replace("{أمازيغي}",str(get_amazigh_year(year))) \
               .replace("{هولوسيني}",str(get_holocene_year(year)))
        roman_year = get_roman_year(year)
        print(roman_year)
        if roman_year is None:
            text = text.replace(ROMAN_PART,"")
        else:
            text = text.replace("{روماني}",str(roman_year))
    
    return text

def run_for_years_list(years, site):
    
    for year in years:
        print(year)
        if is_year_templates_available(site, year):
            year_text = get_year_text(year)
            print(year_text)
            if year < 32 and year > 0:
                year_text2 = year_text+" "+YEAR_PART
                page = pywikibot.Page(site,year_text2)
            else:
                page = pywikibot.Page(site,year_text)
            if page.text == "":
            
                for page_part in list_page_parts[:-1]:
                    title = page_part+" "+year_text
                    tmp_page = pywikibot.Page(site,title)
                    if tmp_page.text == "":
                        tmp_page.text = ""
                        tmp_page.save(TMP_PAGE_SAVE_MESSAGE)
                
                page.text = get_full_text(year).strip().replace("\n\n\n","\n")
                page.save(PAGE_SAVE_MESSAGE)

if __name__ == '__main__':
    years = list(range(1,MAX_YEAR+1))
    
    site = pywikibot.Site()
    
    
    run_for_years_list(years, site)

    years = list(range(MIN_YEAR,0))
    #print(years)

    run_for_years_list(years, site)

    
            
    #"""
