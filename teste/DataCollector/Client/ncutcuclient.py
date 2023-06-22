from Client.clientmodbus import ClientMODBUS

from datetime import datetime

import timecfg

import Info.Trackers.P4Q.build_table as table

import pandas as pd

import ast

import os

import coleta.backend as backend

import json

from functools import reduce

class TCUNCUClient(ClientMODBUS):
    def __init__(self, server_ip, porta, ID, usina_name, tcu_number_to_read):
        super().__init__(server_ip, porta, ID, usina_name)
        self._tcu_number_to_read = tcu_number_to_read
        self._MBT_NCU = table.MBT_NCU_CFG
        self._MBT_TCU = table.MBT_TCU
        self.Log_NCU_TCU = []
        # if ncu_cfg_scan == 1:
        #     self._MBT_NCU = table.MBT_NCU_CFG
        # else:
        #     self._MBT_NCU = table.MBT_NCU_ALARM
        try:    
            self.log_to_send = pd.read_csv('TCU_NCU' + str(self._ID) +  "_" + ".csv").values.tolist()
            for i in range(len(self.log_to_send)):
                self.log_to_send[i] = [ast.literal_eval(self.log_to_send[i][1])]
                
        except:
            self.log_to_send = []
            

        
        
    def read_NCU_TCU(self):
        '''
            Função de leitura dos dados do NCU e TCU
                Leitura feita a partir da csv com os dados inseridos

                Ela tem com saída um arquivo CSV com as leituras e um arquivo JSON
        '''   
        print(self.log_to_send)
        self._client.open()
        if(self._client.open()):
            print("Connection " + self._MBT_NCU["equipment"][0] +str(self._ID)+ " done")
            print(self._MBT_NCU["equipment"][0] +str(self._ID)+ " reading...")
            date_a = datetime.now()
            for tcu_number in range(int(self._tcu_number_to_read)+1):
                #Identifica se é leitura de NCU ou TCU
                if(tcu_number == 0):
                    #print(self._MBT_NCU["equipment"][0] + str(self._ID))
                    self.MB_Table = self._MBT_NCU
                    self.read_and_decode_data(tcu_number)
                else:
                    #print(self._MBT_TCU["equipment"][0] + str(tcu_number))
                    self.MB_Table = self._MBT_TCU
                    self.read_and_decode_data(tcu_number-1)
                                    
                if(tcu_number == 0):
                    self.Log_NCU_TCU.append((self._MBT_NCU["equipment"][0]+ str(self._ID) , self.Log))
                else:
                    self.Log_NCU_TCU.append((self._MBT_TCU["equipment"][0] + str(tcu_number), self.Log))
                
            self.log_to_send.append([self.Log_NCU_TCU])
            self.data_manager()
            #self.build_csv(self.log_to_send, 'NCU'+ str(self._ID))
            #self.build_jsonfile()
            #print(self._MBT_NCU["equipment"][0] +str(self._ID)+ " done")

            date_b = datetime.now()
            timecfg.scan_time(date_a,date_b)
            self.hour_check()
        else:
            print("Connection " + "NCU" +str(self._ID)+ "fail")
            pass
        
    
    def hour_check(self):
        date = timecfg.datetime.now()
        if(timecfg.t1 < date.time() < timecfg.t2):
            self._MBT_NCU = table.MBT_NCU_CFG
        else:
            self._MBT_NCU = table.MBT_NCU_ALARM
        
    def build_jsonfile(self):
        data_log = self.data_to_json(self.Log_NCU_TCU,4)
        with open('TCU_NCU'+ str(self._ID) +".json", "w") as outfile:
            outfile.write(data_log)
            
    def insert_to_db(self, log):
        json_obj = json.loads(self.data_to_json(log[0],4))
        # regress = backend.send_ncu(json_obj)
        # if(regress):
        #     print('Send done')
        # else:
        #     print('Send fail')
        return False
    
    def data_manager(self):
        i=0
        while i < len(self.log_to_send):
            if(self.insert_to_db(self.log_to_send[i])):
                self.log_to_send.pop(i)
            else:
                break
        if(self.log_to_send == []):
            file = str('TCU_NCU'+ str(self._ID) +  "_" + ".csv")
            if(os.path.exists(file) and os.path.isfile(file)): 
                os.remove(file)
        else:
            self.build_csv(self.log_to_send, 'NCU'+ str(self._ID))
            
    def data_to_json(self ,data: list, indent: int = None)-> str:
        print(data)
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