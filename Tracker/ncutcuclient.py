from clientemodbus import ClienteMODBUS
from pyModbusTCP.client import ModbusClient

from datetime import datetime
import datetime
import timecfg


import Trackers.P4Q.build_table as table

class TCUNCUClient(ClienteMODBUS):
    def __init__(self, server_ip, porta, ID, usina_name, tcu_number_to_read, ncu_scan):
        super().__init__(server_ip, porta, ID, usina_name)
        self._tcu_number_to_read = tcu_number_to_read
        self._ncu_scan = ncu_scan

        self._MBT_NCU = table.MBT_NCU
        self._MBT_TCU = table.MBT_TCU
        self._MBT_WS = table.MBT_WS
        self._MBT_NCU_WIND = table.MBT_NCU_WIND
        
        
def read_NCU_TCU(self):

        '''
            Função de leitura dos dados do NCU e TCU
                Leitura feita a partir da csv com os dados inseridos

                Ela tem com saída um arquivo CSV com as leituras e um arquivo JSON
        '''
        self._cliente.open()
        if(self._cliente.open() == True):
            print("Connection " + self._MBT_NCU["equipment"][0] +str(self._ID)+ " done")
            print(self._MBT_NCU["equipment"][0] +str(self._ID)+ " reading...")
            date_a = datetime.now()
            log = []
            for tcu_number in range(self._tcu_number_to_read+1):
                #Identifica se é leitura de NCU ou TCU
                if(tcu_number == 0 and self._ncu_scan == 1):
                    #print(self._MBT_NCU["equipment"][0] + str(self._ID))
                    modbus_table = self._MBT_NCU
                    data_read = self.read_and_decode_data(modbus_table,tcu_number)
                elif(tcu_number == 0 and self._ncu_scan == 0):
                    continue
                else:
                    #print(self._MBT_TCU["equipment"][0] + str(tcu_number))
                    modbus_table = self._MBT_TCU
                    data_read = self.read_and_decode_data(modbus_table,tcu_number-1)
                                    
                if(tcu_number == 0):
                    log.append((self._MBT_NCU["equipment"][0]+ str(self._ID) , data_read))
                else:
                    log.append((self._MBT_TCU["equipment"][0] + str(tcu_number), data_read))
                

            #self.build_jsonfile(log, 'NCU')
            self.insert_to_mongodb(log,'RB_NCU')
            
            print(self._MBT_NCU["equipment"][0] +str(self._ID)+ " done")

            date_b = datetime.now()
            timecfg.scan_time(date_a,date_b)
            
        else:
            print("Connection " + "NCU" +str(self._ID)+ "fail")
            pass
def read_wind_speed(self):
    
    '''
        Função de leitura dos dados de velocidade de vento e hora/data do NCU
            Leitura feita a partir da csv com os dados inseridos
    '''
    self._cliente.open()
    if(self._cliente.open() ==True):
        print('WIND' + str(self._ID))
        modbus_table = self._MBT_WS
        wind_speed_log = self.read_and_decode_data(modbus_table,0)
        #self.build_jsonfile(wind_speed_log,'WIND')
        self.insert_to_mongodb(wind_speed_log,'RB_WS')
        
        
    else:
        print("Connection" + "NCU" +str(self._ID)+ " fail")
        pass
    
def read_wind_peak(self):
    
    self._cliente.open()
    if(self._cliente.open() == True):
        log = []
        print("Connection " + self._MBT_NCU["equipment"][0] +str(self._ID)+ " done")
        
        for eqp_number in range(31):
            modbus_table = self._MBT_NCU_WIND
            data_read = self.read_and_decode_data(modbus_table,eqp_number)
            log.append((self._MBT_NCU_WIND["equipment"][0] + str(eqp_number+1), data_read))
            self.build_jsonfile(log, 'WS_PEAK')
                
    else:
        print("Connection " + "NCU" +str(self._ID)+ "fail")
        pass