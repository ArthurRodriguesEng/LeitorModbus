from pyModbusTCP.client import ModbusClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian

from datetime import datetime

import math
import json

import pandas as pd
import os

import pickle
import coleta.mongodb as MongoDB



class ClientMODBUS():
    '''
        Construtor da Classe Cliente MODBUS
    '''

    
    def __init__(self, server_ip, porta , ID , usina_name, unit_id = 1, framer = None ):
        if(framer == None):self._client = ModbusClient(host=server_ip, port=porta, unit_id= unit_id, auto_close= True, auto_open=True)
        if(framer != None):self._client = ModbusClient(host=server_ip, port=porta, unit_id= unit_id, framer = framer, auto_close= True, auto_open=True)
        #self._server_ip = server_ip
        self.byteorder = Endian.Little
        self.wordorder = Endian.Big
        self._usina_name = usina_name
        self._ID = ID
        self.MB_Table = []
        self.log = []
        self.tag = ''
        self.log_to_send = []
        
        
 
    def read_and_decode_data(self, EQP_number = 0):
        
        #print(self.MB_Table)
        data_read_dict = {}
        for tag_count in range(len(self.MB_Table["address"])):
            #print(self._server_ip)
            print(self.MB_Table["address"][tag_count],self.MB_Table["var_name"][tag_count])
            try:
                decoder = "NaN"
                if(int(self.MB_Table["n_bit"][tag_count]) == 64):
                    if(self.MB_Table["type"][tag_count] == "S64"):
                        decoder = self.read_data(int(self.MB_Table["func"][tag_count]),int(self.MB_Table["address"][tag_count] + self.MB_Table["up_addr"][tag_count]*(EQP_number)), int(4))
                if(int(self.MB_Table["n_bit"][tag_count]) == 32):
                    if(self.MB_Table["type"][tag_count] == "F32"):
                        decoder = self.read_data(int(self.MB_Table["func"][tag_count]),int(self.MB_Table["address"][tag_count] + self.MB_Table["up_addr"][tag_count]*(EQP_number) +1), int(2))
                        print(decoder)
                        decoder = self.decode_float32(decoder)
                    elif(self.MB_Table["type"][tag_count] == "D32"):
                        decoder = self.read_data(int(self.MB_Table["func"][tag_count]),int(self.MB_Table["address"][tag_count] + self.MB_Table["up_addr"][tag_count]*(EQP_number)), int(2))
                        decoder = str(self.float_to_date(decoder))
                    elif(self.MB_Table["type"][tag_count] == "U32"):
                        decoder = self.read_data(int(self.MB_Table["func"][tag_count]),int(self.MB_Table["address"][tag_count] + self.MB_Table["up_addr"][tag_count]*(EQP_number)), int(2))
                        decoder = str(self.decode_uint32(decoder))
                    elif(self.MB_Table["type"][tag_count] == "S32"):
                        decoder = self.read_data(int(self.MB_Table["func"][tag_count]),int(self.MB_Table["address"][tag_count] + self.MB_Table["up_addr"][tag_count]*(EQP_number)), int(2))
                        decoder = str(self.decode_int32(decoder))
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
                try:
                    if(int(self.MB_Table["mult"][tag_count]) != int(1)):
                        decoder = float(decoder)* float(self.MB_Table["mult"][tag_count])
                except:
                    continue
            # print(decoder)
                #data_read.append({self.MB_Table["var_name"][tag_count]: decoder})
                data_read_dict[self.MB_Table["var_name"][tag_count]] =  decoder
                #print(data_read_dict)
                
            except Exception as e:
                    print('Erro scan: ', e.args)
                    continue

        #self.log = data_read
        self.log_dict = data_read_dict
        #print(self.log_dict)

    def read_data(self, tipo, addr, n):
        '''
            Função de leitura dos dados modbus
                Paramaters:
                    tipo : tipo de leitura que deve ser feito (Default = 6, Holding_register)
                    addr : endereço da tabela modbus +1
                    n_reg : número de registrador
        '''
        if tipo == 1:
            return self._client.read_coils(addr,  n)
        if tipo == 2:
            return self._client.read_discrete_inputs(addr,  n)
        if tipo == 3:
            return self._client.read_holding_registers(addr,  n)
        if tipo == 4:
            return self._client.read_input_registers(addr,  n)
    

    

    def load_data(self):
        try:
            self.log_to_send = self.read_pkl()  
        except:
            self.log_to_send = []
            
    def build_pkl(self, log):
        with open(str(self.tag) +  "_" +  str(self._ID) + '.pkl', 'wb') as arquivo:
            return pickle.dump(log, arquivo)
    
    def read_pkl(self):
        with open(str(self.tag) +  "_" +  str(self._ID) + '.pkl', 'rb') as arquivo:
            return pickle.load(arquivo)
        
    def data_to_json(self, data):
        return json.dumps(data, indent = 4)
    
    def destroy_pkl(self):
        file = str(str(self.tag) + '_'+ str(self._ID) + ".pkl")
        if(os.path.exists(file) and os.path.isfile(file)): 
            os.remove(file)
    
    def data_manager(self):
        i=0
        while i < len(self.log_to_send):
            if(self.insert_to_db(self.log_to_send[i])):
                self.log_to_send.pop(i)
                print('sent')
                #print(self.log_to_send)
            else:
                break     
        if(self.log_to_send == []):
            self.destroy_pkl()
        else:
            self.build_pkl(self.log_to_send)
    
    def get_byteorder(self):
        return self.byteorder
    
    def get_wordorder(self):
        return self.wordorder
    
    # def get_framer(self):
    #     return self.framer

    def insert_to_db(self, log):
        '''
            Método usado para enviar um objeto json para o banco de dados
        '''
        json_obj = json.loads(self.data_to_json(log))
        mongo_obj = MongoDB.MongoDB()
        regress = mongo_obj.insert(self._usina_name, str(self.tag) + str(self._ID), json_obj)
        #print(json_obj)
        #regress = self.send(json.loads(self.data_to_json(log,4)))
        # if(regress):
        #     print('Send done')
        # else:
        #     print('Send fail')
        return regress
        
    def build_csv(self,log):
        '''
            Gera o arquivo CSV com todos os dados passados pelo objeto
        '''
        df = pd.DataFrame(log)
        df.to_csv(str(self.tag) + '_'+ str(self._ID) + ".csv", header= False, index= False)

    def destroy_csv(self):
        '''
            Exclui o CSV criado pelo objeto
        '''
        file = str(str(self.tag) + '_'+ str(self._ID) + ".csv")
        if(os.path.exists(file) and os.path.isfile(file)): 
            os.remove(file)
            
    def send(self):return False

    def build_jsonfile(self , n = ''):
        '''
            Método usado para criar um arquivo json
        '''
        data_log = self.data_to_json(self.log)
        with open(str(self.tag) + '_'+ str(self._ID)+ str(n) +".json", "w") as outfile:
            outfile.write(data_log)

    def build_dict(self):
        data =[
                {
                'name': str(str(self.tag).lower() + str(self._ID)),
                str(self.tag).lower()+'datetime': str(datetime.now()),
                'id': self._ID,
                'data': self.log_dict
                }
                ]
                 
        self.log = {
                    'usina': self._usina_name,
                    str(self.tag).lower()+'s': data
                    }
            
    
    
    def bin_decoder(self,decoder):
        return BinaryPayloadDecoder.fromRegisters(decoder, byteorder=str(self.get_byteorder()) , wordorder=str(self.get_wordorder()))
        

    def decode_float64(self,decoder):
        decoder = self.bin_decoder(decoder)
        decoder = decoder.decode_64bit_float()
        return decoder
    
    def decode_int64(self,decoder):
        decoder = self.bin_decoder(decoder)
        decoder = decoder.decode_64bit_int()
        return decoder
    
    def decode_uint64(self,decoder):
        decoder = self.bin_decoder(decoder)
        decoder = decoder.decode_64bit_uint()
        return decoder
        
    #Decodifica os 2 registradores em 1 valor float
    def decode_float32(self,decoder):
        decoder = self.bin_decoder(decoder)
        decoder = decoder.decode_32bit_float()
        return decoder
    
    def decode_int32(self,decoder):
        decoder = self.bin_decoder(decoder)
        decoder = decoder.decode_32bit_int()
        return decoder
    
    def decode_uint32(self,decoder):
        decoder = self.bin_decoder(decoder)
        decoder = decoder.decode_32bit_uint()
        return decoder

    #Decodifica 1 registrador em 1 valor inteiro sem sinal
    def decode_uint16(self,decoder):
        decoder = self.bin_decoder(decoder)
        decoder = decoder.decode_16bit_uint()
        return decoder
    
    #Decodifica 1 registrador em 1 valor inteiro
    def decode_int16(self,decoder):
        decoder = self.bin_decoder(decoder)
        decoder = decoder.decode_16bit_int()
        return decoder
    
    #Decodifica 8 bits em 1 valor inteiro
    def decode_uint8(self,decoder):
        decoder = self.bin_decoder(decoder)
        decoder = decoder.decode_8bit_uint()
        return decoder
    
    def decode_int8(self,decoder):
        decoder = self.bin_decoder(decoder)
        decoder = decoder.decode_8bit_int()
        return decoder

    
    def rad_to_grau(self, decoder):
        '''
            Transforma radianos em grau
        '''
        decoder = self.decode_float32(decoder)
        return decoder*180/ math.pi
    

    def float_to_date(self,decoder):
        '''
            Transforma o valor do registrador em formato data
        '''
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


        


