import datetime
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import math

# decoder = [13476, 25701]
# # print(decoder, type(decoder))


# #decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
# epoch = (2**16*decoder[1]) + decoder[0]
# print(epoch)
# date = datetime.datetime.fromtimestamp(epoch)
# print(date)


# alarme = 1026
# alarm_report = []
# j=15
# while j>-1:
#     if(alarme - 2**j >= 0):
#         print(".")
#         alarm_report.append(j)
#         alarme = alarme - 2**j
#     j -= 1

# print(alarm_report)

# from pyModbusTCP.client import ModbusClient
# from time import sleep
# from pymodbus.payload import BinaryPayloadDecoder
# from pymodbus.payload import BinaryPayloadBuilder
# from pymodbus.constants import Endian
# import pyModbusTCP.utils
# import scipy
# import datetime
# from Adafruit_IO import Client
# import math

# valor = 1024
# builder = BinaryPayloadBuilder()
# print(builder)
# #builder.add_bits()
# builder.add_16bit_uint(int(valor))
# print(builder)
# payload = builder.to_registers()
# print(payload)

# addr = [6,5,4,3,2,1]
# addr_count = 0

# while addr_count < len(addr) +1:
#     if(id == addr[0]):
#         addr[0] += 2
#     else:
#         addr[addr_count] += 22
#     addr_count += 1
#     print(id)
#     print(addr)
      

# a = [65280]

# b = a[0] >>8
# c = a[0] & 255


# print(b,c)



# import math
# decoder = [16467, 0]
# decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
# decoder = decoder.decode_32bit_float()
# #decoder = decoder*180/ math.pi
# print(decoder)

# class TCU():

#     def __init__( number):

#         _number = number
#         addres = []
#         start_bit = []
#         n_bit = []
#         type = []
#         var_name = []
#         unit = []
#         print("Tcu" + str(number)+ "criado")

# tcu = []
# tcu.append([TCU(1)]) 
# tcu.append([TCU(2)]) 
# print (tcu[0]._number)

# import json

# def lista_para_json(lista):
#     dicionario = {}
#     for i, item in enumerate(lista):
#         chave = str(i)  # Usando o índice como chave
#         dicionario[chave] = item
#     return json.dumps(dicionario)

# # Exemplo de lista
# minha_lista = ['item1', 'item2', 'item3']

# # Convertendo a lista em JSON
# json_resultado = lista_para_json(minha_lista)
# print(json_resultado)




# TCU = {'TCU1':{
#        '30000':{
#         'TAG':30000,
#         'VALOR': 30000}
#         ,
#        '30001':{
#         'TAG':30000,
#         'VALOR': 30000}
        
#         }}
# print(TCU['TCU1']['30000'])


from threading import Thread
import time
from time import sleep
from multiprocessing import Process

def decode_float32(decoder):

        dec= BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        dec = dec.decode_32bit_float()
        print(dec)
        sleep(1)
        #return decoder

#Decodifica 1 registrador em 1 valor inteiro
def decode_uint16(decoder):

        de = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        de = de.decode_16bit_uint()
        print(de)
        sleep(1)
        # return decoder

#Decodifica 8 bits em 1 valor inteiro
def decode_uint8(decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_8bit_uint()
        return decoder

#Transforma radianos em grau
def rad_to_grau( decoder):
        decoder = decode_float32(decoder)
        return decoder*180/ math.pi

#Transforma o valor do registrador em formato data
def float_to_date(decoder):
        epoch = (2**16*decoder[1] + decoder[0])
        date = datetime.datetime.fromtimestamp(epoch)
        return date

def decode_16_to_2_8_int(decoder,part):
        decoder_1 = decoder[0] >> 8
        decoder_2 = decoder[0] & 255
        if(part == 1):
                return decoder_1
        elif(part ==2):
                return decoder_2
        else:
                print('erro')

#passa o valor inteiro e o bit que deseja ler e ele retorna o valor do bit
def read_bit(decoder, bit):
        decoder_bit = list(format(decoder[0], 'b'))
        return decoder_bit[15-bit]

#passa o valor inteiro e retorna quais os bits que estão ativos
def read_all_bits(decoder):
        count=15
        report = []
        while count>-1:
                if((decoder - 2**count) >= 0):
                        report.append(count)
                        decoder = decoder - 2**count
                        count -= 1
        return report

#decoder = [65380]
# Thread.start_new_thread(target = decode_float32([400,50])).start()
# print("x")
# Process(target =read_all_bits([65380])).start()


import time
import threading

class AddDaemon(object):
    def __init__(self):
        self.stuff = 'hi there this is AddDaemon'

    def add(self):
        while True:
            decode_uint16([65380])
            time.sleep(1)


class RemoveDaemon(object):
    def __init__(self):
        self.stuff = 'hi this is RemoveDaemon'

    def rem(self):
        while True:
            decode_float32([400,50])
            time.sleep(1)

def main():
    a = AddDaemon()
    r = RemoveDaemon()
    t1 = threading.Thread(target=r.rem)
    t2 = threading.Thread(target=a.add)
    t1.setDaemon(True)
    t2.setDaemon(True)
    t1.start()
    t2.start()
    time.sleep(10)

if __name__ == '__main__':
    main()

