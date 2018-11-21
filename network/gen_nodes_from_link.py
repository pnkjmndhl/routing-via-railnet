from rail import *
import arcpy
import math

arcpy.env.overwriteOutput = True

temp1 = "in_memory/t1"
temp2 = "in_memory/t2"
temp3 = "in_memory/t3"
temp4 = "C:/GIS/allnodes.shp"


arcpy.GeneratePointsAlongLines_management(link_shp, temp1, 'PERCENTAGE', Percentage = 100,
                                          Include_End_Points='END_POINTS')
print ("End Points Generated")

drop_field = arcpy.ListFields (temp1)

drop_field = [x.name for x in drop_field if x.name not in ['FID', 'OID', 'Shape']]

arcpy.DeleteField_management (temp1, drop_field)

arcpy.AddXY_management(temp1)
arcpy.CalculateField_management (temp1, "POINT_X", "math.ceil(!POINT_X!*10000)/10000", "PYTHON")
arcpy.CalculateField_management (temp1, "POINT_Y", "math.ceil(!POINT_Y!*10000)/10000", "PYTHON")

arcpy.Dissolve_management(temp1, temp2, ['POINT_X', 'POINT_Y'], "", "SINGLE_PART", "UNSPLIT_LINES")
arcpy.AddField_management(temp2, "ID",field_type="Integer")
arcpy.DeleteIdentical_management(temp2, ['POINT_X', 'POINT_Y'])



arcpy.CopyFeatures_management(temp2,temp4)

