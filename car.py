import pygame
from constants import *
from idm_model import IDM
from mobil_model import MOBIL


class Car:
    def __init__(self, lane, speed, target_in_lane_index):
        self.current_lane = lane
        self.speed = speed
        self.progress = 0.0  # 0 = start, 1 = end
        self.length = CAR_LENGTH
        self.position = lane.start.copy()
        self.last_lane_change = LANE_CHANGE_COOLDOWN - 0.2
        self.in_crossing = False
        self.crossing_target = None
        self.target_in_lane_index = target_in_lane_index
        self.idm = IDM(
            max_speed=self.current_lane.speed_limit,
            time_headway=0.5,
            min_gap=1,
            acc=1.5,
            dcc=3
        )

        self.mobil = MOBIL(
            politeness=0.4,
            save_dcc=3,
            acc_thr=0.4,
            bias=0.5
        )

    def update(self, following_car, right_lane, left_lane, dt):
        # if self.animate_driving_on_crossing(dt): return False
        lane_vector = self.current_lane.end - self.current_lane.start
        lane_length = lane_vector.length()

        gap = self.get_gap(following_car)
        following_car_speed = following_car.speed if following_car else self.speed
        self.acc = self.idm.get_acc(self.speed, following_car_speed, gap)

        if self.speed + self.acc * dt < 0:
            stop_distance = -0.5 * self.speed**2 / self.acc * PIXELS_PER_METER
            self.speed = 0
            self.progress += stop_distance / lane_length
        else:
            self.progress += (self.speed * dt + 0.5 * self.acc * dt**2) * PIXELS_PER_METER/ lane_length
            self.speed += self.acc * dt

        if self.progress >= 1:
            return True

        self.position = self.current_lane.start.lerp(
            self.current_lane.end,
            self.progress
        )

        self.last_lane_change += dt
        if self.last_lane_change < LANE_CHANGE_COOLDOWN or self.speed < LANE_CHANGE_SPEED_THRESHOLD:
            return False

        distance_to_crossing = (1 - self.progress) * lane_length / PIXELS_PER_METER
        if distance_to_crossing < 60:
            if right_lane:
                if self.consider_lane_change(right_lane, to_right=True):
                    print("changing")
                    self.do_lane_change(right_lane)
                    return True
            if left_lane:
                if self.consider_lane_change(left_lane, to_right=False):
                    print("changing")
                    self.do_lane_change(left_lane)
                    return True

        return False

    def animate_driving_on_crossing(self, dt):
        if self.in_crossing:
            direction = self.crossing_target - self.position
            dist = direction.length()

            if dist < 1:
                self.progress = 1
                return True

            direction = direction.normalize()

            move = self.speed * dt * PIXELS_PER_METER

            if move >= dist:
                self.position = self.crossing_target
                self.progress = 1
            else:
                self.position += direction * move

            return True
        return False

    def get_gap(self, following_car):
        if following_car is None:
            return float("inf")

        center_distance = (following_car.position - self.position).length()
        gap = (center_distance - (self.length / 2) - (following_car.length / 2)) / PIXELS_PER_METER

        return max(gap, 0.1)
    
    def _get_neighbour_cars(self, target_lane):
        for i, car in enumerate(target_lane.cars):
            if car.progress > self.progress: 
                lead_car = car
                lag_car = target_lane.cars[i - 1] if i - 1 >= 0 else None
                break
        else:
            lead_car = None
            lag_car = target_lane.cars[-1] if target_lane.cars else None

        return lead_car, lag_car

    def consider_lane_change(self, target_lane, to_right):
        current_index = self.current_lane.road.lanes.index(self.current_lane)
        if to_right and current_index <= self.target_in_lane_index:
            return False
        if not to_right and current_index >= self.target_in_lane_index:
            return False
        lead_car, lag_car = self._get_neighbour_cars(target_lane)
        if lead_car is not None and lead_car.last_lane_change == 0: # lead_car is changing lane
            return False

        new_acc = self.idm.get_acc(
            self.speed,
            lead_car.speed if lead_car else self.speed,
            self.get_gap(lead_car)
        )

        new_lag_acc = 0
        if lag_car:
            new_lag_acc = lag_car.idm.get_acc(
                lag_car.speed,
                self.speed,
                lag_car.get_gap(self)
            )

        return self.mobil.consider_line_change(self.acc, new_acc, new_lag_acc, to_right)
    
    def do_lane_change(self, target_lane):
        target_lane.add_car(self)
        self.current_lane = target_lane

        self.position = self.current_lane.start.lerp(
            self.current_lane.end,
            self.progress
        )
        self.last_lane_change = 0


    def draw(self, screen, car_image):
        # compute lane direction vector
        direction = self.current_lane.end - self.current_lane.start
        if direction.length() == 0:
            return
        angle = direction.angle_to(pygame.Vector2(0, -1))  # angle between lane and upward vector

        # rotate the car image
        rotated_image = pygame.transform.rotate(car_image, angle)

        # get the rect centered at car position
        rect = rotated_image.get_rect(center=self.position)

        screen.blit(rotated_image, rect)
