import pandas
import sys
import os


os.system("python create_od.py scenario")

scenario_list = os.listdir('input/scenario/')
scenario_list = [x.split('.')[0] for x in scenario_list]

for scenario in scenario_list:
    os.system("python snap.py "+scenario+ " update")

for scenario in scenario_list:
    scenario_df = pandas.read_csv("intermediate/"+scenario+"_1.csv")
    base_df = pandas.read_csv("intermediate/base_1.csv")
    base_df = base_df.append(scenario_df)
    base_df = base_df[['OFIPS', 'DFIPS', 'comm', 'quantity', 'startRR', 'ONode', 'DNode', 'ODIST']]
    base_df.to_csv("intermediate/"+scenario+"_1.csv")