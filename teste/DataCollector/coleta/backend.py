import requests
import json

#HOST = "http://localhost:8080"
#HOST = "http://alcindogandhi.com.br:8080"
HOST = "http://ec2-34-231-243-80.compute-1.amazonaws.com:8080"

def send_windspeed(data: dict) -> bool:
    '''
    Envia os dados de velocidade do vento para o backend.

    Parâmetros:
    -----------
    data: dict
        Dados da velocidade do vento.
    
    Retorno:
    --------
        True, se executado com sucesso, ou False, caso contrário.
    '''
    URL = HOST + '/velocidadeVento'
    response = requests.post(URL, json=data)
    return (response.status_code == 200)

def send_ncu(data: dict) -> bool:
    '''
    Envia os dados da NCU para o backend.

    Parâmetros:
    -----------
    data: dict
        Dados da NCU.
    
    Retorno:
    --------
        True, se executado com sucesso, ou False, caso contrário.
    '''
    URL = HOST + '/ncu'
    response = requests.post(URL, json=data)
    return (response.status_code == 200)
