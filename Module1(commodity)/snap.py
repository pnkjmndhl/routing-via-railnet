import pandas
import arcpy
import sys

#arguments
if sys.argv[1] in ['-h', 'help']:
    print("Usage: python codename.py update/new ")

if sys.argv[1] == "new":
    # read the new copy of csv file
    OD = pandas.read_csv(r"intermediate\OD1.csv")
    index_of_od = range(len(OD))
    fips_orr_to_node_odist_df = pandas.DataFrame({"OFIPS": [], "startRR": [], "ONODE": [], "ODIST": []})


elif sys.argv[1] == "update":
    # read the new copy of csv file
    OD = pandas.read_csv(r"intermediate\OD2.csv")
    index_of_od = OD.index[OD.ONode.isnull()]
    fips_orr_to_node_odist_df = pandas.read_csv(r"intermediate\OFIPSORR.csv")


#get the name of columns
column_list = list(OD.columns.values)
column_list =[x for x in column_list if 'Unnamed' not in x]
OD = OD[column_list]


# change the encoding to utf-8
reload(sys)
sys.setdefaultencoding('utf-8')

# overwrite files if its already present
arcpy.env.overwriteOutput = True
# arcpy.env.autoCancelling = False

# inputs from files
fips_shp = r"../GIS/standards/FIPS.shp"
node_shp = r"../GIS/allnodes.shp"
link_shp = r"../GIS/alllinks.shp"

#################work on copies####################
fips_shp1 = "C:/GIS/FIPS.shp"
node_shp1 = "C:/GIS/allnodes.shp"
link_shp1 = "C:/GIS/alllink.shp"
arcpy.CopyFeatures_management(fips_shp, fips_shp1)
arcpy.CopyFeatures_management(node_shp, node_shp1)
arcpy.CopyFeatures_management(link_shp, link_shp1)
fips_shp = fips_shp1
node_shp = node_shp1
link_shp = link_shp1

# search distance
dist = "100 Miles"

link_shpf = "linkshp"
fips_shpf = "FIPS"
node_shpf = "nodeshp"


arcpy.MakeFeatureLayer_management(link_shp, link_shpf)
arcpy.MakeFeatureLayer_management(fips_shp, fips_shpf)
arcpy.MakeFeatureLayer_management(node_shp, node_shpf)

fips_nearnodeid_dictionary = {}

# origin_fips = 40063
# origin_rr = 802
# get_nearest_onode_with_orr(40063, 802)

def get_network_rrs():
    dumm1 = [[row.getValue("RR1"), row.getValue("RR2"), row.getValue("RR3"), row.getValue("RR4"), row.getValue("RR5")]
             for row in arcpy.SearchCursor(link_shp)]
    flat_list = list(set([x for sublist in dumm1 for x in sublist]))
    flat_list.remove(0)
    return flat_list


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
    if origin_rr == 0:  # if the originRR == nan, then no need to do the selection based on the railroad
        where_clause = ""
    else:
        where_clause = "\"RR1\" = " + str(origin_rr) + " OR \"RR2\" = " + str(origin_rr) + " OR \"RR3\" = " + str(
            origin_rr) + " OR \"RR4\" = " + str(origin_rr) + " OR \"RR5\" = " + str(origin_rr) + " OR \"RR6\" = " + str(
            origin_rr) + " OR \"RR7\" = " + str(origin_rr)
    arcpy.SelectLayerByAttribute_management(link_shpf, "NEW_SELECTION", where_clause)
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


def update_nearest_node_dictionary():
    global fips_nearnodeid_dictionary
    arcpy.Near_analysis(fips_shp, node_shp, "", "NO_LOCATION", "NO_ANGLE", "GEODESIC")
    fips_to_near_fid = {row.getValue("FIPS"): row.getValue("NEAR_FID") for row in
                        arcpy.SearchCursor(fips_shp)}
    near_fid_to_node_id = {row.getValue("FID"): row.getValue("ID") for row in
                           arcpy.SearchCursor(node_shp)}
    fips_nearnodeid_dictionary = {x: near_fid_to_node_id[y] for x, y in fips_to_near_fid.iteritems()}


# OD = OD.head(10000)
update_nearest_node_dictionary()

OD['ODIST'] = 0.0

# if the startRR is not in our network, add np.nan
network_railroad_list = get_network_rrs()
OD['startRR'][~OD.startRR.isin(network_railroad_list)] = 0

for i in index_of_od:
    OD['ONode'][i], OD['ODIST'][i] = get_nearest_onode_with_orr(OD.at[i, 'OFIPS'], OD.at[i, 'startRR'])
    OD['DNode'][i] = get_nearest_node(OD.at[i, 'DFIPS'])
    print ("{0}:    OFP:{1:6.0f}    sRR:{3:3.0f}    OND:{4:6.0f}    DIST:{5:6.2f}".format(i, OD.at[i, 'OFIPS'], OD.at[i, 'DFIPS'],
                                                                      OD.at[i, 'startRR'], OD['ONode'][i],
                                                                      OD['ODIST'][i]))
    if i % 1000 == 0:
        OD[column_list].to_csv(r"intermediate\OD2.csv")
        fips_orr_to_node_odist_df[['OFIPS', 'startRR', 'ONODE', 'ODIST']].to_csv(r"intermediate\OFIPSORR.csv")
        print("Progress Saved")

OD[column_list].to_csv(r"intermediate\OD2.csv")