from Client.clientmodbus import ClienteMODBUS


import Info.Inversores.Sungrow.Sungrow as table

class InverterClient(ClienteMODBUS):
    def __init__(self, server_ip, porta, ID, usina_name):
        super().__init__(server_ip, porta, ID, usina_name)
        self._MBT_INVERTER = table.MBT_INVERTER
         
        
    def read_inverter(self):
        self._cliente.open()
        if(self._cliente.open() ==True):
            print('INVERTER' + str(self._ID))
            inverter_log = self.read_and_decode_data(self._MBT_INVERTER,0)
            self.build_csv(inverter_log, self._MBT_INVERTER, self._ID)
            self.build_jsonfile(inverter_log,'INVERSOR')
            #self.insert_to_db(inverter_log,'INVETER')
         