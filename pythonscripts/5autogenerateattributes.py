from rail import *

arcpy.MakeFeatureLayer_management(link_shp, link_shp_feature)

# functions
def change_value(column_name, ID, value, action):
    with arcpy.da.UpdateCursor(link_shp, ['ID', column_name]) as cursor:
        for row in cursor:
            if row[0] == ID:
                if action == "add":
                    row[1] = row[1] + value
                if action == "remove":
                    row[1] = row[1] - value
                if action == "change":
                    row[1] = value
            cursor.updateRow(row)


def select_touching():
    arcpy.SelectLayerByLocation_management(link_shp_feature, 'BOUNDARY_TOUCHES', link_shp_feature, "", "NEW_SELECTION",
                                           "NOT_INVERT")


def get_all_attributes(column_name):
    column_name = [column_name]
    attribute_list = []
    if column_name == ['RR1']:
        column_name = ['RR1', 'RR2', 'RR3', 'RR4', 'RR5', 'RR6', "RR7"]
    with arcpy.da.SearchCursor(link_shp_feature, column_name) as cursor:
        for row in cursor:
            for i in range(len(column_name)):
                attribute_list.append(row[i])
    attribute_list = list(set(attribute_list))
    try:
        attribute_list.remove(0)
    except:
        pass
    return attribute_list


def get_preferred_attribute(mydict, mylist):  # return the max value in the list based on the dictionary
    my_list_ordered = []
    for value in mylist:
        my_list_ordered.append({y: x for x, y in mydict.iteritems()}[value])
    try:
        return mydict[min(my_list_ordered)]
    except:
        return 0  # Error: min()arg is an empty sequene, So,... exception was handled


def calculate_missing_attribute(column_name, attribute_list):
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


def update_attributes(column_name,id):
    column_name_to_flag = {"SIGNAL": 100000, "FF_SPEED": 10000, "CAPY_CODE": 1000,
                           "NO_TRACKS": 100, "LINK_TYPE": 10, "RR1": 1}
    default_values_dictionary = {"SIGNAL": 2, "FF_SPEED": 40, "CAPY_CODE": 3, "NO_TRACKS": 2, "LINK_TYPE": 2}
    calculated_value = calculate_missing_attribute(column_name, get_all_attributes(column_name))
    if calculated_value == 0:  # didnt find any links with known attributes around
        calculated_value = default_values_dictionary.get(column_name)
        print("Default Values for {0} given to LinkID: {1}".format(column_name,id))
    # if column_name = RR1, calculated_value returns a list
    if column_name != "RR1":  # for any other attribute, value is simply assigned
        change_value(column_name, id, calculated_value, "change")
    else:  # for RR1
        for i in range(len(calculated_value)):
            change_value("RR" + str(i + 1), id, calculated_value[i], "change")
    # add the respective autoflag value
    change_value("AutoFlag_", id, column_name_to_flag[column_name], "add" )


# returns the indexes of missing columns
def get_indexes_of_missing(row):
    return [i for i in range(len(row)) if row[i] == 0]


def get_auto_generated_column_indexes(auto_flag):
    string_auto_flag = str(auto_flag)
    a_list = []
    for digit in string_auto_flag:
        a_list.append(int(digit))
    index_of_missing = [i for i, e in enumerate(a_list) if e == 1]
    return index_of_missing


def remove_attributes_if_autogenerated():
    allcolumn_names = ["SIGNAL", "FF_SPEED", "CAPY_CODE", "NO_TRACKS", "LINK_TYPE", "RR1", "RR2", "RR3", "RR4", "RR5", "RR6", "AutoFlag_"]
    with arcpy.da.UpdateCursor(link_shp, allcolumn_names) as cursor:
        for row in cursor:
            auto_flag = row[11]
            autoflag_column_indexes = get_auto_generated_column_indexes(auto_flag)
            if len(autoflag_column_indexes) !=0:
                for index in autoflag_column_indexes:
                    row[index] = 0
            # railroads done separately
                if 5 in autoflag_column_indexes:
                    row[5], row[6], row[7], row[8], row[9], row[10] = 0, 0, 0, 0, 0, 0
                row[11] = 0
            cursor.updateRow(row)


# create new node names or update previous?
# if sys.argv[1] == "new":
#     print("Removing current auto-generated attributes ...")
remove_attributes_if_autogenerated()

print ("Auto generating attributes based on ambience ...")
count_generated = 0
count_all = 0
column_list = ["ID", "SIGNAL", "FF_SPEED", "CAPY_CODE", "NO_TRACKS", "LINK_TYPE", "RR1"]
with arcpy.da.SearchCursor(link_shp, column_list) as cursor:
    for row in cursor:
        count_all = count_all + 1
        missing_index = get_indexes_of_missing(row)
        missing_column_name = [column_list[i] for i in missing_index]
        if len(missing_index) != 0:
            # print( "ID: " + str(row[0]))
            where = """ "ID" = %d""" % row[0]
            arcpy.SelectLayerByAttribute_management(link_shp_feature, "NEW_SELECTION", where)
            select_touching()
            for i in range(len(missing_column_name)):
                update_attributes(missing_column_name[i], row[0])
            count_generated = count_generated + 1
print str(count_generated) + " link attributes auto generated."
print str(count_all - count_generated) + " link attributes were already known."
