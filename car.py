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

        self.is_changing_lane = False
        self.lc_timer = 0
        self.source_lane = None
        self.target_lane = None

        self.idm = IDM(
            max_speed=self.current_lane.speed_limit,
            time_headway=0.8,
            min_gap=1,
            acc=2.5,
            dcc=2
        )

        self.mobil = MOBIL(
            politeness=POLITENESS,
            save_dcc=SAVE_DCC,
            acc_thr=ACC_THRESHOLD,
            bias=BIAS
        )

        self.mobil_mandatory_left = MOBIL(
            politeness=M_POLITENESS,
            save_dcc=M_SAVE_DCC,
            acc_thr=M_ACC_THRESHOLD,
            bias=-M_BIAS
        )

        self.mobil_mandatory_right = MOBIL(
            politeness=M_POLITENESS,
            save_dcc=M_SAVE_DCC,
            acc_thr=M_ACC_THRESHOLD,
            bias=M_BIAS
        )

        self.stop_cars = {MOBIL_STOP_CAR: None,
                          CONFLICT_STOP_CAR: None}

    def update(self, following_car, right_lane, left_lane, dt):
        lane_vector = self.current_lane.end - self.current_lane.start
        lane_length = lane_vector.length()       

        self._update_acc(following_car)
        self._update_progress(dt, lane_length)
        
        if self.is_changing_lane:
            self._update_lane_change(dt)
        else:
            self.position = self.current_lane.start.lerp(
                self.current_lane.end,
                self.progress
            )

        # finished current lane
        if self.progress >= 1:
            return True

        self._check_conflicts(lane_length)

        # check if changing line is beneficial or mandatory
        self.last_lane_change += dt
        if not self.is_changing_lane:
            if self.direction == Direction.RIGHT:
                return self._mandatory_mobil_decision(right_lane, lane_length) 
            elif self.direction == Direction.LEFT:
                return self._mandatory_mobil_decision(left_lane, lane_length)
            return self._standard_mobil_decision(left_lane, right_lane, lane_length) 
        
    
    def _update_progress(self, dt, lane_length):
        if self.speed + self.acc * dt < 0:
            stop_distance = -0.5 * self.speed**2 / self.acc * PIXELS_PER_METER
            self.speed = 0
            self.progress += stop_distance / lane_length
        else:
            self.progress += (self.speed * dt + 0.5 * self.acc * dt**2) * PIXELS_PER_METER / lane_length
            self.speed += self.acc * dt
        self.progress = min(self.progress, 1)

    def get_lane_change_duration(self):
        t = min(self.speed / 12.0, 1.0)
        return LANE_CHANGE_DURATION_MAX - (LANE_CHANGE_DURATION_MAX - LANE_CHANGE_DURATION_MIN) * t
    
    def _update_lane_change(self, dt):
        self.lc_timer += dt

        duration = self.get_lane_change_duration()
        t = min(self.lc_timer / duration, 1)
        pos_a = self.source_lane.start.lerp(self.source_lane.end, self.progress)
        pos_b = self.target_lane.start.lerp(self.target_lane.end, self.progress)

        # smoother animation
        t = t * t * (3 - 2 * t)

        self.position = pos_a.lerp(pos_b, t)
        if t >= 1:
            self.is_changing_lane = False

    def _get_following_car(self, following_car, lane):
        if not following_car:
            # if first in lane and next lane exists, check the last car in next lane
            next_lane = lane.get_next_lane(self.direction)
            if next_lane:
                if next_lane.cars:
                    return next_lane.cars[0]
                # as a connector can be quite short, check also next road
                else:
                    next_next_line = next_lane.get_next_lane(Direction.STRAIGHT)
                    if next_next_line and next_next_line.cars:
                        return next_next_line.cars[0]
        return following_car
    
    def _update_acc(self, following_car):
        following_car = self._get_following_car(following_car, self.current_lane)

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
            self.progress * lane_length < LANE_CHANGE_COOLDOWN_PIXELS_BEFORE:
            return False
        
        if self.stop_cars[CONFLICT_STOP_CAR] is not None:
            return False

        distance_to_crossing = (1 - self.progress) * lane_length
        if distance_to_crossing > LANE_CHANGE_COOLDOWN_PIXELS_BEFORE:
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
        self._resolve_mandatory_lc_conflict(neighbour_lane)
        return False

    def _get_stop_car(self, dist_from_end_pixels, lane_length):
        progress = 1 - dist_from_end_pixels / lane_length
        progress = max(0, progress)
        return StopCar(self.current_lane, progress)
    
    def _is_lc_conflict(self, other):
        if other is not None:
            other_stop_car = other.stop_cars[MOBIL_STOP_CAR]
            if other_stop_car and \
                (other_stop_car.position - self.stop_cars[MOBIL_STOP_CAR].position).length() < self.current_lane.lane_width + 1:
                return True
        return False
    
    def _resolve_mandatory_lc_conflict(self, neighbour_lane):
        if self.direction == Direction.LEFT:
            lead_car, lag_car = self._get_neighbour_cars(neighbour_lane)
            if self._is_lc_conflict(lead_car):
                conflict_car = lead_car
            elif self._is_lc_conflict(lag_car):
                conflict_car = lag_car
            else:
                return
            
            conflict_car_id = neighbour_lane.cars.index(conflict_car)
            if conflict_car_id + 1 < len(neighbour_lane.cars):
                lead_conflict_car = neighbour_lane.cars[conflict_car_id + 1]
            else:
                self.stop_cars[MOBIL_STOP_CAR] = None
                return

            gap = (conflict_car.position - lead_conflict_car.position).length() - (conflict_car.length + lead_conflict_car.length) / 2
            if gap > MANDATORY_LC_CONFLICT_SAFE_GAP_PIXELS:
                self.stop_cars[MOBIL_STOP_CAR] = None

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

        new_acc = self.calculate_acc(self.speed, lead_car.speed if lead_car else self.speed, self.get_gap(lead_car))

        new_lag_acc = 0
        if lag_car:
            new_lag_acc = lag_car.calculate_acc(lag_car.speed, self.speed, lag_car.get_gap(self))

        return mobil_model.consider_line_change(self.acc, new_acc, new_lag_acc, to_right)
    
    def do_lane_change(self, target_lane):
        target_lane.add_car(self)
        self.source_lane = self.current_lane
        self.current_lane = target_lane
        self.target_lane = target_lane
        self.last_lane_change = 0
        self.lc_timer = 0
        self.is_changing_lane = True


    def draw(self, screen):
        direction = self.current_lane.end - self.current_lane.start
        angle = direction.angle_to(pygame.Vector2(0, -1))

        rotated_image = pygame.transform.rotate(self.image, angle)
        rect = rotated_image.get_rect(center=self.position)
        screen.blit(rotated_image, rect)
