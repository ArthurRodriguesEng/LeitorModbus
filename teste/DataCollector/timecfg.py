from datetime import datetime
from datetime import time
from datetime import timedelta

t1 = time(second=0,minute=0,hour=0)
t2 = time(second=0,minute=4,hour=0)

def scan_time(time1, time2):
    delta2 = timedelta(seconds=time2.time().second,minutes=time2.time().minute,hours=time2.time().hour)
    delta1 = timedelta(seconds=time1.time().second,minutes=time1.time().minute,hours=time1.time().hour)    
    print('Scan time: ' + str(delta2 - delta1))