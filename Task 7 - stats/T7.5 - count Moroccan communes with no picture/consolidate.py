import csv, os
from openpyxl import Workbook

communes = {}
for file in os.listdir():
    with open(file, mode='r') as f:
        reader = csv.reader(f)
        temp += {rows[0]:[file.split('.')[0],rows[1],rows[2]] for rows in reader}
        for key,value in temp.items():
            if key in communes.keys():
                if value[0] not in communes[key][0]:
                    communes[key][0] += ', '+value[0]
                if communes[key][2].strip() == "":
                    communes[key][2] = value[2]
                
            else:
                communes[key] = value


wb = Workbook()

sheet = wb.active

sheet['A1'] = 'QCode'
sheet['B1'] = 'Type'
sheet['C1'] = 'QCode'
sheet['D1'] = 'QCode'
sheet['E1'] = 'QCode'
sheet['F1'] = 'QCode'
sheet['G1'] = 'QCode'

for key,value in communes.items():
    
