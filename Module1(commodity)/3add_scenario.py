import pandas
import sys
import os

scenario_list = os.listdir('input/scenario/')
scenario_list = [x.split('-')[1].split('.')[0] for x in scenario_list]

for scenario in scenario_list:
    scenario_df = pandas.read_csv("input/scenario/OD2-"+scenario+".csv")
    base_df = pandas.read_csv("intermediate/OD2.csv")
    base_df = base_df.append(scenario_df)
    base_df = base_df[['OFIPS', 'DFIPS', 'comm', 'quantity', 'startRR', 'ONode', 'DNode']]
    #base_df = base_df[['OFIPS', 'DFIPS', 'comm', 'quantity', 'startRR', 'ONode', 'DNode', 'ODIST']]
    base_df.to_csv("intermediate/OD2-"+scenario+".csv")