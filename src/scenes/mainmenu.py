import pygame
from menubutton import MenuButton
import os

class MainMenu():
    def __init__(self, screen: pygame.Surface, switch_to_game):
        self.intro_timer = 1000
        self.screen = screen
        self.switch_to_game = switch_to_game

        # Load background image
        base_path = os.path.dirname(__file__)
        self.background = pygame.image.load(os.path.join(base_path, "../tiles/menu/background.png")).convert()

        # Buttons
        self.buttons = pygame.sprite.Group()
        self.buttons.add(MenuButton(
            self.screen.get_width() // 2,
            self.screen.get_height() // 2,
            lambda: self.start_game()
        ))

    def start_game(self):
        self.switch_to_game()

    def handle_event(self, event):
        pass

    def loop(self, dt):
        # Update
        self.intro_timer -= dt

        intro = self.intro_timer > 0
        menu = not intro

        self.buttons.update()

        # Render background image
        self.screen.blit(self.background, (0, 0))

        if intro:
            myfont = pygame.font.SysFont("None", 50)
            text = myfont.render("Car Game", True, (250, 80, 100))
            self.screen.blit(text, (self.screen.get_width() // 2 - 100, self.screen.get_height() // 2))
        
        if menu:
            self.buttons.draw(self.screen)

        pygame.display.flip()
