from rail import *
import arcpy

base_flows_shpf = "base_flows_df"
arcpy.env.overwriteOutput = True


arcpy.MakeFeatureLayer_management(link_shp, link_shpf)
arcpy.MakeFeatureLayer_management(base_flows_shp, base_flows_shpf)


base_flows_df = pandas.DataFrame({"ID":[],"DIR":[], "RR":[], "COSTPTRHR":[],"COSTPTML":[]})
base_flows_dict = {}

def get_field_names(shp):
    fieldnames = [f.name for f in arcpy.ListFields(shp)]
    return fieldnames

#print(get_field_names(base_flows_shp))


with arcpy.da.SearchCursor(base_flows_shp, ["FID","vol_ab", "vol_ba", "tob_ab", "ton_ba"]) as cursor:
    for row in cursor:
        where_clause = """ "FID" = %d""" % row[0]
        arcpy.SelectLayerByAttribute_management(base_flows_shpf, "NEW_SELECTION", where_clause)
        arcpy.Buffer_analysis(base_flows_shpf, disk_shp, "50 feet")
        arcpy.SelectLayerByLocation_management(link_shpf, "COMPLETELY_WITHIN", disk_shp)
        IDs = [row1.getValue("ID") for row1 in arcpy.SearchCursor(link_shpf)]
        for ID in IDs:
            base_flows_dict[ID] = [row[1], row[2], row[3], row[4]]


base_flows_df = pandas.DataFrame(base_flows_dict).transpose().reset_index()
base_flows_df.columns = ["ID", "base_vol_daily_ab", "base_vol_daily_ba", "base_ton_daily_ab", "base_ton_daily_ba"]

base_flows_df.ID = base_flows_df.ID.astype(int)
base_flows_df.base_vol_daily_ab = base_flows_df.base_vol_daily_ab.astype(int)
base_flows_df.base_vol_daily_ba = base_flows_df.base_vol_daily_ba.astype(int)
base_flows_df.base_ton_daily_ba = base_flows_df.base_ton_daily_ba.astype(float)
base_flows_df.base_ton_daily_ba = base_flows_df.base_ton_daily_ba.astype(float)

base_flows_df['ID'] = base_flows_df['ID'].map('{:8d}'.format)
base_flows_df['base_vol_daily_ab'] = base_flows_df['base_vol_daily_ab'].map('{:5d}'.format)
base_flows_df['base_vol_daily_ba'] = base_flows_df['base_vol_daily_ba'].map('{:5d}'.format)
base_flows_df['base_ton_daily_ab'] = base_flows_df['base_ton_daily_ab'].map('{:10.0f}'.format)
base_flows_df['base_ton_daily_ba'] = base_flows_df['base_ton_daily_ba'].map('{:10.0f}'.format)

base_flows_df = base_flows_df[['ID', 'base_vol_daily_ab', 'base_vol_daily_ba', 'base_ton_daily_ab', 'base_ton_daily_ba']].apply(
    lambda x: '  {}{}{}{}{}'.format(x[0], x[1], x[2], x[3], x[4]), axis=1)

base_flows_df.to_csv(base_flows_output, index=False)
