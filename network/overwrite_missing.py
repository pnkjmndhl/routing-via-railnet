from rail import *
import arcpy
import pandas
import re
# import geopandas


from rail import *
import arcpy
import pandas as pd
import numpy as np


all_field_names = [x.name for x in arcpy.ListFields(link_shp)]
rr_field_names = [x for x in all_field_names if re.match(r'RR\d', x)]

input = link_shp
field_names = [f.name for f in arcpy.ListFields(input)]
arr = arcpy.da.TableToNumPyArray(input, field_names[2:])
link_shp_df = pandas.DataFrame(arr)  # 1st row as the column names
link_shp_df.to_csv("network/intermediate/before_autogen.csv")


def get_colnames_from_autogen(auto_flag):
    flag_to_colname = {0: "SIGNAL", 1: "FF_SPEED", 2: "CAPY_CODE", 3: "NO_TRACKS", 4: "LINK_TYPE", 5: "RR1"}
    string_auto_flag = str(auto_flag)
    a_list = []
    for digit in string_auto_flag:
        a_list.append(int(digit))
    index_of_missing = [i for i, e in enumerate(a_list) if e == 1]
    return [flag_to_colname[x] for x in index_of_missing]


def get_nodes(ID):
    return [list(link_shp_df[link_shp_df.ID == ID]['A_NODE'])[0], list(link_shp_df[link_shp_df.ID == ID]['B_NODE'])[0]]


def get_connecting_link(ID):
    link_list = []
    abnode = get_nodes(ID)
    for node in abnode:
        link_list.extend(list(link_shp_df[link_shp_df.A_NODE == node]['ID']))
        link_list.extend(list(link_shp_df[link_shp_df.B_NODE == node]['ID']))
    link_list = list(set(link_list))
    link_list.remove(ID)
    return link_list


def get_nearby_attributes_list(colname, links_list):
    attribute_list = []
    if colname == 'RR1':
        for id in links_list:
            for rr in rr_field_names:
                attribute_list.extend(list(link_shp_df[link_shp_df.ID == id][rr]))
                attribute_list = list(set(attribute_list))
        #print "{0}".format(attribute_list)
    else:
        for id in links_list:
            attribute_list.extend(list(link_shp_df[link_shp_df.ID == id][colname]))
    if 0 in attribute_list: attribute_list.remove(0)
    return attribute_list


def get_singular_attribute(column_name, attribute_list):
    signal_order = {1: 1, 2: 2, 3: 4, 4: 0, 5: -1}  # CTC, ABS, non signalled
    tracks_order = {1: 4, 2: 2, 3: 3, 4: 1, 5: 0, 6: -1}  # 4,3,2,1
    linktype_order = {1: 4, 2: 3, 3: 2, 4: 1, 5: 0, 6: -1}  # multiple bi, multiple di, single bi, single di
    capacity_order = {1: 1, 2: 5, 3: 9, 4: 2, 5: 6, 6: 10, 7: 3, 8: 7, 9: 11, 10: 4, 11: 8, 12: 12, 13: 0, 14: -1}
    # ff speed greater taken
    # idk how the railroad would be taken
    # empty arguments
    try:
        max(attribute_list)
    except:
        attribute_list.append(0)
    if column_name == "SIGNAL":
        return get_preferred_attribute(signal_order, attribute_list)
    if column_name == "NO_TRACKS":
        return get_preferred_attribute(tracks_order, attribute_list)
    if column_name == "CAPY_CODE":
        return get_preferred_attribute(capacity_order, attribute_list)
    if column_name == "FF_SPEED":
        return max(attribute_list)
    if column_name == "LINK_TYPE":
        return get_preferred_attribute(linktype_order, attribute_list)
    if column_name == "RR1":
        return attribute_list


def get_preferred_attribute(mydict, mylist):  # return the max value in the list based on the dictionary
    my_list_ordered = []
    for value in mylist:
        my_list_ordered.append({y: x for x, y in mydict.iteritems()}[value])
    try:
        return mydict[min(my_list_ordered)]
    except:
        return 0  # Error: min()arg is an empty sequene, So,... exception was handled


def generate_missing(colname, linkID):
    links_list = get_connecting_link(linkID)
    attributes = get_nearby_attributes_list(colname, links_list)
    attributes = [x for x in attributes if str(x) != 'nan'] #removing nan
    attribute = get_singular_attribute(colname, attributes)
    return attribute


for i in range(len(link_shp_df)):
    autogen = link_shp_df['AutoFlag_'][i]
    if autogen == 0:
        continue
    else:
        colnames_list = get_colnames_from_autogen(autogen)
        for column in colnames_list:
            attribute = generate_missing(column, link_shp_df['ID'][i])
            if column != "RR1":
                link_shp_df[column][i] = int(attribute)
            else:
                print "linkID: {0} RR:{1}".format(link_shp_df["ID"][i],attribute)
                for j in range(len(attribute)):
                    link_shp_df["RR" + str(j + 1)][i] = int(attribute[j])
                for j in range(len(attribute),len(rr_field_names)): #remaining should be set to 0
                    link_shp_df["RR" + str(j + 1)][i] = 0

        # link_shp_df[column][i] = generate_missing(column, link_shp_df['ID'][i])

link_shp_df.to_csv("network/intermediate/after_autogen.csv")

print ("Auto generating attributes based on ambience ...")
column_list = ["ID", "SIGNAL", "FF_SPEED", "CAPY_CODE", "NO_TRACKS", "LINK_TYPE", "RR1", "RR2", "RR3", "RR4", "RR5",
               "RR6", "RR7"]
with arcpy.da.UpdateCursor(link_shp, column_list) as cursor:
    for row in cursor:
        for i in range(len(column_list) - 1):
            row[i + 1] = list(link_shp_df[link_shp_df.ID == row[0]][column_list[i + 1]])[0]
        cursor.updateRow(row)
