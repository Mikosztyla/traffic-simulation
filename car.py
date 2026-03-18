import pygame
from constants import *
from models.idm_model import IDM
from models.mobil_model import MOBIL
from direction import Direction
from stop_car import StopCar

MOBIL_STOP_CAR = "Mobil_stop_car"
CONFLICT_STOP_CAR = "Conflict_stop_car"


class Car:
    def __init__(self, lane, speed, direction: Direction, image):
        self.current_lane = lane
        self.speed = speed
        self.acc = 0
        self.progress = 0.0  # 0 = start, 1 = end
        self.length = CAR_LENGTH
        self.position = lane.start.copy()
        self.last_lane_change = LANE_CHANGE_COOLDOWN - 0.2
        self.direction = direction
        self.image = image
        self.idm = IDM(
            max_speed=self.current_lane.speed_limit,
            time_headway=0.5,
            min_gap=1,
            acc=1.8,
            dcc=3
        )

        self.mobil = MOBIL(
            politeness=0.4,
            save_dcc=3,
            acc_thr=0.4,
            bias=0.5
        )

        self.mobil_mandatory_left = MOBIL(
            politeness=0.1,
            save_dcc=3,
            acc_thr=0,
            bias=-10
        )

        self.mobil_mandatory_right = MOBIL(
            politeness=0.1,
            save_dcc=3,
            acc_thr=0,
            bias=10
        )

        self.stop_cars = {MOBIL_STOP_CAR: None,
                          CONFLICT_STOP_CAR: None}

    def update(self, following_car, right_lane, left_lane, dt):
        lane_vector = self.current_lane.end - self.current_lane.start
        lane_length = lane_vector.length()

        self._update_acc(following_car)

        if self.speed + self.acc * dt < 0:
            stop_distance = -0.5 * self.speed**2 / self.acc * PIXELS_PER_METER
            self.speed = 0
            self.progress += stop_distance / lane_length
        else:
            self.progress += (self.speed * dt + 0.5 * self.acc * dt**2) * PIXELS_PER_METER / lane_length
            self.speed += self.acc * dt

        # finished current lane
        if self.progress >= 1:
            return True

        self.position = self.current_lane.start.lerp(
            self.current_lane.end,
            self.progress
        )

        self._check_conflicts(lane_length)

        # check if changing line is beneficial or mandatory
        self.last_lane_change += dt
        if self.direction == Direction.RIGHT:
            return self._mandatory_mobil_decision(right_lane, lane_length)
        elif self.direction == Direction.LEFT:
            return self._mandatory_mobil_decision(left_lane, lane_length)
        return self._standard_mobil_decision(left_lane, right_lane, lane_length)

    
    def _update_acc(self, following_car):
        if not following_car:
            # if first in lane and next lane exists, check the last car in next lane
            next_lane = self.current_lane.get_next_lane(self.direction)
            if next_lane:
                if next_lane.cars:
                    following_car = next_lane.cars[0]
                # as a connector can be quite short, check also next road
                else:
                    next_next_line = next_lane.get_next_lane(Direction.STRAIGHT)
                    if next_next_line and next_next_line.cars:
                        following_car = next_next_line.cars[0]

        gap = self.get_gap(following_car)
        following_car_speed = following_car.speed if following_car else self.speed
        self.acc = self.calculate_acc(self.speed, following_car_speed, gap)

        stop_car = self._get_closer_stop_car()
        if stop_car:
            stop_car_gap = self.get_gap(stop_car)
            self.acc = min(self.acc, self.calculate_acc(self.speed, stop_car.speed, stop_car_gap))

    def _get_closer_stop_car(self):
        stop_cars = [stop_car for stop_car in self.stop_cars.values() if stop_car is not None]
        min_progress = 1
        best_car = None
        for stop_car in stop_cars:
            if stop_car.progress <= min_progress:
                min_progress = stop_car.progress
                best_car = stop_car
        return best_car

    def _check_conflicts(self, lane_length):
        if (1 - self.progress) * lane_length > CHECK_CONFLICT_DIST_PIXELS:
            return # too far from intersection to check conflicts
        
        for possible_conflict in self.current_lane.conflicts.get(self.direction, []):
            if possible_conflict.is_conflict(self):
                self.stop_cars[CONFLICT_STOP_CAR] = self._get_stop_car(STOP_CONFLICT_DIST_M * PIXELS_PER_METER, lane_length)
                return
        self.stop_cars[CONFLICT_STOP_CAR] = None

    def calculate_acc(self, speed, following_car_speed, gap):
        return self.idm.get_acc(speed, following_car_speed, gap)

    def _standard_mobil_decision(self, left_lane, right_lane, lane_length):
        if self.last_lane_change < LANE_CHANGE_COOLDOWN or \
            self.speed < LANE_CHANGE_SPEED_THRESHOLD or \
            self.progress * lane_length < LANE_CHANGE_COOLDOWN_PIXELS:
            return False

        distance_to_crossing = (1 - self.progress) * lane_length
        if distance_to_crossing > LANE_CHANGE_COOLDOWN_PIXELS:
            if right_lane:
                if self.consider_lane_change(right_lane, to_right=True, mobil_model=self.mobil):
                    self.do_lane_change(right_lane)
                    return True
            if left_lane:
                if self.consider_lane_change(left_lane, to_right=False, mobil_model=self.mobil):
                    self.do_lane_change(left_lane)
                    return True

        return False
    

    def _mandatory_mobil_decision(self, neighbour_lane, lane_length):
        # already in good lane
        if neighbour_lane is None:
            self.stop_cars[MOBIL_STOP_CAR] = None
            return False
        
        number_of_lanes_to_change = self.current_lane.get_number_of_neighbour_lanes_in_direction(self.direction)
        if self.last_lane_change < MANDATORY_LC_COOLDOWN:
            self.stop_cars[MOBIL_STOP_CAR] = self._get_stop_car(number_of_lanes_to_change * MANDATORY_LC_DISTANCE_PER_LANE_PIXELS, lane_length)
            return False
        
        to_right = self.direction == Direction.RIGHT

        if to_right and self.consider_lane_change(neighbour_lane, True, self.mobil_mandatory_right) or \
            not to_right and self.consider_lane_change(neighbour_lane, False, self.mobil_mandatory_left):
            self.do_lane_change(neighbour_lane)
            self.stop_cars[MOBIL_STOP_CAR] = None
            return True

        self.stop_cars[MOBIL_STOP_CAR] = self._get_stop_car(number_of_lanes_to_change * MANDATORY_LC_DISTANCE_PER_LANE_PIXELS, lane_length)
        return False

    def _get_stop_car(self, dist_from_end_pixels, lane_length):
        progress = 1 - dist_from_end_pixels / lane_length
        progress = max(0, progress)
        return StopCar(self.current_lane, progress, 0, None)

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

    def consider_lane_change(self, target_lane, to_right, mobil_model):
        lead_car, lag_car = self._get_neighbour_cars(target_lane)
        if lead_car is not None and lead_car.last_lane_change == 0: # lead_car is changing lane
            return False

        new_acc = self.calculate_acc(self.speed, lead_car.speed if lead_car else self.speed, self.get_gap(lead_car))

        new_lag_acc = 0
        if lag_car:
            new_lag_acc = lag_car.calculate_acc(lag_car.speed, self.speed, lag_car.get_gap(self))

        return mobil_model.consider_line_change(self.acc, new_acc, new_lag_acc, to_right)
    
    def do_lane_change(self, target_lane):
        target_lane.add_car(self)
        self.current_lane = target_lane

        self.position = self.current_lane.start.lerp(
            self.current_lane.end,
            self.progress
        )
        self.last_lane_change = 0


    def draw(self, screen):
        # compute lane direction vector
        direction = self.current_lane.end - self.current_lane.start
        if direction.length() == 0:
            return
        angle = direction.angle_to(pygame.Vector2(0, -1))  # angle between lane and upward vector

        # rotate the car image
        rotated_image = pygame.transform.rotate(self.image, angle)

        # get the rect centered at car position
        rect = rotated_image.get_rect(center=self.position)

        screen.blit(rotated_image, rect)
