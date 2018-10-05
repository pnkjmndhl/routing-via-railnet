import pandas
import arcpy
from simpledbf import Dbf5
from math import isnan

MyNodes = 'M://RAIL//OngoingWork//newconnections//railway_ln//Rail2_Nodes.shp' #newNodes
SnappedNodes = 'M://RAIL//OngoingWork//newconnections//railway_ln//allnodes_Snapped_rail2.shp'


newoldnodesconversion = 'M:/RAIL/OngoingWork/new_old_node_conversion.csv'

new_old_node_conversion = pandas.read_csv(newoldnodesconversion,index_col = 0, header = None)

#create dictionary of id1 to id2
snapDi = {}
for nodeA in list(new_old_node_conversion.index.values):
   snapDi[nodeA] = new_old_node_conversion[1][nodeA]

print ("Dictionary of Old-New coordinates generated")

#delete the dictionary with "", the position of snapped nodes doesn't change
snapDi = {x:y for x,y in snapDi.items() if not isnan(y)}

#create dictionary with xy from new nodes by id
xyDi = {}
#spatial reference of all_snapped shapefile
sr = arcpy.Describe(SnappedNodes).spatialReference

#iterate MyNodes
with arcpy.da.SearchCursor (MyNodes, ["FID", "SHAPE@XY"], spatial_reference = sr) as curs:
    for id2, xy in curs:
        #update xy
        xyDi [id2] = xy

print("New coordinates recorded")

#update SnappedNodes
with arcpy.da.UpdateCursor (SnappedNodes, ["ID", "SHAPE@XY"]) as curs:
    for id1, xy in curs:
        #get xy of id2
        #print "Working on {0}, [{1}]".format(id1,xy)
        try: 
           xy = xyDi [snapDi [id1]]
        except KeyError: 
           continue
           print "Exception Encountered at Snapped ID {0} and New ID {1}".format(id1, snapDi[id1])
        row = (id1, xy)
        curs.updateRow(row)

print("All snapped nodes snapped to new nodes")
