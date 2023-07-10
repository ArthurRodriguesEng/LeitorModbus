from Client.clientmodbus import ClientMODBUS

from datetime import datetime

import timecfg

import Info.Trackers.P4Q.build_table as table

from functools import reduce

import coleta.backend as backend

from pymodbus.constants import Endian

import os


class TCUNCUClient(ClientMODBUS):
    def __init__(self, server_ip, porta, ID, usina_name, tcu_number_to_read):
        super().__init__(server_ip, porta, ID, usina_name)
        self._tcu_number_to_read = tcu_number_to_read
        self.log_ncu_tcu = []
        self.byteorder = Endian.Big
        self.wordorder = Endian.Big
        self._MBT_NCU = table.MBT_NCU_CFG
        self._MBT_TCU = table.MBT_TCU
        self.MB_Table = self._MBT_NCU

        self.tag = 'TCU_NCU'
        
        try:
            self.load_data()   
        except:
            self.log_to_send = []
            
        print(self.log_to_send)
        #self._MBT_NCU_WIND = table.MBT_NCU_WIND
        
        
    def read(self):
        '''
            Função de leitura dos dados do NCU e TCU
                Leitura feita a partir da csv com os dados inseridos

                Ela tem com saída um arquivo CSV com as leituras e um arquivo JSON
        '''
        if(self._client.open()):
            print("Connection " + self._MBT_NCU["equipment"][0] + str(self._ID) + " done")
            print(self._MBT_NCU["equipment"][0] +str(self._ID)+ " reading...")
            date_a = datetime.now()
            tcus = []
            for tcu_number in range(int(self._tcu_number_to_read)+1):
                #Identifica se é leitura de NCU ou TCU
                if(tcu_number == 0):
                    self.read_and_decode_data(EQP_number = tcu_number)
                    self.hour_check()
                else:
                    self.MB_Table = self._MBT_TCU
                    self.read_and_decode_data(EQP_number = tcu_number-1)
                                    
                if(tcu_number == 0):
                    self.log_ncu_tcu = {'usina': self._usina_name,
                                    'ncu': 
                                        {
                                        'name': self._MBT_NCU["equipment"][0]+ str(self._ID),
                                        'datetime': str(datetime.now()),
                                        'config': self.log_dict,   
                                        'tcus': []
                                        }
                                    }
                    
                else:
                    self.log_tcu = {"name": self._MBT_TCU["equipment"][0] + str(tcu_number),
                                    'data':self.log_dict}
                    tcus.append(self.log_tcu)

            self.log_ncu_tcu['ncu']['tcus'] = tcus
            self.log = self.log_ncu_tcu 
            self._client.close()   
            self.build_jsonfile()
            self.log_to_send.append(self.log)
            self.data_manager()

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
    
    def send(self,json_obj):
        return backend.send_ncu(json_obj)
        

    # def load_data(self):
    #     self.read_pkl()
    
    # def data_to_json(self, data):
    #     return json.dumps(data, 4)
    
    # def destroy_pkl(self):
    #     '''
    #         Exclui o CSV criado pelo objeto
    #     '''
    #     file = str(str(self.tag) + '_'+ str(self._ID) + ".pkl")
    #     if(os.path.exists(file) and os.path.isfile(file)): 
    #         os.remove(file)
    
    # def data_manager(self):
    #     i=0
    #     while i < len(self.log_to_send):
    #         if(self.insert_to_db(self.log_to_send[i])):
    #             self.log_to_send.pop(i)
    #             print('sent')
    #             #print(self.log_to_send)
    #         else:
    #             break
            
    #     if(self.log_to_send == []):
    #         self.destroy_pkl()
    #     else:
    #         self.build_pkl(self.log_to_send)
    

            
    # def data_to_json(self ,data: list, indent: int = None)-> str:
    #     #print(data)
    #     '''
    #     Converte os dados de coleta para o formato JSON.

    #             Parameters:
    #                 a (list): lista com os dados lidos da coleta.
    #                 indent (int): Tamanho da indentação usada nacodificação.

    #             Returns:
    #                 json (str): Json dos dados de coleta
    #     '''
    #     f = lambda v:reduce(lambda a, b: {**a, **b}, v)
        
    #     if(data[0][0] == 'NCU'+ str(self._ID)):
    #         tcus = [ {"name": v[0], "data": f(v[1])} for v in data[1:] ]
    #         ncu = {"name": data[0][0], "config": f(data[0][1]), "tcus": tcus }
    #         usina = { "usina": self._usina_name, "ncu": ncu}
    #     else:
    #          tcus = [ {"name": v[0], "data": f(v[1])} for v in data[0:]]
    #          ncu = {"name": 'NCU'+str(self._ID) , "tcus": tcus }
    #          usina = { "usina": self._usina_name, "ncu":ncu }
            
    #     return json.dumps(usina, indent=indent)
    

    
           
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
    
