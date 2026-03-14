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
from random import random, choice

pygame.init()

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
center = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
road_length = 700  # length from crossing to edge
offset = LANE_WIDTH * LANES_PER_SIDE
offset_road = offset / 2
north_road_in = Road(pygame.Vector2(center.x + offset_road, center.y + road_length), pygame.Vector2(center.x + offset_road, center.y + offset), Side.N)
north_road_out = Road(pygame.Vector2(center.x + offset_road, center.y - offset), pygame.Vector2(center.x + offset_road, center.y - road_length), Side.N)
south_road_in = Road(pygame.Vector2(center.x - offset_road, center.y - road_length), pygame.Vector2(center.x - offset_road, center.y - offset), Side.S)
south_road_out = Road(pygame.Vector2(center.x - offset_road, center.y + offset), pygame.Vector2(center.x - offset_road, center.y + road_length), Side.S)

# Horizontal roads (E-W)
west_road_in = Road(pygame.Vector2(center.x + road_length, center.y - offset_road), pygame.Vector2(center.x + offset, center.y - offset_road), Side.W)
west_road_out = Road(pygame.Vector2(center.x - offset, center.y - offset_road), pygame.Vector2(center.x - road_length, center.y - offset_road), Side.W)
east_road_in = Road(pygame.Vector2(center.x - road_length, center.y + offset_road), pygame.Vector2(center.x - offset, center.y + offset_road), Side.E)
east_road_out = Road(pygame.Vector2(center.x + offset, center.y + offset_road), pygame.Vector2(center.x + road_length, center.y + offset_road), Side.E)

roads_in = [north_road_in, south_road_in, west_road_in, east_road_in]
roads_out = [north_road_out, south_road_out, west_road_out, east_road_out]
all_roads = roads_in + roads_out
# -----------------------------
# Crossing
# -----------------------------
crossing = Crossing(north_road_in, north_road_out, east_road_in, east_road_out, south_road_in, south_road_out, west_road_in, west_road_out)
traffic_lights = []
# for road in roads_in:
#     for lane in road.lanes:
#         # Position slightly before the crossing
#         offset = lane.end - lane.start
#         pos = lane.end - offset.normalize() * 30
#         traffic_lights.append(TrafficLight(lane, pos, (TRAFFIC_LIGHT_WIDTH, TRAFFIC_LIGHT_HEIGHT)))

running = True
def fill_background(screen):
    screen.fill((0, 160, 0))

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for tl in traffic_lights:
                tl.handle_click(event.pos)

    fill_background(screen)

    # Draw roads
    for road in all_roads:
        road.draw(screen)

    # Update traffic lights
    for tl in traffic_lights:
        tl.update(dt)
        tl.draw(screen)

    spawn_timer += dt
    if spawn_timer >= spawn_interval:
        road = choice(roads_in)
        lane = choice(road.lanes)
        speed = ROAD_SPEED_LIMIT if random() > 0.8 else random() * 10
        cars.append(lane.spawn_car(10, speed))
        spawn_timer = 0
        spawn_interval = random() * (MAX_SPAWN_INTERVAL - MIN_SPAWN_INTERVAL) + MIN_SPAWN_INTERVAL

    for road in all_roads:
        for i, lane in enumerate(road.lanes):
            right_lane = road.lanes[i - 1] if i > 0 else None
            left_lane = road.lanes[i + 1] if i + 1 < len(road.lanes) else None
            lane.update_cars(dt, right_lane, left_lane)
    crossing.update_cars(dt)
    # Draw cars
    for car in cars:
        car.draw(screen, car_image)
    crossing.draw_connectors(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
