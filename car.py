from lane import Lane
import pygame


class Car:
    def __init__(self, lane: Lane, speed=100):
        self.current_lane = lane
        self.speed = speed
        self.progress = 0.0  # 0 = start, 1 = end
        self.position = lane.start.copy()

    def update(self, dt):
        lane_vector = self.current_lane.end - self.current_lane.start
        lane_length = lane_vector.length()

        if lane_length == 0:
            return

        self.progress += (self.speed * dt) / lane_length
        if self.progress >= 1:
            return True

        self.position = self.current_lane.start.lerp(
            self.current_lane.end,
            self.progress
        )
        return False

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
