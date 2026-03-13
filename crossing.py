import random
import pygame
import math
from side import Side
from lane import Lane


class Crossing:
    def get_random_incoming_lane(self):
        side = random.choice(list(self.sides.keys()))
        return random.choice(self.sides[side]["in"])

    def get_random_outgoing_lane(self, exclude_side):
        possible_sides = [s for s in self.sides.keys() if s != exclude_side]
        side = random.choice(possible_sides)
        return random.choice(self.sides[side]["out"])

    def _create_lanes(self):
        half = self.size / 2
        total_lanes = self.lanes_per_side * 2
        total_width = total_lanes * self.lane_width

        def lane_offset(index):
            return -total_width / 2 + self.lane_width / 2 + index * self.lane_width

        for i in range(self.lanes_per_side):
            # =====================
            # SOUTH
            # =====================
            out_offset = lane_offset(i)
            in_offset = lane_offset(i + self.lanes_per_side)

            # OUT
            lane = Lane(
                pygame.Vector2(self.center.x + out_offset, self.center.y + half * 2),
                pygame.Vector2(self.center.x + out_offset, self.center.y + half + self.road_length)
            )
            lane.side = Side.S
            lane.direction = "out"
            self.sides[Side.S]["out"].append(lane)

            # IN
            lane = Lane(
                pygame.Vector2(self.center.x + in_offset, self.center.y + half + self.road_length),
                pygame.Vector2(self.center.x + in_offset, self.center.y + half * 2)
            )
            lane.side = Side.S
            lane.direction = "in"
            self.sides[Side.S]["in"].append(lane)

            # =====================
            # WEST
            # =====================
            lane = Lane(
                pygame.Vector2(self.center.x - half * 2, self.center.y + out_offset),
                pygame.Vector2(self.center.x - half - self.road_length, self.center.y + out_offset)
            )
            lane.side = Side.W
            lane.direction = "out"
            self.sides[Side.W]["out"].append(lane)

            lane = Lane(
                pygame.Vector2(self.center.x - half - self.road_length, self.center.y + in_offset),
                pygame.Vector2(self.center.x - half * 2, self.center.y + in_offset)
            )
            lane.side = Side.W
            lane.direction = "in"
            self.sides[Side.W]["in"].append(lane)

            # =====================
            # NORTH
            # =====================
            in_it = self.lanes_per_side - i - 1
            out_it = - i - 1
            in_offset = lane_offset(in_it)
            out_offset = lane_offset(out_it)

            # IN
            lane = Lane(
                pygame.Vector2(self.center.x + in_offset, self.center.y - half - self.road_length),
                pygame.Vector2(self.center.x + in_offset, self.center.y - half * 2)
            )
            lane.side = Side.N
            lane.direction = "in"
            self.sides[Side.N]["in"].append(lane)

            # OUT
            lane = Lane(
                pygame.Vector2(self.center.x + out_offset + total_width, self.center.y - half * 2),
                pygame.Vector2(self.center.x + out_offset + total_width, self.center.y - half - self.road_length)
            )
            lane.side = Side.N
            lane.direction = "out"
            self.sides[Side.N]["out"].append(lane)

            # =====================
            # EAST
            # =====================
            lane = Lane(
                pygame.Vector2(self.center.x + half + self.road_length, self.center.y + in_offset),
                pygame.Vector2(self.center.x + half * 2, self.center.y + in_offset)
            )
            lane.side = Side.E
            lane.direction = "in"
            self.sides[Side.E]["in"].append(lane)

            lane = Lane(
                pygame.Vector2(self.center.x + half * 2, self.center.y + out_offset + total_width),
                pygame.Vector2(self.center.x + half + self.road_length, self.center.y + out_offset + total_width)
            )
            lane.side = Side.E
            lane.direction = "out"
            self.sides[Side.E]["out"].append(lane)

    def draw(self, screen):
        half = self.size / 2

        rect = pygame.Rect(
            self.center.x - half - self.lane_width / 2 * self.lanes_per_side,
            self.center.y - half - self.lane_width / 2 * self.lanes_per_side,
            self.size * 2,
            self.size * 2
        )
        pygame.draw.rect(screen, (50, 50, 50), rect)

        for side in self.sides.values():
            for lane in side["out"]:
                lane.draw(screen)
            for lane in side["in"]:
                lane.draw(screen)

    def __init__(self, center: pygame.Vector2, lanes_per_side: int, lane_width=40, road_length=200):
        self.center = center
        self.lanes_per_side = lanes_per_side
        self.lane_width = lane_width
        self.road_length = road_length

        self.size = lanes_per_side * lane_width

        self.sides = {
            Side.N: {"in": [], "out": []},
            Side.E: {"in": [], "out": []},
            Side.S: {"in": [], "out": []},
            Side.W: {"in": [], "out": []},
        }

        self._create_lanes()

    def draw_connectors(self, screen):
        color = (0, 200, 255)
        thickness = 2
        sides = [Side.N, Side.E, Side.S, Side.W]

        for side in sides:
            in_lanes = self.sides[side]["in"]

            for i, in_lane in enumerate(in_lanes):

                for other_side in sides:
                    if other_side == side:
                        continue  # skip U-turn

                    out_lanes = self.sides[other_side]["out"]
                    if i >= len(out_lanes):
                        continue

                    out_lane = out_lanes[self.lanes_per_side - i - 1]

                    start = in_lane.end
                    end = out_lane.start

                    in_index = sides.index(side)
                    out_index = sides.index(other_side)
                    diff = (out_index - in_index) % 4

                    # =========================
                    # STRAIGHT
                    # =========================
                    if diff == 2:
                        pygame.draw.line(screen, color, start, end, thickness)

                    # =========================
                    # TURN (LEFT or RIGHT)
                    # =========================
                    else:
                        clockwise = diff == 1  # right turn
                        half = self.size

                        # Determine center offset
                        # Use intersection center shifted to quadrant
                        if side == Side.N:
                            cx = self.center.x
                            cy = self.center.y - half
                        elif side == Side.S:
                            cx = self.center.x
                            cy = self.center.y + half
                        elif side == Side.W:
                            cx = self.center.x - half
                            cy = self.center.y
                        else:  # E
                            cx = self.center.x + half
                            cy = self.center.y

                        center = pygame.Vector2(cx, cy)

                        # radius = distance from center to start
                        radius = (start - center).length()

                        # angles
                        v1 = start - center
                        v2 = end - center

                        angle1 = math.atan2(v1.y, v1.x)
                        angle2 = math.atan2(v2.y, v2.x)

                        # fix direction
                        if clockwise and angle2 > angle1:
                            angle2 -= 2 * math.pi
                        if not clockwise and angle2 < angle1:
                            angle2 += 2 * math.pi

                        steps = 20
                        points = []

                        for s in range(steps + 1):
                            t = s / steps
                            angle = angle1 + (angle2 - angle1) * t
                            p = center + pygame.Vector2(
                                math.cos(angle), math.sin(angle)
                            ) * radius
                            points.append(p)

                        pygame.draw.lines(screen, color, False, points, thickness)

    def draw_in_traffic_lights(self, screen, traffic_light_images):
        for side_name, side_data in self.sides.items():
            for lane in side_data["in"]:
                image = traffic_light_images[side_name]
                rect = image.get_rect(center=lane.end)
                screen.blit(image, rect)
