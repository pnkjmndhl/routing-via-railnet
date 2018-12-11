from rail import *
import arcpy

temp_layer = "C:/GIS/temp.shp"
base_flows_shpf = "base_flows_dfeptionshpf"
arcpy.env.overwriteOutput = True


arcpy.MakeFeatureLayer_management(link_shp, link_shpf)
arcpy.MakeFeatureLayer_management(base_flows_shp, base_flows_shpf)


base_flows_df = pandas.DataFrame({"ID":[],"DIR":[], "RR":[], "COSTPTRHR":[],"COSTPTML":[]})
base_flows_dict = {}

def get_field_names(shp):
    fieldnames = [f.name for f in arcpy.ListFields(shp)]
    return fieldnames


with arcpy.da.SearchCursor(base_flows_shp, ["FID","dir", "RR", "comm", "costptrhr", "costptml"]) as cursor:
    for row in cursor:
        where_clause = """ "FID" = %d""" % row[0]
        arcpy.SelectLayerByAttribute_management(base_flows_shpf, "NEW_SELECTION", where_clause)
        arcpy.Buffer_analysis(base_flows_shpf, temp_layer, "100 feet")
        arcpy.SelectLayerByLocation_management(link_shpf, "COMPLETELY_WITHIN", temp_layer)
        IDs = [row1.getValue("ID") for row1 in arcpy.SearchCursor(link_shpf)]
        for ID in IDs:
            base_flows_dict[ID] = [row[1], row[2], row[3], row[4], row[5]]


base_flows_df = pandas.DataFrame(base_flows_dict).transpose().reset_index()
base_flows_df.columns = ["ID", "direction", "RR", "comm", "costpertrainhr", "costpertonmile"]


base_flows_df = base_flows_df[['ID', 'RR', 'comm', 'direction', 'costpertrainhr', 'costpertonmile']]
base_flows_df.ID = base_flows_df.ID.astype(int)
base_flows_df.RR = base_flows_df.RR.astype(int)
base_flows_df.comm = base_flows_df.comm.astype(int)
base_flows_df.direction = base_flows_df.direction.astype(int)
base_flows_df.costpertonmile = base_flows_df.costpertonmile.astype(float)

base_flows_df['ID'] = base_flows_df['ID'].map('{:5d}'.format)
base_flows_df['RR'] = base_flows_df['RR'].map('{:5d}'.format)
base_flows_df['comm'] = base_flows_df['comm'].map('{:5d}'.format)
base_flows_df['direction'] = base_flows_df['direction'].map('{:5d}'.format)
base_flows_df['costpertrainhr'] = base_flows_df['costpertrainhr'].map('{:10.2f}'.format)
base_flows_df['costpertonmile'] = base_flows_df['costpertonmile'].map('{:10.2f}'.format)

base_flows_df = base_flows_df[['ID', 'RR', 'comm', 'direction', 'costpertrainhr', 'costpertonmile']].apply(
    lambda x: '{}{}{}{}{}{}'.format(x[0], x[1], x[2], x[3], x[4], x[5]), axis=1)

base_flows_df.to_csv("output/link.exc", index=False)
