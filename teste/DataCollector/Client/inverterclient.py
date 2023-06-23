from Client.clientmodbus import ClientMODBUS

import pandas as pd

import Info.Inversores.Sungrow.Sungrow as table

import ast

class InverterClient(ClientMODBUS):
    def __init__(self, server_ip, porta, ID, usina_name):
        super().__init__(server_ip, porta, ID, usina_name)
        self._MBT_INVERTER = table.MBT_INVERTER
        self.tag = 'INVERTER'
        
        try:    
            self.log_to_send = pd.read_csv(self.tag +  "_" +  str(self._ID) + ".csv").values.tolist()
            for i in range(len(self.log_to_send)): 
                self.log_to_send[i] = [ast.literal_eval(str(self.log_to_send[i][1]))]
                
        except:
            self.log_to_send = []
         
        
    def read_inverter(self):
        self._client.open()
        if(self._client.open() ==True):
            print("Connection " + self.tag + str(self._ID) + " done")
            
            self.MB_Table = self._MBT_INVERTER
            self.read_and_decode_data(0)
            self.log_to_send.append([self.Log])
            self.data_manager()
            # self.build_csv(self.log_to_send)
            # self.build_jsonfile([self.Log])
            #self.build_jsonfile(inverter_log,'INVERSOR')
            #self.insert_to_db(inverter_log,'INVETER')
            
            #self.build_csv(self.log_to_send, modbus_table, 'WS'+ str(self._ID))
        
        else:
            print("Connection" + "INVERTER" +str(self._ID)+ " fail")
            pass
        

            
            
        