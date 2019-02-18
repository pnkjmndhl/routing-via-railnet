# plot by commodity and railroad
from rail import *
import pandas
import arcpy
import sys
import os
import re
import numpy as np

name_of_commodity = sys.argv[2]
name_of_railroad = sys.argv[1]
base_lmf = sys.argv[3]


def get_adf_filename(path):
    return path.split('/')[-1].split('.')[0]


folder_name = base_lmf.split('/')[
    -2]  # sample base_lmf =  ../netdata/ADF/20190110172541/base_volume0_20190110172541.ADF
adf_file_name = get_adf_filename(base_lmf)

try:
    scenario_lmf = sys.argv[4]
    print ("Scenario Found.")
    scenario_switch = 1
except:
    scenario_switch = 0

ADF_path_of_plot_folder = plot_folder_path + folder_name




def convert_to_list(argument):
    argument = re.sub(r'\[|\]', '', argument)
    argument_list = argument.split(',')
    return argument_list


if name_of_railroad == '0' and name_of_commodity == '0':
    type_of_plot = "all"
elif name_of_commodity != '0':
    type_of_plot = 'commodity'
elif name_of_railroad != '0':
    type_of_plot = 'railroad'
else:
    print("Something Unexpected happened")
    print "Railroad: {0}".format(name_of_railroad)
    print "Commodity: {0}".format(name_of_commodity)

# conversion to list
if name_of_railroad != '0':
    railroad_list = convert_to_list(name_of_railroad)
    railroad_list = [int(x) for x in railroad_list]
else:
    all_railroads = get_network_rrs(link_shp)
    railroad_list = all_railroads

if -1 in railroad_list:  # 0 = all railroads
    railroad_list.extend(all_railroads)
    railroad_list.remove(-1)

remove_railroads = [x for x in railroad_list if x < 0]
remove_railroads = remove_railroads + [x * -1 for x in remove_railroads]
railroad_list = [x for x in railroad_list if x not in remove_railroads]

if name_of_commodity != '0':
    commodity_list = convert_to_list(name_of_commodity)
    commodity_list = [int(x) for x in commodity_list]
else:
    all_commodities = range(1, no_of_commodity + 1)
    commodity_list = all_commodities

if -1 in commodity_list:
    commodity_list.extend(all_commodities)
    commodity_list.remove(-1)

remove_commodities = [x for x in commodity_list if x < 0]
remove_commodities = remove_commodities + [x * -1 for x in remove_commodities]
commodity_list = [x for x in commodity_list if x not in remove_commodities]
# adding emptys
empty_list = [x + commodity_adder for x in commodity_list]
commodity_list = commodity_list + empty_list

# setting default values
if type_of_plot == 'all':
    lyr_base = 'gis/symbology/Plot_all.lyr'
    lyr_diff = 'gis/symbology/Plotdiff_all.lyr'
    name_of_railroad = '0'
    name_of_commodity = '0'


# #for commodities
elif type_of_plot == 'commodity':
    lyr_base = 'gis/symbology/Plot_commodity.lyr'
    lyr_diff = 'gis/symbology/Plotdiff_commodity.lyr'
    name_of_railroad = '0'
    name_of_commodity = name_of_commodity

# for railroads
elif type_of_plot == 'railroad':
    lyr_base = 'gis/symbology/Plot_railroad.lyr'
    lyr_diff = 'gis/symbology/Plotdiff_railroad.lyr'
    name_of_railroad = name_of_railroad
    name_of_commodity = '0'

else:
    print ("Invalid Argument")
    print (type_of_plot)
    exit(0)

print("Expanded: ")
print("Commodity List: {0}".format(commodity_list))
print("Railroad List: {0}".format(railroad_list))


# read the file
def get_flow_from_adf(location):
    commodity_df = pandas.read_csv(location)
    commodity_df.columns = ["ID", "Arc", "DIR", "Comm", "RR", "NetTons", "X", "Delay", "traveltime", "length",
                            "payload"]
    commodity_df['GrossTons'] = commodity_df['NetTons'] * commodity_df['X']
    commodity_df = commodity_df[commodity_df["RR"].isin(railroad_list) & commodity_df["Comm"].isin(commodity_list)]
    commodity_table = pandas.pivot_table(commodity_df, values='GrossTons', index=['ID'], aggfunc=np.sum).reset_index()
    return commodity_table


