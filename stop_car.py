from constants import *


# istnieje szansa że pojawi się problem, jak gdzieś się wywoła self.idm.get_acc przy mobilu ale jak coś to zrobię fixa
class StopCar():

    def __init__(self, lane, progress, speed, target_in_lane_index):
        self.last_lane_change = float('inf')
        self.length = STOP_OFFSET_METERS * PIXELS_PER_METER * 2
        self.progress = progress
        self.speed = 0
        self.position = lane.start.lerp(lane.end, progress)

    def calculate_acc(self, *args, **kwargs):
        return 0
    
    def get_gap(self, following_car):
        if following_car is None:
            return float("inf")

        center_distance = (following_car.position - self.position).length()
        gap = (center_distance - (self.length / 2) - (following_car.length / 2)) / PIXELS_PER_METER

        return max(gap, 0.1)

    def update(self, *args, **kwargs):
        return False

    def draw(self, *args, **kwargs):
        pass