import pygame
import sys
from side import Side
from crossing import Crossing
from car import Car
from lane import Lane
from road import Road
from random import random
from constants import *
from traffic_light import TrafficLight
from car_generator import CarGenerator

pygame.init()

WIDTH, HEIGHT = 1200, 800
SPEED = 300
LANES_PER_SIDE = 1
LANE_WIDTH = 40

def fill_background(screen):
    screen.fill((0, 160, 0))


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic simulation")

clock = pygame.time.Clock()
clock.tick(60)
running = True

car_image = pygame.image.load("media/zygzak.png").convert_alpha()
car_image = pygame.transform.scale(car_image, (40, CAR_LENGTH))

car_pos = pygame.Vector2(WIDTH // 2 - 20, HEIGHT)
car_speed = 100

# car_rect = car_image.get_rect(topleft=car_pos)

# cars = []

# spawn_timer = 0
# MAX_SPAWN_INTERVAL = 2
# MIN_SPAWN_INTERVAL = 0.5

# spawn_interval = MIN_SPAWN_INTERVAL

# road = Road(pygame.Vector2(WIDTH // 2, -CAR_LENGTH), pygame.Vector2(WIDTH // 2, HEIGHT + CAR_LENGTH), Side.S, 14, 2)
road = Road(pygame.Vector2(WIDTH // 2, HEIGHT + CAR_LENGTH), pygame.Vector2(WIDTH // 2, -CAR_LENGTH), Side.N, 14, 2)
traffic_lights = [
    TrafficLight(road.lanes[0], (WIDTH // 2 + 60, HEIGHT // 2 - 100), (TRAFFIC_LIGHT_WIDTH, TRAFFIC_LIGHT_HEIGHT)),
    TrafficLight(road.lanes[1], (WIDTH // 2 - 100, HEIGHT // 2 - 100), (TRAFFIC_LIGHT_WIDTH, TRAFFIC_LIGHT_HEIGHT))]

car_generator = CarGenerator([road], 0.1)

while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            for traffic_light in traffic_lights:
                traffic_light.handle_click(event.pos)

    fill_background(screen)
    road.draw(screen, car_image)

    for traffic_light in traffic_lights:
        traffic_light.update(dt)
    
    car_generator.update(dt)
    road.update_cars(dt)

    # for car in cars:
    #     car.draw(screen, car_image)

    for traffic_light in traffic_lights:
        traffic_light.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
