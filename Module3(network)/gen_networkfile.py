import pandas
import arcpy
import sys
from simpledbf import Dbf5

# whenever the attributes of any link is changed, its other attributes changes accordingly. This program makes sure that
# all those changes are reflected in the other columns TTIME, P1, P2, GAMMA, CAPACITY and NO_RRS

# Set the workspace environment to local file geodatabase
arcpy.env.workspace = r"C:/GIS"
arcpy.env.overwriteOutput = True

# shape files
link_shp = r'..\GIS\alllinks.shp'
# link_shp = r'..\GIS\test_alllinks.shp'
node_shp = r'..\GIS\allnodes.shp'

# excel files
to_constants = r"input\COEFFS.XLS"
exception_xl = r"input\networkexc.xlsx"

# colnames and format and other lists
integer_list = ['ID', 'A_NODE', 'B_NODE', 'ML_CLASS', 'LINK_TYPE', 'NO_RRS', 'RR1', 'RR2', 'RR3', 'RR4', 'RR5', 'RR6',
                'RR7', 'RR8']
all_list = ['ID', 'A_NODE', 'B_NODE', 'LENGTH', 'TTIME', 'CAPACITY', 'P1', 'P2', 'GAMMA', 'TADJ', 'ML_CLASS',
            'LINK_TYPE', 'NO_RRS', 'RR1', 'RR2', 'RR3', 'RR4', 'RR5', 'RR6', 'RR7', 'RR8']
format_list = ['{:5d}', '{:5d}', '{:5d}', '{:6.1f}', '{:6.2f}', '{:6.1f}', '{:10.6f}', '{:10.6f}', '{:6.2f}', '{:6.2f}',
               '{:1d}', '{:1d}', '{:1d}', '{:3d}', '{:3d}', '{:3d}', '{:3d}', '{:3d}', '{:3d}', '{:3d}', '{:3d}']
RRs = ['RR1', 'RR2', 'RR3', 'RR4', 'RR5', 'RR6', 'RR7', 'RR8', 'RR9']

# network exception file forces to changes some specific attributes of the network

# main program
# read from excel and shp files
signal_capacity_to_constants = pandas.ExcelFile(to_constants).parse("Sheet2")
network_df = Dbf5(link_shp.split(".shp")[0] + ".dbf").to_dataframe()

# calculate columns
columns_network = list(network_df.columns.values)
RRs_not_present = [x for x in RRs if x not in columns_network]
for RR in RRs_not_present:
    network_df[RR]=0
network_df['DIR'] = 0
network_df['NO_RRS'] = (network_df[RRs] != 0).astype(int).sum(axis=1)
network_df['TTIME'] = network_df['LENGTH'] / network_df['FF_SPEED'] * 60  # travel time in minutes (FFS)
network_df['TADJ'] = 0

# COEFFS.XLS has the default values of the columns for all values of SIGNAL and CAPY_CODE
signal_capacity_to_constants.columns = [['trackclass', 'SIGNAL', 'CAPY_CODE', 'to', 'P1', 'P2', 'GAMMA', 'CAPACITY', 'miles']]
network_df = pandas.merge(network_df, signal_capacity_to_constants, how='left', left_on=['SIGNAL', 'CAPY_CODE'],
                          right_on=['SIGNAL', 'CAPY_CODE'])

network_df = network_df[all_list]

# changing linkIDS
network_df.to_csv(r"intermediate\network.csv")

dictionary_of_column_name_and_format = dict(zip(all_list, format_list))

for column_name in integer_list:
    network_df[column_name] = network_df[column_name].astype(int)
for column_name, formatting in dictionary_of_column_name_and_format.iteritems():
    network_df[column_name] = network_df[column_name].map(formatting.format)

network_df['new'] = network_df.apply(''.join, axis=1)
network_df = network_df['new']
network_df.to_csv(r"output\network.dat", index=False)
