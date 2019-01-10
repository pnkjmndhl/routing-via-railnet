# plot by commodity and railroad
from rail import *
import pandas
import arcpy
import sys
import os
import re
import numpy as np


filenames = sys.argv[1]
commodities = sys.argv[2]
railroads = sys.argv[3]
folder = "netdata/ADF/"+ sys.argv[4]


plot_folder = 'Plots/'


#setting default values
name_of_railroad = 'all'
name_of_commodity = 'all'
mxdfile = r"Rail3_plot2.mxd"

# #for commodities
# mxdfile = r"Rail3_plot2_comm.mxd"
# name_of_railroad = 'all'
# name_of_commodity = commodities

#for railroads
# mxdfile = r"Rail3_plot2_railroad.mxd"
# name_of_railroad = railroads
# name_of_commodity = 'all'


# This program plots the output commodity.lmf file to plot.shp

# folder_in_LMF = "20181128152725"
# base_arg = "BASE"
# list_of_list_commodity = [range(1,no_of_commodity+1)]
# list_of_list_railroad = [get_network_rrs('gis/alllinks.shp')]
# bases = os.listdir("./netdata/ADF/" + folder_in_LMF)
# scenarios = [x for x in bases if base_arg not in x]
# base_lmf = [x for x in bases if base_arg in x]
# filenames_list = base_lmf + scenarios
# filenames = str(filenames_list)
# commodities = '[-1]'
# railroads = '[-1]'
# folder = "netdata/ADF/"+ folder_in_LMF

#default values to be commented


def convert_to_list(argument):
    argument = re.sub(r'\[|\]','',argument)
    argument_list = argument.split(',')
    return argument_list

##### dont run this
# default values
plot_folder = 'Plots/'







#conversion to list
filenames_list = convert_to_list(filenames)

#### upto this point

commodity_list = convert_to_list(commodities)
print commodity_list
commodity_list = [int(x) for x in commodity_list]
railroad_list = convert_to_list(railroads)
railroad_list = [int(x) for x in railroad_list]

#expand
all_commodities = range(1,no_of_commodity+1)

if -1 in commodity_list:
    commodity_list.extend(all_commodities)
    commodity_list.remove(-1)

remove_commodities = [x for x in commodity_list if x <0]
remove_commodities = remove_commodities + [x * -1 for x in remove_commodities]
commodity_list = [x for x in commodity_list if x not in remove_commodities]
#adding emptys
empty_list = [ x + commodity_adder for x in commodity_list ]
commodity_list = commodity_list + empty_list


all_railroads = get_network_rrs('gis/alllinks.shp')
if -1 in railroad_list: # 0 = all railroads
    railroad_list.extend(all_railroads)
    railroad_list.remove(-1)

remove_railroads = [x for x in railroad_list if x <0]
remove_railroads = remove_railroads + [x * -1 for x in remove_railroads]
railroad_list = [x for x in railroad_list if x not in remove_railroads]

print("Commodity List: {0}".format(commodity_list))
print("Railroad List: {0}".format(railroad_list))


#read the file
def get_flow_from_adf(location):
    commodity_df = pandas.read_csv(location)
    commodity_df.columns = ["ID", "Arc", "DIR", "Comm", "RR", "NetTons", "X", "Delay", "traveltime", "length", "payload"]
    commodity_df['GrossTons'] = commodity_df['NetTons']*commodity_df['X']
    commodity_df = commodity_df[commodity_df["RR"].isin(railroad_list) & commodity_df["Comm"].isin(commodity_list)]
    commodity_table = pandas.pivot_table(commodity_df, values='GrossTons', index=['ID'], aggfunc=np.sum).reset_index()
    return commodity_table


plot_folder = 'Plots/' + sys.argv[4]

base_lmf = filenames_list[0]

try:
    scenarios = filenames_list[1:]
except:
    scenarios = []

bases = filenames_list


arcpy.env.overwriteOutput = True  # overwrite files if already present

def add_column_to_shp(col_name):
    arcpy.DeleteField_management(plot, col_name)
    arcpy.AddField_management(plot, col_name, "Double")
    with arcpy.da.UpdateCursor(plot, ['ID', col_name]) as cursor:
        for row in cursor:
            try:
                row[1] = flow[flow.ID == row[0]][col_name].values[0]
            except:
                #pass
                print("Error on: linkID: " + str(row[0]))
            cursor.updateRow(row)


