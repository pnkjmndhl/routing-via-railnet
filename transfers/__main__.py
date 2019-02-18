from rail import *
import arcpy

arcpy.env.overwriteOutput = True

arcpy.Near_analysis(transfer_shp, node_shp, "", "NO_LOCATION", "NO_ANGLE", "GEODESIC")

transfer_shp_dict = {
row.getValue("FID"): [row.getValue("JRR1NO"), row.getValue("JRR2NO"), row.getValue("BIDIR"), row.getValue("NEAR_FID")]
for row in arcpy.SearchCursor(transfer_shp)}

node_fid_id_dict = {row.getValue("FID"): row.getValue("ID") for row in arcpy.SearchCursor(node_shp)}

for key, value in transfer_shp_dict.items():
    value[3] = node_fid_id_dict[value[3]]

transfer_df = pandas.DataFrame(
    {"ID": [x[3] for x in transfer_shp_dict.values()], "JRR1NO": [x[0] for x in transfer_shp_dict.values()],
     "JRR2NO": [x[1] for x in transfer_shp_dict.values()], "BIDIR": [x[2] for x in transfer_shp_dict.values()]})

transfer_df = transfer_df[['ID', 'JRR1NO', "JRR2NO", "BIDIR"]]

# remove duplicate transfers
transfer_df = transfer_df.drop_duplicates()
transfer_df = transfer_df.sort_values(["ID", 'JRR1NO', "JRR2NO"], ascending=[True, True, True])

transfer_df.to_csv(transfer_csv)
# working on dataframes for creating xfr file

transfer_df.ID = transfer_df.ID.astype(int)
transfer_df.JRR1NO = transfer_df.JRR1NO.astype(int)
transfer_df.JRR2NO = transfer_df.JRR2NO.astype(int)
transfer_df.BIDIR = transfer_df.BIDIR.astype(int)

# create formatted output
transfer_df['ID'] = transfer_df['ID'].map('{:05}'.format)
transfer_df['JRR1NO'] = transfer_df['JRR1NO'].map('{:05d}'.format)
transfer_df['JRR2NO'] = transfer_df['JRR2NO'].map('{:05d}'.format)
transfer_df['BIDIR'] = transfer_df['BIDIR'].map('{:05d}'.format)

transfer_df = transfer_df.apply(lambda x: '{}{}{}{}'.format(x[0], x[1], x[2], x[3]), axis=1)
transfer_df.to_csv(transfer_xfr_output, index=False)
