from Client.clientmodbus import ClientMODBUS


import Info.Inversores.Sungrow.Sungrow as table

import coleta.backend as backend

class InverterClient(ClientMODBUS):
    def __init__(self, server_ip, porta, ID, usina_name):
        super().__init__(server_ip, porta, ID, usina_name)
        self.MB_Table = table.MBT_INVERTER
        self.tag = 'INVERTER'
        self.load_data()
         
        
    def read_inverter(self):
        #self._client.open()
        if(self._client.open()):
            print("Connection " + str(self.tag) + str(self._ID) + " done")
            self.read_and_decode_data(0)
            self._client.close()
            self.build_jsonfile([self.Log])
            self.log_to_send.append([self.Log])
            self.data_manager()
            
        else:
            print("Connection" + str(self.tag) +str(self._ID)+ " fail")
            pass

    
    def send(self):
        #return backend.send_inverter(json_obj)
        return False
        

            
            
        