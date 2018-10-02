# creates OD1.csv file from base excel file

import pandas as pd

# input
commodity_filename = r"input/base/NEWFLOW3.xlsx"
commodity_sheetname = "Sheet1"
orra_to_orr = r"../Module4(Transfers)/input/allAARCode.csv"
ParameterList = ['OFIP', 'TFIP', 'RNCG', 'XTON', 'ORRA']

OD = pd.ExcelFile(commodity_filename).parse(commodity_sheetname)[ParameterList]
orra_to_orr_df = pd.read_csv(orra_to_orr)
orra_to_orr_dict = dict(zip(orra_to_orr_df.AARCode, orra_to_orr_df.ABBR))

# ORR converted to actual ORR
OD['ORR'] = OD['ORRA'].map(orra_to_orr_dict)
OD = OD.drop(['ORRA'], axis=1)

OD.columns = ['OFIPS', 'DFIPS', 'comm', 'quantity', 'startRR']
OD['ONode'] = ""
OD['DNode'] = ""
OD.to_csv(r"intermediate/OD1.csv")
print("OD1.csv updated successfully")
