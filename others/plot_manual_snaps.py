import arcpy
import pandas
from rail import *
import math


arcpy.env.overwriteOutput = True

all_fips_to_xy = {}
all_nodes_to_xy = {}

manual_snaps_df = pandas.read_csv('intermediate/OFIPSORRcomm.csv')
fips_coordinates_dict = {}
nodes_coordinates_dict = {}


arcpy.AddXY_management(fips_shp)
all_fips_to_xy = {int(row.getValue("GEOID")): [row.getValue("POINT_X"), row.getValue("POINT_Y")] for row in
                  arcpy.SearchCursor(fips_shp)}
arcpy.AddXY_management(node_shp)
all_nodes_to_xy = {row.getValue("ID"): [row.getValue("POINT_X"), row.getValue("POINT_Y")] for row in
                   arcpy.SearchCursor(node_shp)}




manual_snaps_df['FIPSXY'] = manual_snaps_df['FIPS'].map(all_fips_to_xy)
manual_snaps_df['NODEXY'] = manual_snaps_df['NODE'].map(all_nodes_to_xy)

manual_snaps_df['FIPS_X'] = 0.0
manual_snaps_df['FIPS_Y'] = 0.0
manual_snaps_df['NODE_X'] = 0.0
manual_snaps_df['NODE_Y'] = 0.0

#look for a faster method (this consumes time)
for i in range(len(manual_snaps_df)):
    manual_snaps_df['FIPS_X'][i] = manual_snaps_df['FIPSXY'][i][0]
    manual_snaps_df['FIPS_Y'][i] = manual_snaps_df['FIPSXY'][i][1]
    manual_snaps_df['NODE_X'][i] = manual_snaps_df['NODEXY'][i][0]
    manual_snaps_df['NODE_Y'][i] = manual_snaps_df['NODEXY'][i][1]



manual_snaps_df.to_csv(csv)

arcpy.XYToLine_management (csv, manual_snap_lines_shp, "FIPS_X", "FIPS_Y", "NODE_X", "NODE_Y", "", "ID", "")


arcpy.AddField_management(manual_snap_lines_shp, "FIPS", "SHORT")
arcpy.AddField_management(manual_snap_lines_shp, "RR", "SHORT")
arcpy.AddField_management(manual_snap_lines_shp, "comm", "SHORT")
arcpy.AddField_management(manual_snap_lines_shp, "NODE", "TEXT")
arcpy.AddField_management(manual_snap_lines_shp, "Descrip", "TEXT")


#fieldnames = [f.name for f in arcpy.ListFields(manual_snap_lines_shp)]


with arcpy.da.UpdateCursor(manual_snap_lines_shp, ["ID", "FIPS", "RR", "comm", "NODE", "Descrip"]) as cursor:
    for row in cursor:
        row[1] = manual_snaps_df[manual_snaps_df.ID == row[0]]['FIPS'].values[0]
        row[2] = manual_snaps_df[manual_snaps_df.ID == row[0]]['RR'].values[0]
        row[3] = manual_snaps_df[manual_snaps_df.ID == row[0]]['comm'].values[0]
        row[4] = manual_snaps_df[manual_snaps_df.ID == row[0]]['NODE'].values[0]
        value = manual_snaps_df[manual_snaps_df.ID == row[0]]['Description'].values[0]
        if not pandas.isnull(value):
            row[5] = value
        else:
            row[5] = ""
        cursor.updateRow(row)

arcpy.DeleteField_management (manual_snap_lines_shp, "FIPS_X")
arcpy.DeleteField_management (manual_snap_lines_shp, "FIPS_Y")
arcpy.DeleteField_management (manual_snap_lines_shp, "NODE_X")
arcpy.DeleteField_management (manual_snap_lines_shp, "NODE_Y")



