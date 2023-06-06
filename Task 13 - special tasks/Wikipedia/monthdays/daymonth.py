from lib.pgvbotLib import *
from lib.params import *
import pywikibot
#from copy import deepcopy
#import re
#from openpyxl import Workbook



site = pywikibot.Site()

# set month constants
MONTHS = [{"en_name":"January","ary_name":u"يناير","day_count":31,"alt_name":""}
         ,{"en_name":"February","ary_name":u"فبراير","day_count":29,"alt_name":u"يبراير"}
         ,{"en_name":"March","ary_name":u"مارس","day_count":31,"alt_name":""}
         ,{"en_name":"April","ary_name":u"أبريل","day_count":30,"alt_name":""}
         ,{"en_name":"May","ary_name":u"ماي","day_count":31,"alt_name":""}
         ,{"en_name":"June","ary_name":u"يونيو","day_count":30,"alt_name":""}
         ,{"en_name":"July","ary_name":u"يوليوز","day_count":31,"alt_name":""}
         ,{"en_name":"August","ary_name":u"غشت","day_count":31,"alt_name":""}
         ,{"en_name":"September","ary_name":u"شتنبر","day_count":30,"alt_name":""}
         ,{"en_name":"October","ary_name":u"أكتوبر","day_count":31,"alt_name":u"كتوبر"}
         ,{"en_name":"November","ary_name":u"نونبر","day_count":30,"alt_name":""}
         ,{"en_name":"December","ary_name":u"دجنبر","day_count":31,"alt_name":""}]

# set string constants
OPENING_TEMPLATE_TAG = "{{"
CLOSING_TEMPLATE_TAG = "}}"
CLOSING_CAT_TAG = "]]"
DAL = "د"

CALENDAR_TAG_PART = u"{{التقويم المعدل|شهر="
START_FIRST_SENTENCE_PATTERN = "'''{} {}'''"
REST_FIRST_SENTENCE_PATTERN = u"ؤلا '''نهار {} شهر {}''' هوّا نّهار نمرة {} من [[تقويم ݣريݣوري|تّقويم لميلادي]] ({} يلا كان [[عام مكبس|لعام مكبّس]])."
ADDITIONAL_SENTENCE_FORM_0 = u"هاد [[يوم|نّهار]] هوّا لّخر ف لعام."
ADDITIONAL_SENTENCE_FORM_1 = u"باقي [[يوم|نهار]] واحد من موراه تال لّخر د لعام."
ADDITIONAL_SENTENCE_FORM_2 = u"باقين [[يوم|يوماين]] من موراه تال لّخر د لعام."
ADDITIONAL_SENTENCE_FORM_3 = u"باقين {} [[يوم|يّام]] من موراه تال لّخر د لعام."
ADDITIONAL_SENTENCE_FORM_MANY = u"باقين {} يوم من موراه تال لّخر د لعام"

LEAP_YEAR_ADDITIONAL = u"({} يلا كان لعام مكبّس)"

REF_TEXT = u'<ref name="isotr">{{Cite web|url=https://web.archive.org/web/*/https://isotropic.org/date/|title=أرشيڤ ديال نهارات لعام}}</ref>'

COMMONS_CAT_PART = "{{Commons category|"

BIRTH_TITLE = u"== ناس تزادو =="
DEATH_TITLE = u"== ناس توفاو =="
EVENT_TITLE = u"== حوايج وقعو =="
HOLID_TITLE = u"== أعياد ؤ عطلات =="

QUASI_FOOTER = u"""
== عيون لكلام ==

{{عيون}}

{{زريعة}}

{{ضبط مخازني}}

{{شهورا}}
"""

CATEGORY_PART = u"[[تصنيف:"
DARIJABOT_ADDED_REDIRECTS_CATEGORY = u"[[تصنيف:تحويلات زادهوم داريجابوت]]"
DARIJABOT_ADDED_TEMPLATE_CATEGORY = u"[[تصنيف:قوالب زادهوم داريجابوت]]"
DARIJABOT_ADDED_ARTICLE_CATEGORY = u"[[تصنيف:مقالات زادهوم داريجابوت]]"

DAYS_OF_THE_YEAR_CAT = u"[[تصنيف:نهارات د لعام]]"

DATE_BOT_TEMPLATE_CATEGORY = u"[[تصنيف:قوالب زادهوم داريجابوت]][[تصنيف:قوالب د توارخ]]"

