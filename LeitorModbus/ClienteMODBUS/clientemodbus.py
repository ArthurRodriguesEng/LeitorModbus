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

    def __init__(self, server_ip, porta, scan_time=10):
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
    

    def atendimento(self):
        """
        Método para atendimento do usuário
        """

        self._cliente.open()
        addr = (30506,30510,29499,30502)
        addr
        name_addr = ('angle_pos','target','lascomm', 'state')
        n_reg = (2,2,2,1)
        name_addr
        try:
            atendimento = True
            while atendimento:
                sel = input("Deseja iniciar a varredura? (Y/N) ")
                if sel == 'Y':
                    i = 0
                    while True:
                        while i<5:

                            if(i < 2):
                                print(name_addr[i]+ ":"+str(self.RadToGrau(self.lerDado(int(5),int(addr[i]), int(n_reg[1])))) +"°")
                            if(i==2):
                                print(name_addr[i]+ ":"+str(self.FloatToDate(self.lerDado(int(5),int(addr[i]), int(n_reg[1])))))
                            if(i==3):
                                print(name_addr[i]+ ":"+str(self.read_alarm(self.lerDado(int(5),int(addr[i]), int(n_reg[1])))))
                            i+=1
                         
                        i=0
                        sleep(self._scan_time)

                elif sel == 'N':
                    self._cliente.close()
                    atendimento = False
                else:
                    print("Seleção inválida")
        except Exception as e:
            print('Erro no atendimento: ', e.args)

    def lerDado(self, tipo, addr, n_reg):
        """
        Método para leitura de um dado da Tabela MODBUS
        """
        #Leitura do Registrador
        if tipo == 5:
            result = self._cliente.read_holding_registers(addr+1, n_reg)
            return result

        
    #def Read_Data(self,decoder):
        #decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        #decoder = decoder.decode_32bit_float()


    def RadToGrau(self, decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_32bit_float()
        return decoder*180/ math.pi
    def FloatToDate(self,decoder):
        epoch = (2**16*decoder[1] + decoder[0] -7200)
        date = datetime.datetime.fromtimestamp(epoch)
        return  date
    def read_alarm(self,decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_32bit_float()
        return decoder




    
    # def escreveDado(self, tipo, addr, valor):
    #     """
    #     Método para a escrita de dados na Tabela MODBUS
    #     """
    #     if tipo == 1:
    #         return self._cliente.write_single_register(addr, valor)

    #     if tipo == 2:
    #         return self._cliente.write_single_coil(addr, valor)

    #     if tipo == 3:
    #         builder = BinaryPayloadBuilder()  # cria um objeto BinaryPayloadBuilder
    #         # Adciona o valor em formato float no builder
    #         builder.add_32bit_float(float(valor))
    #         # converte o buffer do payload em um de registro que pode ser usado como um bloco de contexto
    #         payload = builder.to_registers()
    #         # escreve no endereço passado o payload em questão
    #         return self._cliente.write_multiple_registers(addr, payload)

    #     if tipo == 4:
    #         builder = BinaryPayloadBuilder()  # cria um objeto BinaryPayloadBuilder
    #         v = len(valor)  # obtem o número de dígitos da string
    #         # escreve no primeiro registrador no endereço passado o numero de dígitos da string
    #         self._cliente.write_single_register(addr, v)
    #         # adiciona o valor em forma de stirng no builder
    #         builder.add_string(str(valor))
    #         # converte o buffer, em formato de lita, do payload em um de registro que pode ser usado como um bloco de contexto
    #         payload = builder.to_registers()
    #         # escreve no endereço a frente o payload, que é a informação que deve ser armazenada depois da conversão
    #         return self._cliente.write_multiple_registers(addr+1, payload)
