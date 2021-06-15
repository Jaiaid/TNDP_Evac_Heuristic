from typing import List
from NetworkLink import NetworkLink, StopFacility
from NetworkNode import NetworkNode
from Vehicle import Vehicle
from Schedule import Schedule

class NetworkRouteProfileEntry():
    def __init__(self, stopfacility: StopFacility, arrival_offset: str, deperture_offset: str, wait_early_arrival: bool) -> None:
        self.stopfacility = stopfacility
        self.arrival_offset = arrival_offset
        self.deperture_offset = deperture_offset
        self.wait_early_arrival = wait_early_arrival

class NetworkRoute:
    def __init__(self, id: int):
        self.id = id
        self.route_link_list = []
        self.return_route_link_list = []
        self.shelter_link_id = None
        self.stop_node_list = []
        self.round_trip_count = 0
        self.vehicle_list = []
        self.deperture_list = []
        self.profilelist = []
        self.node_id_to_nearest_stop_id_dict = {}
        self.sat_demand = None

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self.id == other.id)

    def add_link(self, link: NetworkLink):
        #if len(self.route_link_list) > 0:
        #    print(self.route_link_list[-1].dest.id, link.origin.id)
        assert len(self.route_link_list) == 0 or link.origin.id == self.route_link_list[-1].dest.id

        self.route_link_list.append(link)
        if link.is_stop:
            self.stop_node_list.append(link.origin)
    
    def add_return_link(self, link: NetworkLink):
        assert len(self.return_route_link_list) == 0 or link.origin.id == self.return_route_link_list[-1].dest.id

        self.return_route_link_list.append(link)
        if link.is_stop:
            self.stop_node_list.append(link.origin)

    def add_vehicle(self, vehicle: Vehicle):
        self.vehicle_list.append(vehicle)

    def set_round_trip_count(self, count: int):
        self.round_trip_count = count

    def set_shelter_link(self, link_id):
        self.shelter_link_id = link_id

    def set_stop_at_last_node(self):
        self.return_route_link_list[0].is_stop = True
        self.return_route_link_list[0].origin.is_stop = True 

    def __calc_euclid_dist(coord1: tuple((int, int)), coord2: tuple((int, int))):
        return ((coord1[0]-coord2[0])**2 + (coord1[1]-coord2[1])**2)**0.5 


    def set_sat_demand(self, sat_demand: int):
        self.sat_demand = sat_demand

    def get_sat_demand(self):
        assert self.sat_demand is not None   
        return self.sat_demand

    def get_length(self) -> float:
        length = 0
        for link in self.route_link_list:
            length += link.length
        for link in self.return_route_link_list:
            length += link.length
        
        return length

    def get_stopfacilities(self) -> List[NetworkLink]:
        stoplist = []
        for link in self.route_link_list:
            if link.is_stop:
                stoplist.append(link.stopfacility)
                assert link.origin.is_stop
        stoplist.append(self.return_route_link_list[0].stopfacility)
        assert self.return_route_link_list[0].origin.is_stop

        return stoplist

    def get_nearest_stop(self, node: NetworkNode):
        if node.id in self.node_id_to_nearest_stop_id_dict:
            return self.node_id_to_nearest_stop_id_dict[node.id]

        coord_node = (node.x, node.y)
        mindist = float("inf")
        mindist_stop = None
        for link in self.route_link_list:
            if link.is_stop:
                dist = self.__calc_euclid_dist(coord_node, (link.origin.x, link.origin.y))
                if mindist_stop is None or mindist > dist:
                    mindist_stop = link.origin
                    mindist = dist

        assert mindist_stop is not None

        self.node_id_to_nearest_stop_id_dict[node.id] = mindist_stop
        return self.node_id_to_nearest_stop_id_dict[node.id]

    def set_depertures(self, schedule_list: List[Schedule]):
        for schedule in enumerate(schedule_list):
            self.deperture_list.append(schedule)

    def set_profilelist(self, profile_list: List[NetworkRouteProfileEntry]):
        self.profilelist = profile_list