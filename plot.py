# plots the LMF file to jpg

import pandas as pd
import arcpy
import sys
import os


#default values
plot_folder = 'Plots/'
folder_in_LMF = "" # finds the LMFs in Netdata


# This program plots the output commodity.lmf file to plot.shp
switch = sys.argv[1]

if switch == '-d':
    base = sys.argv[2]
    scenarios = sys.argv[3:]
    plot_type = "Plotdiff"

elif switch == '-p':
    bases = sys.argv[2:]
    plot_type = "Plot"

elif switch in ['-df', '-fd']:
    folder_in_LMF = sys.argv[2]
    base = sys.argv[3]
    #all files in the folder except base are scenarios
    lmfs = os.listdir("./netdata/LMF/" + folder_in_LMF)
    lmfs = [x.split('.')[0] for x in lmfs if base not in x]
    scenarios = lmfs
    plot_folder = 'Plots/' + folder_in_LMF

elif switch in ['-pf', '-fp']:
    folder_in_LMF = sys.argv[2]
    lmfs = os.listdir("./netdata/LMF/" + folder_in_LMF)
    lmfs = [x.split('.')[0] for x in lmfs]
    #print lmfs
    #all the lmf files in the folder are bases
    bases = lmfs
    plot_folder = 'Plots/' + folder_in_LMF

else:
    print ("Invalid arguments")
    print ("Usage: python plot.py [-d|-p] [list of LMFs]")
    print ("Usage: python plot.py [-df|-fd] [foldername] [basename] [list of LMFs]")
    print ("Usage: python plot.py [-pf|-fp] [foldername] [list of LMFs]")
    exit(0)

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


def export_to_jpeg(plot_type, exclude_plot, plot_path):
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
    arcpy.mapping.ExportToJPEG(mxd, plot_path +"_"+ now.strftime("%Y%m%d_%H%M") + ".jpg", "PAGE_LAYOUT", resolution=800)
    del mxd
    print ("Completed")



# main program
link_shp = 'gis/alllinks.shp'
field_names = get_field_names(link_shp)  # getting field names
field_names = [e for e in field_names if e not in ["ID", "FID", "Shape"]]

if switch in ['-d', '-df', '-fd']: #scenario plots
    print("Generating Difference plot ...")
    plot = 'gis/plots/Plotdiff.shp'
    file_1 = "Netdata/LMF/" + folder_in_LMF + "/" + base
    file_1 = file_1.replace("//", "/")  # if folder_in_LMF is empty, the // will be replaced by /
    for scenario in scenarios:
        print ("working on: " + base + "," + scenario)
        file_2 = "Netdata/LMF/"+ folder_in_LMF + "/" + scenario
        file_2 = file_2.replace("//", "/")
        flow_1 = split_to_dataframe(file_1 + ".LMF", ['ID', 'qty'])
        flow_2 = split_to_dataframe(file_2 + ".LMF", ['ID', 'qty'])
        flow = flow_1  # flow1 is always the base flow
        get_plot_with_fieldnames(field_names)
        flow['qty'] = flow_2['qty'] - flow_1['qty']
        add_column_to_shp("qty")
        plot_type = ["Plotdiff",'allnodes']
        exclude_plot = ['Plot']
        plot_name = base + "_" + scenario
        plot_path = 'plots/' + folder_in_LMF + "/" + plot_name
        if folder_in_LMF != "":
            os.system("Mkdir plots\\"+folder_in_LMF)
        print plot_path
        export_to_jpeg(plot_type, exclude_plot, plot_path)

if switch in ['-f', '-pf', '-fp']: #base plots
    print("Generating normal plot ...")
    plot = 'gis/plots/Plot.shp'
    for base in bases:
        print ("working on: " + base)
        file_name = "Netdata/LMF/"+ folder_in_LMF + "/" + base
        flow = split_to_dataframe(file_name + ".LMF", ['ID', 'qty'])
        get_plot_with_fieldnames(field_names)
        add_column_to_shp("qty")
        plot_type = ['Plot','allnodes']
        exclude_plot = ['Plotdiff']
        plot_name = base
        plot_path = 'plots/' + folder_in_LMF + "/" + plot_name
        if folder_in_LMF != "":
            os.system("Mkdir plots\\"+folder_in_LMF)
        print plot_path
        export_to_jpeg(plot_type, exclude_plot, plot_path)
