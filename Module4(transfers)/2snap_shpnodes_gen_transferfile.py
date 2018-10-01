import pandas
import arcpy
from simpledbf import Dbf5
import itertools

arcpy.env.overwriteOutput = True

# inputs from files
transfer_shp = r"../GIS/transfers.shp"
transfer_manual_shp = r"../GIS/manualtransfers.shp"
node_shp = r"../GIS/allnodes.shp"
link_shp = r"../GIS/alllinks.shp"
transfer_table = r"C:/GIS/transfertable.dbf"

node_shp_f = r"nodeshp"
link_shp_f = r"linkshp"

closest_count = 30  # search for start railroad for the first closest_count nodes, if not found, ignore the transfer

arcpy.MakeFeatureLayer_management(node_shp, node_shp_f)
arcpy.MakeFeatureLayer_management(link_shp, link_shp_f)


def get_link_railroad_table():
    dummy = {row.getValue("ID"): [row.getValue("RR1"), row.getValue("RR2"), row.getValue("RR3"), row.getValue("RR4"),
                                  row.getValue("RR5")] for row in arcpy.SearchCursor(link_shp)}
    link_railroads_df = pandas.DataFrame(
        {"LinkID": dummy.keys(), "RRs": dummy.values(), "RR1": [x[0] for x in dummy.values()],
         "RR2": [x[1] for x in dummy.values()], "RR3": [x[2] for x in dummy.values()],
         "RR4": [x[3] for x in dummy.values()], "RR5": [x[4] for x in dummy.values()]})
    return link_railroads_df


def get_node_link_table_dictionary():
    dummy = {row.getValue("ID"): [row.getValue("A_NODE"), row.getValue("B_NODE")] for row in
             arcpy.SearchCursor(link_shp)}
    df = pandas.DataFrame(
        {"ID": dummy.keys(), "A_NODE": [x[0] for x in dummy.values()], "B_NODE": [x[1] for x in dummy.values()]})
    all_nodes = list(set(list(df['A_NODE']) + list(df['B_NODE'])))
    dictionary_new = {}
    for value in all_nodes:
        dictionary_new[value] = df[(df['A_NODE'] == value) | (df['B_NODE'] == value)]['ID'].tolist()
    node_link_table_df = pandas.DataFrame(dictionary_new.items(), columns=["NodeID", "LinkID"])
    return node_link_table_df


# generate near table for closest_count
def generate_near_table_df():  # uses node_shp and transfer_shp
    arcpy.GenerateNearTable_analysis(transfer_shp, node_shp, transfer_table, "", "", "", "ALL", closest_count,
                                     "GEODESIC")
    df = Dbf5(transfer_table).to_dataframe()
    fid_to_id = {row.getValue("FID"): row.getValue("ID") for row in arcpy.SearchCursor(node_shp)}
    fid_to_id_df = pandas.DataFrame(fid_to_id, index=[0]).transpose().reset_index()
    fid_to_id_df.columns = ["FID", "ID"]
    df = df.merge(fid_to_id_df, left_on='NEAR_FID', right_on='FID')
    df['NEAR_DIST'] = df['NEAR_DIST'] / 1609.34
    return df


def add_list(current_list, add_list):
    for i in range(len(current_list)):
        current_list = current_list + [(x, y) for x in current_list[i] for y in add_list]
    return current_list


def create_railroads_list(dictionary_link_ids):
    rr_list = []
    length = len(dictionary_link_ids.keys())
    if length > 1:
        rr_list = [(x, y) for x in dictionary_link_ids.values()[0] for y in dictionary_link_ids.values()[1]]
    if length > 2:
        for i in range(2, length):
            rr_list = add_list(rr_list, dictionary_link_ids.values()[i])
    for x in rr_list:  # remove duplicates
        if x[0] == x[1]:
            rr_list.remove(x)
    s = []
    for i in rr_list:
        if i not in s:
            s.append(i)
    return s


# list_of_link_ids = [9002, 9005, 9006]
def get_transfer_lists(list_of_link_ids):
    dictionary_link_ids = {}
    for link_ids in list_of_link_ids:
        railroad_list = [item for sublist in list(link_rr_df[link_rr_df.LinkID == link_ids]['RRs']) for item in sublist]
        dictionary_link_ids.update({link_ids: railroad_list})
    for link_id in dictionary_link_ids.keys():  # remove if duplicates or 0 present
        dictionary_link_ids[link_id] = list(set(dictionary_link_ids[link_id]))
        if 0 in dictionary_link_ids[link_id]: dictionary_link_ids[link_id].remove(0)
    # delete links with same RRs and empty RRs
    new_list = {}
    for key, value in dictionary_link_ids.items():
        if value not in new_list.values() and value != []:
            new_list[key] = value
    return create_railroads_list(new_list)


