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



class ClienteMODBUS():
    """
    Classe Cliente MODBUS
    """

    def __init__(self, server_ip, porta, scan_time=120):
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
    

    def atendimento(self):

        self._cliente.open()
        self.tcu_number_to_read = 12
        self.addr_default  = [30506,30510,29499,30501,30512]
        self.name_addr = ('angle_pos','target', 'lastcomm', 'state', 'battery')
        self.n_reg = (2,2,2,1,2,1)



        # ADAFRUIT_IO_USERNAME = "Caian_Jesus"
        # ADAFRUIT_IO_KEY = "aio_hrPU04BNGGe6bqelRwPY4ahrMzXe"
        # aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
        creds = enviar_web.inicializar_web()

        try:
            atendimento = True
            while atendimento:
                
                while True:
                        tcu_number = 1
                        
                        addr = [30506,30510,29499,30501,30512]
                        while tcu_number < self.tcu_number_to_read+1:
                            tcu_data_log=[]
                            print('TCU' + str(tcu_number))
                            # print(addr)
                            tag_count = 0
                            while tag_count<len(self.addr_default):
                                try:
                                    
                                    if(tag_count == 0):
                                        # Position = aio.feeds('position')
                                        pos = self.rad_to_grau(self.read_data(int(6),int(addr[tag_count]), int(self.n_reg[tag_count])))
                                        # aio.send_data(Position.key, pos)
                                        print(self.name_addr[tag_count]+ ":"+str(pos) +"°")
                                    if(tag_count == 1):
                                        # Target = aio.feeds('target')
                                        tgt = self.rad_to_grau(self.read_data(int(6),int(addr[tag_count]), int(self.n_reg[tag_count])))
                                        # aio.send_data(Target.key, tgt)
                                        print(self.name_addr[tag_count]+ ":"+str(tgt) +"°")
                                    if(tag_count== 2):
                                        # Date = aio.feeds('com')
                                        date = self.float_to_date(self.read_data(int(6),int(addr[tag_count]), int(self.n_reg[tag_count])))
                                        # aio.send_data(Date.key, str(date))
                                        print(self.name_addr[tag_count]+ ":"+str(date))
                                    # if(tag_count==3):
                                    #     # Speed = aio.feeds('speed')
                                    #     wind = self.decode_uint16(self.read_data(int(6),int(addr[tag_count]), int(self.n_reg[tag_count])))
                                    #     # aio.send_data(Speed.key, wind)
                                    #     print(self.name_addr[tag_count]+ ":"+str(wind)+"m/s")
                                    if(tag_count==3):
                                        # Alarme = aio.feeds('alarme-tracker')
                                        alarme = self.decode_uint16(self.read_data(int(6),int(addr[tag_count]), int(self.n_reg[tag_count])))
                                        # aio.send_data(Alarme.key, alarme)
                                        #print(self.name_addr[i]+ ":"+str(alarme))
                                        alarm_report = self.read_all_bits(alarme)
                                        print(self.name_addr[tag_count]+ ":"+str(alarm_report))
                                    if(tag_count==4):
                                        # Battery = aio.feeds('battery')
                                        battery = self.decode_16_to_2_8_int(self.read_data(int(6),int(addr[tag_count]), int(self.n_reg[tag_count])),2)
                                        # aio.send_data(Battery.key, battery)
                                        print(self.name_addr[tag_count]+ ":"+str(int(battery))+"%")
                                        
                                    tag_count+=1
                                except:
                                    tag_count+=1
                                    pass 

                            tcu_data_log = [[tcu_number,pos,tgt,str(date),alarme,battery]]
                            enviar_web.atualizar_dados(creds,tcu_data_log,tcu_number)

                            addr_count = 0
                            while addr_count < len(addr):
                                if(addr_count == 2):
                                    addr[2] += 2
                                # elif(addr_count == 3):
                                #     pass
                                else:
                                    addr[addr_count] += 22
                                addr_count +=  1                       
                            tcu_number +=1

                        tcu_number = 1

                        sleep(self._scan_time)


        except Exception as e:
            print('Erro no atendimento: ', e.args)

    def read_data(self, tipo, addr, n_reg):
        if tipo == 6:
            result = self._cliente.read_holding_registers(addr+1, n_reg)
            #print(result)
            return result
        
    def decode_float32(self,decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_32bit_float()
        return decoder

    def decode_uint16(self,decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_16bit_uint()
        return decoder
    
    def decode_uint8(self,decoder):
        decoder = BinaryPayloadDecoder.fromRegisters(decoder, Endian.Big)
        decoder = decoder.decode_8bit_uint()
        return decoder

    def rad_to_grau(self, decoder):
        decoder = self.decode_float32(decoder)
        return decoder*180/ math.pi
    
    def float_to_date(self,decoder):
        epoch = (2**16*decoder[1] + decoder[0] -3600)
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



    
    


