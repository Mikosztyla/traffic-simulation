from conflict import Conflict
from side import LEFT, RIGHT, OPPOSITE
from direction import Direction

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

            # # left turn
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
        pass

    def _create_conflict(self, in_lane, in_lane_direction, conflict_lane, directions, v1, v2):
        conflict = Conflict(conflict_lane, directions, v1, v2)
        in_lane.add_conflict(conflict, in_lane_direction)
        self.conflicts.append(conflict)

    def draw_conflicts(self, screen):
        for conflict in self.conflicts:
            conflict.draw_collision_point(screen)