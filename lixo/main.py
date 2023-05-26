from clientemodbus import ClienteMODBUS
import time
import usina
from time import sleep
from datetime import datetime
from datetime import time

t1 = time(second=0,minute=0,hour=0)
t2 = time(second=0,minute=3,hour=0)

'''
    Se o valor de ncu_scan for igual a -1 a leitura do ncu será feita.
'''
ncu_scan = -1
while True:
    date = datetime.now()
    for i in usina.dict_plant:
        c = ClienteMODBUS(i['IP'], 502, i['ID'], i['TCUs'], usina.name, ncu_scan)
        c.start_scan()
    
    if(t1 < date.time() < t2):
        ncu_scan = -1
    else:
        ncu_scan = 0
    sleep(120) 

while True:
    date = datetime.now()
    for i in usina.dict_plant:
        c = ClienteMODBUS(i['IP'], 502, i['ID'], i['TCUs'], usina.name, ncu_scan)
        c.wind_speed()
    
    sleep(10) 
