import pygame


class Lane:
    def __init__(self, start: pygame.Vector2, end: pygame.Vector2):
        self.start = start
        self.end = end

    def draw(self, screen, lane_width):
        direction = (self.end - self.start)
        length = direction.length()

        if length == 0:
            return

        direction = direction.normalize()
        normal = pygame.Vector2(-direction.y, direction.x)

        half_width = lane_width / 2
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
