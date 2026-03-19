from conflict import Conflict
from side import LEFT, RIGHT, OPPOSITE
from direction import Direction

ALL_DIRECTIONS = [Direction.LEFT, Direction.STRAIGHT, Direction.RIGHT]

class ConflictManager:
    def __init__(self, roads_in, roads_out):
        self.roads_in = roads_in
        self.roads_out = roads_out
        self.conflicts = []
        self._generate_conflicts_in_roads()
        self._generate_conflicts_connectors()


    def _generate_conflicts_in_roads(self):
        for in_side, road in self.roads_in.items():

            # right turn - pass

            # straight
            conflict_road = self.roads_in[RIGHT[in_side]]
            for i, lane in enumerate(road.lanes):
                print(i)
                for conflict_lane in conflict_road.lanes:
                    conflict_directions = [Direction.LEFT, Direction.STRAIGHT]
                    if i == 0:
                        conflict_directions.append(Direction.RIGHT)
                    self._create_conflict(lane, Direction.STRAIGHT, conflict_lane, conflict_directions, lane, conflict_lane)

            # left turn
            lane = road.lanes[-1]
            conflict_road = self.roads_in[RIGHT[in_side]]
            conflict_lane = conflict_road.lanes[-1]
            # from right going left
            connector1 = lane.get_next_lane(Direction.LEFT)
            connector2 = conflict_lane.get_next_lane(Direction.LEFT)
            self._create_conflict(lane, Direction.LEFT, conflict_lane, [Direction.LEFT], connector1, connector2)
            # from right going straight
            opp_lane = self.roads_in[OPPOSITE[in_side]].lanes[0]
            self._create_conflict(lane, Direction.LEFT, conflict_lane, [Direction.STRAIGHT], opp_lane, conflict_lane)

            # from opposite going right (if only 1 lane available) or straight 
            conflict_road = self.roads_in[OPPOSITE[in_side]]
            if len(road.lanes) == 1:
                conflict_lane = conflict_road.lanes[0]
                out_lane = self.roads_out[LEFT[in_side]]
                self._create_conflict(lane, Direction.LEFT, conflict_lane, [Direction.STRAIGHT, Direction.RIGHT], conflict_lane, out_lane)
            else:
                connector = lane.get_next_lane(Direction.LEFT)
                for conflict_lane in conflict_road.lanes:
                    self._create_conflict(lane, Direction.LEFT, conflict_lane, [Direction.STRAIGHT], connector, conflict_lane)

    def _generate_conflicts_connectors(self):
        for in_side, road in self.roads_in.items():
            # right turn
            lane = road.lanes[0]
            connector = self.roads_in[LEFT[in_side]].lanes[0].get_next_lane(Direction.STRAIGHT)
            self._create_conflict(lane, Direction.RIGHT, connector, ALL_DIRECTIONS, lane, connector)
            # if 1 lane, also opposite to left
            if len(road.lanes) == 1:
                connector = self.roads_in[OPPOSITE[in_side]].lanes[0].get_next_lane(Direction.LEFT)
                self._create_conflict(lane, Direction.RIGHT, connector, ALL_DIRECTIONS, lane, self.roads_in[LEFT[in_side]].lanes[0])

            # straight
            for i, lane in enumerate(road.lanes):
                # FROM RIGHT: every connector stright and left, and right-turn connector for right-most lane
                right_road = self.roads_in[RIGHT[in_side]]
                for j, right_lane in enumerate(right_road.lanes):
                    if i == 0 and j == 0:
                        connector = right_lane.get_next_lane(Direction.RIGHT)
                        self._create_conflict(lane, Direction.STRAIGHT, connector, ALL_DIRECTIONS, lane, right_lane)
                    if j == len(right_road.lanes) - 1:
                        connector = right_lane.get_next_lane(Direction.LEFT)
                        self._create_conflict(lane, Direction.STRAIGHT, connector, ALL_DIRECTIONS, lane, connector)
                    connector = right_lane.get_next_lane(Direction.STRAIGHT)
                    self._create_conflict(lane, Direction.STRAIGHT, connector, ALL_DIRECTIONS, lane, connector)

                # FROM OPPOSITE: connector left
                connector = self.roads_in[OPPOSITE[in_side]].lanes[-1].get_next_lane(Direction.LEFT)
                self._create_conflict(lane, Direction.STRAIGHT, connector, ALL_DIRECTIONS, lane, connector)

                # FROM LEFT: connector straight, and left-turn connector for left-most lane
                left_road = self.roads_in[LEFT[in_side]]
                for j, left_lane in enumerate(left_road.lanes):
                    if i == len(road.lanes) - 1 and j == len(left_road.lanes):
                        connector = left_lane.get_next_lane(Direction.LEFT)
                        self._create_conflict(lane, Direction.STRAIGHT, connector, ALL_DIRECTIONS, lane, right_road.lanes[0])
                    connector = left_lane.get_next_lane(Direction.STRAIGHT)
                    self._create_conflict(lane, Direction.STRAIGHT, connector, ALL_DIRECTIONS, lane, connector)

            # left turn
            lane = road.lanes[-1]
            # FROM RIGHT: connector left, connector straight for left-most lane
            right_road = self.roads_in[RIGHT[in_side]]
            connector = right_road.lanes[-1].get_next_lane(Direction.LEFT)
            self._create_conflict(lane, Direction.LEFT, connector, ALL_DIRECTIONS, lane.get_next_lane(Direction.LEFT), connector)
            connector = right_road.lanes[-1].get_next_lane(Direction.STRAIGHT)
            self._create_conflict(lane, Direction.LEFT, connector, ALL_DIRECTIONS, connector, self.roads_in[OPPOSITE[in_side]].lanes[0])

            # FROM OPPOSITE: connector straight, right (if only 1 lane)
            opp_road = self.roads_in[OPPOSITE[in_side]]
            for opp_lane in opp_road.lanes:
                connector = opp_lane.get_next_lane(Direction.STRAIGHT)
                self._create_conflict(lane, Direction.LEFT, connector, ALL_DIRECTIONS, lane.get_next_lane(Direction.LEFT), connector)
            if len(opp_road.lanes) == 1:
                connector = opp_road.lanes[0].get_next_lane(Direction.RIGHT)
                self._create_conflict(lane, Direction.LEFT, connector, ALL_DIRECTIONS, opp_road.lanes[0], self.roads_in[RIGHT[in_side]].lanes[0])

            # FROM LEFT: connector straight, left 
            left_road = self.roads_in[LEFT[in_side]]
            for j, left_lane in enumerate(left_road.lanes):
                if j == len(left_road.lanes) - 1:
                    connector = left_lane.get_next_lane(Direction.LEFT)
                    self._create_conflict(lane, Direction.LEFT, connector, ALL_DIRECTIONS, lane.get_next_lane(Direction.LEFT), connector)
                connector = left_lane.get_next_lane(Direction.STRAIGHT)
                self._create_conflict(lane, Direction.LEFT, connector, ALL_DIRECTIONS, lane.get_next_lane(Direction.LEFT), connector)

    def _create_conflict(self, in_lane, in_lane_direction, conflict_lane, directions, v1, v2):
        conflict = Conflict(conflict_lane, directions, v1, v2)
        in_lane.add_conflict(conflict, in_lane_direction)
        self.conflicts.append(conflict)

    def draw_conflicts(self, screen):
        for conflict in self.conflicts:
            conflict.draw_collision_point(screen)
            