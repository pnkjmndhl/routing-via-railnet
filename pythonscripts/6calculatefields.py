from rail import *


def get_direction(linktype):
    if linktype in [1, 3]:
        return "SD"
    elif linktype in [2, 4]:
        return "BI"
    else:
        return "NA"


def get_average_siding(cap):
    if cap in [1, 5, 9]:
        return -99
    elif cap in [2, 6, 10]:
        return 5
    elif cap in [3, 7, 11]:
        return 15
    elif cap in [4, 8, 12]:
        return 25
    else:
        return 0


def get_signal(signal):
    if signal == 1:
        return "CTC"
    elif signal == 2:
        return "ABS"
    elif signal == 4:
        return "NON"
    else:
        return 0


def get_terrain(capcode):
    if capcode in [1, 2, 3, 4]:
        return "FLAT"
    elif capcode in [5, 6, 7, 8]:
        return "HILLY"
    elif capcode in [9, 10, 11, 12]:
        return "MNTNS"
    else:
        return 0


# main program
# for calculation of length
arcpy.CalculateField_management(link_shp, "LENGTH", '!Shape.length@miles!', "PYTHON")

spatref = arcpy.SpatialReference(102100)
with arcpy.da.UpdateCursor(link_shp,
                           ["LINK_TYPE", "SIGNAL", "CAPY_CODE", "SIGNAL_", "TERRAIN_", "DIRECTION_", "SIDING_",
                            "LENGTH", "RR1", "NO_TRACKS", "FF_SPEED", "SHAPE@"],
                           spatial_reference=spatref) as cursor:
    for row in cursor:
        row[3] = get_signal(row[1])
        row[4] = get_terrain(row[2])
        row[5] = get_direction(row[0])
        row[6] = get_average_siding(row[2])
        cursor.updateRow(row)
