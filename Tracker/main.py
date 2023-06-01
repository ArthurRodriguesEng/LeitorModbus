from clientemodbus import ClienteMODBUS
from time import sleep
import timecfg
import Usinas.ribeirao_bonito as usina

'''
    Se o valor de ncu_scan for igual a -1 a leitura do ncu será feita.
'''
ncu_scan = True
while True:
    for usina_parameters in usina.usina_parameters:
        c = ClienteMODBUS(usina_parameters['IP'], 502, usina_parameters['ID'], usina_parameters['TCUs'], usina.name, int(ncu_scan))
        c.start_scan()
    date = timecfg.datetime.now()
    if(timecfg.t1 < date.time() < timecfg.t2):
        ncu_scan = True
    else:
        ncu_scan = False
    sleep(120)

# while True:
#     for usina_parameters in usina.usina_parameters:
#         c = ClienteMODBUS(usina_parameters['IP'], 502, usina_parameters['ID'], usina_parameters['TCUs'], usina.name, ncu_scan = int(False))
#         c.wind_speed()
#     sleep(10) 
