from rail import *
import arcpy

arcpy.env.overwriteOutput = True

nodea_nodeb_df = pandas.DataFrame({row.getValue("FID"): [0, 0] for row in arcpy.SearchCursor(link_shp)}).transpose().reset_index()
nodea_nodeb_df.columns = ["FID", "NODEA", "NODEB"]

node_fid_to_id = {row.getValue("FID"): int(row.getValue("ID")) for row in arcpy.SearchCursor(node_shp)}

#NODE_A
arcpy.FeatureVerticesToPoints_management (link_shp, disk_shp, "START")
arcpy.Near_analysis(disk_shp,node_shp)
nearfid_to_node_fid = {row.getValue("FID"): row.getValue("NEAR_FID") for row in arcpy.SearchCursor(disk_shp)}
nodea_nodeb_df['NODEA'] = nodea_nodeb_df['FID'].map(nearfid_to_node_fid).map(node_fid_to_id)

#NODE_B
arcpy.FeatureVerticesToPoints_management (link_shp, disk_shp, "END")
arcpy.Near_analysis(disk_shp,node_shp)
nearfid_to_node_fid = {row.getValue("FID"): row.getValue("NEAR_FID") for row in arcpy.SearchCursor(disk_shp)}
nodea_nodeb_df['NODEB'] = nodea_nodeb_df['FID'].map(nearfid_to_node_fid).map(node_fid_to_id)


with arcpy.da.UpdateCursor(link_shp, ["FID", "A_NODE", "B_NODE"]) as cursor:
    for row in cursor:
        row[1] = nodea_nodeb_df[nodea_nodeb_df.FID == row[0]]['NODEA'].values[0]
        row[2] = nodea_nodeb_df[nodea_nodeb_df.FID == row[0]]['NODEB'].values[0]
        cursor.updateRow(row)
