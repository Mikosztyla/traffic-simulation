from math import sqrt
from constants import IDM_DELTA

class IDM:
    def __init__(self, max_speed, time_headway, min_gap, acc, dcc):
        self.max_speed = max_speed
        self.time_headway = time_headway
        self.min_gap = min_gap
        self.acc = acc
        self.dcc = dcc

    def get_acc(self, speed, following_speed, gap):
        speed_diff = speed - following_speed
        s_star = self._calculate_s_star(speed, speed_diff)
        acc = self.acc * (1 - (speed / self.max_speed) ** IDM_DELTA - (s_star / gap) ** 2)
        return acc
    
        
    def _calculate_s_star(self, speed, speed_diff):
        return self.min_gap + max(0, speed * self.time_headway + speed * speed_diff / (2 * sqrt(self.acc * self.dcc)))
    
    def update_max_speed(self, max_speed):
        self.max_speed = max_speed