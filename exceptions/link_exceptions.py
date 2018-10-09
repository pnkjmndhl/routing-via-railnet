from rail import *
import arcpy

arcpy.env.overwriteOutput = True

arcpy.Near_analysis(link_exception_shp, link_shp, "", "NO_LOCATION", "NO_ANGLE", "GEODESIC")

link_exception_shp_dict = {row.getValue("FID"): [row.getValue("dir"), row.getValue("RR") row.getValue("comm"), row.getValue("costptrhr"), row.getValue("costptml"), row.getValue("NEAR_FID")]  for row in arcpy.SearchCursor(link_exception_shp)}

link_fid_id_dict = {row.getValue("FID"): row.getValue("ID")  for row in arcpy.SearchCursor(link_shp}


for key,value in link_exception_shp_dict.items():
    value[4] = link_fid_id_dict[value[4]]

transfer_exception_df = pandas.DataFrame(link_exception_shp_dict).transpose()
transfer_exception_df.columns = [["DIR", "RR", "comm", "costpthr","costptml", "ID"]]

transfer_exception_df = transfer_exception_df[['DIR','ID','RR','costpthr','costptml']]


# 2 conflicting... need to figure out the right way

linkexc = linkexc[['ID', 'RR', 'comm', 'direction', 'costpertrainhr', 'costpertonmile']]
linkexc.ID = linkexc.ID.astype(int)
linkexc.RR = linkexc.RR.astype(int)
linkexc.comm = linkexc.comm.astype(int)
linkexc.direction = linkexc.direction.astype(int)
linkexc.costpertonmile = linkexc.costpertonmile.astype(float)


linkexc['ID'] = linkexc['ID'].map('{:5d}'.format)
linkexc['RR'] = linkexc['RR'].map('{:5d}'.format)
linkexc['comm'] = linkexc['comm'].map('{:5d}'.format)
linkexc['direction'] = linkexc['direction'].map('{:5d}'.format)
linkexc['costpertrainhr'] = linkexc['costpertrainhr'].map('{:10.2f}'.format)
linkexc['costpertonmile'] = linkexc['costpertonmile'].map('{:10.2f}'.format)

linkexc = linkexc[['ID', 'RR', 'comm', 'direction', 'costpertrainhr', 'costpertonmile']].apply(lambda x : '{}{}{}{}{}{}'.format(x[0],x[1],x[2],x[3],x[4],x[5]), axis=1)

linkexc.to_csv("link.exc", index = False)

