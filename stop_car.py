from constants import *


# istnieje szansa że pojawi się problem, jak gdzieś się wywoła self.idm.get_acc przy mobilu ale jak coś to zrobię fixa
class StopCar():

    def __init__(self, lane, progress, speed, target_in_lane_index):
        self.last_lane_change = 0
        self.length = STOP_OFFSET_METERS * PIXELS_PER_METER * 2
        self.progress = progress
        self.speed = 0
        self.position = lane.start.lerp(lane.end, progress)

    def update(self, *args, **kwargs):
        return False

    def draw(self, *args, **kwargs):
        pass