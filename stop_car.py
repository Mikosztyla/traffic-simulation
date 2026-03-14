from car import Car


class StopCar(Car):

    def __init__(self, lane, progress):
        super().__init__(lane, speed=0)
        self.progress = progress
        self.speed = 0
        self.position = lane.start.lerp(lane.end, progress)

    def update(self, *args, **kwargs):
        return False

    def draw(self, *args, **kwargs):
        pass