## set template and page title patterns
TEMPLATE_NAMESPACE = u"قالب:"
DEATH_DATES_TEMPLATE_TITLE_PART = u"ناس توفاو ف "
BIRTH_DATES_TEMPLATE_TITLE_PART = u"ناس تزادو ف "
EVENT_DATES_TEMPLATE_TITLE_PART = u"حوايج وقعو ف "
HOLID_DATES_TEMPLATE_TITLE_PART = u"أعياد و عطلات ف "

## save messages
TEMPLATE_CREATED_MESSAGE = u"پاج د لقالب تقادات"
TEMPLATE_UPDATED_MESSAGE = u"إصلاح د لمحتوى د لقالب"
TEMPLATE_MOVED_MESSAGE = u"پاج د لقالب تحولات"
TEMPLATE_REDIRECT_CREATED_MESSAGE = u"تّحويلة د لقالب تقادات"
TEMPLATE_CAT_ADDED_MESSAGE = u"تزاد تصنيف د لقالب"
PAGE_ADDED_MESSAGE = u"لپاج تقادات"
DOC_TEMPLATE_CREATED_MESSAGE = u"شّرح د لقالب تزاد"

DOC_PAGE_MESSAGE = """هاد لقالب مديور باش يتليستاو فيه {0} لي طراو نهار {1}.

هاد لقالب كيتزاد ف مقال [[{1}]] ف فقرة "[[{1}#{2}|{2}]]"، ؤ مامديورش باش يتبدّل ب ليد. يلا بدّلتي فيه، توقع بلي تّعديلات غادي غادي تّحيّد معا لأپدييت جّاي.

من لأحسن تزيد لموضوع لي بغيتيه يبان هنا ف ويكيپيديا ب دّاريجة، ؤ تربطو ب صّفحة لمناسبة ف ويكيداطا (شوف [[مساعدة:صفحة لمعاونة|صّفحة د لمعاونة]])."""

DOC_PAGE_MESSAGE_2 = """هاد لقالب مديور باش يتليستاو فيه لعياد لي كيحتافلو بيهوم نّاس ف شي بلاد ؤلا تقافة نهار {0}.

هاد لقالب كيتزاد ف مقال [[{0}]] ف فقرة "[[{0}#أعياد ؤ عطلات|عياد ؤ عطلات]]". يلا بان ليك شي عيد ف هاد نّهار ديال شي بلاد ؤلا تقافة ناقص، تقدر تزيدو."""

BIRTH_STR = u"زّيادات"
DEATH_STR = u"لوفيات"
EVENT_STR = u"لأحدات"

# help functions
def get_day_numbers_in_year(month_number,day_in_month_number):
    print("calculating")
    j = 0
    day_in_year_number = day_in_month_number
    while(j<month_number-1):
        day_in_year_number+=MONTHS[j]['day_count']
        j+=1
    if j>1:
        return day_in_year_number-1,day_in_year_number
    return day_in_year_number,day_in_year_number

