from rail import *
from geopy.geocoders import Nominatim
import arcpy
import math

arcpy.env.overwriteOutput = True


address_df = pandas.read_csv(ofips_orr_comm)
geolocator = Nominatim(user_agent="pnkjmndhl")

to_calc_onode_df = address_df[address_df.NODE.isnull()]

for index in to_calc_onode_df.index.values:
    location = geolocator.geocode(to_calc_onode_df.loc[index]['Address'])
    to_calc_onode_df['lon_x'][index] = location.longitude
    to_calc_onode_df['lat_y'][index] = location.latitude

points = arcpy.Point()
point_geometry = []

for index in to_calc_onode_df.index.values:
    points.X = to_calc_onode_df.loc[index]['lon_x']
    points.Y = to_calc_onode_df.loc[index]['lat_y']
    point_geometry.append(arcpy.PointGeometry(points))


arcpy.CopyFeatures_management(point_geometry, disk_shp)
arcpy.Near_analysis(disk_shp,node_shp)
fid_to_near_fid = {row.getValue("FID"):row.getValue("NEAR_FID") for row in arcpy.SearchCursor(disk_shp)}
nodeFID_to_nodeID = {row.getValue("FID"): row.getValue("ID") for row in arcpy.SearchCursor(node_shp)}
for keys,values in fid_to_near_fid.iteritems():
    fid_to_near_fid.update({keys: nodeFID_to_nodeID[values]})

nodesList = [y for x,y in fid_to_near_fid.iteritems()]
to_calc_onode_df['NODE'] = nodesList

for index in to_calc_onode_df.index.values:
    address_df.set_value(index,['NODE'], to_calc_onode_df.loc[index]['NODE'])

address_df.to_csv("new.csv")