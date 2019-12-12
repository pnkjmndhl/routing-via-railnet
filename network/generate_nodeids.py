from rail import *
import arcpy
import math

arcpy.env.overwriteOutput = True

temp = "C:/GIS/temp.shp"

#Rule 1, always generate nodes from links :)

#get new nodes (calculate this)
arcpy.FeatureVerticesToPoints_management(link_shp, node_shp, "BOTH_ENDS")
arcpy.AddField_management(node_shp, "_X_", "DOUBLE")
arcpy.AddField_management(node_shp, "_Y_", "DOUBLE")
with arcpy.da.UpdateCursor(node_shp, ["SHAPE@XY", "_X_", "_Y_"]) as cursor:
    for row in cursor:
        row[1] = row[0][0]
        row[2] = row[0][1]
        cursor.updateRow(row)

arcpy.DeleteIdentical_management(node_shp, ['_X_', '_Y_'])

arcpy.SpatialJoin_analysis(node_shp, state_shp, temp, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "WITHIN")

#get all the field names and drop them (since they are imported from link_shp)
field_names =  [f.name for f in arcpy.ListFields(temp)]  # getting field names
try:
    arcpy.AddField_management(temp, "ID", "LONG")
except: #if already has IDs, all should be 0 at first (later calculated)
    arcpy.CalculateField_management(temp, "ID", 0, "PYTHON")  # all 0 at first
field_names = [e for e in field_names if e not in ["ID", "FID", "Shape", "STATE_FP"]]
arcpy.DeleteField_management(temp, field_names)


#all states contain no nodes at first
count_of_county_dict = {x: 0 for x in range(1, 99)}


print("List of Nodes added:")
with arcpy.da.UpdateCursor(temp, ["ID", "STATE_FP"]) as cursor:
    for row in cursor:
        if row[0] != 0:
            continue
        row[0] = 1000 * row[1] + count_of_county_dict.get(row[1]) + 1
        count_of_county_dict.update({row[1]: count_of_county_dict.get(row[1]) + 1})
        cursor.updateRow(row)

arcpy.CopyFeatures_management(temp, node_shp)
