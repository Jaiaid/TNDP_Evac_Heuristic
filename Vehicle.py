from NetworkLink import NetworkLink
from simpy import Environment

class Vehicle:
    def __init__(self, id: str, typename: str, seat: int, standing: int, length: float, pce: float):
        self.id = id
        self.typename = typename
        self.seat = seat
        self.standing = standing
        self.length = length
        self.pce = pce

    def set_max_speed(self, max_speed: float):
        self.max_speed = max_speed

    def set_sim_env(self, env: Environment):
        self.env = env
        self.action = env.process(self.run())
        self.cur_passenger_count = 0

    def set_stop_signal(self, signal: bool):
        self.stop= signal
    
    def set_waiting_time(self, wait_time: int):
        self.wait_time = wait_time

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self.id == other.id)

    def run(self):
        assert self.route is not None

        self.set_stop_signal = False
        while not self.stop:
            for route_link in self.route:
                route_link: NetworkLink
                yield self.env.timeout(route_link.length/self.max_speed)
                self.cur_passenger_count = max(self.seat+self.standing, route_link.stopfacility.demand)
                route_link.stopfacility.demand -= max(self.seat+self.standing, route_link.stopfacility.demand)
                yield self.env.timeout(self.wait_time)
