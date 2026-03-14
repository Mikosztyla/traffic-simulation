import pygame
import sys
from side import Side
from crossing import Crossing
from car import Car
from lane import Lane
from road import Road
from random import random
from constants import CAR_LENGTH

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

car_rect = car_image.get_rect(topleft=car_pos)

cars = []

spawn_timer = 0
MAX_SPAWN_INTERVAL = 2
MIN_SPAWN_INTERVAL = 0.5

spawn_interval = MIN_SPAWN_INTERVAL


# road = Road(pygame.Vector2(WIDTH // 2, -CAR_LENGTH), pygame.Vector2(WIDTH // 2, HEIGHT + CAR_LENGTH), Side.S, 14, 2)
road = Road(pygame.Vector2(WIDTH // 2, HEIGHT + CAR_LENGTH), pygame.Vector2(WIDTH // 2, -CAR_LENGTH), Side.N, 14, 2)

while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    fill_background(screen)
    road.draw(screen)
    
    spawn_timer += dt
    if spawn_timer >= spawn_interval:
        speed = random() * 10
        if random() > 0.8: 
            speed = 14
        cars.append(road.spawn_new_car(10, speed))
        spawn_timer = 0
        spawn_interval = random() * (MAX_SPAWN_INTERVAL - MIN_SPAWN_INTERVAL) + MIN_SPAWN_INTERVAL
        # spawn_interval = 100

    road.update_cars(dt)

    for car in cars:
        car.draw(screen, car_image)
    pygame.display.flip()

pygame.quit()
sys.exit()
