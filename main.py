import pygame
import sys
from side import Side
from crossing import Crossing
from road import Road
from constants import *
from car_generator import CarGenerator
from trafficLightsManager import TrafficLightsManager

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic simulation")

clock = pygame.time.Clock()
clock.tick(60)
running = True

car_image = pygame.image.load("media/zygzak.png").convert_alpha()
car_image = pygame.transform.scale(car_image, (40, CAR_LENGTH))

# Horizontal roads (E-W)
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
crossing = Crossing(north_road_in, north_road_out, east_road_in, east_road_out, south_road_in, south_road_out, west_road_in, west_road_out)
car_generator = CarGenerator(roads_in, INFLOW)

traffic_lights_manager = TrafficLightsManager(roads_in)
while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            traffic_lights_manager.handle_click(event.pos)

    # fill background
    screen.fill((0, 160, 0))

    traffic_lights_manager.update(dt)
    
    car_generator.update(dt)
    for road in all_roads:
        road.update_cars(dt)
        road.draw(screen, car_image)

    traffic_lights_manager.draw(screen)
    crossing.update(screen, car_image, dt)
    crossing.draw_connectors(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
