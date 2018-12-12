# This program reads the <filename>.csv on ./intermediate folder
# Either uses GIS near analysis to get nearest node with the specified startRR (new if create a new OFIPSORR.csv)
# Or uses the OFIPSORR.csv file on ./intermediate to vectorically snap and use GIS for remaining (uses current OFIPSORR.csv)
# and then vectorically snaps again the ones present on OFIPSORRcomm.csv {manual refined snapping)

from rail import *
import arcpy
import re
import math
import numpy as np

# change the encoding to utf-8
reload(sys)
sys.setdefaultencoding('utf-8')

count = 0

# overwrite files if its already present
arcpy.env.overwriteOutput = True

if sys.argv[2] not in ['new', 'update', '-h']:
    print sys.argv[1]
    print("Invalid Arguments")
    exit(0)
elif sys.argv[2] in ['-h', '-help']:
    print("Usage: python snap.py <filename> update/new ")
    exit(0)

OD = pandas.read_csv(r"intermediate/" + sys.argv[1] + ".csv")

# if the startRR is not in our network, add 0 (can snap to any railroad)
network_railroad_list = get_network_rrs()
OD['startRR'][~OD.startRR.isin(network_railroad_list)] = 0
OD['termiRR'][~OD.termiRR.isin(network_railroad_list)] = 0

fips_nearnodeid_dictionary = {}

# get the name of columns
column_list = list(OD.columns.values)
column_list = [x for x in column_list if 'Unnamed' not in x]
OD = OD[column_list]

fips_orr_comm_to_node_odist_df = pandas.read_csv(ofips_orr_comm)

arcpy.MakeFeatureLayer_management(link_shp, link_shpf)
arcpy.MakeFeatureLayer_management(fips_shp, fips_shpf)
arcpy.MakeFeatureLayer_management(node_shp, node_shpf)
arcpy.MakeFeatureLayer_management(county_shp, county_shpf)

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


def update_node_county_dictionary():
    # county_shp = r"../GIS/standards/tl_2017_us_county.shp"
    # node_shp = '../GIS/allnodes.shp'
    # node_shpf = "nodeshp"
    # county_shpf = "countyshp"
    # arcpy.MakeFeatureLayer_management(node_shp, node_shpf)
    # arcpy.MakeFeatureLayer_management(county_shp, county_shpf)
    arcpy.SpatialJoin_analysis(county_shpf, node_shpf, "in_memory/p3", "JOIN_ONE_TO_MANY", "KEEP_COMMON", "", "COMPLETELY_CONTAINS", "", "")
    # fieldnames = [f.name for f in arcpy.ListFields("in_memory/p3")]
    node_fid_to_fips_fid = {row.getValue("JOIN_FID"): row.getValue("TARGET_FID") for row in arcpy.SearchCursor("in_memory/p3")}
    node_fid_node_id = {row.getValue("FID"): row.getValue("ID") for row in arcpy.SearchCursor(node_shp)}
    fips_fid_to_fips_id = {row.getValue("FID"): int(row.getValue("GEOID")) for row in arcpy.SearchCursor(county_shp)}
    node_id_to_fips = {node_fid_node_id[x]: fips_fid_to_fips_id[y] for x,y in node_fid_to_fips_fid.iteritems()}
    return node_id_to_fips


def get_if_available(origin_fips, origin_rr):
    onodeofips = fips_orr_to_node_odist_df[
        (fips_orr_to_node_odist_df.FIPS == origin_fips) & (fips_orr_to_node_odist_df.RR == origin_rr)]
    if not onodeofips.empty:
        return [list(onodeofips['NODE'])[0], list(onodeofips['DIST'])[0]]
    else:
        return 0


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
        {"FIPS": origin_fips, "RR": origin_rr, "NODE": origin_node_id, "DIST": fips_to_node_id_snap_distance},
        ignore_index=True)
    global count
    count = count + 1
    if count % 10 == 0:  # every 10 calls envokes saving action
        fips_orr_to_node_odist_df[['FIPS', 'RR', 'NODE', 'DIST']].to_csv(r"intermediate\FIPSRR.csv")
        print("Saved")
    return [origin_node_id, fips_to_node_id_snap_distance]


