import pandas
import arcpy
from simpledbf import Dbf5
import sys
import os


scenario_list = os.listdir('intermediate/')
scenario_list = [x.split('-')[1].split('.')[0] for x in scenario_list if "OD1" in x]

# change the encoding to utf-8
reload(sys)
sys.setdefaultencoding('utf-8')

# overwrite files if its already present
arcpy.env.overwriteOutput = True
# arcpy.env.workspace = "C:\\GIS"


# inputs from files
FIPS = r"..\GIS\standards\FIPS.shp"
nodeshp = r"..\GIS\allnodes.shp"
linkshp = r"..\GIS\alllinks.shp"

#################work on copies####################
FIPS1 = "C:/GIS/FIPS.shp"
nodeshp1 = "C:/GIS/allnodes.shp"
linkshp1 = "C:/GIS/alllink.shp"
arcpy.CopyFeatures_management(FIPS, FIPS1)
arcpy.CopyFeatures_management(nodeshp, nodeshp1)
arcpy.CopyFeatures_management(linkshp, linkshp1)
FIPS = FIPS1
nodeshp = nodeshp1
linkshp = linkshp1

# search distance
dist = "100 Miles"



linkshpf = "linkshp_lyr"
FIPSf = "FIPS_lyr"
nodeshpf = "nodeshp_lyr"

arcpy.MakeFeatureLayer_management(linkshp, linkshpf)
arcpy.MakeFeatureLayer_management(FIPS, FIPSf)
arcpy.MakeFeatureLayer_management(nodeshp, nodeshpf)

FIPSDBF = pandas.DataFrame()
try:
    OFIPSORR = pandas.read_csv(r"intermediate\OFIPSORR.csv")
except:
    OFIPSORR = pandas.DataFrame({"OFIPS": [], "startRR": [], "ONODE": [], "ODIST": []})


# OFIPS = 40063
# OriginRR = 802
# getNearestORRNode(40063, 802)

def getnetworkRRs():
    dumm1 = [[row.getValue("RR1"), row.getValue("RR2"), row.getValue("RR3"), row.getValue("RR4"), row.getValue("RR5")]
             for row in arcpy.SearchCursor(linkshp)]
    flat_list = list(set([x for sublist in dumm1 for x in sublist]))
    flat_list.remove(0)
    return flat_list


# OFIPS = 26147
# OriginRR = 103 
# getNearestORRNode(17091, 103)
def getNearestORRNode(OFIPS, OriginRR):
    global OFIPSORR
    # if present in dataframe, return
    onodeofips = OFIPSORR[(OFIPSORR.OFIPS == OFIPS) & (OFIPSORR.startRR == OriginRR)]
    if not onodeofips.empty:
        return [list(onodeofips['ONODE'])[0], list(onodeofips['ODIST'])[0]]
    where_clause = "\"RR1\" = " + str(OriginRR) + " OR \"RR2\" = " + str(OriginRR) + " OR \"RR3\" = " + str(
        OriginRR) + " OR \"RR4\" = " + str(OriginRR) + " OR \"RR5\" = " + str(OriginRR)
    if OriginRR != 0:  # if the originRR == nan, then no need to do the selection based on the railroad
        arcpy.SelectLayerByAttribute_management(linkshpf, "NEW_SELECTION", where_clause)
    else:
        arcpy.SelectLayerByAttribute_management(linkshpf, "NEW_SELECTION")
    try:
        arcpy.FeatureVerticesToPoints_management(linkshpf, "in_memory/p1", "BOTH_ENDS")
        arcpy.MakeFeatureLayer_management("in_memory/p1", "p1")
        arcpy.SelectLayerByAttribute_management(FIPSf, "NEW_SELECTION", """ "FIPS" = %d""" % OFIPS)  # wtf??
        arcpy.SpatialJoin_analysis(FIPSf, "p1", "in_memory/p2", "", "", "", "CLOSEST", "", "")
        arcpy.Near_analysis(FIPSf, "p1", "", "NO_LOCATION", "NO_ANGLE", "GEODESIC")
        dumm = {row.getValue("NEAR_FID"): row.getValue("NEAR_DIST") for row in arcpy.SearchCursor(FIPSf)}
        arcpy.SelectLayerByAttribute_management("p1", "NEW_SELECTION", """ "FID" = %d""" % dumm.keys()[0])
        arcpy.Near_analysis("p1", nodeshpf, "", "NO_LOCATION", "NO_ANGLE", "GEODESIC")
        dumm1 = [row.NEAR_FID for row in arcpy.SearchCursor("in_memory/p1")]
        dumm1 = filter(lambda a: a != -1, dumm1)
        allFID = {row.getValue("FID"): row.getValue("ID") for row in arcpy.SearchCursor(nodeshpf)}
        onode = allFID.get(dumm1[0])
        odist = dumm.values()[0] / 1609.34
        OFIPSORR = OFIPSORR.append({"OFIPS": OFIPS, "startRR": OriginRR, "ONODE": onode, "ODIST": odist},
                                   ignore_index=True)
        return [onode, odist]  # converting meters to miles
    except:
        return [-99, -99]


def getNearestNode(fips):
    global FIPSDBF
    try:
        return FIPSDBF.loc[fips]['nodeshpID']
    except:
        pass
    else:
        return -99


def updateNearestNode():  # lets hope that the GIS file and dataframe have the same index everytime
    global FIPSDBF
    arcpy.Near_analysis(FIPS, nodeshp, "", "NO_LOCATION", "NO_ANGLE", "GEODESIC")
    FIPSDBF = Dbf5(FIPS.split(".shp")[0] + '.dbf').to_dataframe().set_index("FIPS")
    nodeshpDBF = Dbf5(nodeshp.split(".shp")[0] + '.dbf').to_dataframe()
    FIPSDBF['nodeshpID'] = FIPSDBF['NEAR_FID'].map(nodeshpDBF.ID)


# OD = OD.head(10000)
updateNearestNode()


for scenario in scenario_list:
    # read csv file
    OD = pandas.read_csv(r"intermediate\OD1-" + scenario + ".csv")
    OD['ODIST'] = 0.0
    print("Working on " + scenario)

    # if the startRR is not in our network, add np.nan
    rrlist = getnetworkRRs()
    OD['startRR'][~OD.startRR.isin(rrlist)] = 0

    for i in range(0, len(OD)):
        OD['ONode'][i], OD['ODIST'][i] = getNearestORRNode(OD.at[i, 'OFIPS'], OD.at[i, 'startRR'])
        OD['DNode'][i] = getNearestNode(OD.at[i, 'DFIPS'])
        print ("{0}:	OFP:{1}	sRR:{3}	OND:{4}	DIST:{5}".format(i, OD.at[i, 'OFIPS'], OD.at[i, 'DFIPS'],
                                                                          OD.at[i, 'startRR'], OD['ONode'][i],
                                                                          OD['ODIST'][i]))
    OD.to_csv(r"intermediate\OD2-" + scenario + ".csv")
    OD.to_csv(r"..\Module1(commodity)\input\scenario\OD2-" + scenario + ".csv")
