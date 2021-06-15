from Vehicle import Vehicle

class Schedule:
    def __init__(self, id: int, start_time: str, vehicle: Vehicle) -> None:
        self.id = id
        self.start_time = start_time
        self.vehicle = vehicle

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self.id == other.id)