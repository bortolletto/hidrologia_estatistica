#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 14:29:33 2023

@author: felipe.bortolletto
"""

import pandas as pd 
import xarray as xr
# import geopandas as gpd

# import os 

estac = pd.read_csv("./estac.csv",index_col = 0)
chuva = pd.read_csv("./chuva_pontos.csv",index_col = 0,parse_dates=True)
chuva = chuva.resample("D",closed='left', label='right').sum(min_count = 20)
loc_pontos   =pd.read_csv("loc_pontos.csv",index_col = 0)


years = estac.index.unique()

# Pasta onde os shapefiles serão salvos
output_folder = "shapefiles/"

# Loop pelos anos
# for year in years:
#     # Filtrar as estações operacionais para o ano atual
#     operational_stations = estac.loc[year][estac.loc[year] == True].index.tolist()
    
#     # Filtrar os pontos de localização correspondentes às estações operacionais
#     points_for_year = loc_pontos[loc_pontos['codigo'].isin(operational_stations)]
    
#     # Criar um GeoDataFrame a partir dos pontos filtrados
#     gdf = gpd.GeoDataFrame(points_for_year, geometry=gpd.points_from_xy(points_for_year['longitude'], points_for_year['latitude']))
    
#     # Salvar o GeoDataFrame como shapefile
#     shapefile_path = f"{output_folder}estacoes_{year}.shp"
#     gdf.to_file(shapefile_path)
    
#     print(f"Shapefile para o ano {year} criado em: {shapefile_path}")
    
    
#%%

for ano in estac.index:
    validada = estac.loc[estac.index == ano]
    colunas_com_true = validada.columns[validada.isin([True]).any()]
    temp = chuva[colunas_com_true]
    temp = temp.loc[temp.index.year == ano]
    temp_loc = loc_pontos.loc[loc_pontos['codigo'].isin([int(x) for x in list(temp.columns)])]
    temp_loc = temp_loc[["codigo","nome","latitude","longitude"]]
    temp_loc.to_csv(f"/discolocal/felipe/lisflood_pm/chuva/shapefiles/{ano}.csv")
