import pygame
import sys
from side import Side
from crossing import Crossing
from road import Road
from constants import *
from car_generator import CarGenerator
from trafficLightsManager import TrafficLightsManager
from directionLegend import DirectionLegend
from stats import StatsPanel
from simulationConfig import SimulationConfig
import random
import csv


def run_simulation(config: SimulationConfig, headless=True):
    global LANES_PER_SIDE, INFLOW, LEFT_PROBABILITY, RIGHT_PROBABILITY
    if config:
        LANES_PER_SIDE = config.lanes_per_side
        INFLOW = config.inflow
        LEFT_PROBABILITY = config.left_prob
        RIGHT_PROBABILITY = config.right_prob
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    center = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
    offset = LANE_WIDTH * LANES_PER_SIDE
    offset_road = offset / 2

    north_road_in = Road(pygame.Vector2(center.x + offset_road, center.y + ROAD_LENGTH), pygame.Vector2(center.x + offset_road, center.y + offset), Side.N)
    north_road_out = Road(pygame.Vector2(center.x + offset_road, center.y - offset), pygame.Vector2(center.x + offset_road, center.y - ROAD_LENGTH), Side.N)

    south_road_in = Road(pygame.Vector2(center.x - offset_road, center.y - ROAD_LENGTH), pygame.Vector2(center.x - offset_road, center.y - offset), Side.S)
    south_road_out = Road(pygame.Vector2(center.x - offset_road, center.y + offset), pygame.Vector2(center.x - offset_road, center.y + ROAD_LENGTH), Side.S)

    west_road_in = Road(pygame.Vector2(center.x + ROAD_LENGTH, center.y - offset_road), pygame.Vector2(center.x + offset, center.y - offset_road), Side.W)
    west_road_out = Road(pygame.Vector2(center.x - offset, center.y - offset_road), pygame.Vector2(center.x - ROAD_LENGTH, center.y - offset_road), Side.W)

    east_road_in = Road(pygame.Vector2(center.x - ROAD_LENGTH, center.y + offset_road), pygame.Vector2(center.x - offset, center.y + offset_road), Side.E)
    east_road_out = Road(pygame.Vector2(center.x + offset, center.y + offset_road), pygame.Vector2(center.x + ROAD_LENGTH, center.y + offset_road), Side.E)

    roads_in = [north_road_in, east_road_in, south_road_in, west_road_in]
    roads_out = [north_road_out, south_road_out, west_road_out, east_road_out]
    all_roads = roads_in + roads_out

    crossing = Crossing(north_road_in, north_road_out, east_road_in, east_road_out,
                        south_road_in, south_road_out, west_road_in, west_road_out)

    car_generator = CarGenerator(roads_in, INFLOW)
    if config and not config.traffic_lights:
        traffic_lights_manager = None
    else:
        traffic_lights_manager = TrafficLightsManager(roads_in)
    stats_panel = StatsPanel(all_roads, crossing)
    legend = DirectionLegend(car_generator.car_images)

    running = True

    while running:
        dt = clock.tick(60) / 1000 * SIMULATION_SPEED

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if not headless:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    traffic_lights_manager.handle_click(event.pos)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        traffic_lights_manager.toggle_mode()

        if traffic_lights_manager:
            traffic_lights_manager.update(dt)
        car_generator.update(dt)

        for road in all_roads:
            road.update_cars(dt)

        crossing.update(dt)
        stats_panel.update(dt)

        if not headless:
            screen.fill((0, 160, 0))

            crossing.draw_crossing(screen)
            for road in all_roads:
                road.draw(screen)
            crossing.draw_crossing_cars(screen)

            traffic_lights_manager.draw(screen)
            stats = {
                "Time": f"{stats_panel.simulation_time:.1f}s",
                "Spawned cars": car_generator.total_spawned,
                 "Current cars": len(stats_panel.get_current_cars()),
                 "Avg speed": f"{stats_panel.get_avg_speed():.2f}",
                 "Flow (cars/s)": f"{stats_panel.get_flow_rate():.2f}"}
            stats_panel.draw(screen, stats)
            legend.draw(screen)

            pygame.display.flip()

        if len(stats_panel.get_current_cars()) == 0 and car_generator.total_spawned > 10:
            result = stats_panel.simulation_time
            pygame.quit()
            return result


experiments = [
    SimulationConfig(lanes_per_side=2, inflow=1.0, left_prob=0.2, right_prob=0.3, traffic_lights=True),
    SimulationConfig(lanes_per_side=2, inflow=1.0, left_prob=0.2, right_prob=0.3, traffic_lights=False),
    SimulationConfig(lanes_per_side=4, inflow=2.0, left_prob=0.1, right_prob=0.5, traffic_lights=False),
    SimulationConfig(lanes_per_side=6, inflow=3.0, left_prob=0.3, right_prob=0.3, traffic_lights=True),
]

if RUN_HEADLESS:
    all_results = []

    for exp_id, config in enumerate(experiments):
        print(f"\nRunning experiment {exp_id}")

        run_results = []

        for i in range(config.num_runs):
            random.seed(i)
            t = run_simulation(config, headless=True)

            if t is not None:
                run_results.append(t)

        avg = sum(run_results) / len(run_results)

        all_results.append({
            "experiment_id": exp_id,
            "lanes": config.lanes_per_side,
            "inflow": config.inflow,
            "left_prob": config.left_prob,
            "right_prob": config.right_prob,
            "traffic_lights": config.traffic_lights,
            "avg_time": avg,
            "runs": len(run_results)
        })

    with open("results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
        writer.writeheader()
        writer.writerows(all_results)

else:
    run_simulation(None, headless=False)

pygame.quit()
sys.exit()




