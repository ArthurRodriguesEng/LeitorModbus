from pyModbusTCP.client import ModbusClient
from time import sleep
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import pyModbusTCP.utils
import scipy
import datetime

import math


class ClienteMODBUS():
    """
    Classe Cliente MODBUS
    """

    def __init__(self, server_ip, porta, scan_time=1):
        """
        Construtor
        Cria o objeto do cliente modbus
        """
        self._cliente = ModbusClient(host=server_ip, port=porta)
        self._scan_time = scan_time
        print("Connection done")

    #R	30506	(31..0)	F32	Position_a1_rad_s1	angular position in radians
    #R	30510	(31..0)	F32	TargetAngle_a1_rad_s1	Target angle in radians
    #R	29500	(31..0)	U32	lastComm_s1	Unix Epoch formated timestamp of the last successful read of this TCU
    #R	30502	(15..0)	U16	Alarms1_s1	Group(16): Alarms1
    #R	36240	(15..0)	U16	Second_day_31	Local Wind Sensor 1. Peak of day 31. Second
    

    def atendimento(self):
        """
        Método para atendimento do usuário
        """

        self._cliente.open()
        addr = (30506,30510,29499,36247,30501)
        name_addr = ('angle_pos','target','lastcomm', 'wind speed', 'state')
        n_reg = (2,2,2,1,1)
        try:
            atendimento = True
            while atendimento:
                    i = 0
                    while True:
                        while i<5:

                            if(i < 2):
                                print(name_addr[i]+ ":"+str(self.rad_to_grau(self.read_data(int(5),int(addr[i]), int(n_reg[i])))) +"°")
                            if(i==2):
                                print(name_addr[i]+ ":"+str(self.float_to_date(self.read_data(int(5),int(addr[i]), int(n_reg[i])))))
                            if(i==3):
                                print(name_addr[i]+ ":"+str(self.decode_uint16(self.read_data(int(5),int(addr[i]), int(n_reg[i]))))+"m/s")
                            if(i==4):
                                print(name_addr[i]+ ":"+str(self.decode_uint16(self.read_data(int(5),int(addr[i]), int(n_reg[i])))))

                            i+=1
                         
                        i=0
                        sleep(self._scan_time)

        except Exception as e:
            print('Erro no atendimento: ', e.args)

    def read_data(self, tipo, addr, n_reg):
        """
        Método para leitura de um dado da Tabela MODBUS
        """
        #Leitura do Registrador
        if tipo == 5:
            result = self._cliente.read_holding_registers(addr+1, n_reg)
            return result

        
    def decode_float32(self,decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_32bit_float()
        return decoder
    
    def decode_uint16(self,decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_16bit_uint()
        return decoder


    def rad_to_grau(self, decoder):
        decoder = self.decode_float32(decoder)
        return decoder*180/ math.pi
    
    def float_to_date(self,decoder):
        epoch = (2**16*decoder[1] + decoder[0] -7200)
        date = datetime.datetime.fromtimestamp(epoch)
        return  date
    


