import pygame
from constants import *
from car import Car
from stop_car import StopCar
from direction import Direction


class Lane:
    def __init__(self, start: pygame.Vector2, end: pygame.Vector2, road, speed_limit, lane_width=LANE_WIDTH):
        self.start = start
        self.end = end
        self.lane_width = lane_width
        self.speed_limit = speed_limit
        self.road = road
        # car[0] ----road----> car[n]
        self.stop_car = None
        self.cars = []
        self.should_draw_lane = True

        self.next_lanes = {}

    def add_next_lane(self, lane, direction):
        self.next_lanes[direction] = lane

    def make_lane_invisible(self):
        self.should_draw_lane = False

    def add_car(self, new_car: Car):
        insert_index = 0
        for i, car in enumerate(self.cars):
            if car.progress > new_car.progress:
                insert_index = i
                break
        else:
            insert_index = len(self.cars)

        self.cars.insert(insert_index, new_car)

    def delete_car(self, car: Car):
        self.cars.remove(car)

    def update_cars(self, dt, right_lane, left_lane):
        cars_finished = []
        for i, car in enumerate(self.cars):
            if i == len(self.cars) - 1:
                following_car = None
            else:
                following_car = self.cars[i + 1]
            finished = car.update(following_car, right_lane, left_lane, dt)
            if finished: cars_finished.append(car)

        for car in cars_finished:
            if car.progress >= 1 and car.direction in self.next_lanes:
                new_lane = self.get_next_lane(car.direction)
                car.current_lane = new_lane
                car.progress = 0
                car.current_lane.add_car(car)
                car.direction = Direction.STRAIGHT

            self.delete_car(car)

    def get_next_lane(self, direction):
        return self.next_lanes.get(direction)

    def set_red_light(self, point):
        if self.stop_car is not None:
            return

        stop_car = StopCar(self, self.get_progress_on_lane(point), 0, 0)

        self.stop_car = stop_car
        self.add_car(stop_car)

    def set_green_light(self):
        if self.stop_car is None:
            return

        if self.stop_car in self.cars:
            self.cars.remove(self.stop_car)

        self.stop_car = None

    def get_progress_on_lane(self, point):
        lane_vec = self.end - self.start
        point_vec = point - self.start

        lane_length = lane_vec.length()
        if lane_length == 0:
            return 0

        progress = point_vec.dot(lane_vec) / (lane_length * lane_length)
        offset_pixels = STOP_OFFSET_METERS * PIXELS_PER_METER
        progress -= offset_pixels / lane_length
        if progress > 1:
            progress = 1

        return max(0, progress)
    
    def get_number_of_neighbour_lanes_in_direction(self, direction):
        if direction == Direction.LEFT:
            return len(self.road.lanes) - self.road.lanes.index(self) - 1
        elif direction == Direction.RIGHT:
            return self.road.lanes.index(self)
    
    def draw_cars(self, screen, car_image):
        for car in self.cars:
            car.draw(screen, car_image)

    def draw(self, screen, car_image):
        direction = (self.end - self.start)
        length = direction.length()

        if length == 0:
            return

        if self.should_draw_lane:
            direction = direction.normalize()
            normal = pygame.Vector2(-direction.y, direction.x)

            half_width = self.lane_width / 2
            edge_thickness = 3

            # --- Road surface polygon ---
            p1 = self.start + normal * half_width
            p2 = self.start - normal * half_width
            p3 = self.end - normal * half_width
            p4 = self.end + normal * half_width

            pygame.draw.polygon(screen, (50, 50, 50), [p1, p2, p3, p4])

            # --- Left white edge ---
            left1 = self.start + normal * half_width
            left2 = self.end + normal * half_width
            pygame.draw.line(screen, (255, 255, 255), left1, left2, edge_thickness)

            # --- Right white edge ---
            right1 = self.start - normal * half_width
            right2 = self.end - normal * half_width
            pygame.draw.line(screen, (255, 255, 255), right1, right2, edge_thickness)

        self.draw_cars(screen, car_image)
