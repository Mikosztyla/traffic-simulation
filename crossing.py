import pygame
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
        self._generate_connectors()
        lanes = []

        for road in self.in_roads.values():
            lanes.extend(road.lanes)

        xs = [lane.end.x for lane in lanes]
        ys = [lane.end.y for lane in lanes]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        self.rect = pygame.Rect(
            min_x,
            min_y,
            max_x - min_x,
            max_y - min_y
        )

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
        connector.add_next_lane(end_lane, Direction.STRAIGHT)
        in_lane.add_next_lane(connector, direction)
        self.connectors.append(connector)

    def update(self, screen, dt):
        for connector in self.connectors:
            connector.update_cars(dt, None, None)
            connector.draw(screen)

    def draw(self, screen):
        pygame.draw.rect(screen, (50, 50, 50), self.rect)

    def draw_connectors(self, screen):
        color = (0, 200, 255)
        for connector in self.connectors:
            start = connector.start
            end = connector.end
            pygame.draw.line(screen, color, start, end, 2)
