import arcpy
import pandas
import sys


link_shp = '../GIS/alllinks.shp'
node_shp = '../GIS/allnodes.shp'

link_shp_feature = "linkshp"
node_shp_feature = "nodeshp"

state_shp = "../GIS/standards/tl_2017_us_states.shp"

memory_shp = "in_memory/dumm"
disk_shp = "C:/GIS/dumm.shp"

orra_to_orr = "../transfers/input/allAARCode.csv"

arcpy.env.overwriteOutput = True  # overwrite files if already present

print ("Variables imported..")

if __name__ == "__main__":
    print ("This program is supposed to be used as a module")