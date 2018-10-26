from rail import *
import arcpy
import re
import math
import numpy as np

# change the encoding to utf-8
reload(sys)
sys.setdefaultencoding('utf-8')

# overwrite files if its already present
arcpy.env.overwriteOutput = True

if sys.argv[2] not in ['new', 'update', '-h']:
    print sys.argv[1]
    print("Invalid Arguments")
    exit(0)
elif sys.argv[2] in ['-h', '-help']:
    print("Usage: python snap.py filename update/new ")
    exit(0)

OD = pandas.read_csv(r"intermediate/" + sys.argv[1] + ".csv")

# if the startRR is not in our network, add 0 (can snap to any railroad)
network_railroad_list = get_network_rrs()
OD['startRR'][~OD.startRR.isin(network_railroad_list)] = 0

fips_nearnodeid_dictionary = {}

# get the name of columns
column_list = list(OD.columns.values)
column_list = [x for x in column_list if 'Unnamed' not in x]
OD = OD[column_list]

#################  work on copies  ####################
# fips_shp1 = "C:/GIS/FIPS.shp"
# node_shp1 = "C:/GIS/allnodes.shp"
# link_shp1 = "C:/GIS/alllink.shp"
# arcpy.CopyFeatures_management(fips_shp, fips_shp1)
# arcpy.CopyFeatures_management(node_shp, node_shp1)
# arcpy.CopyFeatures_management(link_shp, link_shp1)
# fips_shp = fips_shp1
# node_shp = node_shp1
# link_shp = link_shp1



fips_orr_comm_to_node_odist_df = pandas.read_csv(ofips_orr_comm)

arcpy.MakeFeatureLayer_management(link_shp, link_shpf)
arcpy.MakeFeatureLayer_management(fips_shp, fips_shpf)
arcpy.MakeFeatureLayer_management(node_shp, node_shpf)

all_field_names = [x.name for x in arcpy.ListFields(link_shp)]
rr_field_names = [x for x in all_field_names if re.match(r'RR\d', x)]


def get_where_clause(rr):
    where_clause = ""
    if rr == 0:
        return ""
    for rrs in rr_field_names:
        where_clause = where_clause + "\"" + rrs + "\"= " + str(rr) + " OR "
    where_clause = where_clause[:-4]
    return where_clause


def update_nearest_node_dictionary():
    arcpy.Near_analysis(fips_shp, node_shp, "", "NO_LOCATION", "NO_ANGLE", "GEODESIC")
    fips_to_near_fid = {row.getValue("FIPS"): row.getValue("NEAR_FID") for row in
                        arcpy.SearchCursor(fips_shp)}
    near_fid_to_node_id = {row.getValue("FID"): row.getValue("ID") for row in
                           arcpy.SearchCursor(node_shp)}
    fips_nearnodeid_dictionary = {x: near_fid_to_node_id[y] for x, y in fips_to_near_fid.iteritems()}
    return fips_nearnodeid_dictionary


# origin_fips = 40063
# origin_rr = 802
# get_nearest_onode_with_orr(40063, 802)

def get_if_available(origin_fips, origin_rr):
    onodeofips = fips_orr_to_node_odist_df[
        (fips_orr_to_node_odist_df.OFIPS == origin_fips) & (fips_orr_to_node_odist_df.startRR == origin_rr)]
    if not onodeofips.empty:
        return [list(onodeofips['ONODE'])[0], list(onodeofips['ODIST'])[0]]
    else:
        return 0


# origin_fips = 26147
# origin_rr = 103
# get_nearest_onode_with_orr(17091, 103)
def get_nearest_onode_with_orr(origin_fips, origin_rr):
    global fips_orr_to_node_odist_df
    # if present in dataframe, return
    yes_or_no = get_if_available(origin_fips, origin_rr)
    if yes_or_no != 0:
        return yes_or_no
    arcpy.SelectLayerByAttribute_management(link_shpf, "NEW_SELECTION", get_where_clause(origin_rr))
    arcpy.FeatureVerticesToPoints_management(link_shpf, "in_memory/p1", "BOTH_ENDS")
    arcpy.MakeFeatureLayer_management("in_memory/p1", "p1")
    arcpy.SelectLayerByAttribute_management(fips_shpf, "NEW_SELECTION",
                                            """ "FIPS" = %d""" % origin_fips)  # select the FIPS
    arcpy.Near_analysis(fips_shpf, "p1", "", "NO_LOCATION", "NO_ANGLE", "GEODESIC")
    dumm = {row.getValue("NEAR_FID"): row.getValue("NEAR_DIST") for row in
            arcpy.SearchCursor(fips_shpf)}  # gets the FID of th nearest Node
    arcpy.SelectLayerByAttribute_management("p1", "NEW_SELECTION", """ "FID" = %d""" % dumm.keys()[0])
    arcpy.SpatialJoin_analysis("p1", node_shpf, "in_memory/p2", "", "", "", "CLOSEST", "", "")
    # ID for nodes gets changed to ID_1 automatically
    origin_node_id = [row.getValue("ID_1") for row in arcpy.SearchCursor("in_memory/p2")][0]
    fips_to_node_id_snap_distance = dumm.values()[0] / 1609.34  # converting meters to miles
    fips_orr_to_node_odist_df = fips_orr_to_node_odist_df.append(
        {"OFIPS": origin_fips, "startRR": origin_rr, "ONODE": origin_node_id, "ODIST": fips_to_node_id_snap_distance},
        ignore_index=True)
    return [origin_node_id, fips_to_node_id_snap_distance]


def get_nearest_node(fips):
    return fips_nearnodeid_dictionary[fips]


def add_string(x, str_):
    if math.isnan(x):
        return np.nan
    else:
        return str_


