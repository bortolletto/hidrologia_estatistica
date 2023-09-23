#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 23 18:19:41 2023

@author: felipe

distribuições probabilisticas 


"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 

vazao_d = pd.read_csv("./csvs/vazao.csv",index_col = 0 ,parse_dates = True).iloc[::-1]
vazao_d["ano_hidrologico"] = vazao_d.index.to_period('M').asfreq('A-FEB').astype(int)+ 1969


vazao_m= vazao_d.resample("M",label = "left",closed = "right").mean()

vazao_m["ano"] = vazao_m.index.year
vazao_m["ano_hidrologico"] = vazao_m.index.to_period('M').asfreq('A-FEB').astype(int)+ 1969


#%%normal
dados = vazao_d.vazao
media = dados.mean()
std = dados.std()
def normal_pdf(dados):
    """
    Calcula a função de densidade de probabilidade (PDF) da distribuição normal.

    Args:
        x (float): O valor para o qual você deseja calcular o PDF.
        mu (float): A média (valor esperado) da distribuição.
        sigma (float): O desvio padrão da distribuição.

    Returns:
        float: O valor da PDF para o valor x dado os parâmetros mu e sigma.
    """
    mu = dados.mean()
    sigma = dados.std()
    x = dados.values
    coeficiente = 1 / (sigma * np.sqrt(2 * np.pi))
    exponent = -((x - mu) ** 2) / (2 * sigma ** 2)
    pdf = coeficiente * np.exp(exponent)
    return pdf

#comparacao
from scipy.stats import norm
pdf_custom = normal_pdf(dados)

# Calcula a PDF usando a implementação do SciPy
pdf_scipy = norm.pdf(dados, loc=dados.mean(), scale=dados.std())
compara = pd.DataFrame()
# Exibe os resultados
compara["custom_normal"] = pdf_custom
compara["custom_scipy"] = pdf_scipy
compara = round(compara,2)
compara["dif_normal"] = abs(compara["custom_normal"] - compara["custom_scipy"])
print(compara["dif_normal"].sum())

# print(f"PDF (custom): {pdf_custom}")
# print(f"PDF (SciPy):  {pdf_scipy}")
# print((np.sum(pdf_custom)-np.sum(pdf_scipy)))

#%%log normal

def lognormal_pdf(x):
    """
    Calcula a função de densidade de probabilidade (PDF) da distribuição log-normal.

    Args:
        x (float): O valor para o qual você deseja calcular o PDF.
        mu (float): O parâmetro da média.
        sigma (float): O parâmetro do desvio padrão.

    Returns:
        float: O valor da PDF para o valor x dado os parâmetros mu e sigma.
    """

    ln_x = np.log(x)
    mu_log = ln_x.mean()
    
    sigma_log = ln_x.std()
    
    coeficiente = 1 / (x * sigma_log * np.sqrt(2 * np.pi))
    exponent = -0.5*((ln_x - mu_log) / (sigma_log))
    pdf = coeficiente * np.exp(exponent)
    return pdf

from scipy.stats import lognorm
ln_x = np.log(dados)
mu = ln_x.mean()
sigma = ln_x.std()

pdf_custom = lognormal_pdf(dados)

# Calcula a PDF usando a implementação do SciPy para a distribuição log-normal
pdf_scipy = lognorm.pdf(dados,mu,sigma)

# Cria um DataFrame para comparar os resultados
compara = pd.DataFrame()
compara["custom_lognormal"] = pdf_custom
compara["scipy_lognormal"] = pdf_scipy

# Calcula a diferença absoluta entre as PDFs
compara["dif_lognormal"] = abs(compara["custom_lognormal"] - compara["scipy_lognormal"])

# Soma das diferenças absolutas
soma_dif = compara["dif_lognormal"].sum()

print(compara)
print(f"Soma das diferenças: {soma_dif:.4f}")

#%% exp
    
import numpy as np

def exponencial_pdf(x):
    """
    Calcula a função de densidade de probabilidade (PDF) da distribuição exponencial.

    Args:
        x (float): O valor para o qual você deseja calcular o PDF.
        lmbda (float): O parâmetro da taxa (lambda) da distribuição exponencial.

    Returns:
        float: O valor da PDF para o valor x dado o parâmetro lambda.
    """
    teta = x.mean()
    lmbda = 1/teta

    pdf = lmbda * np.exp(-lmbda * x)
    return pdf



from scipy.stats import expon

# Parâmetros da distribuição exponencial
lmbda = dados.mean()  # Parâmetro da taxa (lambda)

pdf_custom = exponencial_pdf(dados)

# Calcula a PDF usando a implementação do SciPy
pdf_scipy = expon.pdf(dados, scale=1/lmbda)

# Cria um DataFrame para comparar os resultados
compara = pd.DataFrame()
compara["custom_exponencial"] = pdf_custom
compara["scipy_exponencial"] = pdf_scipy

# Calcula a diferença absoluta entre as PDFs
compara["dif_exponencial"] = abs(compara["custom_exponencial"] - compara["scipy_exponencial"])

# Soma das diferenças absolutas
soma_dif = compara["dif_exponencial"].sum()

print(compara.head())  # Exibe as primeiras linhas para ver os resultados
print(f"Soma das diferenças: {soma_dif:.6f}")

#%%

def gama(dados):
    import scipy
    
    media = dados.mean()
    desvio= dados.std()
    
    teta = desvio * media ** 0.5
    ni   = desvio**2 / teta
    
    numerador = (dados/teta)**(ni-1) * np.exp(-dados/teta)
    denominador = teta * scipy.special.gamma(ni)
    pdf = numerador/denominador
    
    return pdf

gama(dados)

import scipy.stats as stats
import numpy as np

# Parâmetros da distribuição gama (forma e escala)
alpha = 2.0
beta = 1.5

# Calcular a PDF da distribuição gama em um valor específico
x = 3.0
pdf = stats.gamma.pdf(dados, alpha, scale=1/beta)