# return a list of field names in any shape file
def get_field_names(shp):
    fieldnames = [f.name for f in arcpy.ListFields(shp)]
    return fieldnames


# copy current network to plot
def get_plot_with_fieldnames(column_names):
    arcpy.Copy_management(link_shp, plot)
    arcpy.DeleteField_management(plot, column_names)


def export_to_jpeg(plot_type, exclude_plot, plot_path):
    now = datetime.datetime.now()
    mxd = arcpy.mapping.MapDocument(mxdfile)
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    # print arcpy.mapping.ListLayers(mxd, "", df)[0].name
    for lyr in arcpy.mapping.ListLayers(mxd, "", df):
        if lyr.name in plot_type:
            lyr.visible = True
            lyr.transparency = 0
        elif lyr.name in exclude_plot:
            lyr.visible = False
    arcpy.mapping.ExportToJPEG(mxd, plot_path + "_" + now.strftime("%Y%m%d_%H%M") + ".jpg", "PAGE_LAYOUT",
                               resolution=800)
    del mxd
    print ("Completed")


def check_scenario(base_,scenario_):
    # put the checking code here...
    # if no codes, plots everything
    return 0





# main program
link_shp = 'gis/alllinks.shp'
field_names = get_field_names(link_shp)  # getting field names
field_names = [e for e in field_names if e not in ["ID", "FID", "Shape"]]

print("Generating normal plot ...")
plot = 'gis/plots/Plot.shp'

for base in bases:
    print ("working on: " + base)
    file_name = folder + "/" + base
    flow = get_flow_from_adf(file_name)
    print flow
    get_plot_with_fieldnames(field_names)
    add_column_to_shp("GrossTons")
    plot_type = ['Plot', 'allnodes']
    exclude_plot = ['Plotdiff']
    plot_name = base
    plot_path = 'plots/' + sys.argv[4] + "/" + plot_name + "_" + name_of_commodity + "_" + name_of_railroad
    if not os.path.exists('plots/' + sys.argv[4]):
        os.makedirs('plots/' + sys.argv[4])
    print plot_path
    export_to_jpeg(plot_type, exclude_plot, plot_path)


if scenarios == "":
    print("No Scenario Plots generated")
    exit(0)

print("Generating Difference plot ...")
plot = 'gis/plots/Plotdiff.shp'
file_1 = folder + "/" + base_lmf


file_2 = folder + "/" + scenarios[0]

# flow_1 = get_flow_from_adf(file_1)
# flow_2 = get_flow_from_adf(file_2)
#
flow_df1 = get_flow_from_adf(file_1)
flow_df2 = get_flow_from_adf(file_2)

def subtract_values(flow_df1, flow_df2, colname):
    df1_ids = flow_df1.ID.tolist()
    df2_ids = flow_df2.ID.tolist()
    to_add_on_df2 = list(set(df1_ids) - set(df2_ids))
    to_add_on_df1 = list(set(df2_ids) - set(df1_ids))
    add_to_df1 = pandas.DataFrame({"ID": to_add_on_df1, colname:[0] * len(to_add_on_df1)})
    add_to_df2 = pandas.DataFrame({"ID": to_add_on_df2, colname:[0] * len(to_add_on_df2)})
    flow_df1 = flow_df1.append(add_to_df1).sort_values(by=['ID']).reset_index()
    flow_df2 = flow_df2.append(add_to_df2).sort_values(by=['ID']).reset_index()
    flow = flow_df1
    flow[colname] = flow_df2[colname] - flow_df1[colname]
    return flow



for scenario in scenarios:
    check_scenario(base_lmf,scenario)
    print ("working on: " + base_lmf + ", " + scenario)
    file_2 = folder + "/" + scenario
    flow_1 = get_flow_from_adf(file_1)
    flow_2 = get_flow_from_adf(file_2)
    get_plot_with_fieldnames(field_names)
    flow = subtract_values(flow_1, flow_2, "GrossTons") # Base - Scenario
    add_column_to_shp("GrossTons")
    plot_type = ["Plotdiff", 'allnodes']
    exclude_plot = ['Plot']
    plot_name = base_lmf + "_" + scenario + "_" + name_of_commodity + "_" + name_of_railroad
    plot_path = 'plots/' + sys.argv[4] + "/" + plot_name
    if not os.path.exists('plots/' + sys.argv[4]):
        os.makedirs('plots/' + sys.argv[4])
    print plot_path
    export_to_jpeg(plot_type, exclude_plot, plot_path)
