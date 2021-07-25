import math
import datetime
import os
import copy

from NetworkRoute import NetworkRoute, NetworkRouteProfileEntry
from NetworkLink import NetworkLink
from NetworkNode import NetworkNode
from Vehicle import Vehicle
from Schedule import Schedule
from Agent import Agent
from MatsimInputWriter import MatsimInputWriter


class TransitPlanBuilder:
    __node_count = None
    __demand_graph = None
    __network_graph = None
    __pickuppoint_list = None

    __link_capacity_graph = None
    __link_max_speed_graph = None
    __link_lane_count_graph = None

    __node_dict = None
    __node_coordinate_dict = None
    __link_dict = None
    __route_dict = None
    # to avoid large memory footprint, for now agent creation will be done on fly when dumping
    __agent_dict = None
    __vehicle_list = None

    def __init__(
        self, link_cap: int, lane_count: int, link_max_speed: float, 
        network_mode_str: str, transit_mode_str: str):
        self.__network_link_cap = link_cap
        self.__network_link_lane_count = lane_count
        self.__network_max_link_speed = link_max_speed
        self.__network_mode_str = network_mode_str
        self.__transit_mode_str = transit_mode_str

    def __get_link_cap(self, origin_id: int, dest_id: int):
        if self.__link_capacity_graph is None:
            return self.__network_link_cap
        return self.__link_capacity_graph[origin_id][dest_id]

    def __get_link_max_speed(self, origin_id: int, dest_id: int):
        if self.__link_max_speed_graph is None:
            return self.__network_max_link_speed
        return self.__link_max_speed_graph[origin_id][dest_id]

    def __get_link_lane_count(self, origin_id: int, dest_id: int):
        if self.__link_lane_count_graph is None:
            return self.__network_link_lane_count
        return self.__link_lane_count_graph[origin_id][dest_id]

    def __get_node_coord(self, node_id: int):
        if self.__node_coordinate_dict is None:
            return node_id*10, (node_id//20)*100
        return (self.__node_dict[node_id].x, self.__node_dict[node_id].y)

    def __parse_network_file(self, network_file_path):
        assert self.__pickuppoint_list is not None

        self.__network_graph = []
        self.__link_dict = {}
        self.__node_dict = {}
        
        # parse file and populate network graph
        with open(network_file_path) as net_file:
            lines = net_file.readlines()
            self.__node_count=int(lines[0])

            for idx, line in enumerate(lines[1:]):
                number_strings=line.rsplit()
                assert self.__node_count==len(number_strings), \
                    "network row {0} has less entry (={1}) than node count (={2})".format(idx, len(number_strings), self.__node_count)

                self.__network_graph.append([])
                for number_string in number_strings:
                    self.__network_graph[-1].append(float(number_string))

                assert len(self.__network_graph[-1])==self.__node_count

            assert len(self.__network_graph)==self.__node_count
        
        # populate node_dict
        for i in range(self.__node_count):
            coord = self.__get_node_coord(i)
            is_stop = i in self.__pickuppoint_list
            self.__node_dict[i] = NetworkNode(id=i, x=coord[0], y=coord[1], is_stop=is_stop)

        # populate link_dict
        id_no = 0
        for i in range(len(self.__network_graph)):
            for j in range(len(self.__network_graph[i])):
                if self.__network_graph[i][j] > 0:
                    self.__link_dict[(i,j)] = \
                        NetworkLink(
                            id=id_no, origin=self.__node_dict[i], dest=self.__node_dict[j], length= self.__network_graph[i][j], 
                            speed=self.__get_link_max_speed(i, j), capacity=self.__get_link_cap(i, j), 
                            lane_count=self.__get_link_lane_count(i, j), mode=self.__network_mode_str
                        )
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

    
    def __parse_route_files(self, route_file_path):
        assert self.__node_dict is not None

        self.__route_dict = {}

        route_id = 0
        with open(route_file_path) as route_file:
            lines = route_file.readlines()

            for idx in range(0, len(lines), 2):
                # first create the route
                self.__route_dict[route_id] = NetworkRoute(id=route_id, transit_mode=self.__transit_mode_str)
                # from each two line first line contains route stops
                stoppoint_id_list = []
                stop_nodes_str = lines[idx].rsplit()
                #print(stop_nodes_str)
                for i, stop_node_str in enumerate(stop_nodes_str):
                    stoppoint_id_list.append(int(stop_node_str))

                # 2nd line contain all nodes in route
                route_nodes_str = lines[idx+1].rsplit()
                for i, route_node_str in enumerate(route_nodes_str):
                    if i == 0:
                        continue
                    if int(route_nodes_str[i-1]) in stoppoint_id_list:
                        # stop will be made at first appearance 
                        # for a route a stop node can create only one stop facility
                        stoppoint_id_list.remove(int(route_nodes_str[i-1]))
                        assert int(route_nodes_str[i-1]) not in stoppoint_id_list 
                        self.__route_dict[route_id].add_link(
                            link=self.__link_dict[int(route_nodes_str[i-1]), int(route_node_str)], 
                            create_stop_facility=True
                        )
                    else:
                        self.__route_dict[route_id].add_link(
                            link=self.__link_dict[int(route_nodes_str[i-1]), int(route_node_str)], 
                            create_stop_facility=False
                        )

                #print(self.__route_dict[route_id].get_sat_demand(self.__demand_graph))

                route_id += 1

    def __create_route_stop_profile(self, max_roundtrip_minute, wait_minute):
        for route_id in self.__route_dict:
            route = self.__route_dict[route_id]
            route_length = route.get_length()
            route_stops = route.get_stopfacilities()

            route_stop_profiles = []
            # current heuristic is assuming offset time will be min(max_roundtrip_minute, length / (free_speed_metpsec * 60))
            max_roundtrip_minute = min(max_roundtrip_minute, route_length // (16.667 * 60))
            offset_minute_of_next_stop = max_roundtrip_minute // len(route_stops)

            # create deperture offset for all stops in a route
            arrival_offset = "00:00:00"
            deperture_offset = (datetime.datetime.strptime(arrival_offset, "%H:%M:%S") + \
                                datetime.timedelta(minutes=wait_minute)).strftime("%H:%M:%S")
            # trip count should be greater than zero for sensible data
            assert route.round_trip_count > 0
            for trip_count in range(route.round_trip_count):
                for stopfacility in route_stops: 
                    route_stop_profiles.append(
                        NetworkRouteProfileEntry(
                            stopfacility=stopfacility, arrival_offset=arrival_offset, 
                            deperture_offset=deperture_offset, wait_early_arrival="true"
                        )
                    )
                    arrival_offset = (datetime.datetime.strptime(deperture_offset, "%H:%M:%S") + \
                                datetime.timedelta(minutes=offset_minute_of_next_stop)).strftime("%H:%M:%S")
                    deperture_offset = (datetime.datetime.strptime(arrival_offset, "%H:%M:%S") + \
                                datetime.timedelta(minutes=wait_minute)).strftime("%H:%M:%S")

            route.set_profilelist(route_stop_profiles)            
        
    def __create_vehicles(self, vehicle_dict: dict):
        self.__vehicle_list = []

        for vehicle_type in vehicle_dict:
            for i in range(vehicle_dict[vehicle_type]["count"]):
                self.__vehicle_list.append(
                    Vehicle(id=vehicle_dict[vehicle_type]["id"]+"_{0}".format(i),
                        typename=vehicle_type,
                        seat=vehicle_dict[vehicle_type]["seat"],
                        standing=vehicle_dict[vehicle_type]["standing"],
                        length=vehicle_dict[vehicle_type]["length"],
                        pce=vehicle_dict[vehicle_type]["pce"]
                    )
                )

    def __create_schedule(self, start_time, minute_between_start):
        assert self.__demand_graph is not None

        total_demand = sum(map(sum, self.__demand_graph))
        fleet_size = len(self.__vehicle_list)
        allocated_upto_idx = 0

        schedule_id = 0
        for route_id in self.__route_dict:
            route = self.__route_dict[route_id]
            route_sat_demand = route.get_sat_demand(self.__demand_graph)
            allocated_vehicle_count = int(fleet_size * route_sat_demand / total_demand)

            # at least one vehicle will be given in the route
            if allocated_vehicle_count == 0:
                allocated_vehicle_count = 1
            
            # create deperture time for all allocated vehicle
            deperture_list = []
            deperture_time = start_time
            for vehicle_idx in range(allocated_upto_idx, allocated_upto_idx + allocated_vehicle_count):
                deperture_schedule = Schedule(id=schedule_id, start_time=deperture_time, vehicle=self.__vehicle_list[vehicle_idx])
                deperture_list.append(deperture_schedule)

                deperture_time = (datetime.datetime.strptime(deperture_time, "%H:%M:%S") + \
                             datetime.timedelta(minutes=minute_between_start)).strftime("%H:%M:%S")

                schedule_id += 1

            demand_filled_by_allocated_vehicles_in_a_round = allocated_vehicle_count * \
                (self.__vehicle_list[allocated_upto_idx].seat + self.__vehicle_list[allocated_upto_idx].standing)
            needed_round_trip = math.ceil(route_sat_demand / demand_filled_by_allocated_vehicles_in_a_round)

            route.set_round_trip_count(needed_round_trip)
            route.set_depertures(deperture_list)
            allocated_upto_idx += allocated_vehicle_count

    def __create_agents(self, home_left_time):
        assert self.__route_dict is not None

        self.__agent_dict = {}

        id_no = 0
        demand_graph = copy.deepcopy(self.__demand_graph)
        for route_id in self.__route_dict:
            route = self.__route_dict[route_id]
            shelter_link = route.stopfacility_list[-1].link
            for link in route.route_link_list:
                if demand_graph[link.origin.id][shelter_link.origin.id] > 0:
                    person_count = int(demand_graph[link.origin.id][shelter_link.origin.id])

                    for i in range(person_count):
                        self.__agent_dict[id_no] = \
                            Agent(
                                id=id_no, home_link=link, home_left_time=home_left_time, 
                                shelter_link=shelter_link, route=route
                            )
                        id_no += 1

                    # this person plans are written make it zero so overlapped nodes are not written multiple times
                    demand_graph[link.origin.id][shelter_link.origin.id] = 0

    def create_plan(
            self, network_file_path: str, demand_file_path: str, pickuppoint_file_path: str, 
            route_file_path: str, vehicle_dict: dict, 
            start_time: str, minute_between_start: int, max_roundtrip_minute: int, wait_minute_at_stop: int):
        self.__parse_pickuppoint_file(pickup_point_file_path=pickuppoint_file_path)
        self.__parse_network_file(network_file_path=network_file_path)
        self.__parse_demand_file(demand_file_path=demand_file_path)
        self.__parse_route_files(route_file_path=route_file_path)
        self.__create_agents(home_left_time="07:45:00")
        self.__create_vehicles(vehicle_dict=vehicle_dict)
        self.__create_schedule(start_time=start_time, minute_between_start=minute_between_start)
        self.__create_route_stop_profile(max_roundtrip_minute=max_roundtrip_minute, wait_minute=wait_minute_at_stop)

    def write_plan_matsim_format(self, output_dir_path):
        if not os.path.exists(output_dir_path):
            os.mkdir(output_dir_path)

        writer = MatsimInputWriter()
        writer.write_plan_file(
            os.path.join(output_dir_path, "population.xml"), agent_dict=self.__agent_dict
        )
        writer.write_network_file(
            os.path.join(output_dir_path, "network.xml"), 
            link_dict=self.__link_dict, node_dict=self.__node_dict
        )
        writer.write_vehicle_file(os.path.join(
            output_dir_path, "transit_vehicle.xml"), vehicle_list=self.__vehicle_list
        )
        writer.write_schedule_file(
            os.path.join(output_dir_path, "transit_schedule.xml"), route_dict=self.__route_dict
        )

    def write_customsim_input(self, output_dir_path: str, shelterid_list: list, minute_between_start: int, separate_return_route: bool):
        if not os.path.exists(output_dir_path):
            os.mkdir(output_dir_path)

        with open(os.path.join(output_dir_path, "Bus_Edge.txt"), mode="w") as fout:
            for link_id in self.__link_dict:
                # links are unidirectional
                link = self.__link_dict[link_id]
                fout.write(' '.join([str(link.origin.id), str(link.dest.id), str(link.length), "1"+os.linesep]))

        with open(os.path.join(output_dir_path, "Bus_Stops.txt"), mode="w") as fout:
            for node_id in range(len(self.__network_graph)):
                line = str(node_id) + " "
                for shelter_id in shelterid_list:
                    line +=  str(int(self.__demand_graph[node_id][shelter_id])) + " "
                fout.write(line + os.linesep)
 
        route_allocated_vehicle_count_list = []
        with open(os.path.join(output_dir_path, "Bus_Fleet.txt"), mode="w") as fout:
            total_demand = sum(map(sum, self.__demand_graph))
            fleet_size = len(self.__vehicle_list)
            allocated_upto_idx = 1

            for route_id in self.__route_dict:
                route = self.__route_dict[route_id]
                route_sat_demand = route.get_sat_demand(self.__demand_graph)
                allocated_vehicle_count = int(fleet_size * route_sat_demand / total_demand)
                # at least one vehicle will be given in the route
                if allocated_vehicle_count == 0:
                    allocated_vehicle_count = 1
                route_allocated_vehicle_count_list.append(allocated_vehicle_count)

                headway = 0
                stopfacility_list = route.get_stopfacilities()
                for i in range(allocated_vehicle_count):
                    fout.write("Fleet {0} on {1}'th route".format(allocated_upto_idx, route_id) + os.linesep)
                    route_node_id_list = []
                    for route_link in route.route_link_list:
                        route_node_id_list.append(str(route_link.origin.id))
                        # if not separate return route then forward route will be considered backward route
                        if not separate_return_route and \
                            route_link.origin.id == stopfacility_list[-1].link.origin.id:
                            break

                    fout.write(" ".join(route_node_id_list) + os.linesep)
                    fout.write(str(headway * 60) + os.linesep)
                    fout.write(str(route.round_trip_count) + os.linesep)
                    
                    allocated_upto_idx += 1
                    headway += minute_between_start

        assert sum(route_allocated_vehicle_count_list) == allocated_upto_idx - 1
        with open(os.path.join(output_dir_path, "Bus_RouteStop.txt"), mode="w") as fout:
            for route_id in self.__route_dict:
                route = self.__route_dict[route_id]
                stopfacility_list = route.get_stopfacilities()

                route_stopnode_id_str_list = [str(stopfacility.link.origin.id) for stopfacility in stopfacility_list] 
                line = " ".join(route_stopnode_id_str_list)
                for i in range(route_allocated_vehicle_count_list[route_id]):
                    fout.write(line + os.linesep)