def get_nearest_node(fips):
    return fips_nearnodeid_dictionary[fips]


def add_string(x, str_):
    if math.isnan(x):
        return np.nan
    else:
        return str_


def snap_by_commodity_rr_odfips(argument):
    global OD
    if argument == "origin":
        print("Snapping Origin...")
        odfips = "OFIPS"
        odnode = "ONode"
        stRR = "startRR"
        dist = "ODIST"
    elif argument == "destination":
        print("Snapping Destination...")
        odfips = "DFIPS"
        odnode = "DNode"
        stRR = "termiRR"
        dist= "DDIST"
    else:
        print("Invalid arguments at function snap_by_commodity_rr_odfips")
        exit(0)
    print("Manual Snapping By Railroad and Commodity.")
    to_node_odist_df = fips_orr_comm_to_node_odist_df[['FIPS', 'RR', 'comm', 'NODE']]
    to_node_odist_df[dist] = -98
    to_node_odist_df.columns = [[odfips, stRR, 'comm', odnode, dist]]
    # for both commodity and railroad given
    OD = OD.reset_index()
    OD = OD.set_index([odfips, stRR, 'comm'])
    OD.update(to_node_odist_df.set_index([odfips, stRR, 'comm'])[dist])
    OD.update(to_node_odist_df.set_index([odfips, stRR, 'comm'])[odnode])
    # for comm = 0 and startRR = 0
    OD = OD.reset_index()
    OD = OD.set_index([odfips])
    to_node_odist_df_r0_c0 = to_node_odist_df[(to_node_odist_df.comm == 0) & (to_node_odist_df[stRR] == 0)]
    OD.update(to_node_odist_df_r0_c0.set_index([odfips])[dist])
    OD.update(to_node_odist_df_r0_c0.set_index([odfips])[odnode])
    # for comm = 0
    OD = OD.reset_index()
    OD = OD.set_index([odfips, stRR])
    to_node_odist_df_c0 = to_node_odist_df[(to_node_odist_df.comm == 0)]
    OD.update(to_node_odist_df_c0.set_index([odfips, stRR])[dist])
    OD.update(to_node_odist_df_c0.set_index([odfips, stRR])[odnode])
    # for startRR = 0
    OD = OD.reset_index()
    OD = OD.set_index([odfips, 'comm'])
    to_node_odist_df_r0 = to_node_odist_df[to_node_odist_df[stRR] == 0]
    OD.update(to_node_odist_df_r0.set_index([odfips, 'comm'])[dist])
    OD.update(to_node_odist_df_r0.set_index([odfips, 'comm'])[odnode])
    OD = OD.reset_index()
    print("Completed. :)")


def snap_by_rr():
    # for Origin using startRR
    OD['ONode'] = \
    pandas.merge(OD, fips_orr_to_node_odist_df, how='left', left_on=['OFIPS', 'startRR'], right_on=['FIPS', "RR"])[
        'NODE']
    OD['ODIST'] = \
    pandas.merge(OD, fips_orr_to_node_odist_df, how='left', left_on=['OFIPS', 'startRR'], right_on=['FIPS', "RR"])[
        'DIST']
    # for Destination using TermiRR
    OD['DNode'] = \
    pandas.merge(OD, fips_orr_to_node_odist_df, how='left', left_on=['DFIPS', 'termiRR'], right_on=['FIPS', "RR"])[
        'NODE']
    OD['DDIST'] = \
    pandas.merge(OD, fips_orr_to_node_odist_df, how='left', left_on=['DFIPS', 'termiRR'], right_on=['FIPS', "RR"])[
        'DIST']

    # OD['DNode'] = OD.DFIPS.map(fips_nearnodeid_dictionary)


