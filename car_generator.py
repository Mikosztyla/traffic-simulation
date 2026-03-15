import random
from constants import *
from car import Car
from direction import Direction
import pygame

# inflow - [cars/s]

def get_random_direction():
    if RIGHT_PROBABILITY + LEFT_PROBABILITY > 1:
        raise ValueError(f"Sum of left and right turn probabilities grater then 0 ({LEFT_PROBABILITY} + {RIGHT_PROBABILITY} = {LEFT_PROBABILITY + RIGHT_PROBABILITY})")
    
    possible_directions = [Direction.LEFT, Direction.STRAIGHT, Direction.RIGHT]
    weights = [LEFT_PROBABILITY, 1 - (LEFT_PROBABILITY + RIGHT_PROBABILITY), RIGHT_PROBABILITY]
    return random.choices(possible_directions, weights=weights, k=1)[0]


class CarGenerator:
    def __init__(self, inflow_roads, inflow):
        self.inflow_roads = inflow_roads
        self.inflow = inflow
        self.time_since_last = 0
        self.next_spawn_time = self._get_next_spawn_time()
        self.total_spawned = 0
        car_img_right = pygame.image.load("media/zygzak_blue.png").convert_alpha()
        car_img_straight = pygame.image.load("media/zygzak.png").convert_alpha()
        car_img_left = pygame.image.load("media/zygzak_green.png").convert_alpha()
        car_img_right = pygame.transform.scale(car_img_right, (40, CAR_LENGTH))
        car_img_straight = pygame.transform.scale(car_img_straight, (40, CAR_LENGTH))
        car_img_left = pygame.transform.scale(car_img_left, (40, CAR_LENGTH))
        self.car_images = {
            Direction.RIGHT: car_img_right,
            Direction.STRAIGHT: car_img_straight,
            Direction.LEFT: car_img_left
        }

    def _get_next_spawn_time(self):
        return min(MAX_SPAWN_TIME, random.expovariate(self.inflow), MAX_SPAWN_TIME)

    def update(self, dt):
        self.time_since_last += dt
        if self.time_since_last < self.next_spawn_time:
            return

        self.time_since_last = 0
        self.next_spawn_time = self._get_next_spawn_time()
        # self.next_spawn_time = 100

        available_lanes = []
        for road in self.inflow_roads:
            available_lanes.extend(road.get_available_spawn_lanes())

        if not available_lanes:
            # print("Cannot place a new car")
            return
        
        spawn_lane = random.choice(available_lanes)
        direction = get_random_direction()
        car = Car(spawn_lane, random.random() * 10, direction, self.car_images[direction])
        self.total_spawned += 1
        spawn_lane.add_car(car)
