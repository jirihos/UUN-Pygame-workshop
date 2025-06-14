import pygame
import sys

class Game():
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return "exit"

    def loop(self, dt):
        # Update
        myfont = pygame.font.SysFont("None", 50)
        text = myfont.render("Game", True, (250, 80, 100))

        # Render
        self.screen.fill((0, 0, 0))
        self.screen.blit(text, (self.screen.get_width() // 2 - 50, self.screen.get_height() // 2))

        pygame.display.flip()
