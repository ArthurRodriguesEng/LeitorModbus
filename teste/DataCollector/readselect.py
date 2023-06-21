
from time import sleep
import timecfg
import Info.Usinas.ribeirao_bonito as usina
from Client.inverterclient import InverterClient
from Client.ncutcuclient import TCUNCUClient
from Client.windclient import WINDClient

def read_select(read, scan_time):
    if(read == 'NCU'):
        ncu_scan(scan_time)
        
    elif(read == 'WIND'):
        wind_scan(scan_time)
            
    elif(read == 'INVERTER'):
        inverter_scan(scan_time)
    
    else:
        print("Incorrect input parameters")
        
def ncu_scan(scan_time):
    ncu_scan = True
    NCUs = []
    for usina_parameters in usina.usina_parameters:
        NCUs.append(TCUNCUClient(usina_parameters['IP'], 502, usina_parameters['ID'], usina.name, usina_parameters['TCUs'], int(ncu_scan)))
    while True:
        for i in range(len(NCUs)):
            NCUs[i].read_NCU_TCU()  
        date = timecfg.datetime.now()
        if(timecfg.t1 < date.time() < timecfg.t2):
            ncu_scan = True
        else:
            ncu_scan = False
        sleep(scan_time * 60)

def wind_scan(scan_time):
    NCUs = []
    for usina_parameters in usina.usina_parameters:
        NCUs.append(WINDClient(usina_parameters['IP'], 502, usina_parameters['ID'], usina.name)) 
    while True:
        for i in range(len(NCUs)):
            NCUs[i].read_wind_speed()
        sleep(scan_time*60) 

def inverter_scan(scan_time):
    INVERTERs = []
    for inverter in usina.inverter:
            INVERTERs.append(InverterClient(inverter['IP'], 502,  inverter['ID'], usina.name))
    while True:
        for i in range(len(INVERTERs)):
            INVERTERs[i].read_inverter()
        sleep(scan_time * 60)