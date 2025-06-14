import pygame, sys
from scenes.mainmenu import MainMenu
from scenes.game import Game

BLACK = (0,0,0)
PURPLE = (150, 10, 100)
RED = (255, 0, 0)
GREEN = (0,255, 0)
BLUE  = (0, 0, 255)
WHITE = (0, 0, 0)

WIDTH = 800
HEIGHT = 600
FPS = 45


pygame.init()

# Grafika!


# Definice spritu


# Nastaveni okna aj.
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My caption of the game")


# hodiny - FPS CLOCK / heart rate
clock = pygame.time.Clock()

# Kolecke spritů
my_sprites = pygame.sprite.Group()

# start:
running = True

current_scene = None
def switch_to_game():
    global current_scene
    current_scene = Game(screen)
current_scene = MainMenu(screen, lambda: switch_to_game())

# cyklus udrzujici okno v chodu
while running:
    # FPS kontrola / jeslti bezi dle rychlosti!
    dt = clock.tick(FPS)

    if current_scene is not None:
        current_scene.loop(dt)
        continue

    # Event
    for event in pygame.event.get():
        # print(event) - pokud potrebujete info co se zmacklo.
        if event.type == pygame.QUIT:
            running = False
    

    # Update
    my_sprites.update()
    

    # Render
    # screen.fill(BLACK)
    # my_sprites.draw(screen)
    # pygame.display.flip()
    


pygame.quit()
