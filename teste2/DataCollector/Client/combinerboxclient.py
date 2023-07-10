from Client.clientmodbus import ClientMODBUS

import Info.Inversores.Sungrow.Sungrow as table

import coleta.backend as backend

import timecfg
from datetime import datetime
from pymodbus.constants import Endian

class CombinerboxClient(ClientMODBUS):
    def __init__(self, server_ip, porta, ID, usina_name, unit_id):
        super().__init__(server_ip, porta, ID, usina_name, unit_id)
        self.MB_Table = table.MBT_C_BOX
        self.byteorder = Endian.Big
        self.wordorder = Endian.Little
        self.tag = 'C_BOX'
        self.load_data()
         
        
    def read(self):
        #self._client.open()
        if(self._client.open()):
            print("Connection " + str(self.tag) + str(self._ID) + " done")
            print(self.MB_Table["equipment"][0] +str(self._ID)+ " reading...")
            date_a = datetime.now()
            self.read_and_decode_data()
            self._client.close()
            self.build_dict()
            self.build_jsonfile()
            self.log_to_send.append(self.log)
            self.data_manager()
            date_b = datetime.now()
            timecfg.scan_time(date_a,date_b)
            
        else:
            print("Connection" + str(self.tag) +str(self._ID)+ " fail")
            pass
    
    def send(self):
        #return backend.send_inverter(json_obj)
        return False