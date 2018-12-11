#!/bin/bash

$WEBDIR = $(ls -t openlayers_api | head -1)

echo $WEBDIR

# delete the last directory, commented
# $DELDIR = $(ls -t openlayers_api | tail -1) 
# rm -r openlayers_api/$(DELDIR)

chmod -R 755 openlayers_api/$($WEBDIR)



#scp -r openlayers_api/$($WEBDIR)* pdahal@hydra4.eecs.utk.edu:~/webhome/



chmod -R 755 openlayers_api/qgis2web_2018_11_18-23_15_47_248000/*





scp -r openlayers_api/qgis2web_2018_11_18-23_15_47_248000/* pdahal@hydra4.eecs.utk.edu:~/webhome/

ssh pdahal@hydra4.eecs.utk.edu

chmod -R 755 webhome/*








