# plots the LMF file to jpg

import pandas as pd
import arcpy
import sys
import os


# This program plots the output commodity.lmf file to plot.shp

argument = sys.argv

if len(argument) == 2:
    plot_type = "Plot"
elif len(argument) == 3:
    plot_type = "Plotdiff"
else:
    print ("Invalid argument")
    exit()

arcpy.env.overwriteOutput = True  # overwrite files if already present


def add_column_to_shp(col_name):
    arcpy.DeleteField_management(plot, col_name)
    arcpy.AddField_management(plot, col_name, "Double")
    i = 0
    with arcpy.da.UpdateCursor(plot, ['ID', col_name]) as cursor:
        for row in cursor:
            try:
                row[1] = flow[flow.ID == row[0]]['qty'].values[0]
            except:
                print("Failed to plot linkID: " + str(row[0]))
            i += 1
            cursor.updateRow(row)


# split the *.lmf file and change it to data frame
def split_to_dataframe(file_name, column_names):
    my_list = []
    columns = len(column_names)  # extract columns for #columns from left to right
    for i in range(columns):
        my_list.append([])
    with open(file_name, "rt") as f:
        for line in f:
            for column in range(columns):
                my_list[column].append(line.split(',')[column])
    my_list[column] = [x.split('\n')[0] for x in my_list[column]]  # to remove the last \n
    my_list[column] = [0 if x == "************" else x for x in my_list[column]]  # replace ****
    flow_df = pd.DataFrame()
    for i in range(columns):  # column_names should be equal to columns
        flow_df[column_names[i]] = my_list[i]
        flow_df[column_names[i]] = flow_df[column_names[i]].astype(float)  # some values may not be float but string
    return flow_df


# return a list of field names in any shape file
def get_field_names(shp):
    fieldnames = [f.name for f in arcpy.ListFields(shp)]
    return fieldnames


# copy current network to plot
def get_plot_with_fieldnames(column_names):
    arcpy.Copy_management(link_shp, plot)
    arcpy.DeleteField_management(plot, column_names)


# main program
link_shp = 'gis/alllinks.shp'
field_names = get_field_names(link_shp)  # getting field names
field_names = [e for e in field_names if e not in ["ID", "FID", "Shape"]]

if len(argument) == 3: #scenario plots
    print("Generating Scenario plot ...")
    plot = 'gis/plots/Plotdiff.shp'
    file_1 = "Netdata/"+argument[1]
    file_2 = "Netdata/"+argument[2]
    flow_1 = split_to_dataframe(file_1 + ".LMF", ['ID', 'qty'])
    flow_2 = split_to_dataframe(file_2 + ".LMF", ['ID', 'qty'])
    flow = flow_1  # flow1 is always the base flow
    get_plot_with_fieldnames(field_names)
    flow['qty'] = flow_2['qty'] - flow_1['qty']

if len(argument) == 2: #base plots
    print("Generating base plot ...")
    plot = 'gis/plots/Plot.shp'
    file_name = "Netdata/"+argument[1]
    flow = split_to_dataframe(file_name + ".LMF", ['ID', 'qty'])
    get_plot_with_fieldnames(field_names)

add_column_to_shp("qty")

#now printing
if len(argument) == 2:
    plot_type = ["Plot"]
    exclude_plot = ['Plotdiff']
    plot_name = argument[1]
elif len(argument) == 3:
    plot_type = ["Plotdiff"]
    exclude_plot = ['Plot']
    plot_name = argument[1] + "_" + argument[2]


plot_type.append("allnodes")
plot_folder = 'Plots/'

now = datetime.datetime.now()

mxd = arcpy.mapping.MapDocument(r"Rail3_plot.mxd")
df = arcpy.mapping.ListDataFrames(mxd)[0]

print arcpy.mapping.ListLayers(mxd, "", df)[0].name

for lyr in arcpy.mapping.ListLayers(mxd, "", df):
    if lyr.name in plot_type:
        lyr.visible = True
        lyr.transparency = 0
    elif lyr.name in exclude_plot:
        lyr.visible = False

arcpy.mapping.ExportToJPEG(mxd, plot_folder + plot_name +"_"+ now.strftime("%Y%m%d_%H%M") + ".jpg", "PAGE_LAYOUT", resolution=500)
del mxd

print("Completed.")






