#!/bin/bash

OUT_DIR="halifax_matsim"
IN_DIR="../data/Halifax"
ROUTE_DIR="exp20210530_result"

python3 main.py -nf $IN_DIR/HalifaxDistances.txt -df $IN_DIR/HalifaxOriginDestination.txt \
 -pf $IN_DIR/HalifaxPickupPoint.txt -rf $ROUTE_DIR/halifax_5_1_result.txt \
-rrf $ROUTE_DIR/halifax_5_1_return_route.txt -o $OUT_DIR

