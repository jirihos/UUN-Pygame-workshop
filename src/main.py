import pygame,sys

# konstanty a fce které neinteragují s pygame!
BLACK = (0,0,0)
PURPLE = (150, 10, 100)
RED = (255, 0, 0)
GREEN = (0,255, 0)
BLUE  = (0, 0, 255)
WHITE = (0, 0, 0)

WIDTH = 800
HEIGHT = 600
FPS = 45

#fce které interagují s pygame!


## Start pygame + start modulů! 
pygame.init()
pygame.mixer.init()

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

# cyklus udrzujici okno v chodu
while running:
    # FPS kontrola / jeslti bezi dle rychlosti!
    clock.tick(FPS)

    # Event
    for event in pygame.event.get():
        # print(event) - pokud potrebujete info co se zmacklo.
        if event.type == pygame.QUIT:
            running = False
    

    # Update
    my_sprites.update()
    

    # Render
    screen.fill(BLACK)
    my_sprites.draw(screen)
    pygame.display.flip()
    


pygame.quit()
