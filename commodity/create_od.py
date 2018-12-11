# creates OD1.csv file from base and scenario excel file
from rail import *
import pandas as pd
import os
import sys

commodity_list = os.listdir('input/' + sys.argv[1] + '/')
commodity_list = [x.split('.')[0] for x in commodity_list]
commodity_sheetname = "Sheet1"

ParameterList = ['OFIP', 'TFIP', 'RNCG', 'XTON', 'ORRA', 'TRRA']

print("working on "+sys.argv[1]+ ' folder..')

for commodity_filename in commodity_list:
    OD = pd.ExcelFile('input/' + sys.argv[1] + '/' + commodity_filename + '.xlsx').parse(commodity_sheetname)[
        ParameterList]
    orra_to_orr_df = pd.read_csv(orra_to_orr)
    orra_to_orr_dict = dict(zip(orra_to_orr_df.AARCode, orra_to_orr_df.ABBR))

    # ORR converted to actual ORR
    OD['ORR'] = OD['ORRA'].map(orra_to_orr_dict)
    OD['TRR'] = OD['TRRA'].map(orra_to_orr_dict)
    OD = OD.drop(['ORRA','TRRA'], axis=1)
    OD = OD.fillna(0)
    OD.columns = ['OFIPS', 'DFIPS', 'comm', 'quantity', 'startRR', 'termiRR']
    OD['ONode'] = ""
    OD['DNode'] = ""
    OD['ODIST'] = ""
    OD['DDIST'] = ""
    OD.to_csv(r'intermediate/' + commodity_filename + '.csv')
    print(commodity_filename + '.csv created successfully')
