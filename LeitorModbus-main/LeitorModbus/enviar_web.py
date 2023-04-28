from __future__ import print_function
#Importar bibliotecas api do google
import os
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
'pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib'



def inicializar_web ():
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    # ID da planilha e quais colunas quer usar
    SAMPLE_SPREADSHEET_ID = '13BwaIqIPSyNHb8Sog4tBhE_NAxxiggo0W_3VXYlvG0Y'
    SAMPLE_RANGE_NAME = 'Página1!A1:G'
    #deixa as credenciais vazias
    creds = None
    #verifica se já existe um token de acesso válido ou cria um
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    #Se não tiver credencial de token válida, pedirá acesso para sua conta google
    if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                'cores.json', SCOPES)
            creds = flow.run_local_server(port=0)
    return creds

def ler_dados(creds):
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    # ID da planilha e quais colunas quer usar
    SAMPLE_SPREADSHEET_ID = '13BwaIqIPSyNHb8Sog4tBhE_NAxxiggo0W_3VXYlvG0Y'
    SAMPLE_RANGE_NAME = 'Página1!A1:G'
    try:
        service = build('sheets', 'v4', credentials=creds)
        # Ler informações do Google Sheets
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values',[])

        return len(values)

    except HttpError as err:
        print(err)

def atualizar_dados (creds,tcu_data_log):
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    # ID da planilha e quais colunas quer usar
    SAMPLE_SPREADSHEET_ID = '13BwaIqIPSyNHb8Sog4tBhE_NAxxiggo0W_3VXYlvG0Y'
    SAMPLE_RANGE_NAME = 'Página1!A1:G'
    i = ler_dados(creds)
    try:
        service = build('sheets', 'v4', credentials=creds)
        # Ler informações do Google Sheets
        sheet = service.spreadsheets()      
        l = len(tcu_data_log)
        sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range='A'+str(i+1)+':G'+str(i+l),valueInputOption="USER_ENTERED", body ={'values':tcu_data_log}).execute()
        
    except HttpError as err:
        print(err)