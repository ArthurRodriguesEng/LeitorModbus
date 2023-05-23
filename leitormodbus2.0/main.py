from clientemodbus import ClienteMODBUS
from threading import Thread
import time


c = ClienteMODBUS('192.168.112.110',502)
#c = ClienteMODBUS('192.168.112.120',502)
# c = ClienteMODBUS('192.168.0.35',502)
#c.start_scan()

Thread(c.start_scan()).start()
Thread(c.wind_speed()).start()