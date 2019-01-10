# plots everything in the ADF folder to plot folder
import pandas as pd
from rail import *
import sys
import os
import datetime
import ast

# default values
plot_folder = 'Plots/'

# This program plots the output commodity.lmf file to plot.shp

folder_in_LMF = sys.argv[1]
base_arg = sys.argv[2]

try:
    if sys.argv[3]=='0':
        list_of_list_commodity = [range(1,no_of_commodity+1)]
    else:
        list_of_list_commodity = ast.literal_eval(sys.argv[3])
except:
    list_of_list_commodity = [range(1,no_of_commodity+1)]
try:
    if sys.argv[4]=='0':
        list_of_list_railroad = [get_network_rrs('gis/alllinks.shp')]
    else:
        list_of_list_railroad = ast.literal_eval(sys.argv[4])
except:
    list_of_list_railroad = [get_network_rrs('gis/alllinks.shp')]

bases = os.listdir("./netdata/ADF/" + folder_in_LMF)
scenarios = [x for x in bases if base_arg not in x]
base_lmf = [x for x in bases if base_arg in x]

filenames_list = base_lmf + scenarios

for list_of_commodity in list_of_list_commodity:
    for list_of_railroad in list_of_list_railroad:
        print("python plot2.py " + str(filenames_list).replace(" ", "").replace("'","") + " " + str(list_of_commodity).replace(" ", "") + " "+ str(list_of_railroad).replace(" ", "") + " " + folder_in_LMF)
        os.system("python plot2.py " + str(filenames_list).replace(" ", "").replace("'","") + " " + str(list_of_commodity).replace(" ", "") + " "+ str(list_of_railroad).replace(" ", "") + " " + folder_in_LMF)

