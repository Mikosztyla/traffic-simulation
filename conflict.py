from math import sqrt
from constants import *
import pygame


class Conflict:
    def __init__(self, lane, directions, v1, v2):
        self.lane = lane
        self.directions = directions
        self.colision_point = self._calculate_colision_point(v1, v2)

    def _calculate_colision_point(self, v1, v2):
        d1 = v1.end - v1.start
        d2 = v2.end - v2.start
        cross = d1.x * d2.y - d1.y * d2.x

        diff = v2.start - v1.start
        t = (diff.x * d2.y - diff.y * d2.x) / cross

        intersection = v1.start + d1 * t

        return intersection
    
    def is_conflict(self, car):
        dist_to_conflict = (car.position - self.colision_point).length() / PIXELS_PER_METER
        # time to conflict, car.acc = const.
        v, a = car.speed, car.acc
        if abs(a) < 0.001:
            tc = dist_to_conflict / max(v, 0.1)
        else:
            disc = (v / a) ** 2 + 2 * dist_to_conflict / a
            if disc < 0:
                return False  # stop before collision point
            tc = - v / a + sqrt(disc)

        for other_car in self.lane.cars[::-1]:
            if other_car.direction is None:
                return False # stop car is placed - red light
            if other_car.direction in self.directions:
                other_s = (other_car.speed * tc + 0.5 * other_car.acc * tc ** 2) * PIXELS_PER_METER
                direction = (self.colision_point - other_car.position).normalize()
                pos_other_at_tc = other_car.position + direction * other_s
                car_gap = ((pos_other_at_tc - self.colision_point).length() - car.length) / PIXELS_PER_METER

                time_other_to_colision = car_gap / max(car.speed, other_car.speed, 0.1)

                if abs(car_gap) < SAFE_CONFLICT_GAP_METERS or \
                    (time_other_to_colision < TIME_BEFORE_CONFLICT and \
                    -TIME_AFTER_CONFLICT < time_other_to_colision):
                    return True
                
                # if abs(car_gap) > SAFE_CONFLICT_GAP_METERS and time_other_to_colision > TIME_BEFORE_CONFLICT:
                #     return False
                
        return False
    
    def draw_collision_point(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (int(self.colision_point.x), int(self.colision_point.y)), 5)