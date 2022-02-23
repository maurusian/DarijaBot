import pywikibot

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
