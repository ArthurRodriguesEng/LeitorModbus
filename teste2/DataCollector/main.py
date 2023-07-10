from readselect import read_select


'SETUP'

'Tempo de Scan em minutos'
scan_time = 0.1 #minutos

'Tipo de Leitura(NCU ou WIND)'
read = 'NCU'
read_select(read, scan_time)
