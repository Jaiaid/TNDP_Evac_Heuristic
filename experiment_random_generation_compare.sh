#!/bin/bash

MIN_HOP=5
MAX_HOP=5
WEIGHT=1

for hop_count in $(seq $MIN_HOP $MAX_HOP); 
do 
    time python3 evac_route_generate_random_compare.py ../data/Halifax/HalifaxDistances.txt ../data/Halifax/HalifaxOriginDestination.txt ../data/Halifax/HalifaxPickupPoint.txt $hop_count $WEIGHT
#    cat $DIR/halifax_${hop_count}_${WEIGHT}_result.txt >> $DIR/solution_set.txt
done

