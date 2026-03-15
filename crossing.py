import random
import pygame
import math
from side import Side
from lane import Lane
from direction import Direction


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

        for road in [south_in, west_in, north_in, east_in]:
            road.crossing = self

        self._generate_connectors()
        print("-----connectors-------")
        for _, c, _ in self.connectors:
            print(c)
        print("-----connectors-------")

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

                self.add_connector(lane, target_lane, Direction.STRAIGHT)
                # RIGHT TURN
                if i == 0:
                    right_road = self.out_roads[RIGHT[side]]
                    right_lane = right_road.lanes[0]

                    self.add_connector(lane, right_lane, Direction.RIGHT)

                # LEFT TURN
                if i == len(in_road.lanes) - 1:
                    left_road = self.out_roads[LEFT[side]]
                    left_lane = left_road.lanes[-1]
                    self.add_connector(lane, left_lane, Direction.LEFT)

    def add_connector(self, in_lane, end_lane, direction: Direction):
        connector = Lane(in_lane.end.copy(), end_lane.start.copy(), None, in_lane.speed_limit)
        connector.make_lane_invisible()
        connector.next_lane = end_lane
        connector.is_connector = True
        self.connectors.append((in_lane, connector, direction))

    def get_connector(self, lane, direction: Direction):
        for in_lane, connector, d in self.connectors:
            if in_lane == lane and d == direction:
                return connector
        return None

    def update(self, screen, car_image, dt):
        for _, connector, _ in self.connectors:
            connector.update_cars(dt, None, None)
            connector.draw(screen, car_image)

    def draw_connectors(self, screen):

        color = (0, 200, 255)

        for in_lane, connector, _ in self.connectors:
            start = in_lane.end
            end = connector.next_lane.start

            pygame.draw.line(screen, color, start, end, 2)
