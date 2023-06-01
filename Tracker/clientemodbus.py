from pyModbusTCP.client import ModbusClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
import datetime
import math
import build_table as table
import json
from functools import reduce
from datetime import datetime
from datetime import timedelta
import mongodb as MongoDB
import pandas





class ClienteMODBUS():
    '''
        Construtor da Classe Cliente MODBUS
    '''

    def __init__(self, server_ip, porta, ncu_number, tcu_number_to_read, usina_name, ncu_scan):
        try:
            self._cliente = ModbusClient(host=server_ip, port=porta)
            self._ncu_number = ncu_number
            self._tcu_number_to_read = tcu_number_to_read
            self._usina_name = usina_name
            self._ncu_scan = ncu_scan
            self._MBT_NCU = table.MBT_NCU
            self._MBT_TCU = table.MBT_TCU
            self._MBT_WS = table.MBT_WS
            self._MBT_NCU_WIND = table.MBT_NCU_WIND
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
            print("Connection " + self._MBT_NCU["equipment"][0] +str(self._ncu_number)+ " done")
            date_a = datetime.now()
            all_data_read = []
            json_data = {}
            for tcu_number in range(self._tcu_number_to_read+1):
                #Identifica se é leitura de NCU ou TCU
                if(tcu_number == 0 and self._ncu_scan == 1):
                    print(self._MBT_NCU["equipment"][0] + str(self._ncu_number))
                    modbus_table = self._MBT_NCU
                elif(tcu_number == 0 and self._ncu_scan == 0):
                    continue
                else:
                    print(self._MBT_TCU["equipment"][0] + str(tcu_number))
                    modbus_table = self._MBT_TCU
                data_read = []
                for tag_count in range(len(modbus_table["address"])):
                    try:
                        decoder = "NaN"
                        if(int(modbus_table["n_bit"][tag_count]) == 32):
                            if(modbus_table["type"][tag_count] == "F32"):
                                decoder = self.read_data(int(6),int(modbus_table["address"][tag_count] + modbus_table["up_addr"][tag_count]*(tcu_number-1) +1), int(2))
                                decoder = self.decode_float32(decoder)
                            elif(modbus_table["type"][tag_count] == "U32"):
                                decoder = self.read_data(int(6),int(modbus_table["address"][tag_count] + modbus_table["up_addr"][tag_count]*(tcu_number-1)), int(2))
                                decoder = str(self.float_to_date(decoder))
                            else:
                                decoder = self.read_data(int(6),int(modbus_table["address"][tag_count] + modbus_table["up_addr"][tag_count]*(tcu_number-1) +1 ), int(2))
                                
                        if(int(modbus_table["n_bit"][tag_count]) == 16):
                            decoder = self.read_data(int(6),int(modbus_table["address"][tag_count]+ modbus_table["up_addr"][tag_count]*(tcu_number-1)), int(1))
                            if(int(modbus_table["alarm"][tag_count]) == 1):
                                decoder = self.read_all_bits(self.decode_uint16(decoder))
                            else:
                                if(modbus_table["type"][tag_count] == "S16"):
                                    decoder= int(self.decode_int16(decoder))
                                elif(modbus_table["type"][tag_count] == "U16"):
                                    decoder= int(self.decode_uint16(decoder))
                                else:
                                    pass
                                    
                        if(int(modbus_table["n_bit"][tag_count]) == 8):
                            decoder = self.read_data(int(6),int(modbus_table["address"][tag_count]+ modbus_table["up_addr"][tag_count]*(tcu_number-1)), int(1))
                            if(int(modbus_table["start_bit"][tag_count]) == 15):
                                decoder = self.decode_16_to_2_8_int(decoder,1)
                            elif(int(modbus_table["start_bit"][tag_count]) == 7):
                                decoder = self.decode_16_to_2_8_int(decoder,2)
                            else:
                                pass

                            # if(modbus_table["type"][tag_count] == "S8"):
                            #     decoder = int(self.decode_int8(decoder))
                            # else:
                            #     decoder = int(self.decode_uint8(decoder))

                        if(int(modbus_table["n_bit"][tag_count]) < 8):
                            decoder = self.read_bits(self.read_data(int(6),int(modbus_table["address"][tag_count]+ modbus_table["up_addr"][tag_count]*(tcu_number-1)), int(1)),int(modbus_table["start_bit"][tag_count]),(int(modbus_table["start_bit"][tag_count] -int(modbus_table["n_bit"][tag_count]))))
                        
                        data_read.append({modbus_table["var_name"][tag_count]: decoder})
                    except Exception as e:
                        print('Erro scan: ', e.args)
                        continue
                                    
                if(tcu_number == 0):
                    all_data_read.append((self._MBT_NCU["equipment"][0]+ str(self._ncu_number) , data_read))
                else:
                    all_data_read.append((self._MBT_TCU["equipment"][0] + str(tcu_number), data_read))

            #print(all_data_read)
            json_data = self.data_to_json(all_data_read,4)
            #json_data = json.loads(self.data_to_json(all_data_read,4))
            #print(json_data)
            #print(type(json_data))
            with open("json_data" + str(self._ncu_number)+ ".json", "w") as outfile: 
                    file = outfile.write(json_data)

            # with open("json_data" + str(self._ncu_number)+ ".json") as file:
            #     to_base = json.load(file) 

            # mongo_obj = MongoDB.MongoDB()
            # mongo_obj.insert(self._usina_name,"RB_NCU" + str(self._ncu_number), json_data)

            # df = pd.DataFrame(all_data_read)
            # df.to_csv("dados_lidos_" + str(self._ncu_number)  + ".csv")

            date_b = datetime.now()
            delta_1 = timedelta(seconds=date_b.time().second,minutes=date_b.time().minute,hours=date_b.time().hour)
            delta = timedelta(seconds=date_a.time().second,minutes=date_a.time().minute,hours=date_a.time().hour)
            print('Tempo de scan: ' + str(delta_1 - delta))
        else:
            print("Connection " + "NCU" +str(self._ncu_number)+ " fail")
            pass
        
    def wind_speed(self):
        
        '''
            Função de leitura dos dados de velocidade de vento e hora/data do NCU
                Leitura feita a partir da csv com os dados inseridos
        '''
        self._cliente.open()
        if(self._cliente.open() ==True):
            modbus_table = self._MBT_WS
            print(modbus_table)
            wind_speed_log = []
            try:
                for tag_count in range(len(modbus_table["address"])):
                    if(modbus_table["type"][tag_count] == "F32"):
                        decoder = self.read_data(int(6),int(modbus_table["address"][tag_count] +1 ), int(2))
                        decoder = self.decode_float32(decoder)
                    else:
                        decoder = self.read_data(int(6),int(modbus_table["address"][tag_count] ), int(2))
                        decoder = str(self.float_to_date(decoder))
                    wind_speed_log.append({modbus_table["var_name"][tag_count]: decoder})
                #wind_speed_log.append(wind_speed_log)
                wind_json = json.loads(self.windspeed_to_json(wind_speed_log,4))
                #print(wind_json)
                # with open("wind_json" + str(self._ncu_number) + ".json","w") as outfile: 
                #     outfile.write(wind_json) 
                # with open("wind_json" + str(self._ncu_number)+ ".json") as file:
                #     to_base = json.load(file) 
                # print(to_base)
                
                mongo_obj = MongoDB.MongoDB()
                mongo_obj.insert(self._usina_name,"RB_WS" + str(self._ncu_number), wind_json)
                
                # df_wind = pd.DataFrame(wind_speed_log)
                # df_wind.to_csv("wind_speed" + str(self._ncu_number)+ ".csv")
            except Exception as e:
                print('Erro scan: ', e.args)
                pass
        else:
            print("Connection" + "NCU" +str(self._ncu_number)+ " fail")
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
    
    #Ler o intervalo de bits determinado e retorna o valor em decimal
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
            'NcuDatetime': wind[1]['NcuDatetime'], 
            'WindSpeed_mps_rsu1': wind[0]['WindSpeed_mps_rsu1'] 
        }
        return json.dumps(data, indent=indent)


    
    


