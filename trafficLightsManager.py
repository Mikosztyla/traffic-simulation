import pygame
from traffic_light import TrafficLight
from constants import *


class TrafficLightsManager:

    def __init__(self, in_roads):
        self.lights = []

        for road in in_roads:
            for lane in road.lanes:

                lane_vec = lane.end - lane.start
                direction = lane_vec.normalize()

                # perpendicular vector
                normal = pygame.Vector2(-direction.y, direction.x)

                # move back from intersection
                base_pos = lane.end - direction * TRAFFIC_LIGHT_OFFSET

                # shift to lane center
                pos = base_pos - normal

                angle = direction.angle_to(pygame.Vector2(0, -1))

                light = TrafficLight(
                    lane,
                    pos,
                    (TRAFFIC_LIGHT_WIDTH, TRAFFIC_LIGHT_HEIGHT)
                )

                light.angle = angle

                self.lights.append(light)

    def update(self, dt):
        for light in self.lights:
            light.update(dt)

    def draw(self, screen):
        for light in self.lights:
            light.draw(screen)

    def handle_click(self, mouse_pos):
        for light in self.lights:
            light.handle_click(mouse_pos)