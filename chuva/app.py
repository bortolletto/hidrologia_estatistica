import dash
from dash import dcc,html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import dash_bootstrap_components as dbc
import numpy as np 
from dash import dash_table


def calcular_estatisticas(df):
    media = df.mean()
    mediana = df.median()
    desvio_padrao = df.std()
    variancia = df.var()
    minimo = df.min()
    maximo = df.max()
    percentis = df.quantile([0.25, 0.5, 0.75])
    coef_variacao = (desvio_padrao / media) * 100
    
    return {
        'Média': media,
        'Mediana': mediana,
        'Desvio Padrão': desvio_padrao,
        'Variância': variancia,
        'Mínimo': minimo,
        'Máximo': maximo,
        'Percentil 25': percentis.loc[0.25],
        'Percentil 50 (Mediana)': percentis.loc[0.5],
        'Percentil 75': percentis.loc[0.75],
        'Coeficiente de Variação': coef_variacao
    }




app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


chuva_test = pd.read_csv("./possivel_chuva_final.csv",index_col = 0,parse_dates = True)
chuva_test = chuva_test[["pr"]]
# estac = pd.read_csv("./estac.csv",index_col = 0)


chuva = pd.read_csv("./chuva_pontos.csv",index_col = 0,parse_dates=True)
chuva = chuva.resample("D",closed='left', label='right').sum(min_count = 20)
loc_pontos   =pd.read_csv("loc_pontos.csv",index_col = 0)
loc_pontos = loc_pontos[["codigo","nome","latitude","longitude"]]






dropd = dcc.Dropdown(
    id="dropdown-anos",
    options=[{'label': str(year), 'value': year} for year in range(2013, 2024)],
    value=2023)

legenda_grafico = dict(
         x=0,
         y=1,
         traceorder="reversed",
         title_font_family="Times New Roman",
         font=dict(
             family="Courier",
             size=12,
             color="black"
         ),
         bgcolor="LightSteelBlue",
         bordercolor="Black",
         borderwidth=2
     )

input_box = dcc.Input(id = "input_{}".format("number"),type = "number",debounce=True)

mapa =   dcc.Graph(id = "mapa", figure={},style={"height": 330,"margin-left": 15})   

grafico = dcc.Graph(id="grafico",figure= {},style={"height": 500}) 

acumulado_anual =  dcc.Graph(id = "acumulado_anual", figure={},style={"height": 500,"margin-left": 15})   

acumulado_mensal = dcc.Graph(id="acumulado_mensal",figure= {},style={"height": 500}) 

reseta = html.Button('Ler Estaca 1', id='btn-nclicks-1', n_clicks=0),

banco = dcc.Store(
        id = "store_data",data = [],storage_type ='memory'
    )

bc_estac = dcc.Store(
        id = "store_estac",data = [],storage_type ='memory'
    )

tabela = dash_table.DataTable(
    id="tabela_descritiva",
    columns=[
    {"name": "Estatística", "id": "Estatística"},
    {"name": "Mensal", "id": "Mensal"},
    {"name":"Geral Mensal","id":"Geral Mensal"},
    {"name": "Anual", "id": "Anual"},
    {"name":"Geral Anual","id":"Geral Anual"}

],
    data=[],
    style_cell={'textAlign': 'left',
                'padding': '5px',
                },
    style_as_list_view=True,
    style_header = {
        "backgroundColor":"white",
        "fontWeight":"bold",
        "border": "1px solid black",
        "textAlign":"left",

        }    ,
 )

#%% cores

# Definindo uma paleta de cores de verde com diferentes tons
green_palette = [
    '#f0f0ff', '#c1c1ff', '#a1a1ff', '#8181ff', '#6161ff', 
    '#4141ff', '#2121ff', '#0000ff', '#0000df', '#0000bf', 
    '#00009f', '#00007f'
]

# Mapeando os intervalos de valores para as cores correspondentes na legenda
legenda = {
    '<-500': green_palette[0],
    '-500--400': green_palette[1],
    '-400--300': green_palette[2],
    '-300--200': green_palette[3],
    '-200--100': green_palette[4],
    '-100-0' : green_palette[5],
    '0-100'  : green_palette[6],
    '100-200': green_palette[7],
    '200-300': green_palette[8],
    '300-400': green_palette[9],
    '400-500': green_palette[10],
    '>500'   :   green_palette[11],
    'NaN': 'black'  # Preto
}

