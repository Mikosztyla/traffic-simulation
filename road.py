import pygame
from lane import Lane
from constants import *
from side import Side
from car import Car
from constants import *

# direction - w którą stronę wskazuje wektor
# przyjmuję że najbardziej prawy pas to lanes[0]

class Road:
    def __init__(self, start: pygame.Vector2, end: pygame.Vector2, direction: Side, speed_limit=ROAD_SPEED_LIMIT, number_of_lanes=LANES_PER_SIDE):
        self.start = start
        self.end = end
        self.number_of_lanes = number_of_lanes
        self.lanes = []
        self.direction = direction
        self.speed_limit = speed_limit
        self._create_lanes()

    def _create_lanes(self):
        if self.start.x == self.end.x: # vertical (N-S)
            left_start = self.start.x - (self.number_of_lanes * LANE_WIDTH) // 2 + LANE_WIDTH // 2
            for _ in range(self.number_of_lanes):
                self.lanes.append(Lane(pygame.Vector2(left_start, self.start.y), pygame.Vector2(left_start, self.end.y), self, self.speed_limit, LANE_WIDTH))
                left_start += LANE_WIDTH
            if self.direction == Side.N:
                self.lanes.reverse()
        
        elif self.start.y == self.end.y: # horizontal (E-W)
            up_start = self.start.y - (self.number_of_lanes * LANE_WIDTH) // 2 + LANE_WIDTH // 2
            for _ in range(self.number_of_lanes):
                self.lanes.append(Lane(pygame.Vector2(self.start.x, up_start), pygame.Vector2(self.end.x, up_start), self, self.speed_limit, LANE_WIDTH))
                up_start += LANE_WIDTH
            if self.direction == Side.E:
                self.lanes.reverse()
        else:
            raise NotImplementedError("Only vertical or horizontal roads are allowed")

    def add_car(self, car: Car, lane_id):
        self.lanes[lane_id].add_car(car)

    def get_available_spawn_lanes(self):
        available_lanes = []
        for lane in self.lanes:
            if not lane.cars or lane.cars[0].progress * (lane.end - lane.start).length() > MIN_SPAWN_GAP_M * PIXELS_PER_METER:
                available_lanes.append(lane)
        return available_lanes
    
    def update_cars(self, dt):
        for i, lane in enumerate(self.lanes):
            right_lane = self.lanes[i - 1] if i > 0 else None
            left_lane = self.lanes[i + 1] if i + 1 < self.number_of_lanes else None
            lane.update_cars(dt, right_lane, left_lane)
    
    def draw(self, screen):
        for lane in self.lanes:
            lane.draw(screen)
