#PROGRAM: convert SPLC fid to nodeid
from rail import *
import arcpy
import re
import math
import numpy as np
import random

# overwrite files if its already present
arcpy.env.overwriteOutput = True

# if the startRR is not in our network, add 0 (can snap to any railroad)
network_railroad_list = get_network_rrs()

splc_fid_to_node_id_dict = {}

arcpy.MakeFeatureLayer_management(splc_shp, splc_shpf)
arcpy.MakeFeatureLayer_management(link_shp, link_shpf)
arcpy.MakeFeatureLayer_management(node_shp, node_shpf)


def check_if_in_network(rr):
    if rr in network_railroad_list:
        return rr
    else:
        return 0


# get where clause from RR to select the links where any of the RR# = rr
def get_where_clause(rr):
    where_clause = ""
    if rr == 0:
        return ""
    for rrs in rr_field_names:
        where_clause = where_clause + "\"" + rrs + "\"= " + str(rr) + " OR "
    where_clause = where_clause[:-4]  # removing ' OR ' from last
    return where_clause


def get_int_of(string_value):
    try:
        a = int(string_value)
    except:
        a = 0
    return a


def get_geoid(a, b):
    try:
        a = int(a)
        b = int(b)
    except:
        a = 0
        b = 0
    return a * 1000 + b


print ("Programs started")

# get countyFIPS in nodes
arcpy.SpatialJoin_analysis(node_shp, county_shp, disk_shp, "JOIN_ONE_TO_ONE", match_option="COMPLETELY_WITHIN")
arcpy.AddField_management(disk_shp, "geoid2", "SHORT")
arcpy.CalculateField_management(disk_shp, "geoid2", 'int(!STATEFP!)*1000+int(!COUNTYFP!)', "PYTHON")

arcpy.MakeFeatureLayer_management(disk_shp, disk_shpf)

count = -1
with arcpy.da.SearchCursor(splc_shp, ["FID", "RR", "SPLC", "STATEFP", "COUNTYFP"]) as cursor:
    for row in cursor:
        count = count + 1
        fid = row[0]
        origin_rr = check_if_in_network(row[1])
        splc = row[2]
        geoid = get_geoid(row[3], row[4])
        if geoid == 0:
            continue
        where_clause = """ "FID" = %d""" % fid
        arcpy.SelectLayerByAttribute_management(splc_shpf, "NEW_SELECTION", where_clause)
        arcpy.SelectLayerByAttribute_management(link_shpf, "NEW_SELECTION", get_where_clause(origin_rr))
        arcpy.FeatureVerticesToPoints_management(link_shpf, "in_memory/p1", "BOTH_ENDS")
        arcpy.MakeFeatureLayer_management("in_memory/p1", "p1")
        where_clause = """ "FID" = %d""" % fid
        arcpy.SelectLayerByAttribute_management(splc_shpf, "NEW_SELECTION", where_clause)  # select the specific splc
        arcpy.Near_analysis(splc_shpf, "p1", "", "NO_LOCATION", "NO_ANGLE", "GEODESIC")
        dumm = {row.getValue("NEAR_FID"): row.getValue("NEAR_DIST") for row in
                arcpy.SearchCursor(splc_shpf)}  # gets the FID of th nearest Node
        where_clause = """ "geoid2" = %d""" % geoid
        if geoid == 0:
            where_clause = ""
        arcpy.SelectLayerByAttribute_management(disk_shpf, "NEW_SELECTION", where_clause)  # select
        arcpy.SpatialJoin_analysis("p1", disk_shpf, "in_memory/p2", "", "", "", "CLOSEST", "", "")
        # ID for nodes gets changed to ID_1 automatically
        origin_node_id = [row.getValue("ID_1") for row in arcpy.SearchCursor("in_memory/p2")][0]
        fips_to_node_id_snap_distance = dumm.values()[0] / 1609.34  # converting meters to miles
        splc_fid_to_node_id_dict[splc] = [splc,fid, origin_node_id, geoid, fips_to_node_id_snap_distance]
        splc_df = pandas.DataFrame(splc_fid_to_node_id_dict).transpose()
        #splc_df.columns = [['SPLC', "FID", "NodeID", "FIPS" "DIST"]]
        count = count + 1
        # if count%100 ==0:
        #     try:
        #         splc_df.to_csv("splc_df.csv")
        #     except:
        #         splc_df.to_csv("splc_df"+str(random.random()*1000).split('.')[0])
