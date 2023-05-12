from clientemodbus import ClienteMODBUS

c = ClienteMODBUS('192.168.112.110',502)
# c = ClienteMODBUS('192.168.0.35',502)
c.start_scan()

