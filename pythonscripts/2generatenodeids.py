from rail import *

arcpy.env.autoCancelling = False

fieldsfinal = ["FID", "Shape", "ID", "STATE_FP", "Abbr", "Name"]
fieldnew = ["FID", "Shape", "ID"]


def keep_fields(shape_file, keep):
    fields = [x.name for x in arcpy.ListFields(shape_file)]
    # delete if any of these fields are present
    arcpy.DeleteField_management(shape_file, [x for x in fields if x not in keep])

# create new node names or update previous?
if sys.argv[1] == "new":
    count_in_county_dictionary = {}
    print("Creating new NodeIDs")
    arcpy.DeleteField_management(disk_shp, "ID")
    arcpy.AddField_management(disk_shp, "ID", "LONG", "")

elif sys.argv[1] == "update":
    count_in_county_df = pandas.read_csv("data/countofIDs.csv")
    count_in_county_dictionary = dict(
        zip([int(i) for i in list(count_in_county_df)], list(count_in_county_df.iloc[0])))
    print("Updating NodeIDs")

else:
    print ("Invalid argument")
    exit()


# strip down the attributes to fieldnew
keep_fields(node_shp, fieldnew)
# get FIPS of each Node in a field
arcpy.SpatialJoin_analysis(node_shp, state_shp, disk_shp, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "COMPLETELY_WITHIN", "",
                           "")
keep_fields(disk_shp, fieldsfinal)

count = 0
with arcpy.da.UpdateCursor(disk_shp, ["ID", "STATE_FP"]) as cursor:
    for row in cursor:
        if sys.argv[1] == "update":
            if row[0] != 0:
                continue
        count = count + 1
        if row[1] in count_in_county_dictionary:
            row[0] = 1000 * row[1] + count_in_county_dictionary.get(row[1]) + 1
            count_in_county_dictionary.update({row[1]: count_in_county_dictionary.get(row[1]) + 1})
        else:
            count_in_county_dictionary.update({row[1]: 1})
            row[0] = 1000 * row[1] + count_in_county_dictionary.get(row[1])
        cursor.updateRow(row)

print (str(count) + " new nodes added")

arcpy.CopyFeatures_management(disk_shp, node_shp)

# the count of IDs csv file would be used to obtain the maximum number of nodes in a state in previous run
pandas.DataFrame(count_in_county_dictionary, index=[0]).to_csv("data/countofIDs.csv", index=False)
