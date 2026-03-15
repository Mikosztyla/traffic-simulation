import pygame
from stop_car import StopCar


class StatsPanel:

    def __init__(self, all_roads, crossing):
        self.font = pygame.font.SysFont(None, 26)
        self.roads = all_roads
        self.crossing = crossing

    def get_current_cars(self):
        current_cars_number = 0
        for road in self.roads:
            for lane in road.lanes:
                for car in lane.cars:
                    if isinstance(car, StopCar):
                        continue
                    current_cars_number += 1
        for connector in self.crossing.connectors:
            current_cars_number += len(connector.cars)
        return current_cars_number

    def draw(self, screen, stats):

        padding = 5
        line_height = 22

        x = 10
        y = 10

        # background box
        height = line_height * len(stats) + padding * 2
        width = 220

        rect = pygame.Rect(x - 5, y - 5, width, height)
        pygame.draw.rect(screen, (30, 30, 30), rect)
        pygame.draw.rect(screen, (80, 80, 80), rect, 2)

        for label, value in stats.items():
            text = f"{label}: {value}"
            text_surface = self.font.render(text, True, (255, 255, 255))
            screen.blit(text_surface, (x, y))
            y += line_height