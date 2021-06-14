from .NetworkRoute import NetworkRoute
from .NetworkLink import NetworkLink
from .NetworkNode import NetworkNode
from .Vehicle import Vehicle
from .Agent import Agent

NETWORK_MODE_STR="car,bus"
NETWORK_LANE_CAPACITY=50000 # in vehicle per hour
NETWORK_ROAD_LANE_COUNT=2 # lane in a road
NETWORK_MAX_LINK_SPEED = 60000/3600 # in meter per second

TIME_WAITING_MIN = 2
TIME_BETWEEN_STOP_MINUTE = 5

TRANSIT_MODE="bus"
TIME_TRANSIT_START = "08:00:00"
TIME_BETWEEN_NEW_TRANSIT_RELEASE_MINUTE = 30
TIME_LAST_TRANSIT_START_STRING = "12:00:00"
#TIME_TRANSIT_RETURN_MINUTE = 120
#TIME_LARGEST_ROUTE_UNRESTRAINED_COVERING_HOUR = 10
TOTAL_BUS = 332
SEAT = 40
STANDING = 10
LENGTH = 8


class EvacPlanBuilder:
    __transit_vehicle_type_prop_dict = \
    {
        "pb": {"id": "pb", "count": TOTAL_BUS, "seat": SEAT, "standing": STANDING, "length": LENGTH, "pce": (SEAT+STANDING)/4}
    }

    __node_count = None
    __demand_graph = None
    __network_graph = None
    __pickuppoint_list = None

    __link_capacity_graph = None
    __link_max_speed_graph = None
    __link_lane_count_graph = None

    __node_dict = None
    __link_dict = None
    __route_dict = None 
    __agent_dict = None

    def __init__(self, link_cap=NETWORK_LANE_CAPACITY, lane_count=NETWORK_ROAD_LANE_COUNT, link_max_speed=NETWORK_MAX_LINK_SPEED, \
        early_arrival_waiting_at_stop_min=TIME_WAITING_MIN, travel_time_between_stop_floor_minute=TIME_BETWEEN_STOP_MINUTE, \
        transit_mode=TRANSIT_MODE, transit_start_time_string=TIME_TRANSIT_START, \
        time_between_new_transit_release=TIME_BETWEEN_NEW_TRANSIT_RELEASE_MINUTE, last_transit_start_time_string=TIME_LAST_TRANSIT_START_STRING, \
        ):
        self.__network_link_cap = link_cap
        self.__network_link_lane_count = lane_count
        self.__network_max_link_speed = link_max_speed

        self.__time_between_earlyarrival_deperture_minute = early_arrival_waiting_at_stop_min
        self.__time_travel_between_stop_minute = travel_time_between_stop_floor_minute

        self.__transit_mode = transit_mode
        self.__time_transit_start_time_string = transit_start_time_string
        self.__time_between_new_transit_release_minute = time_between_new_transit_release
        self.__transit_last_start_time_string = last_transit_start_time_string
        self.__round_trip_count = None

    def __get_link_cap(self, origin, dest):
        if self.__link_capacity_graph is None:
            return self.__network_link_cap
        return self.__link_capacity_graph[origin][dest]

    def __get_link_max_speed(self, origin, dest):
        if self.__link_max_speed_graph is None:
            return self.__network_max_link_speed
        return self.__link_max_speed_graph[origin][dest]

    def __get_link_lane_count(self, origin, dest):
        if self.__link_lane_count_graph is None:
            return self.__network_link_lane_count
        return self.__link_lane_count_graph[origin][dest]

    def __get_node_coord(self, node_id):
        if self.__node_coordinate_dict is None:
            return node_id*10, (node_id//20)*100
        return self.__node_dict[node_id]["coord"]


    def __parse_network_file(self, network_file_path):
        self.__network_graph = []
        self.__link_id_dict = {}
        
        # parse file and populate network graph
        with open(network_file_path) as net_file:
            lines = net_file.readlines()
            self.__node_count=int(lines[0])

            for idx, line in enumerate(lines[1:]):
                number_strings=line.rsplit()
                assert self.node_count==len(number_strings), \
                    "network row {0} has less entry (={1}) than node count (={2})".format(idx, len(number_strings), self.__node_count)

                self.__network_graph.append([])
                for number_string in number_strings:
                    self.__network_graph[-1].append(float(number_string))

                assert len(self.__network_graph[-1])==self.__node_count

            assert len(self.__network_graph)==self.__node_count
        
        # populate link id dict
        id_no = 0
        for i in range(len(self.__network_graph)):
            for j in range(len(self.__network_graph[i])):
                if self.__network_graph[i][j] > 0:
                    self.__link_id_dict[(i,j)]["id"] = id_no
                    self.__link_id_dict[(i,j)]["cap"] = self.__get_link_cap(i, j)
                    self.__link_id_dict[(i,j)]["speed"] = self.__get_link_max_speed(i, j)
                    self.__link_id_dict[(i,j)]["lane_count"] = self.__get_link_lane_count(i, j)
                    id_no += 1

        id_no = 0
        for i in range(len(self.__network_graph)):
            for j in range(len(self.__network_graph[i])):
                if self.__network_graph[i][j] > 0:
                    self.__link_id_dict[(i,j)]["id"] = id_no
                    self.__link_id_dict[(i,j)]["cap"] = self.__get_link_cap(i, j)
                    self.__link_id_dict[(i,j)]["speed"] = self.__get_link_max_speed(i, j)
                    self.__link_id_dict[(i,j)]["lane_count"] = self.__get_link_lane_count(i, j)
                    id_no += 1


    def __parse_pickuppoint_file(self, pickup_point_file_path):
        self.__pickuppoint_list = []
        with open(pickup_point_file_path) as pickuppoint_file:
            lines = pickuppoint_file.readlines()
            
            for idx, line in enumerate(lines):
                self.__pickuppoint_list.append(int(line.rsplit()[0]))


    def __parse_demand_file(self, demand_file_path):
        self.__demand_graph = []

        with open(demand_file_path) as demand_file:
            lines = demand_file.readlines()
            node_count=int(lines[0])
            assert self.__node_count is not None and node_count==self.__node_count 

            for idx, line in enumerate(lines[1:]):
                number_strings=line.rsplit()
                assert node_count==len(number_strings), "demand graph row {0} has less entry (={1}) than node count (={2})".format(idx, len(number_strings), node_count)

                self.__demand_graph.append([])
                for number_string in number_strings:
                    self.__demand_graph[-1].append(float(number_string))

                assert len(self.__demand_graph[-1])==node_count

            assert len(self.__demand_graph)==node_count

    
    def __parse_route_files(self, route_file_path, return_route_file_path):
        assert self.__node_coordinate_dict is not None
        assert self.__transit_vehicle_type_prop_dict is not None

        fleet_size = sum([self.__transit_vehicle_type_prop_dict[key]["count"] for key in self.__transit_vehicle_type_prop_dict])

        self.__route_dict = {}
        self.__stop_id_dict = {}

        with open(return_route_file_path) as return_route_file:
            for line in return_route_file.readlines():
                route_nodes_str = line.rsplit()
                self.__return_route_list.append([])
                for route_node_str in route_nodes_str:
                    self.__return_route_list[-1].append(int(route_node_str))

        # this is used to add shelter stop linkrefid, which is got by (shelter id, corresponding return route 2nd node)
        # return_route_list should be in corresponding sequence as route
        parsed_route_no = 0
        with open(route_file_path) as route_file:
            lines = route_file.readlines()
            total_demand = float(lines[0])
            self.__route_count = int(lines[1])

            for idx in range(2, len(lines), 2):
                sat_demand=float(lines[idx].rsplit()[0])

                route_nodes_str = lines[idx+1].rsplit()
                self.__route_list.append([])
                for route_node_str in route_nodes_str:
                    self.__route_list[-1].append(int(route_node_str))

                    # add linkRefId to stop_id_dict
                    if len(self.__route_list[-1]) > 1:
                        # if it is stop id at all
                        if self.__route_list[-1][-2] in self.__pickuppoint_list:
                            stop_node_id = (self.__route_list[-1][-2], self.__route_list[-1][-1])
                            self.__stop_id_dict[stop_node_id] = { "id": str(self.__route_list[-1][-2]) + "_" + str(self.__route_list[-1][-1]), "x": stop_node_id[0]*10, "y": (stop_node_id[0]//20)*100}
                            self.__stop_id_dict[stop_node_id]["linkRefId"] = self.__link_id_dict[(self.__route_list[-1][-2], self.__route_list[-1][-1])]

                # create a stop at shelter
                assert self.__route_list[-1][-1] == self.__return_route_list[parsed_route_no][0]
                shelter_stop_id = (self.__route_list[-1][-1], self.__return_route_list[parsed_route_no][1])
                self.__stop_id_dict[shelter_stop_id] = { "id": str(self.__route_list[-1][-1]) + "_" + str(self.__return_route_list[parsed_route_no][1]), "x": shelter_stop_id[0]*10, "y": (shelter_stop_id[0]//20)*100}
                self.__stop_id_dict[shelter_stop_id]["linkRefId"] = self.__link_id_dict[(self.__route_list[-1][-1], self.__return_route_list[parsed_route_no][1])]

                self.__route_bus_count_list.append(int(sat_demand*fleet_size/total_demand))
                # there will be at least one bus
                if self.__route_bus_count_list[-1] == 0:
                    self.__route_bus_count_list[-1] = 1

                parsed_route_no += 1

            if sum(self.__route_bus_count_list) < fleet_size:
                self.__route_bus_count_list[-1] += fleet_size - sum(self.__route_bus_count_list)



    def __calc_euclid_dist(coord1, coord2):
        return ((coord1[0]-coord2[0])**2 + (coord1[1]-coord2[1])**2)**0.5 


    def __create_nearest_stop_dict(self):
        assert self.__stop_id_dict is not None
        assert self.__route_list is not None
        assert self.__return_route_list is not None
        
        self.__nearest_stop_dict = {}

        for route in self.__route_list:
            for i in range(1, len(route)):
                mindist = float("inf")
                nearest_stop = None
                for j in range(1, len(route)):
                    possible_stop_node_id = (route[j-1], route[j])
                    if possible_stop_node_id in self.__stop_id_dict:
                        dist = self.__calc_euclid_dist(self.__node_coordinate_dict[route[i-1]], self.__node_coordinate_dict[route[j-1]])
                        if dist < mindist:
                            nearest_stop = possible_stop_node_id
                            mindist = dist
                assert nearest_stop is not None, "{0}".format((route[i-1], route[i]))
                self.__nearest_stop_dict[(route[i-1], route[i])] = nearest_stop


    def __create_depertures(self):
        self.__departure_id = {}
        self.__route_

        assert self.__route_list is not None
        assert self.__return_route_list is not None
        assert self.__route_bus_count_list is not None

        for route in


        
        

