from NetworkNode import NetworkNode

class StopFacility:
    def __init__(self, origin: NetworkNode, dest: NetworkNode, linkid: int, is_blocking: str) -> None:
        self.id = str(origin.id) + "_" + str(dest.id)
        self.x = origin.x
        self.y = origin.y
        self.linkid = linkid
        self.is_blocking = is_blocking

class NetworkLink:
    def __init__(self, id: int, origin: NetworkNode, dest: NetworkNode, length: float, speed: float, capacity: int, lane_count: int, mode: str):
        self.id = id
        self.origin = origin
        self.dest = dest
        self.is_stop = origin.is_stop
        self.length = length
        self.speed = speed
        self.capacity = capacity
        self.lane_count = lane_count
        self.mode = mode

        self.arrival_offset = None
        self.deperture_offset = None
        
        self.stopfacility = None
        if self.is_stop:
            self.stopfacility = StopFacility(self.origin, self.dest, self.id, "true")

    def create_stop_facility(self):
        self.is_stop = True
        self.origin.is_stop = True 
        self.stopfacility = StopFacility(self.origin, self.dest, self.id, "true")

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.origin.id == other.origin.id and self.dest.id == other.dest.id

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self.origin.id == other.origin.id and self.dest.id == other.dest.id)
