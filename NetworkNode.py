class NetworkNode:
    def __init__(self, id, x, y, is_stop):
        self.id = id
        self.x = x
        self.y = y
        self.is_stop = is_stop
        self.arrival_offset = None
        self.deperture_offset = None
