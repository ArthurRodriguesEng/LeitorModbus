import pandas as pd
from dash import Dash, html, dcc,  html, Input, Output
import plotly.express as px
import matplotlib.pyplot as plt
import enviar_web
from datetime import datetime

tcu_number = 12
creds = enviar_web.inicializar_web()
df = pd.DataFrame(columns=['tcu','position','target','com','wind_speed','alarm', 'batery'])

for tcu in range(1,tcu_number+1):
    mapeamento = enviar_web.ler_dados(creds,tcu,1)
    df_tcu = pd.DataFrame(mapeamento[1:], columns=mapeamento[0])
    df = pd.concat([df, df_tcu], ignore_index = True)

df['position'] = df['position'].astype(float)
df['alarm'] = df['alarm'].astype(int)
df['wind_speed'] = df['wind_speed'].astype(int)
app = Dash(__name__)

fig = px.line(df, x="com", y="position", color="tcu")

fig_2 = px.area(df, x="com", y="alarm", color="tcu")

fig_3 = px.line(df, x="com", y="wind_speed")

app.layout = html.Div(children=[html.H1(children='MONITORAMENTO WEB'),
                                
html.Div(children=''' Ribeirão Bonito - SP '''),

html.H4("Dados de monitoramento dos trackers da NCU 01 da usina "),
#     html.P("O que deseja ver:"),
#     dcc.Dropdown(
#         id='y-axis',
#         options=['position', 'alarm', 'wind_speed'],
#         value='Informação'),
#     dcc.Graph(id="graph"),

dcc.Graph( id='position-graph', figure=fig ),

dcc.Graph( id='alarm-graph', figure=fig_2 ),

dcc.Graph( id='wind-graph', figure=fig_3 )])

# @app.callback(
#     Output("graph", "figure"), 
#     Input("y-axis", "value"))

# def display_area(y,df):
    
#     fig = px.area(
#         df, x="com", y=y,
#         color="tcu", id = "Figure")
#     return fig

if __name__ == '__main__':
    app.run_server(debug=True)
    
    
    
# print(df)
# scalar = .9# fig = plt.figure()
# ax = fig.add_subplot(1,1,1)
# for tcu in range(1,tcu_number+1):# df_ax = df[df['tcu'] == str(tcu)]# y = df_ax# x = df_ax['com']# x = pd.to_datetime(x, format="%Y-%m-%d %H:%M:%S")# ax.plot(x,y, marker = "*", label = "TCU " + str(tcu))    # ax.set_title("Position x Tempo")# ax.set_xlabel("Hora")# ax.set_ylabel("Angulação [°]") # ax.legend()# ax.grid()# fig.tight_layout()# # plt.show()
# # fig = plot(tcu_number,df)