from openpyxl import Workbook, load_workbook


ORD_A = ord('A')
CRYPTOS = "./data/Moroccan_politicians.json"
EXPORT = "./export/Moroccan_politicians.xlsx"

with open(CRYPTOS,'r',encoding="utf-8") as f:
    crypto_dict_list = eval(f.read())



headers = set()
for crypto_dict in crypto_dict_list:
    temp = set(crypto_dict.keys())
    headers = headers | temp


wb = Workbook()

sheet = wb.active


i = 0
for header in headers:
    sheet[chr(ORD_A+i)+'1'] = header
    i+=1




wb.save(EXPORT)
