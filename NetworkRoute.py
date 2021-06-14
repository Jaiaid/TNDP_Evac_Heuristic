from .NetworkLink import NetworkLink
from .NetworkNode import NetworkNode
from .Vehicle import Vehicle

class NetworkRoute:
    def __init__(self, id):
        self.id = id
        self.route_link_list = []
        self.return_route_link_list = []
        self.shelter_link_id = None
        self.stop_node_list = []
        self.round_trip_count = 0
        self.vehicle_list = []

    def add_link(self, link):
        self.route_node_list.append(link)
        if link.is_stop:
            self.stop_node_list.append(link.stop_node)
    
    def add_return_link(self, link):
        self.return_route_link_list.append(link)
        if link.is_stop:
            self.stop_node_list.append(link.stop_node)

    def add_vehicle(self, vehicle):
        self.vehicle_list.append(vehicle)

    def set_round_trip_count(self, count):
        self.round_trip_count = count

    def __calc_euclid_dist(coord1, coord2):
        return ((coord1[0]-coord2[0])**2 + (coord1[1]-coord2[1])**2)**0.5 

    def get_nearest_stop(node):
        return None

    def get_depertures(self, vehicle_list, schedule_list):
        return None