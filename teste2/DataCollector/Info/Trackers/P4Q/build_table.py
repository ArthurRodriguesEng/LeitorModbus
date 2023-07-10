# import pandas as pd
# MBT_NCU_ALARM = pd.read_csv('DataCollector\Info\Trackers\P4Q\MBT_NCU_ALARM.csv', delimiter=';')
# MBT_NCU_CFG = pd.read_csv('DataCollector\Info\Trackers\P4Q\MBT_NCU_CFG.csv', delimiter=';')
# MBT_TCU = pd.read_csv('DataCollector\Info\Trackers\P4Q\MBT_TCU.csv', delimiter=';')
# MBT_WS = pd.read_csv('DataCollector\Info\Trackers\P4Q\MBT_WS.csv', delimiter=';')
# #MBT_NCU_WIND = pd.read_csv('DataCollector\Info\Trackers\P4Q\MBT_NCU_WIND.csv', delimiter=';')

import pickle

with open('DataCollector\Info\Trackers\P4Q\MBT_NCU_ALARM.pkl', 'rb') as arquivo:
    MBT_NCU_ALARM = pickle.load(arquivo)

with open('DataCollector\Info\Trackers\P4Q\MBT_NCU_CFG.pkl', 'rb') as arquivo:
    MBT_NCU_CFG = pickle.load(arquivo)

with open('DataCollector\Info\Trackers\P4Q\MBT_TCU.pkl', 'rb') as arquivo:
    MBT_TCU = pickle.load(arquivo)

with open('DataCollector\Info\Trackers\P4Q\MBT_WS.pkl', 'rb') as arquivo:
    MBT_WS = pickle.load(arquivo)
                        
