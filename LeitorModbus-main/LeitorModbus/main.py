from clientemodbus import ClienteMODBUS

c = ClienteMODBUS('192.168.112.120',502)
# c = ClienteMODBUS('192.168.0.35',502)
c.atendimento()
