from rail import *
import arcpy
import os


arcpy.env.overwriteOutput = True

# excelfile


# inputs from shapefiles
linkshp = r"..\GIS\alllinks.shp"

# 1: 'RR-Code'
# 2: 'Commod.',
# 3: 'TrainCost/hr'
# 4: 'Cost/gross-ton-mile',
# 5: 'terminal-processing-cost/car,fixed',
# 6: 'terminal-cost/car-hr',
# 7: 'transfer-cost/car',
# 8: 'car-payload',
# 9: 'car-tare-wt',
# 10: 'Gross Car Weight',
# 11: 'Cars per Train',
# 12: 'Gross Train Weight'

add = 50  # 10 columns for cost Attribute file [additional value for empty rail]
CA = pandas.ExcelFile(cost_xl).parse(cost_xl_sheet)


def getnetworkRRs():
    dumm1 = [[row.getValue("RR1"), row.getValue("RR2"), row.getValue("RR3"), row.getValue("RR4"), row.getValue("RR5")]
             for row in arcpy.SearchCursor(linkshp)]
    flat_list = list(set([x for sublist in dumm1 for x in sublist]))
    flat_list.remove(0)
    return flat_list


CA.columns = [['1', '13', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']]
CA = CA[['1', '2', '3', '4', '5', '6', '7', '8', '9', '12']]

CA['1'] = CA['1'].astype(int)
CA['2'] = CA['2'].astype(int)

# add the railroads not in the cost file (shortline 6 AA, is used as a sample for all unknown values)
allshortlinesDF = CA[CA['1'] == 6]
allRRsinCA = set(CA['1'].astype(int).tolist())
RRstoadd = set(getnetworkRRs()) - allRRsinCA

RRstoaddDF = pandas.DataFrame()
for RRs in RRstoadd:
    allshortlinesDF['1'] = RRs
    RRstoaddDF = RRstoaddDF.append(allshortlinesDF, ignore_index=True)

CA = CA.append(RRstoaddDF, ignore_index=True)

# empty CA default values
emptyCA = CA.copy(deep=True)
emptyCA['2'] = emptyCA['2'] + add  # 2: 'Commod.',
emptyCA['3'] = 297.71  # 3: 'TrainCost/hr'
emptyCA['4'] = 0.055  # 4: 'Cost/gross-ton-mile',
emptyCA['5'] = 60.99  # 5: 'terminal-processing-cost/car,fixed',
emptyCA['6'] = 1.99  # 6: 'terminal-cost/car-hr',
emptyCA['7'] = 18.12 * 1.25  # 7: 'transfer-cost/car',
emptyCA['8'] = CA['9']  # 8: 'car-payload' (since payload = tare wt)
emptyCA['9'] = 0  # 9: 'car-tare-wt' = 0

emptyCA['12'] = CA['9'] * CA['12'] / (CA['8'] + CA['9'])

CA = CA.append(emptyCA).reset_index()[['1', '2', '3', '4', '5', '6', '7', '8', '9', '12']]

# changing the formatting
CA['1'] = CA['1'].astype(int)
CA['2'] = CA['2'].astype(int)

CA['1'] = CA['1'].map('{:3d}'.format)
CA['2'] = CA['2'].map('{:5d}'.format)
CA['3'] = CA['3'].map('{:10.2f}'.format)
CA['4'] = CA['4'].map('{:10.2f}'.format)
CA['5'] = CA['5'].map('{:10.2f}'.format)
CA['6'] = CA['6'].map('{:10.2f}'.format)
CA['7'] = CA['7'].map('{:10.2f}'.format)
CA['8'] = CA['8'].map('{:5.1f}'.format)
CA['9'] = CA['9'].map('{:5.1f}'.format)
CA['12'] = CA['12'].map('{:10.1f}'.format)

# combine all the columns to one
CA = CA[['1', '2', '3', '4', '5', '6', '7', '8', '9', '12']].apply(
    lambda x: '  {}{}{}{}{}{}{}{}{}{}'.format(x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8], x[9]), axis=1)

CA.to_csv(r"output\cost.dat", index=False)

print("OPERATION SUCCESSFULL. cost.dat written")
