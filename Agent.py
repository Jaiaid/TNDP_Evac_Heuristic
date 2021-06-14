class Agent:
    def __init__(self, id, home_node, home_link_id, home_left_time, shelter_node, shelter_link_id, route) -> None:
        self.id = id
        self.home = home_node.x
        self.shelter = shelter_node.x
        self.shelter_link = shelter_link_id
        self.home_link_id = home_link_id
        self.home_left_time = home_left_time
        self.stop = route.get_nearest_stop(home_node)