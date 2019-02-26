from rail import *
import arcpy
import math

arcpy.env.overwriteOutput = True

fields_final = [f.name for f in arcpy.ListFields(node_shp)]
fields_new = fields_final[:3]


def keep_field_in_shp(shape_file, keep):
    fields = [x.name for x in arcpy.ListFields(shape_file)]
    # delete if any of these fields are present
    try:
        arcpy.DeleteField_management(shape_file, [x for x in fields if x not in keep])
    except:
        pass


# create a copy of node_shp
arcpy.CopyFeatures_management(node_shp, disk_shp1)

# strip down the attributes to fields_new
keep_field_in_shp(disk_shp1, fields_new)
arcpy.SpatialJoin_analysis(disk_shp1, state_shp, disk_shp, "JOIN_ONE_TO_ONE", "KEEP_ALL", "", "COMPLETELY_WITHIN", "",
                           "")  # get FIPS of each Node in a field
keep_field_in_shp(disk_shp, fields_final)

# creating count of county dictionary:
arr = arcpy.da.TableToNumPyArray(disk_shp, fields_final[2:])
node_shp_df = pandas.DataFrame(arr)  # 1st row as the column names

count_of_county_dict = {x: 0 for x in range(1, 99)}

new_nodes_flag = 0
for ID in node_shp_df["ID"]:
    if ID == 0:  # if the nodeID is new, no need to register
        new_nodes_flag = 1
        continue
    state = math.floor(ID / 1000)
    state_id = ID - state * 1000
    if count_of_county_dict[state] < state_id:
        count_of_county_dict[state] = state_id

count = 0

if new_nodes_flag == 0:
    print "No new nodes found"
    exit(0)

print("List of Nodes added:")
with arcpy.da.UpdateCursor(disk_shp, ["ID", "STATE_FP"]) as cursor:
    for row in cursor:
        if row[0] != 0:
            continue
        count = count + 1
        row[0] = 1000 * row[1] + count_of_county_dict.get(row[1]) + 1
        print "{0}".format(int(row[0]))
        count_of_county_dict.update({row[1]: count_of_county_dict.get(row[1]) + 1})
        cursor.updateRow(row)

arcpy.CopyFeatures_management(disk_shp, node_shp)

print (str(count) + " new nodes added to node_shp")
