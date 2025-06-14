import pygame
import os
import math
from menubutton import MenuButton

class MainMenu():
    def __init__(self, main):
        self.intro_duration = 3000
        self.intro_timer = self.intro_duration
        self.main = main

        # Load background image
        base_path = os.path.dirname(os.path.dirname(__file__))  # path to src
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
            self.main.screen.get_width() // 2,
            self.main.screen.get_height() // 2,
            lambda: self.main.start_game(),
            play_color=self.title_color
        ))

    def loop(self, dt):
        screen = self.main.screen

        # Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.main.running = False

        # Update
        self.intro_timer -= dt
        self.title_anim_time += dt / 1000  # seconds

        intro = self.intro_timer > 0
        menu = not intro

        self.buttons.update()

        # Render background image
        screen.blit(self.background, (0, 0))

        if intro:
            # Calculate elapsed time since intro started
            elapsed = self.intro_duration - self.intro_timer
            # Animate dots every 300 ms, cycle 0-3
            num_dots = (elapsed // 300) % 4
            loading_text = "Loading" + ("." * int(num_dots))
            loading_font = pygame.font.SysFont(None, 48)
            loading_surface = loading_font.render(loading_text, True, (252, 186, 3))
            loading_shadow = loading_font.render(loading_text, True, (40, 40, 40))
            loading_x = (screen.get_width() - loading_surface.get_width()) // 2
            loading_y = screen.get_height() // 2 - 40
            screen.blit(loading_shadow, (loading_x + 2, loading_y + 2))
            screen.blit(loading_surface, (loading_x, loading_y))

            # Authors with shadow (always visible during intro)
            authors_font = pygame.font.SysFont(None, 36)
            authors_lines = [
                "Authors:",
                "Jiří Hošek",
                "Martin Nebehay",
                "Jiří Mrkvica",
                "Samuel Všelko"
            ]
            # Calculate total height and max width
            line_surfaces = [authors_font.render(line, True, (252, 186, 3)) for line in authors_lines]
            total_height = sum(s.get_height() for s in line_surfaces) + (len(line_surfaces) - 1) * 5
            max_width = max(s.get_width() for s in line_surfaces)
            authors_y = loading_y + 60
            authors_x = (screen.get_width() - max_width) // 2

            # Draw semi-transparent black rectangle
            rect_surface = pygame.Surface((max_width + 40, total_height + 20), pygame.SRCALPHA)
            rect_surface.fill((0, 0, 0, 160))  # 160 = průhlednost (0-255)
            screen.blit(rect_surface, (authors_x - 20, authors_y - 10))

            # Draw each line with shadow
            y = authors_y
            for i, line in enumerate(authors_lines):
                authors_surface = line_surfaces[i]
                authors_shadow = authors_font.render(line, True, (40, 40, 40))
                x = (screen.get_width() - authors_surface.get_width()) // 2
                screen.blit(authors_shadow, (x + 2, y + 2))
                screen.blit(authors_surface, (x, y))
                y += authors_surface.get_height() + 5

        if menu:
            # Animated title (wobble effect) - show only after intro
            amplitude = 10
            frequency = 2
            offset_y = int(amplitude * math.sin(self.title_anim_time * frequency))
            title_surface = self.title_font.render(self.title_text, True, self.title_color)
            shadow_surface = self.title_font.render(self.title_text, True, (40, 40, 40))
            title_x = (screen.get_width() - title_surface.get_width()) // 2
            title_y = 40 + offset_y
            screen.blit(shadow_surface, (title_x + 2, title_y + 2))
            screen.blit(title_surface, (title_x, title_y))

            for button in self.buttons:
                button.draw(screen)

        pygame.display.flip()
