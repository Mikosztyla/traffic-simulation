import random
from constants import *
from car import Car
from direction import Direction


# jak byśmy chcieli żeby spawnowały się niezależnie to wystarczy osobne generatory dla każdej drogi
# jaki speed?

# inflow - [cars/s]


# TODO: lepsze losowanie kierunku jazdy przy spawnowaniu auta
def get_random_direction():
    return random.choice(list(Direction))


class CarGenerator:
    def __init__(self, inflow_roads, inflow):
        self.inflow_roads = inflow_roads
        self.inflow = inflow
        self.time_since_last = 0

    def update(self, dt):
        self.time_since_last += dt
        # real_interval = random.expovariate(self.inflow)
        real_interval = 1
        # print(self.time_since_last, real_interval)
        if self.time_since_last < real_interval:
            return

        self.time_since_last = 0

        available_lanes = []
        for road in self.inflow_roads:
            available_lanes.extend(road.get_available_spawn_lanes())

        for available_lane in available_lanes:
            if available_lane.is_connector:
                available_lanes.remove(available_lane)

        if not available_lanes:
            # print("Cannot place a new car")
            return
        spawn_lane = random.choice(available_lanes)
        # for _, c, _ in spawn_lane.road.crossing.connectors:
        #     if c == spawn_lane:
        #         print("dupa")
        # print(f"spawning car on {spawn_lane}")
        car = Car(spawn_lane, random.random() * 10, get_random_direction())
        spawn_lane.add_car(car)
