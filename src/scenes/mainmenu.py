import os
import pygame
from menubutton import MenuButton
import math

class MainMenu():
    def __init__(self, screen: pygame.Surface, switch_to_game):
        self.intro_timer = 1000
        self.screen = screen
        self.switch_to_game = switch_to_game

        # Load background image
        base_path = os.path.dirname(os.path.dirname(__file__))  # cesta do složky src
        self.background = pygame.image.load(os.path.join(base_path, "tiles/menu/background.png")).convert()

        # Animated title setup
        font_path = os.path.join(base_path, "fonts/Kenney_Future.ttf")
        self.title_font = pygame.font.Font(font_path, 64)
        self.title_color = (252, 186, 3)
        self.title_text = "Ruber Car Game"
        self.title_anim_time = 0

        # Buttons
        self.buttons = pygame.sprite.Group()
        self.buttons.add(MenuButton(
            self.screen.get_width() // 2,
            self.screen.get_height() // 2,
            lambda: self.start_game(),
            play_color=self.title_color
        ))

    def start_game(self):
        self.switch_to_game()

    def loop(self, dt):
        # Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                # TODO

        # Update
        self.intro_timer -= dt
        self.title_anim_time += dt / 1000  # seconds

        intro = self.intro_timer > 0
        menu = not intro

        self.buttons.update()

        # Render background image
        self.screen.blit(self.background, (0, 0))

        # Animated title (wobble effect)
        amplitude = 10
        frequency = 2
        offset_y = int(amplitude * math.sin(self.title_anim_time * frequency))
        title_surface = self.title_font.render(self.title_text, True, self.title_color)
        title_x = (self.screen.get_width() - title_surface.get_width()) // 2
        title_y = 40 + offset_y
        self.screen.blit(title_surface, (title_x, title_y))

        if intro:
            myfont = pygame.font.SysFont("None", 50)
            text = myfont.render("Car Game", True, (250, 80, 100))
            self.screen.blit(text, (self.screen.get_width() // 2 - 100, self.screen.get_height() // 2))
        
        if menu:
            for button in self.buttons:
                button.draw(self.screen)

        pygame.display.flip()
