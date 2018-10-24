# creates links between given nodes (snapped from old network)
import arcpy
from simpledbf import Dbf5

# takes time but works like charm

arcpy.env.overwriteOutput = True  # overwrite files if its already present

linksfinal = 'M:/RAIL/part4(network)/shapefiles/Links_Final2'
SnappedNodes = "allnodes_Snapped_rail2.shp"
sumlayer = "C:/GIS/temptemptemp.shp"
templayer = "C:/GIS/temp1.shp"
linkslayer = "rail2.shp"
emptyshapefile = "C:/GIS/empty.shp"

Links_Final2 = Dbf5(linksfinal + '.dbf').to_dataframe()

o = "C:\\GIS\\o.shp"  # temporary files
d = "C:\\GIS\\d.shp"
m = "C:\\GIS\\m.shp"

B1_ND = "M:/RAIL/OngoingWork/newconnections/railway_ln/Rail2_ND.nd"
feature = "M:/RAIL/OngoingWork/newconnections/intermediate/feature_unlocked.shp"  # i guess this is just a temporary layer/ no worries
arcpy.MakeRouteLayer_na(B1_ND, "Route", "Length")


def add_route_to_layer(nodeA, nodeB, sumlayer):
    print ("ArgGIS analyst: Job Received, ONODE: {0}, DNODE: {1} *".format(nodeA,
                                                                           nodeB))  # *these nodes are in different layers
    arcpy.CheckOutExtension("Network")
    arcpy.Select_analysis(SnappedNodes, o, 'ID = {0}'.format(nodeA))
    arcpy.Select_analysis(SnappedNodes, d, 'ID = {0}'.format(nodeB))
    arcpy.Merge_management([o, d], m)
    arcpy.AddLocations_na("Route", "Stops", m, "Name Name #", "5000 Kilometers", "", "B1 SHAPE;B1_ND_Junctions SHAPE",
                          "MATCH_TO_CLOSEST", "CLEAR", "NO_SNAP", "5 Meters", "INCLUDE", "B1 #;B1_ND_Junctions #")
    try:
        arcpy.Solve_na("Route", "SKIP", "TERMINATE", "500 Kilometers")
        arcpy.SelectData_management("Route", "Routes")
        arcpy.FeatureToLine_management("Route\\Routes", feature, "", "ATTRIBUTES")
    except:
        print ("Route not found. 999999 Returned")
        return 0
    arcpy.Merge_management([feature, sumlayer], templayer)
    arcpy.Copy_management(templayer, sumlayer)
    return 0


arcpy.Copy_management(emptyshapefile, sumlayer)

for i in range(len(Links_Final2)):
    # for i in range(20):
    add_route_to_layer(Links_Final2['A_NODE'][i], Links_Final2['B_NODE'][i], sumlayer)
