from rail import *
import arcpy

temp_layer = "C:/GIS/temp.shp"
link_exception_shpf = "link_exception_dfeptionshpf"
arcpy.env.overwriteOutput = True


arcpy.MakeFeatureLayer_management(link_shp, link_shpf)
arcpy.MakeFeatureLayer_management(link_exception_shp, link_exception_shpf)


link_exception_df = pandas.DataFrame({"ID":[],"DIR":[], "RR":[], "COSTPTRHR":[],"COSTPTML":[]})
link_exception_dict = {}

def get_field_names(shp):
    fieldnames = [f.name for f in arcpy.ListFields(shp)]
    return fieldnames


with arcpy.da.SearchCursor(link_exception_shp, ["FID","dir", "RR", "comm", "costptrhr", "costptml"]) as cursor:
    for row in cursor:
        where_clause = """ "FID" = %d""" % row[0]
        arcpy.SelectLayerByAttribute_management(link_exception_shpf, "NEW_SELECTION", where_clause)
        arcpy.Buffer_analysis(link_exception_shpf, temp_layer, "100 feet")
        arcpy.SelectLayerByLocation_management(link_shpf, "COMPLETELY_WITHIN", temp_layer)
        IDs = [row1.getValue("ID") for row1 in arcpy.SearchCursor(link_shpf)]
        for ID in IDs:
            link_exception_dict[ID] = [row[1], row[2], row[3], row[4], row[5]]


link_exception_df = pandas.DataFrame(link_exception_dict).transpose().reset_index()
link_exception_df.columns = ["ID", "direction", "RR", "comm", "costpertrainhr", "costpertonmile"]


link_exception_df = link_exception_df[['ID', 'RR', 'comm', 'direction', 'costpertrainhr', 'costpertonmile']]
link_exception_df.ID = link_exception_df.ID.astype(int)
link_exception_df.RR = link_exception_df.RR.astype(int)
link_exception_df.comm = link_exception_df.comm.astype(int)
link_exception_df.direction = link_exception_df.direction.astype(int)
link_exception_df.costpertonmile = link_exception_df.costpertonmile.astype(float)

link_exception_df['ID'] = link_exception_df['ID'].map('{:5d}'.format)
link_exception_df['RR'] = link_exception_df['RR'].map('{:5d}'.format)
link_exception_df['comm'] = link_exception_df['comm'].map('{:5d}'.format)
link_exception_df['direction'] = link_exception_df['direction'].map('{:5d}'.format)
link_exception_df['costpertrainhr'] = link_exception_df['costpertrainhr'].map('{:10.5f}'.format)
link_exception_df['costpertonmile'] = link_exception_df['costpertonmile'].map('{:10.5f}'.format)

link_exception_df = link_exception_df[['ID', 'RR', 'comm', 'direction', 'costpertrainhr', 'costpertonmile']].apply(
    lambda x: '{}{}{}{}{}{}'.format(x[0], x[1], x[2], x[3], x[4], x[5]), axis=1)

link_exception_df.to_csv("output/link.exc", index=False)
