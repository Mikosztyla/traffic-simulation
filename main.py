import pygame
import sys
from side import Side
from crossing import Crossing
from car import Car

pygame.init()

WIDTH, HEIGHT = 1200, 800
SPEED = 300
LANES_PER_SIDE = 1


def connect_crossings(c1, c2, c1_to_c2_side):

    OPPOSITE = {
        Side.N: Side.S,
        Side.S: Side.N,
        Side.E: Side.W,
        Side.W: Side.E
    }

    side1 = c1_to_c2_side
    side2 = OPPOSITE[side1]

    c1_out = c1.sides[side1]["out"]
    c2_in = c2.sides[side2]["in"]
    c2_out = c2.sides[side2]["out"]
    c1_in = c1.sides[side1]["in"]

    lane_count = min(len(c1_out), len(c2_in))

    # ==============================
    # Connect c1 → c2
    # ==============================
    for i in range(lane_count):

        lane = c1_out[LANES_PER_SIDE - i - 1]

        lane.start = c1_out[LANES_PER_SIDE - i - 1].start
        lane.end = c2_in[i].end
        c2.sides[side2]["in"][i] = lane

    # ==============================
    # Connect c2 → c1
    # ==============================
    lane_count = min(len(c2_out), len(c1_in))

    for i in range(lane_count):

        lane = c2_out[LANES_PER_SIDE - i - 1]

        lane.start = c2_out[LANES_PER_SIDE - i - 1].start
        lane.end = c1_in[i].end
        c1.sides[side1]["in"][i] = lane


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic simulation")

clock = pygame.time.Clock()
clock.tick(60)
running = True

car_image = pygame.image.load("media/zygzak.png").convert_alpha()
car_image = pygame.transform.scale(car_image, (40, 55))

car_pos = pygame.Vector2(WIDTH // 2 - 20, HEIGHT)
car_speed = 100

car_rect = car_image.get_rect(topleft=car_pos)

crossing1 = Crossing(
    center=pygame.Vector2(WIDTH // 2 - 200, HEIGHT // 2),
    lanes_per_side=LANES_PER_SIDE
)

crossing2 = Crossing(
    center=pygame.Vector2(WIDTH // 2 + 200, HEIGHT // 2),
    lanes_per_side=LANES_PER_SIDE
)
connect_crossings(crossing1, crossing2, Side.E)
cars = []
spawn_timer = 0
spawn_interval = 1
lane = crossing1.get_random_incoming_lane()
cars.append(Car(lane, speed=120))

traffic_light_image = pygame.image.load("media/traffic.png").convert_alpha()
traffic_light_image = pygame.transform.scale(traffic_light_image, (20, 45))
traffic_light_images = {
    Side.N: pygame.transform.rotate(traffic_light_image, 180),
    Side.S: traffic_light_image,
    Side.E: pygame.transform.rotate(traffic_light_image, 90),
    Side.W: pygame.transform.rotate(traffic_light_image, -90),
}


def fill_background(screen):
    screen.fill((0, 160, 0))


while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    fill_background(screen)
    crossing1.draw(screen)
    crossing2.draw(screen)

    car_pos.y -= car_speed * dt
    car_rect.topleft = car_pos
    spawn_timer += dt
    crossing1.draw_in_traffic_lights(screen, traffic_light_images)
    crossing2.draw_in_traffic_lights(screen, traffic_light_images)
    # crossing2.draw_connectors(screen)
    if spawn_timer >= spawn_interval:
        lane = crossing1.get_random_incoming_lane()
        cars.append(Car(lane, speed=120))
        spawn_timer = 0
    for car in cars:
        finished = car.update(dt)

        if finished:
            new_lane = crossing2.get_random_outgoing_lane(car.current_lane.side)
            car.current_lane = new_lane
            car.progress = 0

    for car in cars:
        car.draw(screen, car_image)
    pygame.display.flip()

pygame.quit()
sys.exit()
