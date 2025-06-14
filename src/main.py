import pygame
import sys
from scenes.mainmenu import MainMenu
from scenes.game import Game

# Colors (not used yet, but you can use them)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)
PURPLE = (150, 10, 100)

# Dimensions and FPS
WIDTH = 768
HEIGHT = 768
FPS = 45

# Pygame initialization
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rubert Car Game")
clock = pygame.time.Clock()

# ===== Scene switching =====
current_scene = None
def switch_to_game():
    global current_scene
    current_scene = Game(screen)

# Start the default scene (menu)
current_scene = MainMenu(screen, switch_to_game)

# ===== Main loop =====
running = True
while running:
    dt = clock.tick(FPS)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if hasattr(current_scene, "handle_event"):
            result = current_scene.handle_event(event)
            if result == "exit":
                running = False

    # Logic + rendering of the current scene
    if current_scene is not None:
        current_scene.loop(dt)

# Exit
pygame.quit()
sys.exit()
