import pygame
import sys

# Initialize pygame
pygame.init()

# Window settings
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Pygame Project")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (70, 130, 180)
DARK_BLUE = (40, 90, 140)

# Font
FONT = pygame.font.SysFont("arial", 36)

# Button settings
button_width, button_height = 200, 80
button_rect = pygame.Rect(
    (WIDTH - button_width) // 2,
    (HEIGHT - button_height) // 2,
    button_width,
    button_height
)

clock = pygame.time.Clock()
running = True

while running:
    SCREEN.fill(WHITE)

    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()

    # Change color on hover
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(SCREEN, DARK_BLUE, button_rect)
        if mouse_pressed[0]:  # Left mouse button
            running = False
    else:
        pygame.draw.rect(SCREEN, BLUE, button_rect)

    # Draw button text
    text_surface = FONT.render("Click Me", True, WHITE)
    text_rect = text_surface.get_rect(center=button_rect.center)
    SCREEN.blit(text_surface, text_rect)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()