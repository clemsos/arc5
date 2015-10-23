#!/bin/bash

# export nodes
echo
echo "###### NODES ######"
mongoexport --db arc5 --collection nodes --csv --fields _id,name,type,slug,acronyme,start,end,axe.id,bddLink --out nodes.csv
tail -1 nodes.csv

echo 
echo "###### EDGES ######"
# export edges
mongoexport --db arc5 --collection edges --csv --fields _id,source,target,type --out edges.csv
tail -1 edges.csv