# Mapeando as cores personalizadas para os intervalos de valores na classe_cores
classe_cores = {
    '<-500': (green_palette[0],  
              '<b>Código</b>: %{customdata[0]}'
              '<i><br>Estação</i>: %{customdata[7]}<br>'
              '<br><b><i>Total (mm anual)</i></b>: <b>%{customdata[1]:.1f}</b>'
             ),
    '-500--400': (green_palette[1],  
                  '<b>Código</b>: %{customdata[0]}'
                  '<i><br>Estação</i>: %{customdata[7]}<br>'
                  '<br><b><i>Total (mm anual)</i></b>: <b>%{customdata[1]:.1f}</b>'
                 ),
    '-400--300': (green_palette[2],  
                  '<b>Código</b>: %{customdata[0]}'
                  '<i><br>Estação</i>: %{customdata[7]}<br>'
                  '<br><b><i>Total (mm anual)</i></b>: <b>%{customdata[1]:.1f}</b>'
                 ),
    '-300--200': (green_palette[3],  
                  '<b>Código</b>: %{customdata[0]}'
                  '<i><br>Estação</i>: %{customdata[7]}<br>'
                  '<br><b><i>Total (mm anual)</i></b>: <b>%{customdata[1]:.1f}</b>'
                 ),
    '-200--100': (green_palette[4],  
                  '<b>Código</b>: %{customdata[0]}'
                  '<i><br>Estação</i>: %{customdata[7]}<br>'
                  '<br><b><i>Total (mm anual)</i></b>: <b>%{customdata[1]:.1f}</b>'
                 ),
    '-100-0': (green_palette[5],  
               '<b>Código</b>: %{customdata[0]}'
               '<i><br>Estação</i>: %{customdata[7]}<br>'
               '<br><b><i>Total (mm anual)</i></b>: <b>%{customdata[1]:.1f}</b>'
              ),
    '0-100': (green_palette[6],  
              '<b>Código</b>: %{customdata[0]}'
              '<i><br>Estação</i>: %{customdata[7]}<br>'
              '<br><b><i>Total (mm anual)</i></b>: <b>%{customdata[1]:.1f}</b>'
             ),
    '100-200': (green_palette[7],  
                '<b>Código</b>: %{customdata[0]}'
                '<i><br>Estação</i>: %{customdata[7]}<br>'
                '<br><b><i>Total (mm anual)</i></b>: <b>%{customdata[1]:.1f}</b>'
               ),
    '200-300': (green_palette[8],  
                '<b>Código</b>: %{customdata[0]}'
                '<i><br>Estação</i>: %{customdata[7]}<br>'
                '<br><b><i>Total (mm anual)</i></b>: <b>%{customdata[1]:.1f}</b>'
               ),
    '300-400': (green_palette[9],  
                '<b>Código</b>: %{customdata[0]}'
                '<i><br>Estação</i>: %{customdata[7]}<br>'
                '<br><b><i>Total (mm anual)</i></b>: <b>%{customdata[1]:.1f}</b>'
               ),
    '400-500': (green_palette[10],  
                '<b>Código</b>: %{customdata[0]}'
                '<i><br>Estação</i>: %{customdata[7]}<br>'
                '<br><b><i>Total (mm anual)</i></b>: <b>%{customdata[1]:.1f}</b>'
               ),
    '>500': (  green_palette[11],  
             '<b>Código</b>: %{customdata[8]}<br>' 
             '<i><br>Estação</i>: %{customdata[1]}<br>'
             '<br><b><i>Total (mm anual)</i></b>: <b>%{customdata[0]:.1f}</b>'
            ),
    'NaN': ('black',  
            '<b>Código</b>: %{customdata[0]}'
            '<i><br>Estação</i>: %{customdata[7]}<br>'
            '<br><b><i>Total (mm anual)</i></b>: <b>%{customdata[1]:.1f}</b>'
           )
}

# Função classifica_inmet_climatologia permanece a mesma
def classifica_inmet_climatologia(y, selected_year):
    
    obs = chuva_test.loc[str(selected_year)].sum()[0]
    x = y - obs
    
    
    if np.isnan(x):
        return 'NaN'
    elif x < -500:
        return '<-500'
    elif x <= -400:
        return '-500--400'
    elif x <= -300:
        return '-400--300'
    elif x <= -200:
        return '-200--100'
    elif x <= -100:
        return '-100-0'
    elif x <= 0:
        return '0-100'
    elif x <= 100:
        return '100-200'
    elif x <= 200:
        return '200-300'
    elif x <= 300:
        return '300-400'
    elif x <= 400:
        return '400-500'
    elif x > 500:
        return '>500'


    
