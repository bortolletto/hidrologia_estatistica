#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 12:34:53 2023

@author: felipe.bortolletto
"""

import pandas as pd 
import xarray as xr
import numpy as np
import os 

dx = xr.open_dataset("/discolocal/felipe/lisflood_pm/catch/meteo/chuvas/pr_média_geral0.nc")
estac = pd.read_csv("./estac_atualizado.csv",index_col = 0)
chuva = pd.read_csv("./chuva_pontos.csv",index_col = 0,parse_dates=True)
chuva = chuva.resample("D",closed='left', label='right').sum(min_count = 20)
chuva = chuva["2013":]

data = pd.date_range("2013-01-01","2023-04-07",freq = "D")
final = pd.DataFrame(index = data,columns = ["pr"])
for ano in chuva.index.year:
    temp = chuva.loc[str(ano)]
    validada = estac.loc[estac.index == ano]
    selected_stations = validada.columns[validada.isin([True]).any()]
    temp = temp[selected_stations]
    temp = temp.mean(axis = 1).to_frame()
    temp.rename(columns = {temp.columns[0]:"pr"},inplace = True)
    for i in temp.index:
        valor = temp.loc[temp.index == i,"pr"]
        final.loc[final.index == i,"pr"] = float(valor[0])
    break



base = xr.open_dataset("../catch/meteo/chuvas/pr_simepar.nc")
temp2 = base.copy()
matrizes = []
   
for _, row in final.iterrows():
   matriz = np.full((12, 20), row["pr"])
   matrizes.append(matriz)
temp2.pr.values = matrizes
 
os.remove("../catch/meteo/pr.nc")
temp2.to_netcdf("../catch/meteo/pr.nc")

que = xr.open_dataset("/discolocal/felipe/lisflood_pm/catch/meteo/pr.nc")
