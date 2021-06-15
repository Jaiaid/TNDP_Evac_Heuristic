class Vehicle:
    def __init__(self, id: str, seat: int, standing: int, length: float, pce: float):
        self.id = id
        self.seat = seat
        self.standing = standing
        self.length = length
        self.pce = pce

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self.id == other.id)