from Client.clientmodbus import ClienteMODBUS

from datetime import datetime

import timecfg

import Info.Trackers.P4Q.build_table as table


class WINDClient(ClienteMODBUS):
    def __init__(self, server_ip, porta, ID, usina_name):
        super().__init__(server_ip, porta, ID, usina_name)
        self._MBT_WS = table.MBT_WS
        
        
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
            self.insert_to_db(wind_speed_log,'RB_WS')
            
            
        else:
            print("Connection" + "NCU" +str(self._ID)+ " fail")
            pass