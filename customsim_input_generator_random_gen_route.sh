#!/bin/bash

IN_DIR="../data/Halifax"
#ROUTE_DIR="exp20210823_result"
ROUTE_DIR="exp_random_route_20220107_result"

MIN_HOP=1
MAX_HOP=56
WEIGHT=1.0
SAME_RET_ROUTE=True
SOLUTION_DIR_COUNT=5

CUSTOMSIM_OUT_DIR_ROOT=halifax_${ROUTE_DIR}_${MIN_HOP}_${MAX_HOP}_customsim_random_gen_route
mkdir -p $CUSTOMSIM_OUT_DIR_ROOT

for solution_no in $(seq 1 $SOLUTION_DIR_COUNT)
do
    mkdir -p $CUSTOMSIM_OUT_DIR_ROOT/solution_${solution_no}

    for hop_count in $(seq $MIN_HOP $MAX_HOP);
    do
	ls -lsh $ROUTE_DIR/solution_${solution_no}/halifax_${hop_count}_1.0_result.txt
        python3 main.py -nf $IN_DIR/HalifaxDistances.txt -df $IN_DIR/HalifaxOriginDestination.txt \
        -pf $IN_DIR/HalifaxPickupPoint.txt -rf $ROUTE_DIR/solution_${solution_no}/halifax_${hop_count}_1.0_result.txt  -smret $SAME_RET_ROUTE -co .
        mv Bus_Stops.txt $CUSTOMSIM_OUT_DIR_ROOT/solution_${solution_no}/Bus_Stops${hop_count}.txt
        mv Bus_Edge.txt $CUSTOMSIM_OUT_DIR_ROOT/solution_${solution_no}/Bus_Edge${hop_count}.txt
        mv Bus_Fleet.txt $CUSTOMSIM_OUT_DIR_ROOT/solution_${solution_no}/Bus_Fleet${hop_count}.txt
        mv Bus_RouteStop.txt $CUSTOMSIM_OUT_DIR_ROOT/solution_${solution_no}/Bus_RouteStop${hop_count}.txt
    done
done
