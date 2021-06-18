from NetworkNode import NetworkNode

class NetworkLink:pass

class StopFacility:
    def __init__(self, link: NetworkLink, is_blocking: str) -> None:
        self.id = str(link.origin.id) + "_" + str(link.dest.id)
        self.link = link
        self.is_blocking = is_blocking

class NetworkLink:
    def __init__(self, id: int, origin: NetworkNode, dest: NetworkNode, length: float, speed: float, capacity: int, lane_count: int, mode: str):
        self.id = id
        self.origin = origin
        self.dest = dest
        self.length = length
        self.speed = speed
        self.capacity = capacity
        self.lane_count = lane_count
        self.mode = mode

        self.arrival_offset = None
        self.deperture_offset = None
        
        self.stopfacility = None

    def create_stop_facility(self):
        self.is_stop = True
        self.origin.is_stop = True 
        self.stopfacility = StopFacility(self, "true")

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.origin.id == other.origin.id and self.dest.id == other.dest.id

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self.origin.id == other.origin.id and self.dest.id == other.dest.id)
