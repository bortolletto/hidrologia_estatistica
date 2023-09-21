#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 18 18:05:27 2023

@author: felipe

Calculo dos exercicios 2 em diante
"""


import pandas as pd
import plotly.graph_objs as go
import os
import plotly.io as pio
import numpy as np 

vazao_d = pd.read_csv("./csvs/vazao.csv",index_col = 0 ,parse_dates = True).iloc[::-1]

def calcular_estatisticas_descritivas(dados,tipo):
    """
    Calcula estatísticas descritivas para vazões médias anuais.
    
    Args:
        dados (pandas.DataFrame): DataFrame contendo os dados das vazões médias anuais.

    
    Returns:
        pandas.DataFrame: DataFrame com as estatísticas descritivas.
    """
    resultado = dados.groupby(tipo)['vazao'].agg(['mean', 'median', 'std', 'var', 'min', 'max', 'quantile', lambda x: np.percentile(x, 25), lambda x: np.percentile(x, 75)])
    
    resultado.rename(columns={'<lambda_0>': '1º Quartil', '<lambda_1>': '3º Quartil'}, inplace=True)
    
    return resultado

vazao_m= vazao_d.resample("M",label = "left",closed = "right").mean()

vazao_m["ano"] = vazao_m.index.year
vazao_m["ano_hidrologico"] = vazao_m.index.to_period('M').asfreq('A-FEB').astype(int)+ 1969

ano_hidrologico_ = pd.DataFrame(columns = vazao_m.index.year.unique())
ano_civil_       = pd.DataFrame(columns = vazao_m.index.year.unique())
for ano in vazao_m.index.year.unique():
    temp = vazao_m.loc[vazao_m.ano == ano]
    ano_civil = calcular_estatisticas_descritivas(temp,'ano')
    temp = vazao_m.loc[vazao_m.ano_hidrologico == ano]
    ano_hidrologico = calcular_estatisticas_descritivas(temp,"ano_hidrologico")

    ano_hidrologico_[ano] = ano_hidrologico.T
    ano_civil_[ano]       = ano_civil.T
    
    
    
    
