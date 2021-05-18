import sys
import os

EDGE_FILE = '../data/Halifax/HalifaxEdgelist.txt'
TIME_FILE = '../data/Halifax/HalifaxTime.txt'
DEMAND_FILE = '../data/Halifax/HalifaxZoneDemand.txt'
ZONE_FILE = '../data/Halifax/HalifaxZone.txt'
CENTROID_FILE = '../data/Halifax/HalifaxZoneDistance.txt'

OD_FILE = '../data/Halifax/HalifaxOriginDestination.txt'
PICKUP_FILE = '../data/Halifax/HalifaxPickupPoint.txt'


zone_dict = {}
zone_node_list_dict = {}
zone_node_count = {}
graph_dict = {}
demand_dict = {}
centroid_dist_dict = {}
centroid_near_min_node = []

TOTAL_NODE = 383
SHELTER_NODE = [381, 382]

if __name__ == '__main__':
	with open(ZONE_FILE) as zone_file:
		for line in zone_file.readlines():
			line = line.rstrip()
			nodes = line.split(' ')

			zone = int(nodes[0])
			if zone not in zone_node_count:
				zone_node_count[zone] = 0
				zone_node_list_dict[zone] = []
			for node in nodes[1:]:
				node_idx = int(node)
				if zone in zone_node_count:
					zone_node_count[zone] = zone_node_count[zone] + 1
				if node_idx not in zone_dict:
					zone_dict[node_idx] = zone
				zone_node_list_dict[zone].append(node_idx)

	with open(CENTROID_FILE) as centroid_file:
		for line in centroid_file.readlines():
			line = line.rstrip()
			data = line.split(' ')

			zone = int(data[0])
			centroid_dist_dict[zone] = []
			min_dist_node = -1
			min_dist = 1e12
			for i, dist in enumerate(data[1:]):
				if float(dist) < min_dist:
					min_dist = float(dist)
					min_dist_node = zone_node_list_dict[zone][i]
			centroid_near_min_node.append(min_dist_node)	

	with open(DEMAND_FILE) as demand_file:
		for line in demand_file.readlines():
			line = line.rstrip()
			data = line.split(' ')

			zone = int(data[0])
			if zone in zone_node_count:
				demand_dict[zone] = (int(data[1]), int(data[2]))

	graph = [] 
	for i in range(TOTAL_NODE):
		graph.append([0]*TOTAL_NODE)
		if i in centroid_near_min_node:
			for idx, shelter in enumerate(SHELTER_NODE):
				graph[i][shelter] = demand_dict[zone_dict[i]][idx]

	with open(OD_FILE, 'w') as od_file:
		od_file.write(str(TOTAL_NODE) + '\n')
		for i in range(TOTAL_NODE):
			for j in range(TOTAL_NODE):
				od_file.write(str(graph[i][j]) + ' ') 
			od_file.write('\n')

	with open(PICKUP_FILE, 'w') as pickup_file:
		for i in centroid_near_min_node:
			pickup_file.write(str(i) + '\n') 
