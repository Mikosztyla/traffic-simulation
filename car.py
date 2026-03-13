import pygame
from constants import CAR_LENGTH, PIXELS_PER_METER
from idm_model import IDM


class Car:
    def __init__(self, lane, speed):
        self.current_lane = lane
        self.speed = speed
        self.progress = 0.0  # 0 = start, 1 = end
        self.length = CAR_LENGTH
        self.position = lane.start.copy()
        
        self.idm = IDM(
            max_speed=self.current_lane.speed_limit,
            time_headway=0.5,
            min_gap=1,
            acc=2.5,
            dcc=3
        )

    def update(self, following_car, dt):
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

        return False
    
    def get_gap(self, following_car):
        if following_car is None:
            return float("inf")

        center_distance = (following_car.position - self.position).length()
        gap = (center_distance - (self.length / 2) - (following_car.length / 2)) / PIXELS_PER_METER

        return max(gap, 0.1)

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
