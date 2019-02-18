import arcpy
import pandas
from rail import *

arcpy.env.overwriteOutput = True


dbf_to_df = pandas.DataFrame({row.getValue("FID"): [row.getValue("RR"), row.getValue("comm"), row.getValue("Descrip")] for row in arcpy.SearchCursor(manual_snap_lines_shp)}).transpose().reset_index()
dbf_to_df.columns = ["FID", "RR", "comm", "Description"]
dbf_to_df['FIPS'] = 0.0
dbf_to_df['NODE'] = 0.0

arcpy.FeatureVerticesToPoints_management (manual_snap_lines_shp, disk_shp, "START")
arcpy.Near_analysis(disk_shp,fips_shp)
nearfid_to_fips_fid = {row.getValue("FID"): row.getValue("NEAR_FID") for row in arcpy.SearchCursor(disk_shp)}
fips_fid_to_fips = {row.getValue("FID"): int(row.getValue("GEOID")) for row in arcpy.SearchCursor(fips_shp)}

dbf_to_df['FIPS'] = dbf_to_df['FID'].map(nearfid_to_fips_fid).map(fips_fid_to_fips)


arcpy.FeatureVerticesToPoints_management (manual_snap_lines_shp, disk_shp, "END")
arcpy.Near_analysis(disk_shp,node_shp)
near_fid_to_id = {row.getValue("FID"): row.getValue("NEAR_FID") for row in arcpy.SearchCursor(disk_shp)}
node_fid_to_id = {row.getValue("FID"): row.getValue("ID") for row in arcpy.SearchCursor(node_shp)}

dbf_to_df['NODE'] = dbf_to_df['FID'].map(near_fid_to_id).map(node_fid_to_id)

#changing the order of columns
dbf_to_df = dbf_to_df[['FID', 'FIPS', 'RR', 'comm', 'NODE', 'Description']]
dbf_to_df.to_csv(ofips_orr_comm)

