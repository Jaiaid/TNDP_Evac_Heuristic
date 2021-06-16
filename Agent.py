from NetworkRoute import NetworkRoute
from NetworkLink import NetworkLink
from NetworkNode import NetworkNode

class Agent:
    def __init__(self, id: int, home_link: NetworkLink, home_left_time: str, shelter_link: NetworkLink, route: NetworkRoute):
        self.id = id
        self.shelter_link = shelter_link
        self.home_link = home_link
        self.home_left_time = home_left_time
        self.stoplink = route.get_nearest_stoplink(home_link)

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self.id == other.id)