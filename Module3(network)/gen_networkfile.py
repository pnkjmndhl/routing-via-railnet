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
network_shp = r'..\GIS\alllinks.shp'
#network_shp = r'..\GIS\test_alllinks.shp'
node_shp = r'..\GIS\allnodes.shp'

# excel files
to_constants = r"input\COEFFS.XLS"
exception_xl = r"input\networkexc.xlsx"

# colnames and format and other lists
integer_list = ['ID', 'A_NODE', 'B_NODE', 'ML_CLASS', 'LINK_TYPE', 'NO_RRS', 'RR1', 'RR2', 'RR3', 'RR4', 'RR5', 'RR6',
                'RR7',
                'RR8']
all_list = ['ID', 'A_NODE', 'B_NODE', 'LENGTH', 'TTIME', 'CAPACITY', 'P1', 'P2', 'GAMMA', 'TADJ', 'ML_CLASS',
            'LINK_TYPE', 'NO_RRS', 'RR1', 'RR2', 'RR3', 'RR4', 'RR5', 'RR6', 'RR7', 'RR8']
format_list = ['{:5d}', '{:5d}', '{:5d}', '{:6.1f}', '{:6.2f}', '{:6.1f}', '{:10.6f}', '{:10.6f}', '{:6.2f}', '{:6.2f}',
               '{:1d}', '{:1d}', '{:1d}', '{:3d}', '{:3d}', '{:3d}', '{:3d}', '{:3d}', '{:3d}', '{:3d}', '{:3d}']
RRs = ['RR1', 'RR2', 'RR3', 'RR4', 'RR5', 'RR6', 'RR7', 'RR8', 'RR9']


# network exception file forces to changes some specific attributes of the network
# this feature was used to reduce the capacity on line to make the flow through memphis correct.
def overwrite_exceptions_from_xl(attribute_name):
    attribute = exceptions_df.parse(attribute_name)
    for i in range(len(attribute['ID'])):
        network_df[attribute_name][network_df.ID == attribute['ID'][i]] = attribute[attribute_name][i]


# main program
# read from excel and shp files
exceptions_df = pandas.ExcelFile(exception_xl)
to_constants_df = pandas.ExcelFile(to_constants).parse("Sheet2")
network_df = Dbf5(network_shp.split(".shp")[0] + ".dbf").to_dataframe()

# calculate columns
network_df['DIR'] = 0
network_df['RR8'] = 0
network_df['RR9'] = 0
network_df['NO_RRS'] = (network_df[RRs] != 0).astype(int).sum(axis=1)
network_df['TTIME'] = network_df['LENGTH'] / network_df['FF_SPEED'] * 60  # travel time in minutes (FFS)
network_df['TADJ'] = 0

# COEFFS.XLS has the default values of the columns for all values of SIGNAL and CAPY_CODE
to_constants_df.columns = [['trackclass', 'SIGNAL', 'CAPY_CODE', 'to', 'P1', 'P2', 'GAMMA', 'CAPACITY', 'miles']]
to_constants_df['Vlookup'] = to_constants_df['SIGNAL'].astype(str) + to_constants_df['CAPY_CODE'].astype(str)
network_df['Vlookup'] = network_df['SIGNAL'].astype(str) + network_df['CAPY_CODE'].astype(str)
network_df = pandas.merge(network_df, to_constants_df, how='left', left_on='Vlookup', right_on='Vlookup')

# overwrite capacity from networkexc.xlsx
for sheet_names in exceptions_df.sheet_names:
    overwrite_exceptions_from_xl(sheet_names)

network_df = network_df[all_list]

# changing linkIDS
# network.ID = range(1000, len(network)+1000)
network_df.to_csv(r"intermediate\network.csv")

dictionary_of_column_name_and_format = dict(zip(all_list, format_list))

for column_name in integer_list:
    network_df[column_name] = network_df[column_name].astype(int)
for column_name, formatting in dictionary_of_column_name_and_format.iteritems():
    network_df[column_name] = network_df[column_name].map(formatting.format)

network_df['new'] = network_df.apply(''.join, axis=1)
network_df = network_df['new']
network_df.to_csv(r"output\network.dat", index=False)
