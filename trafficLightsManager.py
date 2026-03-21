import pygame
from traffic_light import TrafficLight
from constants import *


class TrafficLightsManager:

    def __init__(self, in_roads):
        self.lights = []
        self.lights_by_road = {}

        self.mode_auto = False

        self.phase_time = 10
        self.timer = 0
        self.current_phase = 0

        for road in in_roads:

            self.lights_by_road[road] = []

            for lane in road.lanes:
                lane_vec = lane.end - lane.start
                direction = lane_vec.normalize()

                normal = pygame.Vector2(-direction.y, direction.x)

                base_pos = lane.end - direction * TRAFFIC_LIGHT_OFFSET
                pos = base_pos - normal

                angle = direction.angle_to(pygame.Vector2(0, -1))

                light = TrafficLight(
                    lane,
                    pos,
                    (TRAFFIC_LIGHT_WIDTH, TRAFFIC_LIGHT_HEIGHT)
                )

                light.angle = angle

                self.lights.append(light)
                self.lights_by_road[road].append(light)

        self.toggle_mode()

    def update(self, dt):

        if self.mode_auto:
            self.timer += dt

            if self.timer >= self.phase_time:
                self.timer = 0
                self.current_phase = (self.current_phase + 1) % len(self.lights_by_road)
                self._apply_phase()

        for light in self.lights:
            light.update(dt)

    def _apply_phase(self):

        roads = list(self.lights_by_road.keys())

        for i, road in enumerate(roads):

            for light in self.lights_by_road[road]:

                if i % 2 == self.current_phase % 2:
                    if light.is_red():
                        light.start_red_to_green()

                else:
                    if light.is_green():
                        light.start_green_to_red()

    def toggle_mode(self):
        self.mode_auto = not self.mode_auto
        self.timer = 0
        self.current_phase = 0

        if self.mode_auto:
            self._apply_phase()

    def draw(self, screen):
        for light in self.lights:
            light.draw(screen)

    def handle_click(self, mouse_pos):
        if self.mode_auto:
            return

        for light in self.lights:
            light.handle_click(mouse_pos)