#%%
app.layout = dbc.Container([
    html.Br(),
    dbc.Row([
        
        dbc.Col(dropd,width=6),
        dbc.Col(input_box,width=2),
        dbc.Col(reseta,width=2),
        dbc.Col(html.Div(id='output_message'),width=1),
        banco,bc_estac
        ,]),
    html.Br(),

    html.Div([
        dbc.Row([
            dbc.Col(mapa, width=6),
            dbc.Col(tabela , width=6),
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col(acumulado_anual, width=4, xs=4, md=4, lg=4, xxl=4, sm=4, xl=4),
            dbc.Col(acumulado_mensal, width=4, xs=4, md=4, lg=4, xxl=4, sm=4, xl=4),
            dbc.Col(grafico, width=4, xs=4, md=4, lg=4, xxl=4, sm=4, xl=4),
        ])
    ], style={"backgroundColor": "#dee2e6"}),

], style={'backgroundColor': '#dee2e6'}, fluid=True)



@app.callback(
    [Output('mapa', 'figure'),
    Output("store_data","data")],
     [Input('dropdown-anos', 'value'),
      Input("store_estac", "data")]
      )

def update_map(selected_year,data):
    estac = pd.read_json(data,orient = "split")
    estac = estac.set_index("hordatahora")
    
    validada = estac.loc[estac.index == selected_year]
    selected_stations = validada.columns[validada.isin([True]).any()]
    temp = loc_pontos.loc[loc_pontos['codigo'].isin([int(x) for x in list(selected_stations)])]
    if selected_year == 2023:
        df_ano = chuva[selected_stations].resample("Y",closed = "left",label="right").sum(min_count = 100)
    else:
        df_ano = chuva[selected_stations].resample("Y",closed = "left",label="right").sum(min_count = 200)
    df_ano_esp = df_ano.loc[df_ano.index.year == selected_year].T
    df_ano_esp["Classe"] = df_ano_esp.apply(lambda x: classifica_inmet_climatologia(x[df_ano_esp.columns[0]],selected_year), axis=1) 
    df_ano_esp.rename(columns ={df_ano_esp.columns[0] : selected_year},inplace = True)
    
    df_mes_classe =pd.DataFrame(df_ano_esp)
    df_mes_classe["codigo"] = temp.index
    df_mes_classe["cor"] = np.nan
    df_mes_classe["hovertemplate"]=np.nan
    temp_loc = loc_pontos.copy()
    temp_loc["codigo"] = [str(x) for x in temp_loc["codigo"]]
    df_mes_classe = pd.merge(df_mes_classe,temp_loc,how = "outer",left_index=True,right_on="codigo")
    for chavin in classe_cores:
        df_mes_classe.loc[df_mes_classe.Classe == chavin,"cor"] = classe_cores[chavin][0]
        df_mes_classe.loc[df_mes_classe.Classe == chavin,"hovertemplate"] = classe_cores[chavin][1]

    fig = go.Figure() 
        
    for classe,cor in zip (legenda.keys(),legenda.values()):
         df_mes_classe_copy = df_mes_classe[df_mes_classe["Classe"] == classe]
         fig.add_trace(go.Scattermapbox(
             lat = df_mes_classe_copy['latitude'],
             lon = df_mes_classe_copy['longitude'],
             customdata = df_mes_classe_copy,
             mode = 'markers',
             name =  classe,
             
    
             hoverinfo = 'text',
             hovertext = df_mes_classe_copy[selected_year],
             hovertemplate = df_mes_classe_copy["hovertemplate"], 
             showlegend=True,
             marker = go.scattermapbox.Marker(
                 size = 15,
                 color = cor,
                 opacity = 1,
                 ),
             )
         )

         fig.update_layout(
         legend_title_text='Total(mm)',
         autosize = True,
         margin=dict(l=20, r=20, t=30, b=20),
         legend=dict(
             y=0.99,
             xanchor="left",
             x=0.01),
         hovermode = 'closest',
         paper_bgcolor="LightSteelBlue",
         
         font=dict(
         family="Courier New, monospace",
         size=13),
         
         mapbox = dict(
             style ='open-street-map', 
             center =  {'lon':loc_pontos.longitude.mean(), 'lat':loc_pontos.latitude.mean()},
             zoom = 8,
             ), 
         )
         
        
    return fig , selected_year
#%%
@app.callback(
             [Output("grafico","figure"),
              Output('acumulado_anual', 'figure'),
              Output('acumulado_mensal', 'figure'),
              Output('tabela_descritiva', 'data')],
              [Input('dropdown-anos', 'value')
               ,Input("mapa","clickData")])