def snap_by_commodity_rr_ofips():
    global OD
    print("Manual Snapping By Railroad and Commodity.")
    to_node_odist_df = fips_orr_comm_to_node_odist_df[['FIPS', 'startRR', 'comm', 'NODE']]
    to_node_odist_df.columns = [['OFIPS', 'startRR', 'comm', 'ONode']]
    # for both commodity and railroad given
    OD = OD.reset_index()
    OD = OD.set_index(['OFIPS', 'startRR', 'comm'])
    OD.update(to_node_odist_df.set_index(['OFIPS', 'startRR', 'comm'])['ONode'])
    # for comm = 0 and startRR = 0
    OD = OD.reset_index()
    OD = OD.set_index(['OFIPS'])
    to_node_odist_df_r0_c0 = to_node_odist_df[(to_node_odist_df.comm == 0) & (to_node_odist_df.startRR == 0)]
    OD.update(to_node_odist_df_r0_c0.set_index(['OFIPS'])['ONode'])
    # for comm = 0
    OD = OD.reset_index()
    OD = OD.set_index(['OFIPS','startRR'])
    to_node_odist_df_c0 = to_node_odist_df[(to_node_odist_df.comm == 0)]
    OD.update(to_node_odist_df_c0.set_index(['OFIPS','startRR'])['ONode'])
    # for startRR = 0
    OD = OD.reset_index()
    OD = OD.set_index(['OFIPS','comm'])
    to_node_odist_df_r0 = to_node_odist_df[to_node_odist_df.startRR == 0]
    OD.update(to_node_odist_df_r0.set_index(['OFIPS','comm'])['ONode'])
    OD = OD.reset_index()
    print("Completed. :)")

def snap_by_commodity_rr_dfips():
    global OD
    print("Manual Snapping By Railroad and Commodity.")
    to_node_odist_df = fips_orr_comm_to_node_odist_df[['FIPS', 'startRR', 'comm', 'NODE']]
    to_node_odist_df.columns = [['DFIPS', 'startRR', 'comm', 'DNode']]
    # for both commodity and railroad given
    OD = OD.reset_index()
    OD = OD.set_index(['DFIPS', 'startRR', 'comm'])
    OD.update(to_node_odist_df.set_index(['DFIPS', 'startRR', 'comm'])['DNode'])
    # for comm = 0 and startRR = 0
    OD = OD.reset_index()
    OD = OD.set_index(['DFIPS'])
    to_node_odist_df_r0_c0 = to_node_odist_df[(to_node_odist_df.comm == 0) & (to_node_odist_df.startRR == 0)]
    OD.update(to_node_odist_df_r0_c0.set_index(['DFIPS'])['DNode'])
    # for comm = 0
    OD = OD.reset_index()
    OD = OD.set_index(['DFIPS','startRR'])
    to_node_odist_df_c0 = to_node_odist_df[(to_node_odist_df.comm == 0)]
    OD.update(to_node_odist_df_c0.set_index(['DFIPS','startRR'])['DNode'])
    # for startRR = 0
    OD = OD.reset_index()
    OD = OD.set_index(['DFIPS','comm'])
    to_node_odist_df_r0 = to_node_odist_df[to_node_odist_df.startRR == 0]
    OD.update(to_node_odist_df_r0.set_index(['DFIPS','comm'])['DNode'])
    OD = OD.reset_index()
    print("Completed. :)")


def snap_by_rr():
    OD['ONode'] = pandas.merge(OD, fips_orr_to_node_odist_df, how='left', on=['OFIPS', 'startRR'])['ONODE']
    OD['ODIST'] = pandas.merge(OD, fips_orr_to_node_odist_df, how='left', on=['OFIPS', 'startRR'])['ODIST_y']
    OD['DNode'] = OD.DFIPS.map(fips_nearnodeid_dictionary)


# main program starts here
# calculate D-node here

# OD['ODIST'] = ""
fips_nearnodeid_dictionary = update_nearest_node_dictionary()

if sys.argv[2] == "new":
    # read the new copy of csv file
    index_of_od = range(len(OD))
    fips_orr_to_node_odist_df = pandas.DataFrame({"OFIPS": [], "startRR": [], "ONODE": [], "ODIST": []})

elif sys.argv[2] == "update":
    # read the FIPS to Node conversion csv file
    fips_orr_to_node_odist_df = pandas.read_csv(r"intermediate\OFIPSORR.csv")
    snap_by_rr()
    index_of_od = OD.index[OD.ONode.isnull()]

#  work only for ONode here ...
for i in index_of_od:
    OD['ONode'][i], OD['ODIST'][i] = get_nearest_onode_with_orr(OD.at[i, 'OFIPS'], OD.at[i, 'startRR'])

    print ("{0}:    OFP:{1:6.0f}    sRR:{3:3.0f}    OND:{4:6.0f}    DIST:{5:6.2f}".format(i, OD.at[i, 'OFIPS'],
                                                                                          OD.at[i, 'DFIPS'],
                                                                                          OD.at[i, 'startRR'],
                                                                                          OD['ONode'][i],
                                                                                          OD['ODIST'][i]))

# after all the dictionary snappings and GIS snappings have occured, do the OFIPSorrcomm snappings
snap_by_commodity_rr_ofips()
snap_by_commodity_rr_dfips()

fips_orr_to_node_odist_df = fips_orr_to_node_odist_df.drop_duplicates()
fips_orr_to_node_odist_df[['OFIPS', 'startRR', 'ONODE', 'ODIST']].to_csv(r"intermediate\OFIPSORR.csv")
OD[column_list].to_csv(r"intermediate/" + sys.argv[1] + "_1.csv")
