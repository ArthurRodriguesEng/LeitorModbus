from Client.clientmodbus import ClientMODBUS


import Info.Trackers.P4Q.build_table as table

import coleta.backend as backend

import timecfg
from datetime import datetime

from pymodbus.constants import Endian


class WINDClient(ClientMODBUS):
    def __init__(self, server_ip, porta, ID, usina_name):
        super().__init__(server_ip, porta, ID, usina_name)
        self.MB_Table = table.MBT_WS
        self.byteorder = Endian.Big
        self.wordorder = Endian.Little
        self.tag = 'WS_NCU'
        self.load_data()

        
    def read(self):
        
        '''
            Função de leitura dos dados de velocidade de vento e hora/data do NCU
                Leitura feita a partir da csv com os dados inseridos
        '''
        #self._client.open()
        if(self._client.open()):
            print("Connection " + str(self.tag) +str(self._ID)+ " done")
            print(self.MB_Table["equipment"][0] +str(self._ID)+ " reading...")
            date_a = datetime.now()
            self.read_and_decode_data()
            self._client.close()
            self.build_dict()
            self.build_jsonfile(self.log)
            self.log_to_send.append(self.log)
            self.data_manager()
            date_b = datetime.now()
            timecfg.scan_time(date_a,date_b)
            
        else:
            print("Connection" + str(self.tag) +str(self._ID)+ " fail")
            pass
        
        
    def send(self,json_obj ):
        return backend.send_windspeed(json_obj)
    
    def build_dict(self):
        self.log = {'usina': self._usina_name,
                    'ncu': 'NCU'+str(self._ID),
                    'datetime': str(datetime.now())
                        }
        self.log.update(self.log_dict)
    
    
    
    
    # def data_to_json(self, wind: list, indent: int = None) -> str:
    #     '''
    #     Converte os dados de leitura da velocidade do vento para o formato JSON.

    #         Parameters:
    #             wind (list): Lista com os dados lidos da coleta.
    #             indent (int): Tamanho da indentação usada na codificação.

    #         Returns:
    #             json (str): JSON dos dados de velocidade do vento
    #     '''
    #     data = { 
    #         'usina': self._usina_name,
    #         'ncu': 'NCU'+str(self._ID),
    #         'NcuDatetime': wind[0][1]['NcuDatetime'], 
    #         'WindSpeed_mps_rsu1': wind[0][0]['WindSpeed_mps_rsu1'] 
    #     }
    #     return json.dumps(data, indent=indent)
    

            
    
            
