class NetworkLink:
    def __init__(self, id, origin, dest, speed, capacity, lane_count, mode):
        self.id = id
        self.origin = origin
        self.dest = dest
        self.is_stop = origin.is_stop
        self.speed = speed
        self.capacity = capacity
        self.lane_count = lane_count
        self.mode = mode