arcpy.env.overwriteOutput = True  # overwrite files if already present


def add_column_to_shp(col_name):
    arcpy.DeleteField_management(plot, col_name)
    arcpy.AddField_management(plot, col_name, "Double")
    with arcpy.da.UpdateCursor(plot, ['ID', col_name]) as cursor:
        for row in cursor:
            try:
                row[1] = flow[flow.ID == row[0]][col_name].values[0]
            except:
                pass
                #print("Error on: linkID: " + str(row[0]))
            cursor.updateRow(row)


# return a list of field names in any shape file
def get_field_names(shp):
    fieldnames = [f.name for f in arcpy.ListFields(shp)]
    return fieldnames


# copy current network to plot
def get_plot_with_fieldnames(column_names):
    arcpy.Copy_management(link_shp, plot)
    arcpy.DeleteField_management(plot, column_names)


def export_to_jpeg(plot_type, plot_file_name, symbologyLayer):
    # modify symbology if necessary
    mxd = arcpy.mapping.MapDocument(plot_mxd_file)
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    lyr = arcpy.mapping.ListLayers(mxd, plot_type, df)[0]
    arcpy.ApplySymbologyFromLayer_management(lyr, symbologyLayer)
    lyr.visible = True
    lyr.transparency = 0
    arcpy.mapping.ExportToJPEG(mxd, plot_file_name + ".jpg", "PAGE_LAYOUT", resolution=800)
    del mxd

# this part is tested and works
def subtract_values(flow_df1, flow_df2, colname):
    df1_ids = flow_df1.ID.tolist()
    df2_ids = flow_df2.ID.tolist()
    to_add_on_df2 = list(set(df1_ids) - set(df2_ids))
    to_add_on_df1 = list(set(df2_ids) - set(df1_ids))
    add_to_df1 = pandas.DataFrame({"ID": to_add_on_df1, colname: [0] * len(to_add_on_df1)})
    add_to_df2 = pandas.DataFrame({"ID": to_add_on_df2, colname: [0] * len(to_add_on_df2)})
    flow_df1 = flow_df1.append(add_to_df1).sort_values(by=['ID']).reset_index()
    flow_df2 = flow_df2.append(add_to_df2).sort_values(by=['ID']).reset_index()
    flow = flow_df1
    flow[colname] = flow_df2[colname] - flow_df1[colname]
    return flow


def get_difference_string(base, scenario):
    base_lmf_list = base.split("_")
    scenario_lmf_list = scenario.split("_")
    list_of_differences = [x for x in scenario_lmf_list if x not in base_lmf_list]
    string_of_differences = '_'.join(list_of_differences)
    return string_of_differences


# main program
field_names = get_field_names(link_shp)  # getting field names
field_names = [e for e in field_names if e not in ["ID", "FID", "Shape"]]

print("Generating normal plot ...")
plot = plot_shp
if scenario_switch == 0:  # do only base plot
    flow = get_flow_from_adf(base_lmf)
    # print flow
    get_plot_with_fieldnames(field_names)
    add_column_to_shp("GrossTons")
    plot_path_name = ADF_path_of_plot_folder + "/" + adf_file_name + "_" + name_of_commodity + "_" + name_of_railroad
    if not os.path.exists(ADF_path_of_plot_folder):
        os.makedirs(ADF_path_of_plot_folder)
    print plot_path_name
    export_to_jpeg('Plot', plot_path_name, lyr_base)
    exit(0)

print("Generating Difference plot ...")
plot = plot_diff_shp
flow_1 = get_flow_from_adf(base_lmf)
flow_2 = get_flow_from_adf(scenario_lmf)


get_plot_with_fieldnames(field_names)

flow = subtract_values(flow_1, flow_2, "GrossTons")  # Base - Scenario

add_column_to_shp("GrossTons")

plot_path_name = ADF_path_of_plot_folder + "/scenario_" + get_adf_filename(base_lmf) + "&" + get_difference_string(
    get_adf_filename(base_lmf),
    get_adf_filename(scenario_lmf)) + "_" + name_of_railroad
if not os.path.exists(ADF_path_of_plot_folder):
    os.makedirs(ADF_path_of_plot_folder)
print plot_path_name
export_to_jpeg('Plotdiff', plot_path_name, lyr_diff)
