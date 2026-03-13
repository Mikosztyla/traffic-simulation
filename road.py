import pygame
from lane import Lane
from constants import LANE_WIDTH
from side import Side
from car import Car
from random import choice

# direction - w którą stronę wskazuje wektor
# przyjmuję że najbardziej prawy pas to lanes[0]

class Road:
    def __init__(self, start: pygame.Vector2, end: pygame.Vector2, direction: Side, speed_limit=50, number_of_lanes=1):
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
                self.lanes.append(Lane(pygame.Vector2(left_start, self.start.y), pygame.Vector2(left_start, self.end.y), self.speed_limit, LANE_WIDTH))
                left_start += LANE_WIDTH
            if self.direction == Side.N:
                self.lanes.reverse()
        
        elif self.start.y == self.end.y: # horizontal (E-W)
            up_start = self.start.y - (self.number_of_lanes * LANE_WIDTH) // 2 + LANE_WIDTH // 2
            for _ in range(self.number_of_lanes):
                self.lanes.append(Lane(pygame.Vector2(self.start.x, up_start), pygame.Vector2(self.end.x, up_start), self.speed_limit, LANE_WIDTH))
                up_start += LANE_WIDTH
            if self.direction == Side.E:
                self.lanes.reverse()
        else:
            raise NotImplementedError("Only vertical or horizontal roads are allowed")

    def add_car(self, car: Car, lane_id):
        self.lanes[lane_id].add_car(car)

    def spawn_new_car(self, max_acc, max_speed=None):
        if not max_speed: max_speed = self.speed_limit
        lane = choice(self.lanes)
        return lane.spawn_car(max_acc, max_speed)
    
    def update_cars(self, dt):
        for lane in self.lanes:
            lane.update_cars(dt)
    
    def draw(self, screen):
        for lane in self.lanes:
            lane.draw(screen)