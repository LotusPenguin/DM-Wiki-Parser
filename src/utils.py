from datetime import datetime
def println(to_print):
    print((datetime.now()).strftime("[%H:%M:%S] ") + str(to_print))
