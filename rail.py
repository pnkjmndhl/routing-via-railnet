from importlib import import_module
import pandas
import sys

#tolerances
odist_tolerance = 100 #miles (greater than this distance will be removed from the OD file)
snap_dist_threshhold = 50 # miles (if they are snapped more than this distance, then they will be snapped to nearest)


# parameters
commodity_adder = 50  # for empty
no_of_commodity = 12


#shapefiles
link_shp = '../GIS/alllinks.shp'
node_shp = '../GIS/allnodes.shp'
fips_shp = r"../GIS/standards/FIPS.shp"
manual_snap_lines_shp = '../GIS/manual_snap_lines.shp'
county_shp = r"../GIS/standards/tl_2017_us_county.shp"
transfer_manual_shp = r"../GIS/manualtransfers.shp"
transfer_shp = r"../GIS/transfers.shp"
transfer_shp_snapped = r"../GIS/transfers_snapped.shp"
transfer_xl_shp = r"../GIS/transfers_xl.shp"
state_shp = "../GIS/standards/tl_2017_us_states.shp"
transfer_exception_shp = '../GIS/transfer_exceptions.shp'
link_exception_shp = '../GIS/link_exception.shp'
base_flows_shp = '../GIS/base_flows.shp'
ofips_orr_comm = r"../commodity/intermediate/OFIPSORRcomm.csv"

#other temporary files
memory_shp = "in_memory/dumm"
disk_shp = "C:/GIS/dumm.shp"
csv = "C:/GIS/temp/temp.csv"


#xls and csv files
orra_to_orr = "../transfers/input/allAARCode.csv"
signal_capacity_to_constants = r"../network/input/COEFFS.XLS"
cost_xl = r'../cost/input/COST_PARMS_10_2018(B).xlsx'
cost_xl_sheet = "COSTS_8_2018"


#dat files
cost_dat = r'..\cost\output\cost.dat'


def get_network_rrs(link_shp_ = link_shp):
    arcpy = import_module('arcpy')
    dumm1 = [[row.getValue("RR1"), row.getValue("RR2"), row.getValue("RR3"), row.getValue("RR4"), row.getValue("RR5"), row.getValue("RR6"), row.getValue("RR7")]
             for row in arcpy.SearchCursor(link_shp_)]
    flat_list = list(set([x for sublist in dumm1 for x in sublist]))
    flat_list.remove(0)
    return flat_list

# search distance for
#dist = "100 Miles"

# arcpy feature files
link_shpf = "linkshp"
fips_shpf = "FIPS"
node_shpf = "nodeshp"
county_shpf = "countyshp"

# functions
if __name__ == "__main__":
    print ("This program is supposed to be used as a module")
