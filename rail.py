from importlib import import_module
import pandas
import sys

link_shp = '../GIS/alllinks.shp'
node_shp = '../GIS/allnodes.shp'
fips_shp = r"../GIS/standards/FIPS.shp"



state_shp = "../GIS/standards/tl_2017_us_states.shp"

memory_shp = "in_memory/dumm"
disk_shp = "C:/GIS/dumm.shp"

orra_to_orr = "../transfers/input/allAARCode.csv"
signal_capacity_to_constants = r"../network/input/COEFFS.XLS"

cost_dat = r'..\cost\output\cost.dat'
cost_xl = r'input\COST_PARMS_8_2018.xlsx'
cost_xl_sheet = "COSTS_8_2018"

def get_network_rrs():
    arcpy = import_module('arcpy')
    dumm1 = [[row.getValue("RR1"), row.getValue("RR2"), row.getValue("RR3"), row.getValue("RR4"), row.getValue("RR5"), row.getValue("RR6"), row.getValue("RR7")]
             for row in arcpy.SearchCursor(link_shp)]
    flat_list = list(set([x for sublist in dumm1 for x in sublist]))
    flat_list.remove(0)
    return flat_list


# search distance for
#dist = "100 Miles"

# arcpy feature files
link_shpf = "linkshp"
fips_shpf = "FIPS"
node_shpf = "nodeshp"
link_shp_feature = "linkshp"
node_shp_feature = "nodeshp"



print ("rail imported")


# functions



if __name__ == "__main__":
    print ("This program is supposed to be used as a module")
