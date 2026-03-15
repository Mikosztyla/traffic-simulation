from car import Car


class StopCar(Car):

    def __init__(self, lane, progress, index):
        super().__init__(lane, 0, index)
        self.progress = progress
        self.speed = 0
        self.position = lane.start.lerp(lane.end, progress)

    def update(self, *args, **kwargs):
        return False

    def draw(self, *args, **kwargs):
        pass