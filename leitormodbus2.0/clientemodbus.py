from pyModbusTCP.client import ModbusClient
from time import sleep
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import pyModbusTCP.utils
import datetime
import math
import pandas as pd
import json
from threading import Thread
import time
from functools import reduce




class ClienteMODBUS():

    def __init__(self, server_ip, porta, scan_time=20,scan_time_wind = 3):
        self._cliente = ModbusClient(host=server_ip, port=porta)
        self._scan_time = scan_time
        self._scan_time_wind = scan_time_wind
        print("Connection done")

    def start_scan(self):

        '''
            Função de leitura dos dados do NCU e TCU
                Leitura feita a partir da csv com os dados inseridos

                Ela tem com saída um arquivo CSV com as leituras e um arquivo JSON
        '''
        self._cliente.open()
        tcu_number_to_read = 12
        try:
            while True:
                    tcu_number = -1
                    all_data_read = []
                    DATA_LOG ={}
                    while tcu_number < tcu_number_to_read:
                        #Identifica se é leitura de NCU ou TCU
                        if(tcu_number == -1):
                            print('NCU')
                            modbus_table = pd.read_csv('NCU_MODBUS_SLIN_CFG.csv', delimiter=';')
                            addr = modbus_table["address"].tolist()
                            
                        else:
                            print('TCU' + str(tcu_number+1))
                            modbus_table = pd.read_csv('TCU MODBUS SLIN.csv', delimiter=';')
                            addr = modbus_table["address"].tolist()
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

                                if(int(modbus_table["n_bit"][tag_count]) == 32):
                                    if(modbus_table["type"][tag_count] == "F32"):
                                        decoder = self.read_data(int(6),int(modbus_table["address"][tag_count] + up_addr*(tcu_number) +1 ), int(2))
                                        decoder = self.decode_float32(decoder)
                                    else:
                                        decoder = self.read_data(int(6),int(modbus_table["address"][tag_count] + up_addr*(tcu_number)), int(2))
                                        decoder = self.float_to_date(decoder)
                                    #print(decoder)
                                    if(str(modbus_table["unit"][tag_count]) == 'rad'):
                                        pos = self.rad_to_grau(decoder)
                                        print(str(self.modbus_table["var_name"][tag_count])+ ":"+str(pos) +"°")
                                    else:
                                        print(str(self.modbus_table["var_name"][tag_count])+ ":"+str(decoder))
                                if(int(modbus_table["n_bit"][tag_count]) == 16):
                                    #print(modbus_table["n_bit"][tag_count]) 
                                    decoder = self.read_data(int(6),int(modbus_table["address"][tag_count]+ up_addr*(tcu_number)), int(1))
                                    if(str(modbus_table["alarm"][tag_count]) == 1):
                                        decoder = self.read_all_bits(decoder)
                                    else:  
                                        decoder = self.decode_uint16(decoder)
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
                                
                                
                                
                                data_read.append({modbus_table["var_name"][tag_count]: decoder})
                                
                                
                                tag_count+=1
                            except:
                                tag_count+=1
                                pass 
                                            
                        if(tcu_number == -1):
                            all_data_read.append(('NCU' , data_read))
                        else:
                            all_data_read.append(('TCU' + str(tcu_number+1), data_read))
                        tcu_number += 1
                        
                   
                    print(all_data_read)
                    self.data_to_json(all_data_read,4)

                    df = pd.DataFrame(all_data_read)
                    df.to_csv("dados_lidos.csv")

                    tcu_number = 0

                    sleep(self._scan_time)

        except Exception as e:
            print('Erro scan: ', e.args)

    def wind_speed(self):
        
        '''
            Função de leitura dos dados de velocidade de vento e hora/data do NCU
                Leitura feita a partir da csv com os dados inseridos
        '''
        self._cliente.open()
        wind_speed = []
        try:
            modbus_table = pd.read_csv('WINDSPEED_MODBUS_SLIN.csv', delimiter=';')
            addr = modbus_table["address"].tolist()
            tag_count = 0
            while tag_count<len(addr):
                if(modbus_table["type"][tag_count] == "F32"):
                    decoder = self.read_data(int(6),int(modbus_table["address"][tag_count]  +1 ), int(2))
                    decoder = self.decode_float32(decoder)
                else:
                    decoder = self.read_data(int(6),int(modbus_table["address"][tag_count] ), int(2))
                    decoder = self.float_to_date(decoder)
                wind_speed.append({modbus_table["var_name"][tag_count]: decoder})
                df_wind = pd.DataFrame(wind_speed)
                df_wind.to_csv("wind_speed.csv")
                sleep(self._scan_time_wind)
        except:
            pass
        
        

    def read_data(self, tipo, addr, n_reg):
        '''
            Função de leitura dos dados modbus
                Paramaters:
                    tipo : tipo de leitura que deve ser feito (Default = 6, Holding_register)
                    addr : endereço da tabela modbus +1
                    n_reg : número de registradores
        '''
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
    
    def data_to_json(data: list, indent: int = None) -> str:
        '''
        Converte os dados de coleta para o formato JSON.

                Parameters:
                    a (list): lista com os dados lidos da coleta.
                    indent (int): Tamanho da indentação usada nacodificação.

                Returns:
                    json (str): Json dos dados de coleta
        '''
        f = lambda v: reduce(lambda a, b: {**a, **b}, v)
        tcus = [ {"name": v[0], "data": f(v[1])} for v in data[1:] ]
        ncu = { "name": data[0][0], "config": f(data[0][1]), "tcus": tcus }
        return json.dumps(ncu, indent=indent)




    
    


