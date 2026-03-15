import random
import pygame
import math
from side import Side
from lane import Lane


class Crossing:

    def __init__(self, north_in, north_out,
                 east_in, east_out,
                 south_in, south_out,
                 west_in, west_out):

        self.in_roads = {
            Side.N: south_in,
            Side.E: west_in,
            Side.S: north_in,
            Side.W: east_in
        }

        self.out_roads = {
            Side.N: north_out,
            Side.E: east_out,
            Side.S: south_out,
            Side.W: west_out
        }

        self.connectors = []

        for road in [north_in, north_out, east_in, east_out, south_in, south_out, west_in, west_out]:
            road.crossing = self

        self._generate_connectors()

    def _generate_connectors(self):

        RIGHT = {
            Side.N: Side.W,
            Side.E: Side.N,
            Side.S: Side.E,
            Side.W: Side.S
        }

        LEFT = {
            Side.N: Side.E,
            Side.W: Side.N,
            Side.S: Side.W,
            Side.E: Side.S
        }

        OPPOSITE = {
            Side.N: Side.S,
            Side.S: Side.N,
            Side.E: Side.W,
            Side.W: Side.E
        }

        for side, in_road in self.in_roads.items():
            for i, lane in enumerate(in_road.lanes):

                # STRAIGHT
                target_road = self.out_roads[OPPOSITE[side]]
                target_lane = target_road.lanes[i]

                self.add_connector(lane, target_lane)
                # RIGHT TURN
                if i == 0:
                    right_road = self.out_roads[RIGHT[side]]
                    right_lane = right_road.lanes[0]

                    self.add_connector(lane, right_lane)

                # LEFT TURN
                if i == len(in_road.lanes) - 1:
                    left_road = self.out_roads[LEFT[side]]
                    left_lane = left_road.lanes[-1]
                    self.add_connector(lane, left_lane)

    def add_connector(self, lane, end_lane):
        connector = Lane(lane.end, end_lane.start, None, lane.speed_limit)
        connector.make_lane_invisible()
        connector.next_lane = end_lane
        lane.next_lane = connector
        self.connectors.append(lane)

    def get_random_out_lane_and_desired_in_lane(self, lane):

        approach_road = None

        for _, road in self.in_roads.items():
            if lane in road.lanes:
                approach_road = road
                break

        if approach_road is None:
            return None

        possible = [
            lane
            for lane in self.connectors
            if lane in approach_road.lanes
        ]

        if not possible:
            return None
        return random.choice(possible)

    def update(self, screen, car_image, dt):
        for lane in self.connectors:
            if len(lane.next_lane.cars) > 0:
                lane.next_lane.update_cars(dt, None, None)
                lane.next_lane.draw(screen, car_image)

    def draw_connectors(self, screen):

        color = (0, 200, 255)

        for lane in self.connectors:
            start = lane.end
            end = lane.next_lane.start

            pygame.draw.line(screen, color, start, end, 2)
