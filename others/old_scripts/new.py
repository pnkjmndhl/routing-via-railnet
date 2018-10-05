import pandas
from simpledbf import Dbf5
import arcpy
import os
import sys #for printing . :D

arcpy.env.overwriteOutput=True #overwrite files if its already present

#os.chdir(path)
#%

buffer_dist = 1.5 #default buffer distance (to find new nodes close to old nodes)
all_nodes = 'M:/RAIL/part1(GIS)/shapefiles/allnodes' #oldnodes
MyNodes = 'M:/RAIL/OngoingWork/newconnections/railway_ln/Rail2_Nodes' #newNodes
linksfinal = 'M:/RAIL/part4(network)/shapefiles/Links_Final2'
SnappedNodes = 'M:/RAIL/OngoingWork/newconnections/railway_ln/allnodes_Snapped_rail2'

newoldnodesconversion = 'M:/RAIL/OngoingWork/new_old_node_conversion.csv'

o = "C:\\GIS\\o.shp" #temporary files
d = "C:\\GIS\\d.shp"
m = "C:\\GIS\\m.shp"
temp = "C:\\GIS\\teemp.shp"
temp1 = "C:\\GIS\\teemp1.shp"
temp2 = "C:\\GIS\\teemp2.shp"

B1_ND = "M:/RAIL/OngoingWork/newconnections/railway_ln/Rail2_ND.nd"
feature = "M:/RAIL/OngoingWork/newconnections/intermediate/feature_unlocked.shp" #i guess this is just a temporary layer/ no worries

arcpy.CheckOutExtension("Network")
arcpy.BuildNetwork_na(B1_ND) #because the Rail2_ND file may have been changed
print("Network Rebuilt")
arcpy.MakeRouteLayer_na(B1_ND, "Route", "Length")

allnodes = Dbf5( all_nodes + '.dbf').to_dataframe()
Links_Final2 = Dbf5(linksfinal + '.dbf').to_dataframe()

#creates a dictionary of two columns
def get_dictionary(columnA, columnB, dataframe_name):
   dict = {}
   for i in range(len(Links_Final2)):   
      dict[dataframe_name[columnA][i]] = []
      dict[dataframe_name[columnB][i]] = []
   for i in range(len(dataframe_name)):   
      dict[dataframe_name[columnA][i]].append(dataframe_name[columnB][i])
      dict[dataframe_name[columnB][i]].append(dataframe_name[columnA][i])
   return dict   

#(nodeID, nodeLayer, columnName) = (nodeID, SnappedNodes + ".shp", "NEAR_DIST")
def get_cell_value(nodeID, nodeLayer, columnName):
   layer = Dbf5(nodeLayer.split('.shp')[0]+ '.dbf').to_dataframe().set_index('ID')
   return layer[columnName][nodeID]

#nodeA and NodeB are integers 

#(nodeAlayer, nodeBlayer, nodeAColumnName, nodeBColumnName, nodeA, nodeB) = (MyNodes, all_nodes, "FID", "ID", bufferID, ID)  
def get_distance(nodeAlayer, nodeBlayer, nodeAColumnName, nodeBColumnName, nodeA, nodeB):
   #create a set of origin and destination FIPS to be loaded in the network analyst
   #print ("ArgGIS analyst: Job Received, ONODE: {0}, DNODE: {1} *".format(nodeA, nodeB)) # *these nodes are in different layers
   sys.stdout.write('.')
   arcpy.CheckOutExtension("Network")
   arcpy.Select_analysis(nodeAlayer + ".shp",o, '{0} = {1}'.format(nodeAColumnName, nodeA) )
   arcpy.Select_analysis(nodeBlayer + ".shp",d, '{0} = {1}'.format(nodeBColumnName, nodeB) )   
   arcpy.Merge_management([o, d], m)
   arcpy.AddLocations_na("Route", "Stops", m, "Name Name #", "5000 Kilometers", "", "B1 SHAPE;B1_ND_Junctions SHAPE", "MATCH_TO_CLOSEST", "CLEAR", "NO_SNAP", "5 Meters", "INCLUDE", "B1 #;B1_ND_Junctions #")
   try:
      arcpy.Solve_na("Route", "SKIP", "TERMINATE", "500 Kilometers")
      arcpy.SelectData_management("Route", "Routes")   
      arcpy.FeatureToLine_management("Route\\Routes", feature, "", "ATTRIBUTES")
   except:
      return 999999
   return ([f[0] for f in arcpy.da.SearchCursor(feature, 'SHAPE@LENGTH')][0])

