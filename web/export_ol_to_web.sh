#!/bin/bash

$WEBDIR = $(ls -t openlayers_api/ | head -1)

chmod -R 755 $WEBDIR
scp -r openlayers_api/$($WEBDIR)/* pdahal@hydra4.eecs.utk.edu:~/webhome/
