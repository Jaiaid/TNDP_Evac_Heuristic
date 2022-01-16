import simpy
from Vehicle import Vehicle

SECOND_TO_SIMULATE = 3600*48
NUMBER_OF_BUS = 5

if __name__=="__main__":
    env = simpy.Environment(SECOND_TO_SIMULATE)
    env.run(until=SECOND_TO_SIMULATE)