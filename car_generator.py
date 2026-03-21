import random
from constants import *
from car import Car
from direction import Direction
from side import Side
import pygame

# inflow - [cars/s]


def get_random_direction():
    if RIGHT_PROBABILITY + LEFT_PROBABILITY > 1:
        raise ValueError(f"Sum of left and right turn probabilities grater then 0 ({LEFT_PROBABILITY} + {RIGHT_PROBABILITY} = {LEFT_PROBABILITY + RIGHT_PROBABILITY})")
    
    possible_directions = [Direction.LEFT, Direction.STRAIGHT, Direction.RIGHT]
    weights = [LEFT_PROBABILITY, 1 - (LEFT_PROBABILITY + RIGHT_PROBABILITY), RIGHT_PROBABILITY]
    return random.choices(possible_directions, weights=weights, k=1)[0]


def generate_input_file(filename, total_time, inflow):
    t = 0.0
    events = []

    while t < total_time:
        dt = random.expovariate(inflow)
        t += dt

        side = random.choice(list(Side))
        direction = get_random_direction()

        events.append((dt, side.name, direction.name))

    with open(filename, "w") as f:
        for dt, side, direction in events:
            f.write(f"{dt},{side},{direction}\n")


def read_input_file(filename):
    events = []

    with open(filename, "r") as f:
        for line in f:
            dt, side, direction = line.strip().split(",")

            events.append({
                "dt": float(dt),
                "side": Side[side],
                "direction": Direction[direction]
            })

    return events

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
        self.events = []
        # self.events = read_input_file("test.csv")
        self.event_index = 0
        self.time_to_next_event = self.events[0]["dt"] if self.events else None

        self.waiting_queue = []
        # generate_input_file("test.csv", 60, INFLOW)

    def _get_next_spawn_time(self):
        return min(MAX_SPAWN_TIME, random.expovariate(self.inflow), MAX_SPAWN_TIME)

    def update(self, dt):
        if self.events:
            self._update_from_file(dt)
        else:
            self._update_random(dt)

    def _update_from_file(self, dt):
        if self.time_to_next_event is None:
            return

        self.time_to_next_event -= dt

        if self.time_to_next_event <= 0:
            event = self.events[self.event_index]
            self._try_spawn(event)

            self.event_index += 1
            if self.event_index < len(self.events):
                self.time_to_next_event = self.events[self.event_index]["dt"]
            else:
                self.time_to_next_event = None

        # Try to spawn queued cars
        self._process_waiting_queue()

    def _try_spawn(self, event):
        side = event["side"]
        direction = event["direction"]

        lanes = []
        for road in self.inflow_roads:
            if road.direction == side:
                lanes.extend(road.get_available_spawn_lanes())

        if not lanes:
            self.waiting_queue.append(event)
            return False

        lane = random.choice(lanes)
        # print(f"spawning car on side {side} with direction {direction}")
        self._spawn_car(lane, direction)
        return True

    def _process_waiting_queue(self):
        still_waiting = []

        for event in self.waiting_queue:
            if not self._try_spawn(event):
                still_waiting.append(event)

        self.waiting_queue = still_waiting

    def _spawn_car(self, lane, direction):
        car = Car(
            lane,
            random.random() * 10,
            direction,
            self.car_images[direction]
        )
        self.total_spawned += 1
        lane.add_car(car)

    def _update_random(self, dt):
        self.time_since_last += dt
        if self.time_since_last < self.next_spawn_time:
            return

        self.time_since_last = 0
        self.next_spawn_time = self._get_next_spawn_time()

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
