# plots everything in the ADF folder to plot folder
import pandas as pd
from rail import *
import sys
import os
import datetime
import ast

# default base commodity filename
scenario_switch = 1
base_arg = 'base'

# if the argument is 0 vs a list
try:
    if sys.argv[2] == '0':
        list_of_list_commodity = [range(1, no_of_commodity + 1)]
    else:
        list_of_list_commodity = ast.literal_eval(sys.argv[2])
except:
    list_of_list_commodity = [0]

# if the argument is the list
try:
    if sys.argv[1] == '0':
        list_of_list_railroad = [0]
    else:
        list_of_list_railroad = ast.literal_eval(sys.argv[1])
except:
    list_of_list_railroad = [0]

try:
    folder_in_LMF = sys.argv[3]
except:
    print("Folder not specified, using the newest folder in ADF")
    cwd = os.getcwd()
    os.chdir(adf_folder_path)
    name_list = os.listdir(".")
    folder_in_LMF = sorted(name_list, key=os.path.getmtime)[-1]
    os.chdir(cwd)

bases = os.listdir(adf_folder_path + folder_in_LMF)
bases = [adf_folder_path+folder_in_LMF+"/"+x for x in bases]
scenarios = [x for x in bases if base_arg not in x]

base_lmf = [x for x in bases if base_arg in x]

# plot for base
for filename in bases:
    for list_of_commodity in list_of_list_commodity:
        for list_of_railroad in list_of_list_railroad:
            print("python plot/plot.py " + str(list_of_commodity).replace(" ", "") + " " + str(list_of_railroad).replace(" ", "") + " " + filename)
            os.system("python plot/plot.py " + str(list_of_commodity).replace(" ", "") + " " + str(list_of_railroad).replace(" ", "") + " " + filename)

if len(base_lmf) > 1:
    print("Multiple base cases found. Skipping scenario plots.")
    scenario_switch = 0

# plot for scenario
print scenarios
if scenario_switch == 1:
    for filename in scenarios:
        for list_of_commodity in list_of_list_commodity:
            for list_of_railroad in list_of_list_railroad:
                print("python plot/plot.py " + str(list_of_commodity).replace(" ", "") + " " + str(list_of_railroad).replace(" ", "") + " " + base_lmf[0] + " " + filename)
                os.system("python plot/plot.py " + str(list_of_commodity).replace(" ", "") + " " + str(list_of_railroad).replace(" ", "") + " " + base_lmf[0] + " " + filename)
