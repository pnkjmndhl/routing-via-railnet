from importlib import import_module
import pandas
import sys




#tolerances
odist_tolerance = 100 #miles (greater than this distance will be removed from the OD file)
snap_dist_threshhold = 50 # miles (if they are snapped more than this distance, then they will be snapped to nearest)


#COMMODITY
base_folder_path = r'../input/base/'
scenario_folder_path = r'../input/scenario/'
fips_to_rr_csv = r'../input/FIPSRR.csv'

# parameters
commodity_adder = 50  # for empty
no_of_commodity = 12

#COST
add_for_emptys = 50
# add railroads are not in the cost file (short-line 6 AA, is used as a sample for all unknown values)
default_copy_railroad = 6

#default cost values for emptys
empty_traincostphr = 520.93
empty_costpgrosstonmie = 0.055
empty_terminalprocessingcostpcar = 96.67
empty_terminalcostpcarhr =  1.14
empty_transfercostphr = 157.92 #not that transfer multiplier is used on top of this

#TRANSFER
transfer_multiplier = 6
# inputs/output files
transfer_xl_file = r'../input/INTERCHANG_G3O.xlsx'
all_aar_csv = r'../input/allAARCode.csv'


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
ofips_orr_comm = r"../input/OFIPSORRcomm.csv"

#other temporary files
memory_shp = "in_memory/dumm"
disk_shp = "C:/GIS/dumm.shp"
csv = "C:/GIS/temp/temp.csv"


#xls and csv files
signal_capacity_to_constants = r"../input/COEFFS.XLS"
cost_xl = r'../input/COST_PARMS_10_2018(B).xlsx'
cost_xl_sheet = "COSTS_8_2018"


#output files
cost_dat = r'../output/cost.dat'
transfer_xfr_output = r'../output/network.xfr'
network_dat_output = r"../output/network.dat"
base_flows_output = r"../output/volume.lvl"
link_exc_output = "../output/link.exc"
transfer_exc_output = "../output/transfer.exc"
cost_dat_output = r"../output/cost" + str(int(transfer_multiplier)) + ".dat"


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
