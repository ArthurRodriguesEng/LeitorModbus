from Client.clientmodbus import ClientMODBUS

from datetime import datetime

import timecfg

import Info.Trackers.P4Q.build_table as table

import pandas as pd

import ast

import os

import coleta.backend as backend

import json


class WINDClient(ClientMODBUS):
    def __init__(self, server_ip, porta, ID, usina_name):
        super().__init__(server_ip, porta, ID, usina_name)
        self._MBT_WS = table.MBT_WS
        
        try:    
            self.log_to_send = pd.read_csv('WIND_WS' + str(self._ID) +  "_" + ".csv").values.tolist()
            for i in range(len(self.log_to_send)): 
                self.log_to_send[i] = [ast.literal_eval(self.log_to_send[i][1])]
        except:
            self.log_to_send = []
        

    def read_wind_speed(self):
        
        '''
            Função de leitura dos dados de velocidade de vento e hora/data do NCU
                Leitura feita a partir da csv com os dados inseridos
        '''
        self._client.open()
        if(self._client.open()):
            print('WIND' + str(self._ID))
            self.MB_Table = self._MBT_WS
            self.read_and_decode_data(0)
            self.log_to_send.append([self.Log])
            self.data_manager()
            self.build_jsonfile()
            
            
        else:
            print("Connection" + "NCU" +str(self._ID)+ " fail")
            pass
        
    def data_to_json(self, wind: list, indent: int = None) -> str:
        '''
        Converte os dados de leitura da velocidade do vento para o formato JSON.

                Parameters:
                    wind (list): Lista com os dados lidos da coleta.
                    indent (int): Tamanho da indentação usada na codificação.

                Returns:
                    json (str): JSON dos dados de velocidade do vento
        '''
        data = { 
            'usina': self._usina_name,
            'ncu': 'NCU'+str(self._ID),
            'NcuDatetime': wind[0][1]['NcuDatetime'], 
            'WindSpeed_mps_rsu1': wind[0][0]['WindSpeed_mps_rsu1'] 
        }
        return json.dumps(data, indent=indent)
            
    def build_jsonfile(self):
        data_log = self.data_to_json([self.Log],4)
        with open('WS' + str(self._ID) +".json", "w") as outfile:
            outfile.write(data_log)
            
    def insert_to_db(self,log):
        json_obj = json.loads(self.data_to_json(log,4))
        regress = backend.send_windspeed(json_obj)
        if(regress):
            print('Send done')
        else:
            print('Send fail')
        return False
    
    def data_manager(self):
        i=0
        while i < len(self.log_to_send):
            if(self.insert_to_db(self.log_to_send[i])):
                self.log_to_send.pop(i)
            else:
                break
            
        if(self.log_to_send == []):
            file = str((self.MB_Table["equipment"][0]) +  "_" + 'WS'+ str(self._ID) +  "_" + ".csv")
            if(os.path.exists(file) and os.path.isfile(file)): 
                os.remove(file)
        else:
            self.build_csv(self.log_to_send, 'WS'+ str(self._ID))