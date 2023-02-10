from pgvbotLib import *

for i in range(1,13):
    #print(str(i).rjust(2,'0'))
    for j in range(1,MONTHS[i-1]['day_count']+1):
        print('j='+str(j))
        daymonth_raw = str(i).rjust(2,'0')+str(j).rjust(2,'0')
        print(daymonth_raw)
        #break




#print(MONTHS)
