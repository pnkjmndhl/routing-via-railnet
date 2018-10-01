import pandas
import arcpy
import numpy as np

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'C:/GIS/'

near_distance = "5 Miles"  # the maximum distance the transfer would be snapped to

# inputs/output files
transfer_file = r'input/INTERCHANG_G3O.xlsx'
sheet_name = "BASE"
all_aar = r'input/allAARCode.csv'
transfer_shp = r"../GIS/transfers.shp"
link_shp = r"../GIS/alllinks.shp"
intermediate_csv = "intermediate/transfers.csv"

# new data frames from files
transfer = pandas.ExcelFile(transfer_file).parse(sheet_name)
all_aar_df = pandas.read_csv(all_aar)


def get_network_railroad_aar_dict():
    dummy = []
    for row in arcpy.SearchCursor(link_shp):
        dummy.append(
            [row.getValue("RR1"), row.getValue("RR2"), row.getValue("RR3"), row.getValue("RR4"), row.getValue("RR5")])
    flat_list = list(set([x for sublist in dummy for x in sublist]))
    flat_list.remove(0)
    new_dict = {x: list(all_aar_df[all_aar_df.ABBR == str(x)]['AARCode'].values) for x in flat_list}
    reverse_dict = {value: key for key in new_dict for value in new_dict[key]}
    return reverse_dict


my_aar_dict = get_network_railroad_aar_dict()

# add new columns with the RR#
transfer['JRR1NO'] = transfer.JRR1.map(my_aar_dict)
transfer['JRR2NO'] = transfer.JRR2.map(my_aar_dict)
transfer = transfer.dropna()  # remove the transfers not found in my_dict
transfer['JRR1NO'].astype(int)
transfer['JRR2NO'].astype(int)

dummy = []
for row in arcpy.SearchCursor(transfer_shp):
    dummy.append([row.getValue("SPLC6"), row.getValue("JRR1"), row.getValue("JRR2"), row.getValue("flag")])
dummy_df = pandas.DataFrame(dummy)
dummy_df.columns = ['SPL_', 'JRR1_', 'JRR2_', 'flag']
dummy_df = dummy_df[dummy_df['flag'] != 0]

transfer = pandas.concat([transfer, dummy_df], axis=1)
transfer = transfer.drop(['SPL_', 'JRR1_', 'JRR2_'], axis=1)
transfer = transfer.fillna(0)
transfer['nearNID'] = ""
transfer['nearNDist'] = ""

transfer.to_csv(intermediate_csv)  # also write the contents to a csv file
arcpy.DeleteFeatures_management(transfer_shp)

arcpy.TableToTable_conversion(intermediate_csv, "intermediate", "transfers.dbf")
arcpy.MakeXYEventLayer_management("intermediate/transfers.dbf", "LONNBR", "LATNBR", 'dummy',
                                  arcpy.SpatialReference(4326))
arcpy.CopyFeatures_management("dummy", transfer_shp)
