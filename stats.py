import pygame
from stop_car import StopCar


class StatsPanel:

    def __init__(self, all_roads, crossing):
        self.font = pygame.font.SysFont(None, 26)
        self.roads = all_roads
        self.crossing = crossing
        self.simulation_time = 0
        self.total_finished = 0
        self.finished_history = []
        self.last_frame_cars = 0

    def get_current_cars(self):
        current_cars = []
        for road in self.roads:
            for lane in road.lanes:
                for car in lane.cars:
                    if isinstance(car, StopCar):
                        continue
                    current_cars.append(car)
        for connector in self.crossing.connectors:
            for car in connector.cars:
                current_cars.append(car)
        return current_cars

    def get_flow_rate(self):
        if len(self.finished_history) < 2:
            return 0

        t0, c0 = self.finished_history[0]
        t1, c1 = self.finished_history[-1]

        dt = t1 - t0
        if dt == 0:
            return 0

        return (c1 - c0) / dt

    def get_avg_speed(self):
        cars = self.get_current_cars()
        if not cars:
            return 0

        total_speed = sum(car.speed for car in cars)
        return total_speed / len(cars)

    def update(self, dt):
        current_cars = len(self.get_current_cars())
        self.simulation_time += dt
        diff = self.last_frame_cars - current_cars
        if diff > 0:
            self.total_finished += diff
            self.finished_history.append((self.simulation_time, self.total_finished))
        cutoff = self.simulation_time - 4
        self.finished_history = [
            (t, c) for (t, c) in self.finished_history if t >= cutoff
        ]
        self.last_frame_cars = current_cars

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