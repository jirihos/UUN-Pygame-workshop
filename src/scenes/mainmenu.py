import pygame
import os
import math
from menubutton import MenuButton

class MainMenu():
    """Into and main menu screen."""

    def __init__(self, main):
        self.intro_duration = 6000
        self.intro_timer = self.intro_duration
        self.main = main

        self.title_text = "Ruber Taxi Service"
        self.title_color = (252, 186, 3)
        self.title_font = pygame.font.SysFont(None, 96)
        self.title_anim_time = 0

        # Definujte base_path zde:
        base_path = os.path.dirname(os.path.dirname(__file__))  # path to src

        # Load background image and scale to fit the screen
        bg_image = pygame.image.load(os.path.join(base_path, "tiles/menu/background.png")).convert()
        self.background = pygame.transform.scale(bg_image, (self.main.screen.get_width(), self.main.screen.get_height()))

        # Buttons
        self.buttons = pygame.sprite.Group()
        self.buttons.add(MenuButton(
            self.main.screen.get_width() // 2,
            self.main.screen.get_height() // 2,
            lambda: self.main.start_game(),
            text="Play",
            play_color=self.title_color
        ))
        # Add Exit button
        # Position Exit button at the bottom right corner
        icon_size = 36
        margin = 12
        self.buttons.add(MenuButton(
            margin + icon_size // 2,
            self.main.screen.get_height() - margin - icon_size // 2,
            lambda: self.main.quit(),
            text="Exit",
            play_color=(220, 40, 40),
            icon_idle=os.path.join(base_path, "tiles/menu/icon_cross_red.png"),
            icon_hover=os.path.join(base_path, "tiles/menu/icon_cross_red.png"),
            icon_click=os.path.join(base_path, "tiles/menu/icon_cross_grey.png"),
            font_size=38
        ))

    def loop(self, dt):
        """Performs the Event, Update, Render cycle."""

        screen = self.main.screen

        # Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.main.quit()
            # Allow skipping intro with mouse click
            if event.type == pygame.MOUSEBUTTONDOWN and self.intro_timer > 0:
                self.intro_timer = 0

        # Update
        self.intro_timer -= dt
        self.title_anim_time += dt / 1000  # seconds

        intro = self.intro_timer > 0
        menu = not intro

        self.buttons.update()

        # Render background image
        screen.blit(self.background, (0, 0))

        if intro:
            # --- Custom intro animation ---
            studio_fadein = 1000
            author_fadein = 800
            fade_time = 500
            authors = [
                "Jiří Hošek",
                "Martin Nebehay",
                "Jiří Mrkvica",
                "Samuel Všelko"
            ]
            present_text = "present the game..."
            authors_font = pygame.font.SysFont(None, 36)
            studio_font = pygame.font.SysFont(None, 48)
            present_font = pygame.font.SysFont(None, 32)
            elapsed = self.intro_duration - self.intro_timer

            # 1. Studio name fade-in (text + shadow only)
            studio_alpha = min(255, int(255 * (elapsed / studio_fadein)))
            studio_surface = studio_font.render("Tým 12 - summer 2025", True, (252, 186, 3))
            studio_shadow = studio_font.render("Tým 12 - summer 2025", True, (40, 40, 40))
            studio_x = (screen.get_width() - studio_surface.get_width()) // 2
            studio_y = screen.get_height() // 2 - 350

            studio_shadow.set_alpha(studio_alpha)
            studio_surface.set_alpha(studio_alpha)
            screen.blit(studio_shadow, (studio_x + 2, studio_y + 2))
            screen.blit(studio_surface, (studio_x, studio_y))

            # 2. Authors fade-in one by one (text + shadow only)
            for i, author in enumerate(authors):
                appear_time = studio_fadein + i * author_fadein
                if elapsed > appear_time:
                    alpha = min(255, int(255 * ((elapsed - appear_time) / fade_time)))
                    alpha = max(0, min(alpha, 255))
                    author_surface = authors_font.render(author, True, (252, 186, 3))
                    author_shadow = authors_font.render(author, True, (40, 40, 40))
                    author_x = (screen.get_width() - author_surface.get_width()) // 2
                    author_y = studio_y + 80 + i * 50

                    author_shadow.set_alpha(alpha)
                    author_surface.set_alpha(alpha)
                    screen.blit(author_shadow, (author_x + 2, author_y + 2))
                    screen.blit(author_surface, (author_x, author_y))

            # 3. "present the game..." fade-in after all authors (text + shadow only)
            present_appear_time = studio_fadein + len(authors) * author_fadein
            if elapsed > present_appear_time:
                alpha = min(255, int(255 * ((elapsed - present_appear_time) / fade_time)))
                alpha = max(0, min(alpha, 255))
                present_surface = present_font.render(present_text, True, (252, 186, 3))
                present_shadow = present_font.render(present_text, True, (40, 40, 40))
                present_x = (screen.get_width() - present_surface.get_width()) // 2
                present_y = studio_y + 80 + len(authors) * 50 + 30

                present_shadow.set_alpha(alpha)
                present_surface.set_alpha(alpha)
                screen.blit(present_shadow, (present_x + 2, present_y + 2))
                screen.blit(present_surface, (present_x, present_y))

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
