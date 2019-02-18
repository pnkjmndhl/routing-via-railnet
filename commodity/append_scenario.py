import pandas
from rail import *
import os

base_file_name = 'base'

scenario_list = os.listdir(scenario_folder_path)
scenario_list = [x.split('.')[0] for x in scenario_list]

for scenario in scenario_list:
    scenario_df = pandas.read_csv(commodity_intermediate_path+scenario+"_1.csv")
    base_df = pandas.read_csv(commodity_intermediate_path + base_file_name + '_1.csv')
    base_df = base_df.append(scenario_df)
    base_df = base_df[['OFIPS', 'DFIPS', 'comm', 'quantity', 'startRR','termiRR', 'ONode', 'DNode', 'ODIST']]
    base_df.to_csv(commodity_intermediate_path+scenario+"_1.csv")
