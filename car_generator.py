import random
from constants import *
from car import Car

# jak byśmy chcieli żeby spawnowały się niezależnie to wystarczy osobne generatory dla każdej drogi
# jaki speed?

# inflow - [cars/s]
class CarGenerator:
    def __init__(self, inflow_roads, inflow):
        self.inflow_roads = inflow_roads
        self.inflow = inflow
        self.time_since_last = 0

    def update(self, dt):
        self.time_since_last += dt
        real_interval = random.expovariate(self.inflow)
        print(self.time_since_last, real_interval)
        if self.time_since_last < real_interval:
            return
        
        self.time_since_last = 0
        
        available_lanes = []
        for road in self.inflow_roads:
            available_lanes.extend(road.get_available_spawn_lanes())

        if not available_lanes:
            # print("Cannot place a new car")
            return

        spawn_lane = random.choice(available_lanes)
        car = Car(spawn_lane, random.random() * 10)
        spawn_lane.add_car(car)

        


    