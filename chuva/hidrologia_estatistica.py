#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 23 09:59:01 2023

@author: felipe.bortolletto

Criar classe de estudos hidrologicos mais simples. 
"""
import pandas as pd
import plotly.graph_objs as go
import os
import plotly.io as pio
import numpy as np 

from collections import Counter
 
 # Exemplo de lista
 
 
 # Contar as ocorrências de cada elemento na lista
 



class Vazao():

        
    def Vdiario(self):
        df = self.vazao_d
        return df
    def Vmensal(self):
        df = self.vazao_d.resample("M",label = "right").mean()
        return df
    def Vanual(self):
        df = self.vazao_d.resample("Y",label = "right").mean()
        return df
    
    def calcula_percentil(self,df,Q):
        Q = 0.07
        valores_ordenados = df.sort_values().to_frame()
        n = len(valores_ordenados)
        valores_ordenados["p"] = [(n-i+1)/(n+1) for i in range(n)]
        valores_ordenados["p-1"] = 1 - valores_ordenados["p"]
        
        vazao_desejada = valores_ordenados.loc[valores_ordenados["p-1"] <= Q+0.0001]
        vazao_desejada = vazao_desejada.iloc[-1].vazao

        return vazao_desejada  
    
    def vazao_minima_anual(self):
        '''
        calcula mês com maior frequência de ocorrência de vazões mínimas anuais

        Returns
        -------
        None.

        '''
        for ano in self.anos:
            temp = self.vazao_d.loc[self.vazao_d.index.year == ano]
            if temp["vazao"].isna().all():
                print(f"{ano}: Todos os dados são nulos.")
                continue
            menor_diario =  temp.loc[temp["vazao"] == temp["vazao"].min()].index.month.values[0]
            self.df_dados.loc[self.df_dados.index == ano,"mes do dia de menor vazao"] = menor_diario  
        return self.df_dados
    
    def menor_média_mensal(self):
        '''
        Calcula mês com a menor média das vazões mensais

        Returns
        -------
        None.

        '''
        df = self.Vmensal()
        
        for ano in self.anos:
            temp = df.loc[df.index.year == ano]
            if temp["vazao"].isna().all():
                print(f"{ano}: Todos os dados são nulos.")
                continue
            menor_media_mensal = temp.loc[temp["vazao"] == temp["vazao"].min()].index.month.values[0]
            self.df_dados.loc[self.df_dados.index == ano,"mes com menor vazao media"]    = menor_media_mensal
        return self.df_dados
         
    def menor_mediana(self):
        '''
        O mês com a menor mediana das vazões mensais

        Returns
        -------
        None.

        '''
        df = self.Vdiario()
        for ano in self.anos:
            temp = df.loc[df.index.year == ano]
            if temp["vazao"].isna().all():
                print(f"{ano}: Todos os dados são nulos.")
                continue
            
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
            
                self.df_dados.loc[self.df_dados.index == ano,"mes com menor vazao Q7"]       = mes_Q7 
                self.df_dados.loc[self.df_dados.index == ano,"mes com menor mediana no mes"] = mes_anomalia
        return self.df_dados
    
    #%%
class Chuva():


    def Cdiario(self):
        df = self.chuva.resample("D").sum(min_count = 12)
        return df
    def Cmensal(self):
        df = self.chuva.resample("M").sum(min_count = 20 )
        return df
    def Canual(self):
        df = self.chuva.resample("Y").sum(min_count = 250)
        return df
    
    def chuva_menor_media_mensal(self):
        '''
        O mês com a menor precipitação média mensal

        Returns
        -------
        None.

        '''
        df = self.Cmensal()

        for ano in self.anos:
            temp = df.loc[df.index.year == ano]
            if temp["horleitura"].isna().all():
                print(f"{ano}: Todos os dados são nulos.")
                continue
            
            menor_chuva =  temp.loc[temp["horleitura"] == temp["horleitura"].min()].index.month.values[0]
            self.df_dados.loc[self.df_dados.index == ano,"mes com menor preciptacao"] = menor_chuva

        return self.df_dados
    
    
    
#%%    
class hidro_estatic(Vazao,Chuva):
    def __init__(self):
        self.vazao_d = pd.read_csv("./vazao.csv",index_col = 0 ,parse_dates = True).iloc[::-1]
        self.anos = self.vazao_d.index.year.unique()
        self.df_dados = pd.DataFrame(index = self.anos)
        self.chuva = pd.read_csv("./chuva_25334953_Porto Amazonas.csv",index_col = 0,parse_dates =True)
        self.chuva = self.chuva.loc[self.chuva.horqualidade == 0]
    def roda_todas(self):
        
        self.vazao_minima_anual()
        self.menor_mediana()
        self.chuva_menor_media_mensal()
        df = self.menor_média_mensal()
        return df
    
    def define_ano_hidrologico(self,dados):
        for coluna in dados.columns:
            # Use o método 'value_counts' para contar a ocorrência de cada valor na coluna
            contagem_valores = dados[coluna].value_counts()
            
            # Obtenha o valor mais recorrente (primeiro valor no índice do DataFrame resultante)
            valor_mais_recorrente = contagem_valores.index[0]
            
            # Obtenha a contagem do valor mais recorrente
            contagem_mais_recorrente = contagem_valores.iloc[0]
            
            print(f"Na coluna '{coluna}', o valor mais recorrente é {valor_mais_recorrente} "
                  f"com um total de {contagem_mais_recorrente} ocorrências.")
    def delimita_ano_hidrologico(self,mes=8):
        df = self.Vmensal()
        self.nv_ano_hidrologico = pd.DataFrame(index = range(1,13))

        mes_inicio = mes -6
        mes_fim = mes_inicio
        for ano in self.anos:
            selected_period = df[(df.index >= f"{ano}-{mes_inicio}-01") & (df.index <= f"{ano+1}-{mes_fim}-01")]
            # print("selected_period ")
            
            selected_period = selected_period.set_index(selected_period.index.month)
            selected_period.rename(columns = {"vazao": ano},inplace = True)
            self.nv_ano_hidrologico = pd.merge(self.nv_ano_hidrologico,selected_period,how = "outer",left_index=True,right_index =True)
        return self.nv_ano_hidrologico
    
if __name__ == "__main__":
    
    dfv = hidro_estatic()
    df  = dfv.roda_todas() 
    dfv.define_ano_hidrologico(df)
    test =  dfv.delimita_ano_hidrologico()
    
    def plota_todas(df):

        fig = go.Figure()
        for coluna in df.columns:
            fig.add_trace(go.Scatter(x = df.index , y = df[coluna],name = coluna,connectgaps=False))
            
            
        fig.write_html("./ano_hidrologico.html")
        return "arquivo './todas as chuvas.html' ja disponivel!"
    
    plota_todas(test)
    # df = dfv.Vmensal()
    # anos = df.index.year.unique()
    # for ano in anos:
    #     selected_period = df[(df.index >= f"{ano}-02-01") & (df.index <= f"{ano+1}-02-01")]
    #     print(selected_period)
    
    # df.loc[df["vazao"] == df["vazao"].min()]
    # dados = dfv.vazao_minima_anual()  
    # contagem_elementos = Counter(dados["mes do dia de menor vazao"])
    # valor_mais_recorrente = contagem_elementos.most_common(1)[0][0]
    

