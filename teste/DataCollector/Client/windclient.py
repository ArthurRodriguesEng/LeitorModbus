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
        self.tag = 'WS'
        
        try:    
            self.log_to_send = pd.read_csv(self.tag +  "_" +  str(self._ID) + ".csv").values.tolist()
            for i in range(len(self.log_to_send)): 
                self.log_to_send[i] = [ast.literal_eval(str(self.log_to_send[i][1]))]
                
        except:
            self.log_to_send = []
        

    def read_wind_speed(self):
        
        '''
            Função de leitura dos dados de velocidade de vento e hora/data do NCU
                Leitura feita a partir da csv com os dados inseridos
        '''
        self._client.open()
        if(self._client.open() ==True):
            print("Connection " + 'NCU_WIND' +str(self._ID)+ " done")
            #print(str(self.tag) + str(self._ID))
            self.MB_Table = self._MBT_WS
            self.read_and_decode_data(0)
            self.log_to_send.append([self.Log])
            print(self.log_to_send)
            self.data_manager()
            # self.build_jsonfile([self.Log])
            # self.build_csv(self.log_to_send)
            
            
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
    
    def send(self,json_obj ):
        return backend.send_windspeed(json_obj)
            
    
            
