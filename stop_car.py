from car import Car
from constants import *

class StopCar(Car):

    def __init__(self, lane, progress, speed, target_in_lane_index):
        super().__init__(lane, speed, target_in_lane_index)
        self.last_lane_change = 0
        self.length = CAR_LENGTH
        self.progress = progress
        self.speed = 0
        self.position = lane.start.lerp(lane.end, progress)

    def update(self, *args, **kwargs):
        return False

    def draw(self, *args, **kwargs):
        pass