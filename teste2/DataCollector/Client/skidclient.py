from Client.clientmodbus import ClientMODBUS
from pymodbus.transaction import ModbusRtuFramer

import Info.Skid.Skid as table

import coleta.backend as backend

import timecfg
from datetime import datetime
from pymodbus.constants import Endian

class SkidClient(ClientMODBUS):
    def __init__(self, server_ip, porta, ID, usina_name, unit_id, type):
        super().__init__(server_ip, porta, ID, usina_name, framer = ModbusRtuFramer)
        self.unit_id = unit_id
        self.MB_Table = table.MBT_SKID
        self.type = type
        self.tag = 'SKID'
        self.load_data()
         
        
    def read(self):
        #self._client.open()
        if(self._client.open()):
            print("Connection " + str(self.tag) + str(self._ID) + " done")
            print(self.MB_Table["equipment"][0] +str(self._ID)+ " reading...")
            date_a = datetime.now()
            print(self.read_and_decode_data())
            self._client.close()
            self.build_jsonfile(self.log)
            self.log_to_send.append(self.log)
            self.data_manager()
            date_b = datetime.now()
            timecfg.scan_time(date_a,date_b)
            
        else:
            print("Connection" + str(self.tag) +str(self._ID)+ " fail")
            pass

    def read_and_decode_data(self):
            self.log = {self._client.read_input_registers(1,self._ID , unit= self.unit_id)}
            return self.log
            
    
    def send(self):
        #return backend.send_inverter(json_obj)
        return False
        