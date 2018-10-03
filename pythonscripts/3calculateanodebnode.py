from rail import *

arcpy.MakeFeatureLayer_management(link_shp, link_shp_feature)
arcpy.MakeFeatureLayer_management(node_shp, node_shp_feature)


def get_vertices_id(end):
    vertices = []
    # arcpy.SelectLayerByLocation_management(node_shp_feature, "INTERSECT", link_shp_feature, "", "NEW_SELECTION")
    arcpy.FeatureVerticesToPoints_management(link_shp_feature, memory_shp, end)
    arcpy.SelectLayerByLocation_management(node_shp_feature, "ARE_IDENTICAL_TO", memory_shp, "", "NEW_SELECTION")
    with arcpy.da.SearchCursor(node_shp_feature, ["ID"]) as cursor:
        for row in cursor:
            vertices.append(row[0])
    if len(vertices) != 1:  # it has to return exactly one vertices per end
        return [0]
    else:
        return vertices[0]


# delete existing A_NODE and B_NODE
arcpy.DeleteField_management(node_shp, ["A_NODE", "B_NODE"])

# main program
arcpy.AddField_management(link_shp, "A_NODE", "LONG", "")
arcpy.AddField_management(link_shp, "B_NODE", "LONG", "")

with arcpy.da.UpdateCursor(link_shp, ["FID", "A_NODE", "B_NODE", "ID"]) as cursor:
    for row in cursor:
        where = """ "FID" = %d""" % row[0]
        arcpy.SelectLayerByAttribute_management(link_shp_feature, "NEW_SELECTION", where)
        row[1] = get_vertices_id("START")
        row[2] = get_vertices_id("END")
        check_if_list = isinstance(row[1], list) or isinstance(row[2], list)
        if 0 in [row[1], row[2]] or check_if_list:  #  if the link has multiple parts, the link returns a list for either row[1] or row[2]
            print ("Error: LinkID: " + str(row[3]) + ", skipped.")
            continue
        cursor.updateRow(row)