from Client.clientmodbus import ClientMODBUS

import pandas as pd

import Info.Inversores.Sungrow.Sungrow as table

class InverterClient(ClientMODBUS):
    def __init__(self, server_ip, porta, ID, usina_name):
        super().__init__(server_ip, porta, ID, usina_name)
        self._MBT_INVERTER = table.MBT_INVERTER
        
        try:    
            self.log_to_send = pd.read_csv('INVERTER' + str(self._ID) +  "_" + ".csv").values.tolist()
            for i in range(len(self.log_to_send)): self.log_to_send[i] = self.log_to_send[i][1]
        except:
            self.log_to_send = []
         
        
    def read_inverter(self):
        self._client.open()
        if(self._client.open() ==True):
            print('INVERTER' + str(self._ID))
            modbus_table = self._MBT_INVERTER
            inverter_log = self.read_and_decode_data(modbus_table,0)
            self.build_jsonfile(inverter_log,'INVERSOR')
            #self.insert_to_db(inverter_log,'INVETER')
            self.log_to_send.append(inverter_log)
            #elf.build_csv(self.log_to_send, modbus_table, 'WS'+ str(self._ID))
            #i=0
            # while i < len(self.log_to_send):
            #     if(self.insert_to_db(self.log_to_send[i],'RB_INVERTER')):
            #         self.log_to_send.pop(i)
            #     else:
            #         while i < len(self.log_to_send):
            #             #self.build_csv(log, modbus_table, 'NCU'+ str(self._ID) + '_' + str(i))
            #             self.build_csv(self.log_to_send, modbus_table, str(self._ID))
            #             self.build_jsonfile(inverter_log)
            #             i += 1
            #         break