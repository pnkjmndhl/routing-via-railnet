# plot by commodity and railroad
from rail import *
import arcpy

folder = 'netdata/ADF/'
base = "base_cost6_20190128134132.ADF"
plot_folder = 'Plots/'
mxdfile = r"symbology.mxd"
dumm_lyr = 'gis/symbology/dumm.lyr'

# setting default values
lyr_base = 'gis/symbology/Plot_all.lyr'
lyr_diff = 'gis/symbology/Plotdiff_all.lyr'


# return a list of field names in any shape file
def get_field_names(shp):
    fieldnames = [f.name for f in arcpy.ListFields(shp)]
    return fieldnames


# copy current network to plot
def get_plot_with_fieldnames(column_names):
    arcpy.Copy_management(link_shp, plot)
    arcpy.DeleteField_management(plot, column_names)


type = 'base'
file_name = folder + "/" + base
plot_type = 'Plot'
exclude_plot = ['Plotdiff']
plot_name = base
plot_path = 'plots/' + base + "/" + plot_name

mxd = arcpy.mapping.MapDocument(mxdfile)
df = arcpy.mapping.ListDataFrames(mxd)[0]
lyr = arcpy.mapping.ListLayers(mxd, "Plot", df)[0]
lyr.visible = True
lyr.transparency = 0

#arcpy.ApplySymbologyFromLayer_management(lyr,dumm_lyr)


lyr.symbology.valueField = "GrossTons"
lyr.symbology.classBreakValues = [0, 1000000, 5000000, 10000000, 20000000, 40000000, 60000000, 600000000]
lyr.symbology.classBreakLabels = ["<1M", "1M to 5M", "5M to 10M", "10M to 20M", "20M to 40M", "40M to 60M",">60M"]

arcpy.mapping.UpdateLayer(df, lyr, arcpy.mapping.Layer(dumm_lyr), True)

arcpy.mapping.ExportToJPEG(mxd, "Export.jpg", "PAGE_LAYOUT", resolution=800)


del mxd


#looked simple but cant do this
#hence this is not available in arcpy and cant be done (waster some hours in finding this out)