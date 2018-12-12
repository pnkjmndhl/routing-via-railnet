import arcpy

multiparts = []

for row in arcpy.da.SearchCursor(link_shp, ["OID@", 'ID' "SHAPE@"]):
    if row[2].isMultipart is True:
        multiparts.append(row[0])

print("List of IDs with multipart: ")
print(multiparts)