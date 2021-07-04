#!/bin/bash

CUSTOMSIM_OUT_DIR="halifax_customsim"
IN_DIR="../data/Halifax"
ROUTE_DIR="exp20210619_result"

python3 main.py -nf $IN_DIR/HalifaxDistances.txt -df $IN_DIR/HalifaxOriginDestination.txt \
 -pf $IN_DIR/HalifaxPickupPoint.txt -rf $ROUTE_DIR/halifax_5_1_result.txt -co $CUSTOMSIM_OUT_DIR