def snap_nearest_if_not_in_same_county_or_within_a_distance(argument):
    print("Snapping to nearest for " + argument + " railroad not found in the county")
    global OD
    #fips_nearnodeid_dictionary
    #change values here
    if argument == "origin":
        odfips = "OFIPS"
        odnode = "ONode"
        odnode1 = "ONode1"
        dist = "ODIST"
        odcounty = "ocounty"
    elif argument == "destination":
        odfips = "DFIPS"
        odnode = "DNode"
        odnode1 = "DNode1"
        dist = "DDIST"
        odcounty = "dcounty"
    else:
        print("Invalid arguments at function snap_nearest_if_not_in_same_county")
        exit(0)

    OD[odcounty] = OD[odnode].map(node_county_dict)
    OD[odnode1] = OD[(OD[odcounty] != OD[odfips]) & (dist > snap_dist_threshhold)][odfips].map(fips_nearnodeid_dictionary)
    OD[odnode].update(OD[odnode1])
    OD.loc[(OD[odcounty] != OD[odfips]) & (dist > snap_dist_threshhold) ,dist] = -99




# main program starts here
# calculate D-node here

# OD['ODIST'] = ""
fips_nearnodeid_dictionary = update_nearest_node_dictionary()
node_county_dict = update_node_county_dictionary()

if sys.argv[2] == "new":
    # read the new copy of csv file
    index_of_od = range(len(OD))
    fips_orr_to_node_odist_df = pandas.DataFrame({"FIPS": [], "RR": [], "NODE": [], "DIST": []})

elif sys.argv[2] == "update":
    # read the FIPS to Node conversion csv file
    fips_orr_to_node_odist_df = pandas.read_csv(r"intermediate\FIPSRR.csv")
    snap_by_rr()  # dictionary snapping
    index_of_od = OD.index[OD.ONode.isnull() | OD.DNode.isnull()]

# snap OFIPS to nearest ONODE that has startRR
# snap DFIPS to nearest DNODE
for i in index_of_od:
    OD['ONode'][i], OD['ODIST'][i] = get_nearest_onode_with_orr(OD.at[i, 'OFIPS'], OD.at[i, 'startRR'])

    print ("{0}:    OFP:{1:6.0f}    sRR:{3:3.0f}    OND:{4:6.0f}    DIST:{5:6.2f}".format(i, OD.at[i, 'OFIPS'],
                                                                                          OD.at[i, 'DFIPS'],
                                                                                          OD.at[i, 'startRR'],
                                                                                          OD['ONode'][i],
                                                                                          OD['ODIST'][i]))
    # OD['DNode'][i] = get_nearest_node(OD.at[i, 'OFIPS'])
    OD['DNode'][i], OD['DDIST'][i] = get_nearest_onode_with_orr(OD.at[i, 'DFIPS'], OD.at[i, 'termiRR'])

    print ("{0}:    DFP:{1:6.0f}    tRR:{3:3.0f}    DND:{4:6.0f}    DIST:{5:6.2f}".format(i, OD.at[i, 'DFIPS'],
                                                                                          OD.at[i, 'DFIPS'],
                                                                                          OD.at[i, 'termiRR'],
                                                                                          OD['DNode'][i],
                                                                                          OD['DDIST'][i]))

#if the OFIPS and ONODE or DFIPS and DNODE are not in the same county:
snap_nearest_if_not_in_same_county_or_within_a_distance("origin")
snap_nearest_if_not_in_same_county_or_within_a_distance("destination")

# after all the dictionary snappings and GIS snappings have occured, do the OFIPSorrcomm snappings
snap_by_commodity_rr_odfips("origin")
snap_by_commodity_rr_odfips("destination")

fips_orr_to_node_odist_df = fips_orr_to_node_odist_df.drop_duplicates()
fips_orr_to_node_odist_df[['FIPS', 'RR', 'NODE', 'DIST']].to_csv(r"intermediate\FIPSRR.csv")

OD[column_list].to_csv(r"intermediate/" + sys.argv[1] + "_1.csv")
