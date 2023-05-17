from pyModbusTCP.client import ModbusClient
from time import sleep
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import pyModbusTCP.utils
#import scipy
import datetime
#from Adafruit_IO import Client
import math
import enviar_web
import pandas as pd
import json



class ClienteMODBUS():
    """
    Classe Cliente MODBUS
    """

    def __init__(self, server_ip, porta, scan_time=240):
        """
        Construtor
        Cria o objeto do cliente modbus
        """
        self._cliente = ModbusClient(host=server_ip, port=porta)
        self._scan_time = scan_time
        print("Connection done")

    'Dados de Leitura'
    #R	30506	(31..0)	F32	Position_a1_rad_s1	angular position in radians
    #R	30510	(31..0)	F32	TargetAngle_a1_rad_s1	Target angle in radians
    #R	29500	(31..0)	U32	lastComm_s1	Unix Epoch formated timestamp of the last successful read of this TCU
    #R	30502	(15..0)	U16	Alarms1_s1	Group(16): Alarms1
    #R	30503	(15..0)	U16	Alarms2_s1	Group(16): Alarms2 (memorized alarms)
    #R	36240	(15..0)	U16	Second_day_31	Local Wind Sensor 1. Peak of day 31. Second
    #R	30521	(7..0)	U8	StateOfHealth_s1	Battery: State Of Health

    #R	30513	(15..8)	S8	FinishCharge_days_s1	"Number of days since the last time the battery has reached its full charge calibration-1=Not calibrated 0..127=days"	0..100	%	Yes
    #R	30513	(7..0)	U8	StateOfCharge_s1	Battery: State Of Charge	0..100	%	Yes



    'Dados para escrita'
    #W	ClearBlockings	40102	(1..1)	B	Clear Axis Blockings in all the TCUs.
    

    def start_scan(self):

        self._cliente.open()
        tcu_number_to_read = 12
        try:
            start_scan = True
            while start_scan:
                while True:
                        tcu_number = -1
                        all_data_read = []
                        while tcu_number < tcu_number_to_read:
                            if(tcu_number == -1):
                                print('NCU')
                            else:
                                print('TCU' + str(tcu_number+1))

                            if(tcu_number == -1):
                                modbus_table = pd.read_csv('NCU_MODBUS_SLIN.csv', delimiter=';')
                                addr = modbus_table["address"].tolist()
                            else:
                                modbus_table = pd.read_csv('TCU MODBUS SLIN.csv', delimiter=';')
                                addr = modbus_table["address"].tolist()
                            # print(addr)
                            tag_count = 0
                            data_read = []
                            while tag_count<len(addr):
                                try:
                                    decoder = "NaN"
                                    if(tcu_number == -1):
                                        up_addr = 0
                                    elif(int(modbus_table["address"][tag_count]) == int(29500) and tcu_number >= 0):
                                        up_addr = 2
                                    else:
                                        up_addr = 22

                                    #print(tag_count)
                                    #print("addr" + str(modbus_table["address"][tag_count]))
                                    if(int(modbus_table["n_bit"][tag_count]) == 32):
                                        if(modbus_table["type"][tag_count] == "F32"):
                                            decoder = self.read_data(int(6),int(modbus_table["address"][tag_count] + up_addr*(tcu_number) +1 ), int(2))
                                        else:
                                            decoder = self.read_data(int(6),int(modbus_table["address"][tag_count] + up_addr*(tcu_number)), int(2))

                                        #print(decoder)
                                        # if(str(modbus_table["unit"][tag_count]) == 'rad'):
                                        #     pos = self.rad_to_grau(decoder)
                                        #     print(str(self.modbus_table["var_name"][tag_count])+ ":"+str(pos) +"°")
                                        # else:
                                        #     print(str(self.modbus_table["var_name"][tag_count])+ ":"+str(decoder))
                                    if(int(modbus_table["n_bit"][tag_count]) == 16):
                                        #print(modbus_table["n_bit"][tag_count]) 
                                        decoder = self.decode_uint16(self.read_data(int(6),int(modbus_table["address"][tag_count]+ up_addr*(tcu_number)), int(1)))
                                        #print(decoder)
                                        # if(str(modbus_table["unit"][tag_count]) == 'K'):
                                        #     print(str(self.modbus_table["var_name"][tag_count])+ ":"+str(decoder /10) + str(modbus_table["unit"][tag_count]))
                                        # else:
                                        #     print(str(self.modbus_table["var_name"][tag_count])+ ":"+str(decoder) + str(modbus_table["unit"][tag_count]))
                                    if(int(modbus_table["n_bit"][tag_count]) == 8):
                                        #print(modbus_table["n_bit"][tag_count]) 
                                        if(int(modbus_table["start_bit"][tag_count]) == 15):
                                            decoder = self.decode_16_to_2_8_int(self.read_data(int(6),int(modbus_table["address"][tag_count]+ up_addr*(tcu_number)), int(1)),1)
                                            #print(decoder)
                                            #print(str(self.modbus_table["var_name"][tag_count])+ ":"+str(decoder) + str(modbus_table["unit"][tag_count]))
                                        elif(int(modbus_table["start_bit"][tag_count]) == 7):
                                            decoder = self.decode_16_to_2_8_int(self.read_data(int(6),int(modbus_table["address"][tag_count]+ up_addr*(tcu_number)), int(1)),2)
                                            #print(decoder)
                                            #print(str(self.modbus_table["var_name"][tag_count])+ ":"+str(decoder) + str(modbus_table["unit"][tag_count]))
                                        else:
                                            pass
                                    if(int(modbus_table["n_bit"][tag_count]) == 1):
                                        #print(modbus_table["n_bit"][tag_count]) 
                                        decoder = self.read_bit(self.read_data(int(6),int(modbus_table["address"][tag_count]+ up_addr*(tcu_number)), int(1)),modbus_table["start_bit"][tag_count])
                                        print(decoder)
                                        #print(str(self.modbus_table["var_name"][tag_count])+ ":"+str(decoder) + str(modbus_table["unit"][tag_count]))
                                    
                                    
                                    data_read.append([int(modbus_table["address"][tag_count])+ up_addr*(tcu_number),modbus_table["var_name"][tag_count], decoder])    

                                    tag_count+=1
                                except:
                                    tag_count+=1
                                    pass 

                            #print(data_read)
                            if(tcu_number == -1):
                                all_data_read.append(['NCU' , data_read])
                            else:
                                all_data_read.append(['TCU' + str(tcu_number+1), data_read])
                            tcu_number += 1
                        print(all_data_read)

                        df = pd.DataFrame(all_data_read)
                        df.to_csv("dados_lidos.csv")

                        tcu_number = 0

                        sleep(self._scan_time)


        except Exception as e:
            print('Erro scan: ', e.args)

    def read_data(self, tipo, addr, n_reg):
        if tipo == 6:
            result = self._cliente.read_holding_registers(addr, n_reg)
            #print(result)
            return result
        
    #Decodifica os 2 registradores em 1 valor float
    def decode_float32(self,decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_32bit_float()
        return decoder

    #Decodifica 1 registrador em 1 valor inteiro
    def decode_uint16(self,decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_16bit_uint()
        return decoder
    
    #Decodifica 8 bits em 1 valor inteiro
    def decode_uint8(self,decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_8bit_uint()
        return decoder

    #Transforma radianos em grau
    def rad_to_grau(self, decoder):
        decoder = self.decode_float32(decoder)
        return decoder*180/ math.pi
    
    #Transforma o valor do registrador em formato data
    def float_to_date(self,decoder):
        epoch = (2**16*decoder[1] + decoder[0])
        date = datetime.datetime.fromtimestamp(epoch)
        return date
    
    def decode_16_to_2_8_int(self,decoder,part):
        decoder_1 = decoder[0] >> 8
        decoder_2 = decoder[0] & 255
        if(part == 1):
            return decoder_1
        elif(part ==2):
            return decoder_2
        else:
            print('erro')

    #passa o valor inteiro e o bit que deseja ler e ele retorna o valor do bit
    def read_bit(self, decoder, bit):
        decoder_bit = list(format(decoder[0], 'b'))
        return decoder_bit[15-bit]
    
    #passa o valor inteiro e retorna quais os bits que estão ativos
    def read_all_bits(self,decoder):
        count=15
        report = []
        while count>-1:
            if((decoder - 2**count) >= 0):
                report.append(count)
                decoder = decoder - 2**count
            count -= 1
        return report
    




    
    


