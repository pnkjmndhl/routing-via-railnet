# creates OD1.csv file from base and scenario excel file
from rail import *
import pandas as pd
import os
import sys

list_of_commodity_files = []
for commodity_xls in os.listdir(base_folder_path):
    list_of_commodity_files.append(base_folder_path + commodity_xls)

for commodity_xls in os.listdir(scenario_folder_path):
    list_of_commodity_files.append(scenario_folder_path + commodity_xls)

commodity_sheetname = "Sheet1"
ParameterList = ['OFIP', 'TFIP', 'RNCG', 'XTON', 'ORRA', 'TRRA']

for commodity_filepath in list_of_commodity_files:
    print("working on " + commodity_filepath)
    commodity_filename = commodity_filepath.split("/")[-1].split('.')[0]
    OD = pd.ExcelFile(commodity_filepath).parse(commodity_sheetname)[ParameterList]
    orra_to_orr = pd.read_csv(all_aar_csv)
    orra_to_orr_dict = dict(zip(orra_to_orr.AARCode, orra_to_orr.ABBR))
    # ORR converted to actual ORR
    OD['ORR'] = OD['ORRA'].map(orra_to_orr_dict)
    OD['TRR'] = OD['TRRA'].map(orra_to_orr_dict)
    OD = OD.drop(['ORRA', 'TRRA'], axis=1)
    OD = OD.fillna(0)
    OD.columns = ['OFIPS', 'DFIPS', 'comm', 'quantity', 'startRR', 'termiRR']
    OD['ONode'] = ""
    OD['DNode'] = ""
    OD['ODIST'] = ""
    OD['DDIST'] = ""
    OD.to_csv(commodity_intermediate_path + commodity_filename + '.csv')
    print(commodity_filename + '.csv created successfully')
