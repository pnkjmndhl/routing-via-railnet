# this program assigns railroads to links using the railroads online.
# uses completely within buffer type

import arcpy
import pandas
from simpledbf import Dbf5

arcpy.env.workspace = r"C:\GIS"
arcpy.env.overwriteOutput = True  # overwrite files if its already present

bufferDistance = "3 Miles"

rootDirectory = 'Z:\\Thesis\\Coal Data\\downloadedonline\\'

listRRs = ['UP', "BNSF", "NS", "KCS", "CSXT", "CP", "CN"]
RRCols = ['RR1', 'RR2', 'RR3', 'RR4', 'RR5', 'RR6', 'RR7']
RRcodes = [802, 777, 555, 400, 712, 105, 103]

# Local variables:
NewLinks = "M:\\RAIL\\OngoingWork\\NewLinks.shp"
# railroads
NewLinksDbf = "M:\\RAIL\\OngoingWork\\NewLinks.dbf"
network = Dbf5(NewLinksDbf).to_dataframe()
network = network[RRCols]


def AddColumn(colName):
    arcpy.DeleteField_management(NewLinks, colName)
    arcpy.AddField_management(NewLinks, colName, "Double")
    i = 0
    with arcpy.da.UpdateCursor(NewLinks, colName) as cursor:
        for row in cursor:
            row[0] = network[colName][i]
            i += 1
            cursor.updateRow(row)
    print("{0} was updated".format(colName))


def getnext(j, i):
    if network[RRCols[j]][i] == 0:
        # print("{0},{1} = 0".format(j,i))
        if j < len(RRCols) - 1:
            return (getnext(j + 1, i))
        else:
            return 0
    else:
        dumm = network[RRCols[j]][i]
        network[RRCols[j]][i] = 0
        # print ("found greater {0}".format(dumm))
        return dumm


for i in range(len(listRRs)):
    print("Finding links for {0}...".format(listRRs[i]))
    railroad = 'Z:\\Thesis\\Coal Data\\downloadedonline\\' + listRRs[i] + '.shp'
    Buffer = "C:\\GIS\\Buffer.shp"
    # create buffer layerProcess: Buffer
    arcpy.Buffer_analysis(railroad, Buffer, bufferDistance, "FULL", "ROUND", "NONE", "", "PLANAR")
    # select on NewLinks
    arcpy.MakeFeatureLayer_management(NewLinks, 'NewLinks_lyr')
    arcpy.SelectLayerByLocation_management('NewLinks_lyr', "COMPLETELY_WITHIN", Buffer, "", "NEW_SELECTION",
                                           "NOT_INVERT")
    count = arcpy.GetCount_management('NewLinks_lyr')
    print("Total number of selected links = {0}".format(count))
    arcpy.CalculateField_management('NewLinks_lyr', RRCols[i], RRcodes[i], "PYTHON")
    print("Values for {0} railroad updated".format(listRRs[i]))
    print("Process Completed Successfully")

# left justify all the RRs
for i in range(len(network)):
    for j in range(len(RRCols)):
        if (network[RRCols[j]][i] == 0):
            network[RRCols[j]][i] = getnext(j, i)
            if network[RRCols[j]][i] == 0:
                break
            # print("obtained value from getnext = {0}".format(network[RRCols[j]][i]))

    print("Row {0} completed".format(i))

# write the new columns to the dbf file
for col in RRCols:
    AddColumn(col)
