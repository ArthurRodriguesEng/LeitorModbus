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
from functools import reduce
from datetime import datetime
from datetime import timedelta
import mongodb as MongoDB





class ClienteMODBUS():

    def __init__(self, server_ip, porta, ncu_number, tcu_number_to_read, usina_name, ncu_scan):
        try:
            self._cliente = ModbusClient(host=server_ip, port=porta)
            self._ncu_number = ncu_number
            self._tcu_number_to_read = tcu_number_to_read
            self._usina_name = usina_name
            self._ncu_scan = ncu_scan
        except:
            pass

    def start_scan(self):

        '''
            Função de leitura dos dados do NCU e TCU
                Leitura feita a partir da csv com os dados inseridos

                Ela tem com saída um arquivo CSV com as leituras e um arquivo JSON
        '''

        self._cliente.open()
        if(self._cliente.open() ==True):
            print("Connection" +" NCU" +str(self._ncu_number)+ " done")
            date_a = datetime.now()
            tcu_number = self._ncu_scan
            try:
                all_data_read = []
                json_data = {}
                while tcu_number < self._tcu_number_to_read:
                    #Identifica se é leitura de NCU ou TCU
                    if(tcu_number == -1):
                        print('NCU' + str(self._ncu_number))
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
                                    decoder = str(self.float_to_date(decoder))
                                    
                            if(int(modbus_table["n_bit"][tag_count]) == 16):
                                decoder = self.read_data(int(6),int(modbus_table["address"][tag_count]+ up_addr*(tcu_number)), int(1))
                                if(int(modbus_table["alarm"][tag_count]) == 1):
                                    decoder = self.read_all_bits(self.decode_uint16(decoder))
                                else:
                                    decoder= int(self.decode_uint16(decoder))

                            if(int(modbus_table["n_bit"][tag_count]) == 8):
                                if(int(modbus_table["start_bit"][tag_count]) == 15):
                                    decoder = self.decode_16_to_2_8_int(self.read_data(int(6),int(modbus_table["address"][tag_count]+ up_addr*(tcu_number)), int(1)),1)
                                elif(int(modbus_table["start_bit"][tag_count]) == 7):
                                    decoder = self.decode_16_to_2_8_int(self.read_data(int(6),int(modbus_table["address"][tag_count]+ up_addr*(tcu_number)), int(1)),2)
                                else:
                                    pass
                            if(int(modbus_table["n_bit"][tag_count]) < 8):
                                decoder = self.read_bits(self.read_data(int(6),int(modbus_table["address"][tag_count]+ up_addr*(tcu_number)), int(1)),int(modbus_table["start_bit"][tag_count]),(int(modbus_table["start_bit"][tag_count] -int(modbus_table["n_bit"][tag_count]))))

                            
                            data_read.append({modbus_table["var_name"][tag_count]: decoder})
                            
                            tag_count+=1
                        except:
                            tag_count+=1
                            pass 
                                        
                    if(tcu_number == -1):
                        all_data_read.append(('NCU'+ str(self._ncu_number) , data_read))
                    else:
                        all_data_read.append(('TCU' + str(tcu_number+1), data_read))
                    tcu_number += 1

                
                #print(all_data_read)
                json_data = self.data_to_json(all_data_read,4)
                #print(json_data)
                with open("json_data" + str(self._ncu_number)+ ".json", "w") as outfile: 
                    file = outfile.write(json_data)

                with open("json_data" + str(self._ncu_number)+ ".json") as file:
                    to_base = json.load(file) 

                mongo_obj = MongoDB.MongoDB()
                mongo_obj.inserir(self._usina_name,"RB_NCU" + str(self._ncu_number), to_base)

                df = pd.DataFrame(all_data_read)
                df.to_csv("dados_lidos_" + str(self._ncu_number)  + ".csv")

                date_b = datetime.now()
                delta_1 = timedelta(seconds=date_b.time().second,minutes=date_b.time().minute,hours=date_b.time().hour)
                delta = timedelta(seconds=date_a.time().second,minutes=date_a.time().minute,hours=date_a.time().hour)
                print('Tempo de scan: ' + str(delta_1 - delta))

            except Exception as e:
                print('Erro scan: ', e.args)
        else:
            print("Connection" +" NCU" +str(self._ncu_number)+ " fail")
            pass
        
    def wind_speed(self):
        
        '''
            Função de leitura dos dados de velocidade de vento e hora/data do NCU
                Leitura feita a partir da csv com os dados inseridos
        '''
        self._cliente.open()
        wind_speed_log = []
        try:
            while True:
                modbus_table = pd.read_csv('WINDSPEED_MODBUS_SLIN.csv', delimiter=';')
                addr = modbus_table["address"].tolist()
                tag_count = 0
                wind_speed_log = []
                wind_speed = []
                while tag_count<len(addr):
                    if(modbus_table["type"][tag_count] == "F32"):
                        decoder = self.read_data(int(6),int(modbus_table["address"][tag_count] +1 ), int(2))
                        decoder = self.decode_float32(decoder)
                    else:
                        decoder = self.read_data(int(6),int(modbus_table["address"][tag_count] ), int(2))
                        decoder = str(self.float_to_date(decoder))
                    
                    wind_speed.append({modbus_table["var_name"][tag_count]: decoder})
                    tag_count+= 1
                    print("windspeed")
                wind_speed_log.append(wind_speed)
                print(wind_speed_log)
                wind_json= self.windspeed_to_json(wind_speed_log,4)
                print(wind_json)
                with open("wind_json" + str(self._ncu_number),"w") as outfile: 
                    outfile.write(wind_json)
                    
                with open("wind_json" + str(self._ncu_number)+ ".json") as file:
                    to_base = json.load(file) 

                mongo_obj = MongoDB.MongoDB()
                mongo_obj.inserir(self._usina_name,"RB_WS" + str(self._ncu_number), to_base)
                
                df_wind = pd.DataFrame(wind_speed_log)
                df_wind.to_csv("wind_speed" + str(self._ncu_number)+ ".csv")
                
        except:
            print("windspeed not read")
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
    
    #Ler o intervalo de bits determinado e retorna o valor em decimal
    def read_bits(self, decoder, bit_start, bit_finish):
        decoder_bit = list(format(decoder[0], 'b'))
        decoder_bit =['0' for i in range(16-len(decoder_bit))] + decoder_bit
        decoder_bit = decoder_bit[15-bit_start: 15-bit_finish]
        decoder_bit = str ('0b' + ''.join(decoder_bit))
        return int(decoder_bit,2)
    
    def data_to_json(self ,data: list, indent: int = None)-> str:
        '''
        Converte os dados de coleta para o formato JSON.

                Parameters:
                    a (list): lista com os dados lidos da coleta.
                    indent (int): Tamanho da indentação usada nacodificação.

                Returns:
                    json (str): Json dos dados de coleta
        '''
        f = lambda v:reduce(lambda a, b: {**a, **b}, v)
        
        if(data[0][0] == 'NCU'+str(self._ncu_number)):
            tcus = [ {"name": v[0], "data": f(v[1])} for v in data[1:] ]
            ncu = {"name": data[0][0], "config": f(data[0][1]), "tcus": tcus }
            usina = { "usina": self._usina_name, "ncu": ncu}
        else:
             tcus = [ {"name": v[0], "data": f(v[1])} for v in data[0:] ]
             ncu = {"name": 'NCU'+str(self._ncu_number) , "tcus": tcus }
             usina = { "usina": self._usina_name, "ncu":ncu }
            
        return json.dumps(usina, indent=indent)

    def windspeed_to_json(self, wind: list, indent: int = None) -> str:
        '''
        Converte os dados de leitura da velocidade do vento para o formato JSON.

                Parameters:
                    wind (list): Lista com os dados lidos da coleta.
                    indent (int): Tamanho da indentação usada na codificação.

                Returns:
                    json (str): JSON dos dados de velocidade do vento
        '''
        data = { 
            'usina': self._usina_name,
            'ncu': 'NCU'+str(self._ncu_number),
            'dateTime': wind[0][1]['NcuDatetime'], 
            'windSpeed': wind[0][0]['WindSpeed_mps_rsu1'] 
        }
        return json.dumps(data, indent=indent)


    
    


