#from pgvbotLib import *
import pywikibot
from copy import deepcopy
#from sys import argv
import re, sys, os, csv
from openpyxl import Workbook


folder = "./data/"

TYPES = {'all moroccan rural communes.csv':'جماعة قروية'
        ,'moroccan communes with pics.csv':'جماعة'
        ,'moroccan communes.csv':'جماعة'
        ,'moroccan rural communes with pics.csv':'جماعة قروية'
        ,'urban communes of Morocco with pics.csv':'جماعة حضرية'
        ,'urban communes of Morocco.csv':'جماعة حضرية'}


image_pattern = r"\[\[فيشي\:.+\]\]?"

def extract_qcode(wkd_url):
    return wkd_url.split('/')[-1]

ary_file = '[[فيشي:'
en_file = '[[File:'
ar_file = '[[ملف:'

file_symbols = [ary_file,en_file,ar_file]

def extract_images(text):
    images = []
    for sym in file_symbols:
        if sym in page.text:
            parts = page.text.split(sym)
            for part in parts[1:]:
                subpart = part.split(']]')[0]
                images.append(subpart.split('|')[0])

    return ', '.join(images)


communes = {}
for file in os.listdir(folder):

    with open(folder+file,'r',encoding='utf-8') as f:

        content = csv.reader(f, delimiter=',')

        
        for row in list(content)[1:]:
            qcode = extract_qcode(row[0])
            if qcode not in communes.keys():
                communes[qcode] = {'Name (en)':row[1]
                                  ,'Name (ary)':''
                                  ,'Type':TYPES[file]
                                  ,'Wikidata Image':row[2]
                                  ,'Wikipedia Image':''
                                   }
            else:
                if TYPES[file] not in communes[qcode]['Type']:
                    communes[qcode]['Type']+='، '+TYPES[file]
                if communes[qcode]['Wikidata Image'] == '':
                    communes[qcode]['Wikidata Image'] = row[2]

                
            


print(len(communes))


for qcode,values in communes.items():
    site = pywikibot.Site("wikidata", "wikidata")
    repo = site.data_repository()
    item = pywikibot.ItemPage(repo, qcode)
    item_dict = item.get()
    interlinks = item_dict["labels"]

    if 'ary' in interlinks.keys():
        communes[qcode]['Name (ary)'] = interlinks['ary']
        site_ary =pywikibot.Site()
        page = pywikibot.Page(site_ary,interlinks['ary'])
        
        communes[qcode]['Wikipedia Image'] = extract_images(page.text)
    else:
        communes[qcode]['Name (ary)'] = 'no linked article'

#save to XLSX file
wb = Workbook()
sheet = wb.active

headers = ['qcode']
headers.extend(list(communes[list(communes.keys())[0]].keys()))

#print(list(communes.keys()))
#print(list(communes.keys())[0])
#print(communes[list(communes.keys())[0]].keys())
#print(['qcode'])
#print

for i in range(len(headers)):
    sheet[chr(65+i)+'1'] = headers[i]

row_counter = 2
has_pic_counter = 0
for qcode,values in communes.items():
    sheet['A'+str(row_counter)] = qcode
    
    for i in range(1,len(headers)):
        sheet[chr(65+i)+str(row_counter)] = values[headers[i]]
    row_counter+=1

    if values["Wikipedia Image"].strip() != '' or values["Wikidata Image"].strip() != '':
        has_pic_counter+=1


print("Communes with pictures :"+str(has_pic_counter))
    
wb.save('communes.xlsx')