#(nodeID, nodeLayer, columnName)=(NodeA, MyNodes, "ID")
def get_buffer_nodes_IDs(nodeID, nodeLayer, columnName):
   global buffer_dist #we are working on the global variable
   local_buffer_dist = buffer_dist
   nearest_old_node_dist = get_cell_value(nodeID, SnappedNodes + ".shp", "NEAR_DIST") #checking the nearest node is too close
   if nearest_old_node_dist < local_buffer_dist*1610: # 1 mile = 1610 meters
      local_buffer_dist = round(nearest_old_node_dist *0.0006,1)
      print("Buffer Distance changed to {0} Miles".format(local_buffer_dist))
   if local_buffer_dist == 0:
      local_buffer_dist = 0.1 #miles (buffer distance cant be 0)
   arcpy.Select_analysis(SnappedNodes + ".shp",temp, '{0} = {1}'.format(columnName, nodeID) )
   arcpy.Buffer_analysis(temp, temp1, "{0} Miles".format(local_buffer_dist), "FULL", "ROUND", "NONE", "", "PLANAR")
   arcpy.MakeFeatureLayer_management(nodeLayer + ".shp", 'feature_lyr')
   arcpy.SelectLayerByLocation_management('feature_lyr', "WITHIN", temp1, "", "NEW_SELECTION", "NOT_INVERT")
   arcpy.SpatialJoin_analysis ('feature_lyr', MyNodes + ".shp", temp2)
   return get_all_IDs(temp2)

def get_all_IDs (layerName):
   layer = Dbf5(layerName.split('.shp')[0] + '.dbf').to_dataframe()
   return list(set(list(layer['TARGET_FID'])))
   
   
#the program begins here  
   
#oldNode_newNode conversion dictionary
old_new_node_dictionary = {}

#get a dictionary of A_NODE and B_NODE
dictionary_of_old_nodes = get_dictionary("A_NODE", "B_NODE", Links_Final2)

#FIVE   
#get 5 values from the dictionary
#dictionary_of_old_nodes = {k:dictionary_of_old_nodes[k] for k in dictionary_of_old_nodes.keys()[:5]}


try:
   new_old_node_conversion = pandas.read_csv( newoldnodesconversion, index_col = 0, header = None)
   #remove if present in the dictionary
   for item in list(dictionary_of_old_nodes.keys()):
      if item in list(new_old_node_conversion.index.values):
         #print "{0}:{1} item deleted".format(item,dictionary_of_old_nodes[item])
         del dictionary_of_old_nodes[item]   
   #initial dataframe (if values already present)
   dataframe_of_the_dictionary = new_old_node_conversion
   for value in new_old_node_conversion.index:
      old_new_node_dictionary[value] = new_old_node_conversion[1][value]
except:
   print ("Oops.. new_old_node_conversion.csv not found. Creating an empty file.")
   emptydatabase = pandas.DataFrame()
   emptydatabase.to_csv(newoldnodesconversion, header = False)


#find near_fid and near_dist of SnappedNodes, overlaps the column, no need to drop existing, to check whether the nearest node is closer than 1 mile
arcpy.Near_analysis( SnappedNodes + ".shp",SnappedNodes + ".shp","","","","GEODESIC")
# arcpy.AlterField_management(SnappedNodes, field.name, 'NEAR_DIST', 'NEAR_DIST1')
# arcpy.Near_analysis( SnappedNodes + ".shp", MyNodes + ".shp","","","","GEODESIC")


for NodeA in dictionary_of_old_nodes:
   print "\n"
   print "Old Node = {0}".format(NodeA)
   IDs_Distance_Dict = {}
   bufferIDs = get_buffer_nodes_IDs(NodeA, MyNodes, "ID")
   print ("IDs within {0} Mile = {1}".format(buffer_dist,bufferIDs))
   if len(bufferIDs) in [0,1]: #if no or 1 node nearby
      old_new_node_dictionary[NodeA] = ""
      bufferIDs = [] #empty for not letting the subsequent for loops run
      IDs_Distance_Dict = {} #empty

   # for ID in bufferIDs:
      # IDs_Distance_Dict[ID] = 0
   for bufferID in bufferIDs:
      IDs_Distance_Dict[bufferID] = 0
      dist = 0
      for ID in dictionary_of_old_nodes[NodeA]: #if route not found, find route in the new layer with the new nodes
         currdist = get_distance(MyNodes, all_nodes, "FID", "ID", bufferID, ID)
         if currdist == 999999:
            print("Switching Layer..")
            currdist = get_distance(MyNodes, MyNodes, "FID", "FID", bufferID, ID)
            if currdist == 999999:
               print("Route not found, using Distance = 999999")
         dist += currdist
      IDs_Distance_Dict[bufferID] = dist
   for key, values in IDs_Distance_Dict.iteritems(): #print id and distance formatted
      print ("{0}: {1}".format(key,values))
   #print ("{0}".format(IDs_Distance_Dict))
   for key, values in IDs_Distance_Dict.iteritems():
      if values == min(IDs_Distance_Dict.values()):
         if values != max(IDs_Distance_Dict.values()): #if min = max, the change of position of the node does not reduce the overall distance (hence left unchanged)
            old_new_node_dictionary[NodeA] = key
         else:
            old_new_node_dictionary[NodeA] = "" #if max == min, just do nothing
   print ("Snapped to Node: {}".format(old_new_node_dictionary[NodeA])) #can be empty value
   dataframe_of_the_dictionary = pandas.DataFrame.from_dict(data= old_new_node_dictionary, orient = 'index')
   dataframe_of_the_dictionary.to_csv(newoldnodesconversion, header = False)

print("Node Conversion complete")



where






