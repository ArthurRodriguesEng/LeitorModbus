from Client.clientmodbus import ClientMODBUS

from datetime import datetime

import timecfg

import Info.Trackers.P4Q.build_table as table

import pandas as pd

import ast

import os

import json

from functools import reduce

import coleta.backend as backend




class TCUNCUClient(ClientMODBUS):
    def __init__(self, server_ip, porta, ID, usina_name, tcu_number_to_read):
        super().__init__(server_ip, porta, ID, usina_name)
        self._tcu_number_to_read = tcu_number_to_read
        self.log_ncu_tcu = []
        self._MBT_NCU = table.MBT_NCU_CFG
        self.MB_Table = self._MBT_NCU
        self._MBT_TCU = table.MBT_TCU
        self.tag = 'TCU_NCU'
        
        
        try:
            csv = pd.read_csv(str(self.tag) + '_' + str(self._ID) + ".csv", header = None).values.tolist()
            for j in range(len(csv)): 
                csv_log = []
                for i in range(len(csv[0])):
                    csv_log.append(ast.literal_eval(str(csv[j][i])))        
                self.log_to_send.append(csv_log)
            #print(csv_log)
            #self.destroy_csv()   
        except:
            self.log_to_send = []
        #self._MBT_NCU_WIND = table.MBT_NCU_WIND
        
        
    def read_NCU_TCU(self):
        '''
            Função de leitura dos dados do NCU e TCU
                Leitura feita a partir da csv com os dados inseridos

                Ela tem com saída um arquivo CSV com as leituras e um arquivo JSON
        '''
        if(self._client.open()):
            print("Connection " + self._MBT_NCU["equipment"][0] + str(self._ID) + " done")
            print(self._MBT_NCU["equipment"][0] +str(self._ID)+ " reading...")
            date_a = datetime.now()
            for tcu_number in range(int(self._tcu_number_to_read)+1):
                #Identifica se é leitura de NCU ou TCU
                if(tcu_number == 0):
                    self.read_and_decode_data(tcu_number)
                    self.hour_check()
                else:
                    self.MB_Table = self._MBT_TCU
                    self.read_and_decode_data(tcu_number-1)
                                    
                if(tcu_number == 0):
                    self.log_ncu_tcu.append((self._MBT_NCU["equipment"][0]+ str(self._ID) ,self.Log))

                else:
                    self.log_ncu_tcu.append((self._MBT_TCU["equipment"][0] + str(tcu_number), self.Log))
                    
            self.Log = self.log_ncu_tcu     
            self._client.close()   
            self.log_to_send.append(self.Log)
            self.data_manager()
            #self.build_jsonfile(self.log_ncu_tcu)
            #self.build_csv(self.log_to_send[0])
            #print(self._MBT_NCU["equipment"][0] +str(self._ID)+ " done")

            date_b = datetime.now()
            timecfg.scan_time(date_a,date_b)
            
        else:
            print("Connection " + "NCU" +str(self._ID)+ "fail")
            pass
        
        
    def hour_check(self):
        date = timecfg.datetime.now()
        if(timecfg.t1 < date.time() < timecfg.t2):
            self.MB_Table = table.MBT_NCU_CFG
        else:
            self.MB_Table = table.MBT_NCU_ALARM
        
            
    def data_to_json(self ,data: list, indent: int = None)-> str:
        #print(data)
        '''
        Converte os dados de coleta para o formato JSON.

                Parameters:
                    a (list): lista com os dados lidos da coleta.
                    indent (int): Tamanho da indentação usada nacodificação.

                Returns:
                    json (str): Json dos dados de coleta
        '''
        f = lambda v:reduce(lambda a, b: {**a, **b}, v)
        
        if(data[0][0] == 'NCU'+ str(self._ID)):
            tcus = [ {"name": v[0], "data": f(v[1])} for v in data[1:] ]
            ncu = {"name": data[0][0], "config": f(data[0][1]), "tcus": tcus }
            usina = { "usina": self._usina_name, "ncu": ncu}
        else:
             tcus = [ {"name": v[0], "data": f(v[1])} for v in data[0:] ]
             ncu = {"name": 'NCU'+str(self._ID) , "tcus": tcus }
             usina = { "usina": self._usina_name, "ncu":ncu }
            
        return json.dumps(usina, indent=indent)
    
    def send(self,json_obj):
        return backend.send_ncu(json_obj)
    
           
    # def read_wind_peak(self):
    #     self._cliente.open()
    #     if(self._cliente.open() == True):
    #         log = []
    #         print("Connection " + self._MBT_NCU["equipment"][0] +str(self._ID)+ " done")
            
    #         for eqp_number in range(31):
    #             self.MB_table = self._MBT_NCU_WIND
    #             data_read = self.read_and_decode_data(self.MB_table,eqp_number)
    #             log.append((self._MBT_NCU_WIND["equipment"][0] + str(eqp_number+1), data_read))
    #             self.build_jsonfile(log, 'WS_PEAK')
                    
    #     else:
    #         print("Connection " + "NCU" +str(self._ID)+ "fail")
    #         pass
    
    # def windspeedpeak_to_json(self, data: list, indent: int = None) -> str:
    #     '''
    #     Converte os dados de leitura da velocidade do vento para o formato JSON.

    #             Parameters:
    #                 wind (list): Lista com os dados lidos da coleta.
    #                 indent (int): Tamanho da indentação usada na codificação.

    #             Returns:
    #                 json (str): JSON dos dados de velocidade do vento
    #     '''
    #     f = lambda v:reduce(lambda a, b: {**a, **b}, v)
            
    #     day = [ {"name": v[0], "data": f(v[1])} for v in data[0:] ]
    #     ncu = {"name": 'NCU'+str(self._ID) , "DAY": day }
    #     usina = { "usina": self._usina_name, "ncu":ncu }
            
    #     return json.dumps(usina, indent=indent)
    
