import arcpy


#takes time but works like charm
print ("Please wait... almost 12 mins")
clip_distance = 3 #miles
XY_tolerance = 30 #feet (minimum distance)

arcpy.env.overwriteOutput=True #overwrite files if its already present

#input
railway = "M:/RAIL/OngoingWork/newconnections/railway_ln/railway_UCM_connected.shp"
Links_Final2 = "M:\RAIL\part4(network)\shapefiles\Links_Final2.shp"
allnodes = "M:\\RAIL\\part1(GIS)\\shapefiles\\allnodes.shp"

#output
ORLinks = "M:/RAIL/OngoingWork/newconnections/railway_ln/OpenRail_Links.shp"
ORNodes = "M:/RAIL/OngoingWork/newconnections/railway_ln/OpenRail_Nodes.shp"
MyLinks = "M:/RAIL/OngoingWork/newconnections/railway_ln/Rail2.shp"
MyNodes = "M:/RAIL/OngoingWork/newconnections/railway_ln/Rail2_Nodes.shp"
SnappedNodes = "M:/RAIL/OngoingWork/newconnections/railway_ln/allnodes_Snapped_rail2.shp"

temp1= "C:/GIS/temp99.shp"


#preparing US Data
print("Converting feature to line with XY_tolerance of {0} feet...".format(XY_tolerance))
arcpy.FeatureToLine_management (railway, "in_memory/T1" , "{0} Feet".format(XY_tolerance), "NO_ATTRIBUTES" )
print("Dissolving all the features, Preparing ORLinks...")
arcpy.Dissolve_management("in_memory/T1", ORLinks, "", "", "SINGLE_PART", "UNSPLIT_LINES")
print("Generating Points at intersections...")
arcpy.FeatureVerticesToPoints_management(ORLinks, ORNodes, "BOTH_ENDS")
#arcpy.GeneratePointsAlongLines_management (ORLinks, ORNodes, "DISTANCE", Distance='50000000 meters', Include_End_Points='END_POINTS') #this takes the longest time
print("Deleting identical points...")
arcpy.DeleteIdentical_management (ORNodes, ["Shape"])
print("US Data prepared successfully")

#snap allnodes to nearest Rail2
arcpy.Copy_management(allnodes, SnappedNodes)
arcpy.Snap_edit (SnappedNodes, [[ORLinks, "VERTEX", "10000 Feet"]])
arcpy.SplitLineAtPoint_management (ORLinks, SnappedNodes, temp1)
arcpy.Copy_management (temp1, ORLinks)

#preparing Clipped data
arcpy.Buffer_analysis(Links_Final2, "in_memory/T2", "{0} Miles".format(clip_distance), "FULL", "ROUND", "NONE", "", "PLANAR")
# arcpy.GetCount_management("in_memory/T3").getOutput (0)
# arcpy.Dissolve_management("in_memory/T2", "in_memory/T3" , "FID", "", "SINGLE_PART", "DISSOLVE_LINES")

fieldname = "in_memory/T3"
fields = arcpy.ListFields(fieldname)
arcpy.GetCount_management(fieldname).getOutput (0)
for field in fields:
    print("{0}" .format(field.name)),


#preparing links
arcpy.Delete_management(MyLinks)
arcpy.Copy_management (ORLinks, MyLinks)
arcpy.MakeFeatureLayer_management(MyLinks, "MyLinks")
arcpy.MakeFeatureLayer_management("in_memory/T2", '"in_memory/T2"')
arcpy.SelectLayerByLocation_management('MyLinks', "WITHIN", "in_memory/T2", "", "NEW_SELECTION", "INVERT") #takes a long time
arcpy.DeleteFeatures_management("MyLinks")
#preparing nodes
arcpy.Copy_management (ORNodes, MyNodes)
arcpy.MakeFeatureLayer_management(MyNodes, 'MyNodes')
arcpy.SelectLayerByLocation_management("MyNodes", "COMPLETELY_WITHIN", "in_memory/T2", "", "NEW_SELECTION", "INVERT")
arcpy.DeleteFeatures_management("MyNodes")
print("Area Data Prepared successfully")

#snap allnodes to nearest Rail2
# arcpy.Copy_management(allnodes, SnappedNodes)
# arcpy.Snap_edit (SnappedNodes, [[ORLinks, "VERTEX", "10000 Feet"]])