for i in range(len(MONTHS)):
    month_number = i+1
    for day_number in range(1,MONTHS[i]['day_count']+1):
        birth_template_page_title = TEMPLATE_NAMESPACE+BIRTH_DATES_TEMPLATE_TITLE_PART+str(day_number)+' '+MONTHS[i]['ary_name']
        page = pywikibot.Page(site,birth_template_page_title)
        # add templates if not exist
        if page.text == "":
            page.text = DATE_BOT_TEMPLATE_CATEGORY
            page.save(TEMPLATE_CREATED_MESSAGE)
        else:
            page.text = page.text.replace("[[تصنيف:قوالب زادهوم داريجابوت]]",'')
            page.text = page.text.replace("[[تصنيف:قوالب د توارخ]]",'')
            page.text = page.text.replace('{{شرح}}','{{شرح}}'+DATE_BOT_TEMPLATE_CATEGORY)
            page.save(TEMPLATE_UPDATED_MESSAGE)

        birth_doc_template_page_title = birth_template_page_title+'/شرح'
        page = pywikibot.Page(site,birth_doc_template_page_title)
        if page.text == "":
            page.text = DOC_PAGE_MESSAGE.format(BIRTH_STR,str(day_number)+' '+MONTHS[i]['ary_name'],BIRTH_TITLE.replace('==','').strip())
            page.save(DOC_TEMPLATE_CREATED_MESSAGE)

        death_template_page_title = TEMPLATE_NAMESPACE+DEATH_DATES_TEMPLATE_TITLE_PART+str(day_number)+' '+MONTHS[i]['ary_name']
        page = pywikibot.Page(site,death_template_page_title)
        # add templates if not exist
        if page.text == "":
            page.text = DATE_BOT_TEMPLATE_CATEGORY
            page.save(TEMPLATE_CREATED_MESSAGE)
        else:
            page.text = page.text.replace("[[تصنيف:قوالب زادهوم داريجابوت]]",'')
            page.text = page.text.replace("[[تصنيف:قوالب د توارخ]]",'')
            page.text = page.text.replace('{{شرح}}','{{شرح}}'+DATE_BOT_TEMPLATE_CATEGORY)
            page.save(TEMPLATE_UPDATED_MESSAGE)

        death_doc_template_page_title = death_template_page_title+'/شرح'
        page = pywikibot.Page(site,death_doc_template_page_title)
        if page.text == "":
            page.text = DOC_PAGE_MESSAGE.format(DEATH_STR,str(day_number)+' '+MONTHS[i]['ary_name'],DEATH_TITLE.replace('==','').strip())
            page.save(DOC_TEMPLATE_CREATED_MESSAGE)

        event_template_page_title = TEMPLATE_NAMESPACE+EVENT_DATES_TEMPLATE_TITLE_PART+str(day_number)+' '+MONTHS[i]['ary_name']
        page = pywikibot.Page(site,event_template_page_title)
        # add templates if not exist
        if page.text == "":
            page.text = DATE_BOT_TEMPLATE_CATEGORY
            page.save(TEMPLATE_CREATED_MESSAGE)
        else:
            page.text = page.text.replace("[[تصنيف:قوالب زادهوم داريجابوت]]",'')
            page.text = page.text.replace("[[تصنيف:قوالب د توارخ]]",'')
            page.text = page.text.replace('{{شرح}}','{{شرح}}'+DATE_BOT_TEMPLATE_CATEGORY)
            page.save(TEMPLATE_UPDATED_MESSAGE)

        event_doc_template_page_title = event_template_page_title+'/شرح'
        page = pywikibot.Page(site,event_doc_template_page_title)
        if page.text == "":
            page.text = DOC_PAGE_MESSAGE.format(EVENT_STR,str(day_number)+' '+MONTHS[i]['ary_name'],EVENT_TITLE.replace('==','').strip())
            page.save(DOC_TEMPLATE_CREATED_MESSAGE)

        holid_template_page_title = TEMPLATE_NAMESPACE+HOLID_DATES_TEMPLATE_TITLE_PART+str(day_number)+' '+MONTHS[i]['ary_name']
        page = pywikibot.Page(site,holid_template_page_title)
        # add templates if not exist
        if page.text == "":
            page.text = "<noinclude>"+DATE_BOT_TEMPLATE_CATEGORY+"</noinclude>"
            page.save(TEMPLATE_CREATED_MESSAGE)
        else:
            page.text = page.text.replace(DATE_BOT_TEMPLATE_CATEGORY,'{{شرح}}'+DATE_BOT_TEMPLATE_CATEGORY)
            page.save(TEMPLATE_UPDATED_MESSAGE)

        holid_doc_template_page_title = holid_template_page_title+'/شرح'
        page = pywikibot.Page(site,holid_doc_template_page_title)
        if page.text == "":
            page.text = DOC_PAGE_MESSAGE_2.format(str(day_number)+' '+MONTHS[i]['ary_name'])
            page.save(DOC_TEMPLATE_CREATED_MESSAGE)

        """
        event_template1_page_title = TEMPLATE_NAMESPACE+EVENT_DATES_TEMPLATE1_TITLE_PART+str(day_number)+' '+MONTHS[i]['ary_name']
        page1 = pywikibot.Page(site,event_template1_page_title)
        # add templates if not exist
        if page1.text == "":
            event_template2_page_title = TEMPLATE_NAMESPACE+EVENT_DATES_TEMPLATE2_TITLE_PART+str(day_number)+' '+MONTHS[i]['ary_name']
            page2 = pywikibot.Page(site,event_template2_page_title)
            if page2.text == "":
                page1.text = DATE_TEMPLATE_CATEGORY
                page1.save(TEMPLATE_CREATED_MESSAGE)
                page1.move(event_template2_page_title,reason=message, movetalk=True, noredirect=False)

            else:
                page1.text = MOVE_TEXT+" [["+event_template2_page_title+"]]\n\n"+REDIRECT_PAGE_CAT_CODE+"\n"+DARIJABOT_ADDED_REDIRECTS_CATEGORY
                page1.save(TEMPLATE_REDIRECT_CREATED_MESSAGE)
                page2.text+="\n"+DATE_TEMPLATE_CATEGORY
                page2.save(TEMPLATE_CAT_ADDED_MESSAGE)

        else:
            event_template2_page_title = TEMPLATE_NAMESPACE+EVENT_DATES_TEMPLATE2_TITLE_PART+str(day_number)+' '+MONTHS[i]['ary_name']
            page2 = pywikibot.Page(site,event_template2_page_title)
            if page2.text == "":
                page1.move(event_template2_page_title,reason=message, movetalk=True, noredirect=False)
            else:
                #do nothing
                pass

        """
        # add pages
        page_title = str(day_number)+' '+MONTHS[i]['ary_name']
        page = pywikibot.Page(site,page_title)
        adding_darijabot_cat = False
        if page.text == "" or DARIJABOT_ADDED_ARTICLE_CATEGORY in page.text:
            adding_darijabot_cat = True

        ## calculate day in year and remaining days
        day_in_year_number_normal, day_in_year_number_leap  = get_day_numbers_in_year(month_number,day_number)
        if day_in_year_number_normal == day_in_year_number_leap:
            day_rem_year_number_normal = 365 - day_in_year_number_normal
            day_rem_year_number_leap = 366 - day_in_year_number_normal
        else:
            day_rem_year_number_normal = 365 - day_in_year_number_normal
            day_rem_year_number_leap = day_rem_year_number_normal
        ## replace values with format
        text = CALENDAR_TAG_PART+str(month_number)+CLOSING_TEMPLATE_TAG+"\n\n"
        text+= START_FIRST_SENTENCE_PATTERN.format(day_number,MONTHS[i]['ary_name'])
        if MONTHS[i]['alt_name'] != "":
            text+= ' ؤلا '+START_FIRST_SENTENCE_PATTERN.format(day_number,MONTHS[i]['alt_name'])
        text+= ' '+REST_FIRST_SENTENCE_PATTERN.format(day_number,month_number,day_in_year_number_normal,day_in_year_number_leap)
        if day_rem_year_number_normal == 0:
            text+= ' '+ADDITIONAL_SENTENCE_FORM_0
        elif day_rem_year_number_normal == 1:
            text+= ' '+ADDITIONAL_SENTENCE_FORM_1
        elif day_rem_year_number_normal == 2:
            text+= ' '+ADDITIONAL_SENTENCE_FORM_2
        elif day_rem_year_number_normal >= 3 and day_rem_year_number_normal <= 10:
            text+= ' '+ADDITIONAL_SENTENCE_FORM_3.format(day_rem_year_number_normal)
        else:
            text+= ' '+ADDITIONAL_SENTENCE_FORM_MANY.format(day_rem_year_number_normal)

        if day_in_year_number_normal == day_in_year_number_leap:
            text+= ' '+LEAP_YEAR_ADDITIONAL.format(day_rem_year_number_leap)
        
        text+='.'
        text+= REF_TEXT+'\n\n'
        text+= COMMONS_CAT_PART+str(day_number)+' '+MONTHS[i]['en_name']+CLOSING_TEMPLATE_TAG+'\n\n'
        text+= BIRTH_TITLE+'\n\n'+OPENING_TEMPLATE_TAG+BIRTH_DATES_TEMPLATE_TITLE_PART+str(day_number)+' '+MONTHS[i]['ary_name']+CLOSING_TEMPLATE_TAG+'\n\n'
        text+= DEATH_TITLE+'\n\n'+OPENING_TEMPLATE_TAG+DEATH_DATES_TEMPLATE_TITLE_PART+str(day_number)+' '+MONTHS[i]['ary_name']+CLOSING_TEMPLATE_TAG+'\n\n'
        text+= EVENT_TITLE+'\n\n'+OPENING_TEMPLATE_TAG+EVENT_DATES_TEMPLATE_TITLE_PART+str(day_number)+' '+MONTHS[i]['ary_name']+CLOSING_TEMPLATE_TAG+'\n\n'
        text+= HOLID_TITLE+'\n\n'+OPENING_TEMPLATE_TAG+HOLID_DATES_TEMPLATE_TITLE_PART+str(day_number)+' '+MONTHS[i]['ary_name']+CLOSING_TEMPLATE_TAG+'\n\n'
        text+= '\n'+QUASI_FOOTER+'\n\n'
        text+= CATEGORY_PART+MONTHS[i]['ary_name']+CLOSING_CAT_TAG+'\n'
        text+= DAYS_OF_THE_YEAR_CAT

        if adding_darijabot_cat:
            text+='\n\n'+DARIJABOT_ADDED_ARTICLE_CATEGORY

        if text != page.text:
            page.text = text
            page.save(PAGE_ADDED_MESSAGE)
        print(str(day_number)+' '+MONTHS[i]['en_name'])

    
