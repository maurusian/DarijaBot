import pywikibot
from datetime import datetime
from random import randint
from subprocess import Popen, PIPE

PARAM_PAGE_TITLE = "ميدياويكي:عطاشة 19.json"

DARIJABOT_ROOT = "C:\\Users\\anton\\Documents\\scripts\\DarijaBot\\"

#abstract class?
class Program:
    def __init__(self):
        prog_name = "abstract program"
        status = 'NOK'
        task_name = "task0"
        task_page_name = ""
        path = ""
        repo = ""
        trigger_type = None
        trigger_value = None
        logpage_name = ""
        error_logpage_name = ""

    def __str__(self):
        pass

    def str_to_ary(self):
        pass

    def launch(self):
        pass

    #do we need this?
    def stop(self):
        pass

    def write_to_log(self,message):
        pass

    def write_to_error_log(self,message):
        pass

    def extract_dicts(self,page):
        return [eval(el.split(']]')[0]) for el in page.text.split('[[')[1:]]

        

if __name__=='__main__':
    site = pywikibot.Site()
    param_page = pywikibot.Page(site,PARAM_PAGE_TITLE)

    prog = Program()

    TASK_LIST = prog.extract_dicts(param_page)

    for task in TASK_LIST:
        JOBID = str(task['tasknumber'])+datetime.now().strftime('%d%m%y')
        print(JOBID)
        print(TASK_LIST[-1]['taskname'])

    #process = Popen(TASK_LIST[0]['program'].strip(), stdout=PIPE, stderr=PIPE)

    if TASK_LIST[-1]['bot'] == 'Darijabot':
        root_folder = DARIJABOT_ROOT

    task_folder = root_folder + TASK_LIST[-1]['program_loc']
    task_file = task_folder + TASK_LIST[-1]['program_name']
    with open(task_file,'r') as prog:
        instr = prog.read().replace('pause','').strip()
        print(instr)

    p = Popen(instr+JOBID, cwd=task_folder, shell=True)


    stdout, stderr = p.communicate()

    print(stdout)


    while True:
        DAY_COUNT_SINCE_LAST_LAUNCH_TASK2 = 0
