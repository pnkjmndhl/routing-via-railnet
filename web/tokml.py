import arcpy
import zipfile
import os
import pandas

arcpy.env.overwriteOutput = True


nodeshp = r'..\GIS\allnodes.shp'
linkshp = r'..\GIS\alllinks.shp'
plotshp = r'..\GIS\plots\Plot.shp'
transfershp = r'..\GIS\transfers.shp'

	
def extractfile(filenamekmz):
   zip_ref = zipfile.ZipFile(filenamekmz, 'r')
   zip_ref.extractall()
   newname = filenamekmz.split(".kmz")[0] + '.kml'
   os.rename('doc.kml', newname)
   zip_ref.close()
   print(filenamekmz + ' extracted')

def shptokmz(shapefile):
   outputname = shapefile.split('\\')[len(shapefile.split('\\'))-1].split('.shp')[0] 
   arcpy.MakeFeatureLayer_management(shapefile, outputname)
   arcpy.LayerToKML_conversion (outputname, outputname + '.kmz' )
   print(outputname + ' kmz created')

#shp to dataframe
def shptodf(shp_path):
   csvpath = "dumm.csv"
   arcpy.TableToTable_conversion (shp_path, ".", csvpath)
   return (pandas.read_csv(csvpath))

os.system('del /S *.kml')
   
shptokmz(nodeshp)
shptokmz(plotshp)
shptokmz(transfershp)


shptokmz(linkshp)
extractfile('alllinks.kmz')

extractfile('allnodes.kmz')
extractfile('Plot.kmz')
extractfile('transfers.kmz')

os.system('del /S *.kmz')
os.system('del /S *.xsl')
os.system('del /S *.png')
os.system('del /S *.xml')
os.system('del /S *.ini')