def criando_grafico(selected_year,clickData):
    
    if clickData:
        #%%primeiro_plot
        clicado = loc_pontos.loc[(loc_pontos.latitude == clickData["points"][0]["lat"]) & (loc_pontos.longitude == clickData["points"][0]["lon"])]
    
        # nome = clicado.nome.values[0]
        codigo = clicado.codigo.values[0]
    
        df_grafico =chuva[str(codigo)].copy().to_frame()
        anual = df_grafico.copy()
        df_grafico.index = pd.to_datetime(df_grafico.index)
        df_grafico  = df_grafico[df_grafico.index.year == selected_year]
        
        chuva_geral_diaria = chuva_test.pr.loc[chuva_test.index.year == selected_year].to_frame()
        chuva_test_anual  = chuva_test.resample("Y",closed = "left",label="right").sum(min_count = 200)
        chuva_test_mensal = chuva_test.resample("M",closed = "left",label="right").sum(min_count = 20)
        
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x = df_grafico.index , y = df_grafico[str(codigo)],name = "est",connectgaps=False))
        fig.add_trace(go.Scatter(x = chuva_geral_diaria.index , y = chuva_geral_diaria["pr"],name= "pr",connectgaps=False,opacity = 0.25))
        fig.update_layout(
                paper_bgcolor="LightSteelBlue",
                margin=dict(l=20, r=20, t=30, b=20),
                title={"text" : f"chuva diaria para o ano de {selected_year}",
                        'y':0.98,
                        'x':0.5,},
                font=dict(
                  family="Courier New, monospace",
                  size=11),
    
                hoverdistance=100,
                hovermode="x",
                legend=legenda_grafico ,
                 xaxis=dict(
    
                     title="Data",
                     linecolor="#BCCCDC",  
                     showgrid=False ,
                     
                    ),
                 yaxis=dict(
                    linecolor="#BCCCDC", 
                    showgrid=False,
                 ),
            )
        fig.update_yaxes(range=[0, 120])
        
        #%%segundo_plot
        mensal = anual.resample("M",closed = "left",label="right").sum(min_count = 20)
        mensal  = mensal[mensal.index.year == selected_year]
        
        pr_mensal = chuva_test_mensal[chuva_test_mensal.index.year == selected_year]
        fig2 = go.Figure()
        
        fig2.add_trace(go.Bar(x = mensal.index.month , y = mensal[str(codigo)],name = "est"))
        fig2.add_trace(go.Bar(x = mensal.index.month , y = pr_mensal["pr"],name = "pr"))
        fig2.update_layout(
          
                            paper_bgcolor="LightSteelBlue",
                margin=dict(l=20, r=20, t=30, b=20),
                title={"text" : f"Acumulados mensais para o ano de {selected_year}",
                        'y':0.98,
                        'x':0.5,},
                font=dict(
                  family="Courier New, monospace",
                  size=11),
                legend=legenda_grafico ,
                hoverdistance=100,
                hovermode="x",
                 xaxis=dict(
                     tickvals=list(range(len(mensal.index.month)+1)),
                     linecolor="#BCCCDC",  
                     showgrid=False ,
                     
                    ),
            )
        
        #%% terceiro plot
        anual  = anual.resample("Y",closed = "left",label="right").sum(min_count = 200)
        anual = anual["2013":]
        
        pr_anual  = chuva_test_anual["2013":]
        
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x = anual.index.year , y = anual[str(codigo)],name = "est"))
        fig3.add_trace(go.Bar(x = pr_anual.index.year , y = pr_anual["pr"],name = "pr"))
        fig3.update_layout(
                paper_bgcolor="LightSteelBlue",
                margin=dict(l=20, r=20, t=30, b=20),
                font=dict(
                  family="Courier New, monospace",
                  size=11),
                legend=legenda_grafico ,
                title={"text" : "Acumulados anuais",
                        'y':0.98,
                        'x':0.5,},
                hoverdistance=100,
                hovermode="x",
                 xaxis=dict(
                     title="Data",
                     linecolor="#BCCCDC",  
                     showgrid=False,    
                    ),

            )
        
        #%% tabela
        dados_anos = pd.DataFrame(calcular_estatisticas(anual[str(codigo)]),index = ["Anual"]).T
        dados_mes  = pd.DataFrame(calcular_estatisticas(mensal[str(codigo)]),index = ["Mensal"]).T
        
        
        
        chuva_geral_anual=  pd.DataFrame(calcular_estatisticas(chuva_test_anual["pr"]),index = ["Geral Anual"]).T
        chuva_geral_mensal =  pd.DataFrame(calcular_estatisticas(chuva_test_mensal["pr"]),index = ["Geral Mensal"]).T
        
        result_df = pd.concat([dados_mes,chuva_geral_mensal,chuva_geral_anual, dados_anos], axis=1)
        result_df  = result_df.round(2)
        result_df = result_df.reset_index()
        
        result_df.rename(columns = { "index": "Estatística"},inplace = True)

        data = result_df.to_dict("records")
        return fig,fig2,fig3,data
        #%%
    else:
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        rainfall = np.random.uniform(0, 20, len(dates))
        
        # Criando o DataFrame
        data = pd.DataFrame({'Date': dates, 'Rainfall': rainfall})
        
        # Criando a figura
        fig = go.Figure()
        
        # Adicionando o traço de linha
        fig.add_trace(go.Scatter(
            x=data['Date'],
            y=data['Rainfall'],
            mode='lines',
            name='Rainfall',
            line=dict(color='blue')
        ))
        
        # Atualizando o layout
        fig.update_layout(
            paper_bgcolor="LightSteelBlue",
            margin=dict(l=20, r=20, t=30, b=20),
            font=dict(
                family="Courier New, monospace",
                size=11
            ),
            hoverdistance=100,
            hovermode="x",
            xaxis=dict(
                title="Data",
                linecolor="#BCCCDC",
                showgrid=False
            ),
            yaxis=dict(
                title="Chuva(mm/dia)*",
                linecolor="#BCCCDC",
                showgrid=False
            )
        )
        return fig,fig,fig,[]
    #%%
