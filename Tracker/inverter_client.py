from clientemodbus import ClienteMODBUS
from pyModbusTCP.client import ModbusClient

import Inversores.Sungrow.Sungrow as table_inverter

class InverterClient(ClienteMODBUS):
    def __init__(self, server_ip, porta, ID, usina_name):
        super().__init__(server_ip, porta, ID, usina_name)
        self._MBT_INVERTER = table_inverter.MBT_INVERTER
         
        
    def read_inverter(self):
        self._cliente.open()
        if(self._cliente.open() ==True):
            print('INVERTER' + str(self._ID))
            inverter_log = self.read_and_decode_data(self._MBT_INVERTER,0)
            self.build_csv(inverter_log, self._MBT_INVERTER, self._ID)
            #self.build_jsonfile(inverter_log,'INVERTER')
            #self.insert_to_mongodb(inverter_log,'INVETER')
         