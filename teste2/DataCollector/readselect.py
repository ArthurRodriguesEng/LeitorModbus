
from time import sleep
import timecfg
import Info.Usinas.ribeirao_bonito as usina
from Client.inverterclient import InverterClient
from Client.ncutcuclient import TCUNCUClient
from Client.windclient import WINDClient
from Client.combinerboxclient import CombinerboxClient
from Client.skidclient import SkidClient
from Client.estacaosolarimetricamodbus import EstSolClient


def read_select(read, scan_time):
    if(read == 'NCU'):
        ncu_scan(scan_time)
        
    elif(read == 'WIND'):
        wind_scan(scan_time)
            
    elif(read == 'INVERTER'):
        inverter_scan(scan_time)
    
    elif(read == 'C_BOX'):
        c_box_scan(scan_time)

    elif(read == 'EST_SOL'):
        est_sol_scan(scan_time)

    elif(read == 'SKID'):
        skid_scan(scan_time)
    
    else:
        print("Incorrect input parameters")
        
def ncu_scan(scan_time):
    NCUs = []
    for usina_parameters in usina.usina_parameters:
        NCUs.append(TCUNCUClient(usina_parameters['IP'], 502, usina_parameters['ID'], usina.name, usina_parameters['TCUs']))
    while True:
        for i in range(len(NCUs)):
            NCUs[i].read() 
        sleep(scan_time * 60)

def wind_scan(scan_time):
    NCUs = []
    for usina_parameters in usina.usina_parameters:
        NCUs.append(WINDClient(usina_parameters['IP'], 502, usina_parameters['ID'], usina.name)) 
    while True:
        for i in range(len(NCUs)):
            NCUs[i].read()
        sleep(scan_time*60) 

def inverter_scan(scan_time):
    INVERTERs = []
    for inverter in usina.inverter:
        INVERTERs.append(InverterClient(inverter['IP'], 502,  inverter['ID'], usina.name, inverter['unit_id']))
    while True:
        for i in range(len(INVERTERs)):
            INVERTERs[i].read()
        sleep(scan_time * 60)
        
def c_box_scan(scan_time):
    c_boxs = []
    for c_box in usina.c_box:
        c_boxs.append(CombinerboxClient(c_box['IP'], 502,  c_box['ID'], usina.name, c_box['unit_id']))
    while True:
        for i in range(len(c_boxs)):
            c_boxs[i].read()
        sleep(scan_time * 60)

def est_sol_scan(scan_time):
    estsols = []
    for estsol in usina.estsol:
        estsols.append(EstSolClient(estsol['IP'], 502,  estsol['ID'] , usina.name))
    while True:
        for i in range(len(estsols)):
            estsols[i].read()
        sleep(scan_time * 60)
        
def skid_scan(scan_time):
    skids = []
    for skid in usina.skid:
        skids.append(SkidClient(skid['IP'], 502,  skid['ID'] , usina.name , skid['unit_id'], skid['TYPE']))
    while True:
        for i in range(len(skids)):
            skids[i].read()
        sleep(scan_time * 60)