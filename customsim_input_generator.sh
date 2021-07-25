#!/bin/bash

IN_DIR="../data/Halifax"
ROUTE_DIR="exp20210717_result"

MIN_HOP=5
MAX_HOP=25
WEIGHT=1
SAME_RET_ROUTE=True

CUSTOMSIM_OUT_DIR=halifax_${ROUTE_DIR}_${MIN_HOP}_${MAX_HOP}_customsim
mkdir -p $CUSTOMSIM_OUT_DIR

for hop_count in $(seq $MIN_HOP $MAX_HOP);
do
    python3 main.py -nf $IN_DIR/HalifaxDistances.txt -df $IN_DIR/HalifaxOriginDestination.txt \
     -pf $IN_DIR/HalifaxPickupPoint.txt -rf $ROUTE_DIR/halifax_${hop_count}_1_result.txt  -smret $SAME_RET_ROUTE -co .
    mv Bus_Stops.txt $CUSTOMSIM_OUT_DIR/Bus_Stops${hop_count}.txt
    mv Bus_Edge.txt $CUSTOMSIM_OUT_DIR/Bus_Edge${hop_count}.txt
    mv Bus_Fleet.txt $CUSTOMSIM_OUT_DIR/Bus_Fleet${hop_count}.txt
    mv Bus_RouteStop.txt $CUSTOMSIM_OUT_DIR/Bus_RouteStop${hop_count}.txt
done
