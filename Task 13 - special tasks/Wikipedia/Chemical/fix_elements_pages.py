import pywikibot
from pgvbotLib import *
from copy import deepcopy

ELEM_CATEGORY = "[[تصنيف:عنصر كيميائي]]"

MAPPING = {'[[نݣليزية|النݣليزية]]':'[[نݣليزية|نّݣليزية]] '
          ,'هو ':'هوّا '
          ,' و ':' ؤ '
          ,'[[نمرة ذرية|النمرة الذرية]]':'[[نمرة درية|نّمرة دّرية]]'
          ,'[[طابلو دوري|لجدول الدوري]]':'[[طابلو دوري|طّابلو دّوري]]'
          ,' ، ':'، '
          ,'ف الظروف لمعيارية د الضغط و الحرارة':'ف ضّروف لمعيارية د [[ضغط جوي|ضّغط]] و [[حرارة (طيرموديناميك)|لحرارة]]'
          ,'[[صلبة|صلب]]':'[[قاسح]]ة'
          ,'خصائص فيزيائية':'لخاصيات لفيزيكية'
          ,'[[كتلة ذرية|لكتلة الذرية]]':'[[كتلة درية|لكتلة دّرية]]'
          ,'[[درجة د لأكسدة|الدرجة د لأكسدة]]':'[[حالة د لأكسدة|لحالات د لأكسدة]]'
          ,'[[كهروسلبية|الكهروسلبية]]':'[[كهروسلبية|لكهروسلبية]]'
          ,'ݣرام/لمول':'[[ݣرام]]/[[مول]]'
          ,'[[السلم د پاولينغ]]':'[[سلوم د پاولينݣ]]'
          ,'[[شعاع ذري|الشعاع الذري]]':'[[شعاع دري]]'
          ,'آنݣستروم':'[[أنݣستروم]]'}

SAVE_MESSAGE = "پاج د عنصر كيماوي تقادات علا نفس لموضيل د [[هيدروجين]]"


           
site = pywikibot.Site()
pool = site.allpages(namespace = ARTICLE_NAMESPACE)
pool_size = len(list(deepcopy(site.allpages(namespace=ARTICLE_NAMESPACE))))
print('Pool size: '+str(pool_size))
i = 1
for page in pool:
    print('*********'+str(i)+'/'+str(pool_size))
    if validate_page(page) and ELEM_CATEGORY in page.text:
        text = page.text
        for key, value in MAPPING.items():
            text = text.replace(key,value)

        if text != page.text:
            page.text = text
            save_page(page,SAVE_MESSAGE)
    i+=1
