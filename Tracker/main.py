from clientemodbus import ClienteMODBUS
from time import sleep
import timecfg
import Usinas.ribeirao_bonito as usina
from inverter_client import InverterClient




'SETUP'

'Tempo de Scan em minutos'
#scan_time = 4 #minutos

'Tipo de Leitura(NCU ou WIND)'
Ler = 'INVERTER'


if(Ler == 'NCU'):
    scan_time = 4
    ncu_scan = True
    while True:
        for usina_parameters in usina.usina_parameters:
            Client = ClienteMODBUS(usina_parameters['IP'], 502, usina_parameters['ID'], usina_parameters['TCUs'], usina.name, int(ncu_scan))
            Client.read_NCU_TCU()
            #Client.read_wind_peak()
        date = timecfg.datetime.now()
        
        if(timecfg.t1 < date.time() < timecfg.t2):
            ncu_scan = True
        else:
            ncu_scan = False
        sleep(scan_time * 60)

elif(Ler == 'WIND'):
    scan_time = 1
    while True:
        for usina_parameters in usina.usina_parameters:
            Client = ClienteMODBUS(usina_parameters['IP'], 502, usina.name, usina_parameters['ID'], usina_parameters['TCUs'],  ncu_scan = int(False))
            Client.read_wind_speed()
        sleep(scan_time*60) 
        
elif(Ler == 'INVERTER'):
    scan_time = 4
    while True:
        for inverter in usina.inverter:
            Client = InverterClient(inverter['IP'], 502, usina.name, inverter['ID'])
            #Client.read_inverter()
        sleep(scan_time * 60)

else:
    print("Incorrect input parameters")
