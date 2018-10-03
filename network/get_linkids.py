from rail import *
import arcpy

count_ab_fips_dict = {}


def get_count(a_node, b_node):
    # ab_node = a_node/1000 *100 + b_node/1000  # first 2 digits would be start FIPS and the next 2 would be end FIPS (discontinued)
    ab_node = a_node / 1000  # only start FIPS used
    if ab_node in count_ab_fips_dict:
        count_ab_fips_dict.update({ab_node: count_ab_fips_dict.get(ab_node) + 1})
        return (1000 * ab_node + count_ab_fips_dict.get(ab_node))
    else:
        count_ab_fips_dict.update({ab_node: 1})
        return (1000 * ab_node + count_ab_fips_dict.get(ab_node))


arcpy.DeleteField_management(link_shp, ["ID"])
arcpy.AddField_management(link_shp, "ID", "LONG", "")

with arcpy.da.UpdateCursor(link_shp, ["ID", "A_NODE", "B_NODE"]) as cursor:
    for row in cursor:
        row[0] = get_count(row[1], row[2])
        cursor.updateRow(row)

print("Summary")
print (count_ab_fips_dict)