# check if the railroad is in the network shape file
def check_id(node_id, rr1, rr2):
    list_of_rrs = (node_link_df[node_link_df.NodeID == node_id]['transferslist']).tolist()
    flat_list = [item for sublist in list_of_rrs for item in sublist]
    if (rr1, rr2) in flat_list or (rr2, rr1) in flat_list:
        return 1
    else:
        return 0


# get the nearest node from the FIPS
def get_nearest_node(fid, rr1, rr2):
    dummy = transfer_node_df[transfer_node_df.IN_FID == fid]
    for i in range(1, closest_count + 1):
        if check_id(int(dummy[dummy.NEAR_RANK == i]['ID']), rr1, rr2) == 1:
            return [int(dummy[dummy.NEAR_RANK == i]['ID']), float(dummy[dummy.NEAR_RANK == i]['NEAR_DIST'])]
        else:
            continue
    return [-99, -99]


# add manually added transfers from manual transfers shapefile
def add_manuals():
    manual_shp_list = []
    arcpy.Near_analysis(transfer_manual_shp, node_shp, "", "NO_LOCATION", "NO_ANGLE", "GEODESIC")
    manual_shp_dictionary = {row.getValue("FID"): [row.getValue("RR1"), row.getValue("RR2"), row.getValue("NEAR_FID")]
                             for row in arcpy.SearchCursor(transfer_manual_shp)}
    near_fid_to_node_id_dictionary = {row.getValue("FID"): row.getValue("ID") for row in arcpy.SearchCursor(node_shp)}
    for key, value in manual_shp_dictionary.iteritems():
        manual_shp_dictionary[key][2] = near_fid_to_node_id_dictionary[manual_shp_dictionary[key][2]]
    for key, value in manual_shp_dictionary.iteritems():
        a = []
        a.append(key)
        a = a + value
        manual_shp_list.append(a)
    manual_shp_df = pandas.DataFrame(manual_shp_list)
    manual_shp_df.columns = [["??", "FROM", "TO", "ID"]]
    manual_shp_df['BIDIR'] = 2
    manual_shp_df = manual_shp_df[['ID', 'FROM', 'TO', 'BIDIR']]
    return manual_shp_df


# main program
transfer_node_df = generate_near_table_df()
node_link_df = get_node_link_table_dictionary()
link_rr_df = get_link_railroad_table()

node_link_df['transferslist'] = ""
for i in range(len(node_link_df)):
    print (node_link_df['LinkID'][i])
    node_link_df['transferslist'][i] = get_transfer_lists(node_link_df['LinkID'][i])

arcpy.DeleteField_management(transfer_shp, "nearNID")
arcpy.DeleteField_management(transfer_shp, "nearNDist")
arcpy.AddField_management(transfer_shp, "nearNID", "LONG", "")
arcpy.AddField_management(transfer_shp, "nearNDist", "DOUBLE", "")

with arcpy.da.UpdateCursor(transfer_shp, ["FID", "nearNID", "nearNDist", "JRR1NO", "JRR2NO"]) as cursor:
    for row in cursor:
        row[1], row[2] = get_nearest_node(row[0], row[3], row[4])
        print "FID:" + str(row[0]) + "    NearNID:" + str(row[1]) + "       NearDIST " + str(row[2])
        cursor.updateRow(row)

# shapefile to dataframe
my_dict = {"ID": [], "FROM": [], "TO": [], "BIDIR": []}
with arcpy.da.UpdateCursor(transfer_shp, ["nearNID", "JRR1NO", "JRR2NO"]) as cursor:
    for row in cursor:
        if row[0] >= 0:  # removing -99s
            my_dict["ID"].append(row[0])
            my_dict["FROM"].append(row[1])
            my_dict["TO"].append(row[2])
            my_dict["BIDIR"].append(2)

new_transfer = pandas.DataFrame(my_dict)
# new_transfer = newtransfer[new_transfer.nearNID != -99]  # remove -99

# add manual
new_transfer = new_transfer.append(add_manuals())

new_transfer.ID = new_transfer.ID.astype(int)
new_transfer.FROM = new_transfer.FROM.astype(int)
new_transfer.TO = new_transfer.TO.astype(int)
new_transfer.BIDIR = new_transfer.BIDIR.astype(int)

# create formatted output
new_transfer['ID'] = new_transfer['ID'].map('{:5d}'.format)
new_transfer['FROM'] = new_transfer['FROM'].map('{:5d}'.format)
new_transfer['TO'] = new_transfer['TO'].map('{:5d}'.format)
new_transfer['BIDIR'] = new_transfer['BIDIR'].map('{:5d}'.format)

new_transfer = new_transfer[['ID', 'FROM', 'TO', 'BIDIR']].apply(lambda x: '{}{}{}{}'.format(x[0], x[1], x[2], x[3]),
                                                                 axis=1)
new_transfer.to_csv(r"output\network.xfr", index=False)
