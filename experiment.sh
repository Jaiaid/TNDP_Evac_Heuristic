#!/bin/bash

DATE=`date +%Y%m%d`
DIR=exp${DATE}_result

mkdir -p $DIR

MIN_HOP=5
MAX_HOP=20
WEIGHT=1

rm -f $DIR/solution_set.txt
for hop_count in $(seq $MIN_HOP $MAX_HOP); 
do 
    time python3 main.py ../data/Halifax/HalifaxDistances.txt ../data/Halifax/HalifaxOriginDestination.txt ../data/Halifax/HalifaxPickupPoint.txt $hop_count $WEIGHT > $DIR/halifax_${hop_count}_${WEIGHT}_result.txt
    mv return_route.txt $DIR/halifax_${hop_count}_${WEIGHT}_return_route.txt
#    cat $DIR/halifax_${hop_count}_${WEIGHT}_result.txt >> $DIR/solution_set.txt
done

