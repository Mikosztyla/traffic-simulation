import pygame
from constants import *


class TrafficLight:

    def __init__(self, lane, position, size=(40, 100)):
        self.lane = lane
        self.position = pygame.Vector2(position)
        self.size = size

        self.images = {
            "red": pygame.transform.smoothscale(
                pygame.image.load("media/traffic_red.png").convert_alpha(), size
            ),
            "yellow": pygame.transform.smoothscale(
                pygame.image.load("media/traffic_yellow.png").convert_alpha(), size
            ),
            "green": pygame.transform.smoothscale(
                pygame.image.load("media/traffic_green.png").convert_alpha(), size
            ),
            "red_yellow": pygame.transform.smoothscale(
                pygame.image.load("media/traffic_red_yellow.png").convert_alpha(), size
            ),
        }

        self.timer = 0
        self.state = "red"
        self.sequence = None
        self.rect = pygame.Rect(self.position.x, self.position.y, *size)
        self.turn_on_red()

    def turn_on_red(self):
        self.state = "red"
        self.sequence = None
        self.lane.set_red_light(self.position)

    def turn_on_green(self):
        self.state = "green"
        self.sequence = None
        self.lane.set_green_light()

    def turn_on_yellow(self):
        self.state = "yellow"
        self.sequence = None

    def turn_on_red_yellow(self):
        self.state = "red_yellow"
        self.sequence = None

    def start_red_to_green(self):
        self.sequence = "red_to_green"
        self.timer = 0
        self.state = "red_yellow"

    def start_green_to_red(self):
        self.sequence = "green_to_red"
        self.timer = 0
        self.state = "yellow"

    def update(self, dt):
        if self.sequence is None:
            return

        self.timer += dt

        if self.sequence == "red_to_green":
            if self.timer >= TRAFFIC_RED_YELLOW_TIME:
                self.turn_on_green()

        elif self.sequence == "green_to_red":
            if self.timer >= TRAFFIC_YELLOW_TIME:
                self.turn_on_red()

    def handle_click(self, mouse_pos):
        if self.sequence is not None:
            return

        if not self.rect.collidepoint(mouse_pos):
            return

        local_x = mouse_pos[0] - self.rect.x
        local_y = mouse_pos[1] - self.rect.y

        if self.mask.get_at((local_x, local_y)) == 0:
            return

        if self.state == "red":
            self.start_red_to_green()
        elif self.state == "green":
            self.start_green_to_red()

    def draw(self, screen):
        image = self.images[self.state]

        self.rotated_image = pygame.transform.rotate(image, self.angle)
        self.rect = self.rotated_image.get_rect(center=self.position)

        screen.blit(self.rotated_image, self.rect)

        self.mask = pygame.mask.from_surface(self.rotated_image)
