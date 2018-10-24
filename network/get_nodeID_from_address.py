from rail import *
from geopy.geocoders import Nominatim
import arcpy
import math

arcpy.env.overwriteOutput = True

address_df = pandas.read_csv(ofips_orr_comm)
geolocator = Nominatim(user_agent="railnet")

nodeFID_to_nodeID = {row.getValue("FID"): row.getValue("ID") for row in arcpy.SearchCursor(node_shp)}


def get_XY(address):
    location = geolocator.geocode(address)
    return location.longitude, location.latitude


def get_node(X, Y):
    points = arcpy.Point()
    point_geometry = []
    points.X = X
    points.Y = Y
    point_geometry.append(arcpy.PointGeometry(points))
    arcpy.CopyFeatures_management(point_geometry, disk_shp)
    arcpy.Near_analysis(disk_shp, node_shp)
    near_fid = [row.getValue("NEAR_FID") for row in arcpy.SearchCursor(disk_shp)][0]
    nodeID = nodeFID_to_nodeID[near_fid]
    return nodeID


# get all coordinates
for index in address_df.index.values:
    if math.isnan(address_df['lon_x'][index]):
        address_df['lon_x'][index], address_df['lat_y'][index] = get_XY(address_df['Address'][index])

# get all nodes
for index in address_df.index.values:
    address_df['NODE'][index] = get_node(address_df['lon_x'][index], address_df['lat_y'][index])


address_df.to_csv(ofips_orr_comm)
