from pyModbusTCP.client import ModbusClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

from functools import reduce
from datetime import datetime

import math
import json

import pandas as pd

import coleta.backend as backend


class ClientMODBUS():
    '''
        Construtor da Classe Cliente MODBUS
    '''

    #def __init__(self, server_ip, porta, usina_name, ID, tcu_number_to_read, ncu_scan):
    def __init__(self, server_ip, porta , ID , usina_name):
        self._client = ModbusClient(host=server_ip, port=porta)
        self._usina_name = usina_name
        self._ID = ID
        self.MB_Table = []
        self.Log = []
 
    def read_and_decode_data(self, EQP_number):
        data_read = []
        for tag_count in range(len(self.MB_Table["address"])):
            #print(self.MB_Table["address"][tag_count],self.MB_Table["var_name"][tag_count])
            try:
                decoder = "NaN"
                if(int(self.MB_Table["n_bit"][tag_count]) == 64):
                    if(self.MB_Table["type"][tag_count] == "S64"):
                        decoder = self.read_data(int(self.MB_Table["func"][tag_count]),int(self.MB_Table["address"][tag_count] + self.MB_Table["up_addr"][tag_count]*(EQP_number)), int(4))
                if(int(self.MB_Table["n_bit"][tag_count]) == 32):
                    if(self.MB_Table["type"][tag_count] == "F32"):
                        decoder = self.read_data(int(self.MB_Table["func"][tag_count]),int(self.MB_Table["address"][tag_count] + self.MB_Table["up_addr"][tag_count]*(EQP_number) +1), int(2))
                        #print(decoder)
                        decoder = self.decode_float32(decoder)
                    elif(self.MB_Table["type"][tag_count] == "D32"):
                        decoder = self.read_data(int(self.MB_Table["func"][tag_count]),int(self.MB_Table["address"][tag_count] + self.MB_Table["up_addr"][tag_count]*(EQP_number)), int(2))
                        decoder = str(self.float_to_date(decoder))
                    elif(self.MB_Table["type"][tag_count] == "U32"):
                        decoder = self.read_data(int(self.MB_Table["func"][tag_count]),int(self.MB_Table["address"][tag_count] + self.MB_Table["up_addr"][tag_count]*(EQP_number)), int(2))
                        decoder = str(self.decode_uint32(decoder))
                    else:
                        decoder = self.read_data(int(self.MB_Table["func"][tag_count]),int(self.MB_Table["address"][tag_count] + self.MB_Table["up_addr"][tag_count]*(EQP_number) +1 ), int(2)) 
                if(int(self.MB_Table["n_bit"][tag_count]) == 16):
                    decoder = self.read_data(int(self.MB_Table["func"][tag_count]),int(self.MB_Table["address"][tag_count]+ self.MB_Table["up_addr"][tag_count]*(EQP_number)), int(1))
                    if(int(self.MB_Table["alarm"][tag_count]) == 1):
                        decoder = self.read_all_bits(self.decode_uint16(decoder))
                    else:
                        if(self.MB_Table["type"][tag_count] == "S16"):
                            decoder= int(self.decode_int16(decoder))
                        elif(self.MB_Table["type"][tag_count] == "U16"):
                            decoder= int(self.decode_uint16(decoder))
                        else:
                            pass      
                if(int(self.MB_Table["n_bit"][tag_count]) == 8):
                    decoder = self.read_data(self.MB_Table["func"][tag_count],int(self.MB_Table["address"][tag_count]+ self.MB_Table["up_addr"][tag_count]*(EQP_number-1)), int(1))
                    if(int(self.MB_Table["start_bit"][tag_count]) == 15):
                        decoder = self.decode_16_to_2_8_int(decoder,1)
                    elif(int(self.MB_Table["start_bit"][tag_count]) == 7):
                        decoder = self.decode_16_to_2_8_int(decoder,2)
                    else:
                        pass

                    # if(self.MB_Table["type"][tag_count] == "S8"):
                    #     decoder = int(self.decode_int8(decoder))
                    # else:
                    #     decoder = int(self.decode_uint8(decoder))

                if(int(self.MB_Table["n_bit"][tag_count]) < 8):
                    decoder = self.read_bits(self.read_data(self.MB_Table["func"][tag_count],int(self.MB_Table["address"][tag_count]+ self.MB_Table["up_addr"][tag_count]*(EQP_number-1)), int(1)),int(self.MB_Table["start_bit"][tag_count]),(int(self.MB_Table["start_bit"][tag_count] -int(self.MB_Table["n_bit"][tag_count]))))
                # try:
                #     if(not type(decoder) == list):
                #         decoder = float(decoder)* float(self.MB_Table["mult"][tag_count])
                #     else:
                #         continue
                # except:
                #     continue
                #print(decoder)
                data_read.append({self.MB_Table["var_name"][tag_count]: decoder})
            except Exception as e:
                    print('Erro scan: ', e.args)
                    continue
        self.Log = data_read        
        #return data_read


    def read_data(self, tipo, addr, n):
        '''
            Função de leitura dos dados modbus
                Paramaters:
                    tipo : tipo de leitura que deve ser feito (Default = 6, Holding_register)
                    addr : endereço da tabela modbus +1
                    n_reg : número de registrador
        '''
        
        if tipo == 1:
            result = self._client.read_coils(addr,  n)
            return result
        if tipo == 2:
            result = self._client.read_discrete_inputs(addr,  n)
            return result
        if tipo == 5:
            result = self._client.read_input_registers(addr,  n)
            return result
        if tipo == 6:
            result = self._client.read_holding_registers(addr,  n)
            return result
        
    def build_csv(self,log,ID):
        df = pd.DataFrame(log)
        df.to_csv(str(self.MB_Table["equipment"][0]) +  "_" + str(ID) +  "_" + ".csv", header= False)

    def build_jsonfile(self, log, tag=None, number=None):
        data_log = json.dumps(log,indent= 4)
        with open(str(tag) + str(self._ID) + '_'+ str(number) +".json", "w") as outfile:
            outfile.write(data_log)
       
        
    def decode_float64(self,decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_64bit_float()
        return decoder
    
    def decode_int64(self,decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_64bit_int()
        return decoder
    
    def decode_uint64(self,decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_64bit_uint()
        return decoder
        
    #Decodifica os 2 registradores em 1 valor float
    def decode_float32(self,decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_32bit_float()
        return decoder
    
    def decode_int32(self,decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_32bit_int()
        return decoder
    
    def decode_uint32(self,decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_32bit_uint()
        return decoder

    #Decodifica 1 registrador em 1 valor inteiro sem sinal
    def decode_uint16(self,decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_16bit_uint()
        return decoder
    
    #Decodifica 1 registrador em 1 valor inteiro
    def decode_int16(self,decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_16bit_int()
        return decoder
    
    #Decodifica 8 bits em 1 valor inteiro
    def decode_uint8(self,decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_8bit_uint()
        return decoder
    
    def decode_int8(self,decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_8bit_int()
        return decoder

    #Transforma radianos em grau
    def rad_to_grau(self, decoder):
        decoder = self.decode_float32(decoder)
        return decoder*180/ math.pi
    
    #Transforma o valor do registrador em formato data
    def float_to_date(self,decoder):
        epoch = (2**16*decoder[1] + decoder[0])
        date = datetime.fromtimestamp(epoch)
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
    
    #passa o valor inteiro e retorna quais os bits que estão ativos
    def read_all_bits(self,decoder):
        report = []
        for count in range(16):
            if((decoder - 2**(15-count)) >= 0):
                report.append(15-count)
                decoder = decoder - 2**(15-count)
        return report
    
    #Ler o intervalo de bits determinado e retorna o valor em inteiro
    def read_bits(self, decoder, bit_start, bit_finish):
        '''
        Converte o valor do registrador nos bits selecioandos em um valor inteiro 

                Parameters:
                    decoder(list): Lista com o valor do registrador.
                    bit_start (int): Bit de inicio
                    bit_finish (int): Bit final 
                Returns:
                    int : valor dos bits selecionados em formato de inteiro
        '''
        decoder_bit = list(format(decoder[0], 'b'))
        decoder_bit =['0' for i in range(16-len(decoder_bit))] + decoder_bit
        decoder_bit = decoder_bit[15-bit_start: 15-bit_finish]
        decoder_bit = str ('0b' + ''.join(decoder_bit))
        return int(decoder_bit,2)
    
    # def data_to_json(self ,data: list, indent: int = None)-> str:
    #     '''
    #     Converte os dados de coleta para o formato JSON.

    #             Parameters:
    #                 a (list): lista com os dados lidos da coleta.
    #                 indent (int): Tamanho da indentação usada nacodificação.

    #             Returns:
    #                 json (str): Json dos dados de coleta
    #     '''
    #     f = lambda v:reduce(lambda a, b: {**a, **b}, v)
        
    #     if(data[0][0] == 'NCU'+ str(self._ID)):
    #         tcus = [ {"name": v[0], "data": f(v[1])} for v in data[1:] ]
    #         ncu = {"name": data[0][0], "config": f(data[0][1]), "tcus": tcus }
    #         usina = { "usina": self._usina_name, "ncu": ncu}
    #     else:
    #          tcus = [ {"name": v[0], "data": f(v[1])} for v in data[0:] ]
    #          ncu = {"name": 'NCU'+str(self._ID) , "tcus": tcus }
    #          usina = { "usina": self._usina_name, "ncu":ncu }
            
    #     return json.dumps(usina, indent=indent)

    # def windspeed_to_json(self, wind: list, indent: int = None) -> str:
    #     '''
    #     Converte os dados de leitura da velocidade do vento para o formato JSON.

    #             Parameters:
    #                 wind (list): Lista com os dados lidos da coleta.
    #                 indent (int): Tamanho da indentação usada na codificação.

    #             Returns:
    #                 json (str): JSON dos dados de velocidade do vento
    #     '''
    #     data = { 
    #         'usina': self._usina_name,
    #         'ncu': 'NCU'+str(self._ID),
    #         'NcuDatetime': wind[0][1]['NcuDatetime'], 
    #         'WindSpeed_mps_rsu1': wind[0][0]['WindSpeed_mps_rsu1'] 
    #     }
    #     return json.dumps(data, indent=indent)


    def windspeedpeak_to_json(self, data: list, indent: int = None) -> str:
        '''
        Converte os dados de leitura da velocidade do vento para o formato JSON.

                Parameters:
                    wind (list): Lista com os dados lidos da coleta.
                    indent (int): Tamanho da indentação usada na codificação.

                Returns:
                    json (str): JSON dos dados de velocidade do vento
        '''
        f = lambda v:reduce(lambda a, b: {**a, **b}, v)
            
        day = [ {"name": v[0], "data": f(v[1])} for v in data[0:] ]
        ncu = {"name": 'NCU'+str(self._ID) , "DAY": day }
        usina = { "usina": self._usina_name, "ncu":ncu }
            
        return json.dumps(usina, indent=indent)
        


