import pygame
from direction import Direction


class DirectionLegend:

    def __init__(self, car_images):
        self.car_images = car_images
        self.font = pygame.font.SysFont(None, 24)

        self.labels = {
            Direction.LEFT: "Left",
            Direction.STRAIGHT: "Straight",
            Direction.RIGHT: "Right"
        }

    def draw(self, screen):

        padding = 30
        icon_size = 40
        spacing = 30

        x = 10
        y = screen.get_height() - (icon_size * 3 + spacing * 2 + padding)

        for direction in [Direction.LEFT, Direction.STRAIGHT, Direction.RIGHT]:

            img = pygame.transform.scale(self.car_images[direction], (icon_size, icon_size * 1.5))
            screen.blit(img, (x, y))

            text_surface = self.font.render(self.labels[direction], True, (255, 255, 255))
            screen.blit(text_surface, (x + icon_size + 10, y + icon_size // 2 + 5))

            y += icon_size + spacing