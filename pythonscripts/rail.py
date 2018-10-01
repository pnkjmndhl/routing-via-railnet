import arcpy
import pandas
import sys

path_of_rail = "C:/Users/pankaj/Desktop/RAIL/"


link_shp = path_of_rail + 'GIS/alllinks.shp'
node_shp = path_of_rail + 'GIS/allnodes.shp'

link_shp_feature = "linkshp"
node_shp_feature = "nodeshp"

state_shp = path_of_rail + "/GIS/standards/tl_2017_us_states.shp"

memory_shp = "in_memory/dumm"
disk_shp = "C:/GIS/dumm.shp"


commodity_filename = path_of_rail + "Module1(commodity)/input/base/NEWFLOW3.xlsx"
commodity_sheetname = "Sheet1"
orra_to_orr = path_of_rail + "/Module4(Transfers)/input/allAARCode.csv"

arcpy.env.overwriteOutput = True  # overwrite files if already present

print ("Variables imported..")


if __name__ == "__main__":
    print ("This program is supposed to be used as a module")