@app.callback(
    [Output('output_message', 'children')],
    [ Input("input_{}".format("number"),"value"),
     Input("store_data","data"),
     Input("store_estac","data")
     ]
    
    
)   
def update_dataframe(value,ano,data):
    estac = pd.read_json(data,orient = "split")
    estac = estac.set_index("hordatahora")
    if value is not None:
        column_name = str(value)
        if column_name in estac.columns:
            estac.loc[estac.index == ano,column_name] = False
            
            # Salva o DataFrame modificado em um arquivo
            estac.to_csv('./estac_atualizado.csv')
            # estac = pd.read_csv("./estac_atualizado.csv",index_col = 0)
            return [f'Atualizado: {column_name} alterado para False. DataFrame salvo.']
        else:
            return ['ERROR']
    return ['']

@app.callback(
    Output("store_estac", "data"),
      Input('btn-nclicks-1', 'n_clicks'),
    
)
def store_current_data(n_clicks):
    # Some loading from file/remote and data processing
    if n_clicks == 0:
        
        estac = pd.read_csv("./estac.csv",index_col = 0)
    else:
        
        estac = pd.read_csv("./estac_atualizado.csv",index_col = 0)
    return estac.reset_index().to_json(orient="split")
#%%
if __name__ == '__main__':
    app.run_server(port='8075', debug=False)
    #     estac = pd.read_csv("./estac_atualizado.csv",index_col = 0)
    #     def ve_numero_estac(ano):
    #         validada = estac.loc[estac.index == ano]
    #         selected_stations = validada.columns[validada.isin([True]).any()]
    #         return f" O ano {ano} tem {len(selected_stations)} estacoes"
    # estac= pd.read_csv("./estac.csv",index_col = 0)
    # for i in range(2013,2023):
        

    #         print(ve_numero_estac(i))

    # import pandas as pd 
    # import re
    
    # df = pd.read_csv("/discolocal/felipe/Diversos/bacias_sias/bacias_v3/metadados_sias.csv",encoding='utf-8')
    # df = df.dropna()
    # df.columns

    # df.latitude_captacao = [float(x.replace(",",".")) for x in df.latitude_captacao]
    # df.longitude_captacao = [float(x.replace(",",".")) for x in df.longitude_captacao]
    # df.area_v3 = [float(x.replace(",",".")) for x in  df.area_v3]
    # df.to_csv("/discolocal/felipe/Diversos/bacias_sias/bacias_v3/metadados_sias_.csv")
    # df["Manancial"] = df["Manancial"].str.replace('\W', '')
    # def identificar_caracteres_estranhos(texto):
    #     # Use uma expressão regular para encontrar caracteres estranhos
    #     caracteres_estranhos = re.findall(r'[^\w\s]', texto, flags=re.UNICODE)
    #     return caracteres_estranhos
    # lista = []
    # df["municipio_errado"] = [identificar_caracteres_estranhos(x) for x in df["Municipio"]]
    # df["manancial_errado"] = [identificar_caracteres_estranhos(x) for x in df["Manancial"]]
    # df.to_excel('/discolocal/felipe/Diversos/bacias_sias/bacias_v3/dados_limpos.xlsx', index=False)
