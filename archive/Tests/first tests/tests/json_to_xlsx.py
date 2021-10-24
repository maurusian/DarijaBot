DATA_SOURCE = "./data/"
EXPORT_FOLDER = "./export/"
CHAR_LIMIT = 600

from openpyxl import Workbook
import pywikibot
from pattern.web import Wikipedia
import urllib.parse as url

with open(DATA_SOURCE+'monuments_no_ary.json','rb') as f:
    data = sorted(eval(f.read()),key=lambda x:len(x),reverse=True)

    #print(data[0])

    keys = list(data[0].keys())

    
    wb = Workbook()
    sheet = wb.active

    #write headers
    for i in range(len(keys)):
        sheet[chr(65+i)+'1'] = keys[i]
    sheet[chr(65+len(keys))+'1'] = "AR paragraph"
    sheet[chr(65+len(keys)+1)+'1'] = "FR paragraph"
    sheet[chr(65+len(keys)+2)+'1'] = "EN paragraph"

    
    for j in range(len(data)):
        try:
            site = pywikibot.Site()
            token = data[j]["articleEN"].split('/')[-1]
            
            token = url.unquote(token).replace('_',' ')
            paragraph_en = Wikipedia(language="en").search(token, throttle=1).string[:CHAR_LIMIT]
            #paragraph = wikipedia.summary(token, sentences=2)
        except:
            paragraph_en = ""

        try:
            site = pywikibot.Site()
            token = data[j]["articleFR"].split('/')[-1]
            
            token = url.unquote(token).replace('_',' ')
            
            paragraph_fr = Wikipedia(language="fr").search(token, throttle=1).string[:CHAR_LIMIT]
            #paragraph = wikipedia.summary(token, sentences=2)
        except:
            paragraph_fr = ""

        try:
            site = pywikibot.Site()
            token = data[j]["articleAR"].split('/')[-1]
            
            token = url.unquote(token).replace('_',' ')
            print(token)
            paragraph_ar = Wikipedia(language="ar").search(token, throttle=1).string[:CHAR_LIMIT]
            #paragraph = wikipedia.summary(token, sentences=2)
        except:
            paragraph_ar = ""
        #print(token)
        for i in range(len(keys)):
            
            if keys[i] in data[j].keys():
                sheet[chr(65+i)+str(j+2)] = data[j][keys[i]]

        #print(paragraph)
        sheet[chr(65+len(keys))+str(j+2)] = paragraph_ar
        sheet[chr(65+len(keys)+1)+str(j+2)] = paragraph_fr
        sheet[chr(65+len(keys)+2)+str(j+2)] = paragraph_en
                
                

    wb.save(EXPORT_FOLDER+"monuments_no_ary.xlsx")
