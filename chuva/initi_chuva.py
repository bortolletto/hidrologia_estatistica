#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 15:38:43 2023

@author: felipe
Classe para manipulação de dados hidrologicos
"""
import pandas as pd
import plotly.graph_objs as go
import os
import plotly.io as pio
import numpy as np 

pio.renderers.default='svg'



class Analise_dados_hidrologicos():
    
    def inicializar(self):
        '''
        Função inicializa o sistema, abrindo o arquivo de chuvas e vazoes, alem de agregar os dados de chuva nas escalas diarias, mensais e anuais.

        Returns
        -------
        None.

        '''
        self.chuva = pd.read_csv("./chuva_pontos.csv",index_col = 0,parse_dates =True)
        self.chuva =  self.chuva["1998":]
        # self.chuva = self.chuva["1998":]
        self.chuva_d = self.chuva.resample("D").sum(min_count = 12)
        self.chuva_m = self.chuva.resample("M").sum(min_count = 20 )
        self.chuva_y = self.chuva.resample("Y").sum(min_count = 250)
        

        self.vazao_d = pd.read_csv("./vazao.csv",index_col = 0 ,parse_dates = True).iloc[::-1]
        self.vazao_m = self.vazao_d.resample("M",label = "right").mean()
        self.vazao_y = self.vazao_d.resample("Y",label = "right").mean()
        
        self.data_vazao =  pd.date_range(start=self.vazao_d.first_valid_index(), end=self.vazao_d.last_valid_index(), freq='D')
        self.data_chuva =  pd.date_range(start=self.chuva_d.first_valid_index(), end=self.chuva_d.last_valid_index(), freq='D')
        
        self.intervalo_de_datas_de_chuva()
        
        return self.chuva_d
    def plota(self,csv):        
        '''
        Funcao que plota todas as colunas de um mesmo dataframe em um grafico de linhas

        Parameters
        ----------
        csv : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        fig2 = go.Figure()        
        for coluna in csv.columns:
            fig2.add_trace(go.Scatter(x = csv.index , y = csv[coluna],name = coluna,connectgaps=False))
        fig2.show()
    
    def intervalo_de_datas_de_chuva(self):
        '''
        Funcao que coleta as datas iniciais e finais dos dados de chuva. 

        Returns
        -------
        None.

        '''
        self.primeiras_datas_nao_nulas = self.chuva_d.apply(lambda col: col.dropna().index[0] if not col.dropna().empty else None).to_frame()
        self.primeiras_datas_nao_nulas.rename(columns = {0:"primeira_data_valida"},inplace= True)
        self.ultimas_datas_nao_nulas = self.chuva_d.apply(lambda col: col.dropna().index[-1] if not col.dropna().empty else None).to_frame()
        self.ultimas_datas_nao_nulas.rename(columns = {0:"ultimas_datas_nao_nulas"},inplace= True)
        self.datas = pd.merge(self.primeiras_datas_nao_nulas,self.ultimas_datas_nao_nulas,left_index = True,right_index=True)

        self.datas['comprimento'] = self.datas['ultimas_datas_nao_nulas'] - self.datas['primeira_data_valida']
        self.datas['comprimento'] = pd.to_timedelta(self.datas['comprimento'])
        

        self.datas['dias'] = self.datas['comprimento'].dt.days
        
    def define_nulos(self):
        '''
        Funcao que define os valores nulos de um dataframe em relação a um ano e em relação as estacoes
        São 109 estacoes por ano, entao caso n se tenha dado algum para determinado ano, a saida sera 109
        
        Ja para estações, a analise contabiliza 26 anos, o raciocinio é semelhante, estações com 26 pontos não possuem dados. 

        Parameters
        ----------
        df : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        

                
        df_nulos = pd.DataFrame(index = self.chuva_d.index.year.unique(),columns = self.chuva.columns)
        for ano in self.chuva_d.index.year.unique():
            temp = self.chuva_d.loc[self.chuva_d.index.year == ano]
            for coluna in temp.columns:
                row = [ano,round(temp[coluna].isnull().sum()/365,2)]
                year = row[0]
                value = row[1]
                df_nulos.loc[year, coluna] = value
        self.contagem_de_nulos_no_ano= df_nulos.sum(axis = 1).to_frame()
        self.contagem_de_nulos_por_estacao= df_nulos.sum().to_frame()        
        return df_nulos
    
    def curva_permanencia_chuva(self):
        '''
        Função retorna data frame com a curva de permanencia de dados de chuva de todo o periodo. 

        Returns
        -------
        end_temp : TYPE
            DESCRIPTION.

        '''
        end_temp = pd.DataFrame()
        for coluna in self.chuva_d:
            temp = self.chuva_d[coluna].to_frame()
            temp = temp.sort_values(coluna)
            temp = temp.reset_index()
            temp.drop(columns =["hordatahora"],inplace = True)
            end_temp = pd.merge(end_temp,temp,how = "outer",left_index=True,right_index=True)
        self.cp = end_temp
        return end_temp
    
    
    def plota_cp(self):
        '''
        Plota as curvas de permanencia de chuva, alem de criar um dataframe monstrando a porcentagem de falhas para cada estação

        Returns
        -------
        nulos_na_serie : TYPE
            DESCRIPTION.

        '''
        fig = go.Figure()
        nulos_na_serie = pd.DataFrame(index = self.cp.columns)
        for estacao in self.cp.columns:
            temp = self.cp[estacao].to_frame()
            temp = temp.dropna()
            
            data = self.datas.loc[self.datas.index == estacao, "dias"].values[0]
            nulo_= data - len(temp)
            nulos_na_serie.loc[nulos_na_serie.index == estacao,"numero_de_nulos_dentro_do_intervalo_da_serie"] = nulo_
            nulos_na_serie.loc[nulos_na_serie.index == estacao,"numero_total_de"] = data
            nulos_na_serie.loc[nulos_na_serie.index == estacao,"porcent"] = nulo_/data
            temp["probabilidade"] = [(len(temp)-i +1)/(len(temp)+1) for i in temp.index]
            fig.add_trace(go.Scatter(x = temp[estacao], y = temp["probabilidade"],name = estacao,connectgaps=False))
        fig.write_html("./plots/cps.html")
        self.nulos_na_serie = nulos_na_serie
        return nulos_na_serie
    
    
    def calcula_percentil(self,df,Q):
        Q = 0.07
        valores_ordenados = df.sort_values().to_frame()
        n = len(valores_ordenados)
        valores_ordenados["p"] = [(n-i+1)/(n+1) for i in range(n)]
        valores_ordenados["p-1"] = 1 - valores_ordenados["p"]
        
        vazao_desejada = valores_ordenados.loc[valores_ordenados["p-1"] <= Q+0.0001]
        vazao_desejada = vazao_desejada.iloc[-1].vazao

        return vazao_desejada  
    #%%
    def analise_ano_hidrologico(self):
        self.df_dados = pd.DataFrame(index = self.vazao_y.index.year.unique() )

        for ano in self.vazao_y.index.year.unique():
                
                temp  = self.vazao_d.loc[self.vazao_d.index.year == ano]
                
                if temp["vazao"].isna().all():
                    # print(f"{ano}: Todos os dados são nulos, pulando a amostra de 12 dados.")
                    continue
                # print(temp.loc[temp["vazao"] == temp["vazao"].min()])
                menor_diario =  temp.loc[temp["vazao"] == temp["vazao"].min()].index.month.values[0]
                
                menor_anomalia= 10000000
                menor_Q7 = 10000000
                for mes in temp.index.month.unique():
                    temp2 = temp.loc[temp.index.month == mes]
                    
                    temp2 = temp2["vazao"].sort_values()
                    mediana_mes = temp2.median()
                    if mediana_mes <= menor_anomalia:
                        menor_anomalia= mediana_mes
                        mes_anomalia = mes
                        
                    Q7 = self.calcula_percentil(temp2, 0.07) 
                    if Q7 <= menor_Q7:
                        menor_Q7 = Q7
                        mes_Q7 = mes
                temp_m = self.vazao_d.loc[self.vazao_d.index.year == ano]  
                menor =  temp_m.loc[temp_m["vazao"] == temp_m["vazao"].min()].index.month.values[0]
              
                
        #         # 
                self.df_dados.loc[self.df_dados.index == ano,"mes com menor vazao Q7"]       = mes_Q7 
                self.df_dados.loc[self.df_dados.index == ano,"mes com menor mediana no mes"] = mes_anomalia
                self.df_dados.loc[self.df_dados.index == ano,"mes com menor vazao media"]    = menor
                self.df_dados.loc[self.df_dados.index == ano,"mes do dia de menor vazao"]    = menor_diario  

        #         # 
                # if temp["chuva"].isna().all():
        #             print(f"{ano}: Todos os dados são nulos, pulando a amostra de 12 dados.")
        #             continue
                
        #         menor_chuva =  temp.loc[temp["chuva"] == temp["chuva"].min()].index.month.values[0]
        #         df_dados.loc[df_dados.index == ano,"mes do dia de menor precptação"] = menor_chuva
                
        contagem_mediana      = self.df_dados['mes com menor mediana no mes'].value_counts()
        contagem_minima       = self.df_dados['mes do dia de menor vazao'].value_counts()
        contagem_minima_media = self.df_dados['mes com menor vazao media'].value_counts()
        # contagem_precptacao   = self.df_dados["mes do dia de menor precptação"].value_counts()
        contagem_Q7           = self.df_dados["mes com menor vazao Q7"].value_counts()

        # print("Tabela de Frequência para 'mes do dia de menor vazao':")
        # print(contagem_minima.sort_index())

        # print("\nTabela de Frequência para 'mes com menor vazao media':")
        # print(contagem_minima_media.sort_index())

        # print("\nTabela de Frequência para 'mes do dia de menor mediana mensal':")
        # print(contagem_mediana.sort_index())

        # print("\nTabela de Frequência para 'mes do dia de menor precptação':")
        # print(contagem_precptacao.sort_index())

        # print("\nTabela de Frequência para 'mes do dia de menor Q7':")
        # print(contagem_Q7.sort_index())
        
        return self.df_dados
    
    def analise_ano_hidrologico_cheia(self):
        self.df_dados_cheia= pd.DataFrame(index = self.vazao_y.index.year.unique() )

        for ano in self.vazao_y.index.year.unique():
                
                temp  = self.vazao_d.loc[self.vazao_d.index.year == ano]
                
                if temp["vazao"].isna().all():
                    # print(f"{ano}: Todos os dados são nulos, pulando a amostra de 12 dados.")
                    continue
                # print(temp.loc[temp["vazao"] == temp["vazao"].min()])
                maior_diario =  temp.loc[temp["vazao"] == temp["vazao"].max()].index.month.values[0]
                
                maior_anomalia= 0
                maior_Q7 = 0
                for mes in temp.index.month.unique():
                    temp2 = temp.loc[temp.index.month == mes]
                    
                    temp2 = temp2["vazao"].sort_values()
                    mediana_mes = temp2.median()
                    if mediana_mes >= maior_anomalia:
                        maior_anomalia= mediana_mes
                        mes_anomalia = mes
                        
                    Q7 = self.calcula_percentil(temp2, 0.07) 
                    if Q7 >= maior_Q7:
                        maior_Q7 = Q7
                        mes_Q7 = mes
                temp_m = self.vazao_d.loc[self.vazao_d.index.year == ano]  
                menor =  temp_m.loc[temp_m["vazao"] == temp_m["vazao"].max()].index.month.values[0]
              
                
        #         # 
                self.df_dados_cheia.loc[self.df_dados_cheia.index == ano,"mes com maior vazao Q7"]       = mes_Q7 
                self.df_dados_cheia.loc[self.df_dados_cheia.index == ano,"mes com maior mediana no mes"] = mes_anomalia
                self.df_dados_cheia.loc[self.df_dados_cheia.index == ano,"mes com maior vazao media"]    = menor
                self.df_dados_cheia.loc[self.df_dados_cheia.index == ano,"mes do dia de maior vazao"]    = maior_diario  

        #         # 
                # if temp["chuva"].isna().all():
        #             print(f"{ano}: Todos os dados são nulos, pulando a amostra de 12 dados.")
        #             continue
                
        #         menor_chuva =  temp.loc[temp["chuva"] == temp["chuva"].min()].index.month.values[0]
        #         df_dados.loc[df_dados.index == ano,"mes do dia de menor precptação"] = menor_chuva
                
        contagem_mediana      = self.df_dados_cheia['mes com menor mediana no mes'].value_counts()
        contagem_minima       = self.df_dados_cheia['mes do dia de menor vazao'].value_counts()
        contagem_minima_media = self.df_dados_cheia['mes com menor vazao media'].value_counts()
        # contagem_precptacao   = self.df_dados["mes do dia de menor precptação"].value_counts()
        contagem_Q7           = self.df_dados_cheia["mes com menor vazao Q7"].value_counts()

        # print("Tabela de Frequência para 'mes do dia de menor vazao':")
        # print(contagem_minima.sort_index())

        # print("\nTabela de Frequência para 'mes com menor vazao media':")
        # print(contagem_minima_media.sort_index())

        # print("\nTabela de Frequência para 'mes do dia de menor mediana mensal':")
        # print(contagem_mediana.sort_index())

        # print("\nTabela de Frequência para 'mes do dia de menor precptação':")
        # print(contagem_precptacao.sort_index())

        # print("\nTabela de Frequência para 'mes do dia de menor Q7':")
        # print(contagem_Q7.sort_index())
        
        return self.df_dados_cheia
#%%
if __name__ == "__main__":
    temp = Analise_dados_hidrologicos()
    xx = temp.inicializar()
    # df = temp.define_nulos()
    # dados = temp.analise_ano_hidrologico()
    # dados_cheia = temp.analise_ano_hidrologico_cheia()
    df = pd.read_csv("/discolocal/felipe/lisflood_pm/chuva/nulos.csv",index_col =0)
    df.drop(columns = ["25254856"],inplace= True)
 #%%   

    def plota(csv,ano):        
        fig2 = go.Figure()
        
        for coluna in csv.columns:
                
            fig2.add_trace(go.Scatter(x = csv.index , y = csv[coluna],name = coluna,connectgaps=False))
            fig2.update_layout(title=ano)
        f.write(fig2.to_html(full_html=False, include_plotlyjs='cdn')) 
    def plota_bar(csv,ano):        
        fig2 = go.Figure()
        
        for coluna in csv.columns:
                
            fig2.add_trace(go.Bar(x = csv.index , y = csv[coluna],name = coluna))
            fig2.update_layout(title=ano)
        f.write(fig2.to_html(full_html=False, include_plotlyjs='cdn')) 
    temp = df 
    # temp = df.replace(1, pd.NA)
    dct = {}
    estac = pd.DataFrame(index = temp.index,columns = temp.columns)
    with open('./plots/plot_por_ano.html', 'a') as f:
    
        for ano in temp.index:
            year = temp.loc[temp.index==ano]
            lista = []
            
            for estacao in year.columns:
                if year[estacao].values[0] <= 0.3:
                    lista.append(estacao)
                    estac.loc[estac.index == ano,estacao] = True
            temp2 = xx[lista]
            temp2 = temp2.loc[temp2.index.year == ano]
            dct[ano] = temp2
    estac = estac.fillna("False")

            # plota(temp2,ano)
    #%%
    
    
    dct_filtro ={
        2015 : 900,
        2016 : 900,
        2017 : 700,
        2019 : 700,
        2021 : 700,
        2023 : 200
        }


    for ano in dct.keys():
        if ano <= 2014:
            continue
        temp = dct[ano]
        
        mensal = temp.resample("M").sum(min_count = 20)
        df_ano = temp.resample("Y").sum(min_count = 100)
        
        if ano in dct_filtro.keys():
            menor_900 = df_ano.columns[df_ano.max() <= dct_filtro[ano]]
        
            for numero in menor_900:
                estac.loc[estac.index == ano,numero] = False
                
        # estac.loc[estac.index == ano,25254856] = False
        # with open('./plots/plot_acumulado_mes.html', 'a') as f:
        #     plota_bar(mensal ,ano)
            
            
        # with open('./plots/plot_acumulado_ano.html', 'a') as f:
        #     plota_bar(df_ano ,ano)
            

    #%%

    temp = df 
    # temp = df.replace(1, pd.NA)
    dct = {}
    for ano in temp.index:
        year = temp.loc[temp.index==ano]
        lista = []
        validada = estac.loc[estac.index == ano]
        colunas_com_true = validada.columns[validada.isin([True]).any()]
        temp2 = xx[colunas_com_true]
        temp2 = temp2.loc[temp2.index.year == ano]
        dct[ano] = temp2
    
    for ano in dct.keys():
        if ano <= 2014:
            continue
        temp = dct[ano]
        mensal = temp.resample("M").sum(min_count = 20)
        df_ano = temp.resample("Y").sum(min_count = 100)
    
        with open('./plots/plot_acumulado_mes.html', 'a') as f:
            plota_bar(mensal ,ano)
            
            
        with open('./plots/plot_acumulado_ano.html', 'a') as f:
            plota_bar(df_ano ,ano)
#%%
# # final = pd.DataFrame(index = xx.index,columns = ["pr"])
# final = pd.DataFrame()
# for ano in dct.keys():
#     temp = dct[ano]
#     temp = temp.mean(axis = 1).to_frame()
#     temp.rename(columns = {0 : "pr"},inplace = True)
#     final = pd.concat([final,temp])

#     # final = pd.merge(final,temp,left_index=True,right_index=True,how = "outer")

# import xarray as xr

# era5 = xr.open_dataset("/discolocal/felipe/lisflood_pm/catch/meteo/chuvas/pr_era5_corrigido.nc").to_dataframe()

# sim  = xr.open_dataset("/discolocal/felipe/lisflood_pm/catch/meteo/chuvas/pr_simepar.nc").to_dataframe()
    
# era5.drop(columns = ["spatial_ref"],inplace = True)
# era5.rename(columns = {"band_data":"era5"},inplace = True)
# era5 = era5.groupby("time").mean()

# sim.drop(columns = ["spatial_ref"],inplace = True)
# sim.rename(columns = {"pr":"simepar"},inplace = True)
# sim = sim.groupby("time").mean()
# sim['simepar'] = sim['simepar'].shift(-1)

# final = pd.merge(final,sim,left_index=True,right_index=True,how="outer")
# final = pd.merge(final,era5,left_index=True,right_index=True,how="outer")
# final.to_csv("./possivel_chuva_final.csv")


# final = final["2014":]
# fig2 = go.Figure()

# for coluna in final.columns:
        
#     fig2.add_trace(go.Scatter(x = final.index , y = final[coluna],name = coluna,connectgaps=False))
# fig2.write_html("./final.html")

        #%%
    # test = pd.DataFrame(index = range(1,13),columns = vazao_m.index.year.unique())
    # for ano in vazao_m.index.year:
    #     temp = vazao_m.loc[vazao_m.index.year == ano]
    #     for mes in temp.index.month:
    #         # print(mes)
    #         test[ano].loc[test.index == mes] = float(temp.loc[temp.index.month == mes].values[0][0])   
    
    # lista = []    
    # for coluna in test.columns:
    #     menor_valor = test[coluna].min()
    #     try:
            
    #         indice = test[coluna][test[coluna] == menor_valor].index[0]
    #     except:
    #         continue
    #     lista.append(indice)
    #     print(f"No ano '{coluna}', o menor valor é {menor_valor} no índice {indice}.")

    # from collections import Counter
    
    # # Exemplo de lista
    
    
    # # Contar as ocorrências de cada elemento na lista
    # contagem_elementos = Counter(lista)
    
    # # Encontrar o elemento mais recorrente
    # valor_mais_recorrente = contagem_elementos.most_common(1)[0][0]
    
    # # Encontrar a contagem do elemento mais recorrente
    # contagem_mais_recorrente = contagem_elementos.most_common(1)[0][1]

    # medias =     temp.mean()
    # medias =     medias.sort_values()
    
    # abaixo = medias[medias.values <=0.30]
    # acima = medias[medias.values >=0.30]
    
    # falha = xx[list(acima.index)]
    
    # plota(falha)
    
    


        