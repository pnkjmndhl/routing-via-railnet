from rail import *
import arcpy

arcpy.env.overwriteOutput = True

arcpy.Near_analysis(transfer_exception_shp, node_shp, "", "NO_LOCATION", "NO_ANGLE", "GEODESIC")

transfer_exception_shp_dict = {row.getValue("FID"): [row.getValue("RR1"),row.getValue("RR2"), row.getValue("commodity"), row.getValue("cost"), row.getValue("NEAR_FID")]  for row in arcpy.SearchCursor(transfer_exception_shp)}

node_fid_id_dict = {row.getValue("FID"): row.getValue("ID")  for row in arcpy.SearchCursor(node_shp)}

for key,value in transfer_exception_shp_dict.items():
    value[4] = node_fid_id_dict[value[4]]


transfer_exception_df = pandas.DataFrame(transfer_exception_shp_dict).transpose()
transfer_exception_df.columns = [["RR1", "RR2", "comm", "cost","ID"]]

transfer_exception_df = transfer_exception_df[['ID','RR1','RR2','comm','cost']]
transfer_exception_df.ID = transfer_exception_df.ID.astype(int)
transfer_exception_df.RR1 = transfer_exception_df.RR1.astype(int)
transfer_exception_df.RR2 = transfer_exception_df.RR2.astype(int)
transfer_exception_df.comm = transfer_exception_df.comm.astype(int)
transfer_exception_df.cost = transfer_exception_df.cost.astype(float)
transfer_exception_df['ID'] = transfer_exception_df['ID'].map('{:5d}'.format)
transfer_exception_df['RR1'] = transfer_exception_df['RR1'].map('{:3d}'.format)
transfer_exception_df['RR2'] = transfer_exception_df['RR2'].map('{:3d}'.format)
transfer_exception_df['comm'] = transfer_exception_df['comm'].map('{:5d}'.format)
transfer_exception_df['cost'] = transfer_exception_df['cost'].map('{:10.2f}'.format)


transfer_exception_df = transfer_exception_df[['ID','RR1',	'RR2','comm','cost']].apply(lambda x : '{}  {}  {}{}{}'.format(x[0],x[1],x[2],x[3],x[4]), axis=1)

transfer_exception_df.to_csv(transfer_exc_output, index = False)