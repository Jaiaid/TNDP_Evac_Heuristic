class NetworkNode:
    def __init__(self, id: int, x: float, y: float, is_stop: bool):
        self.id = id
        self.x = x
        self.y = y
        self.is_stop = is_stop

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self.id == other.id)
