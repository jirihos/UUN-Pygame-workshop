import pygame
import os
import math
from menubutton import MenuButton

class MainMenu():
    """Into and main menu screen.
    Displays the game title, animated intro, and buttons to start the game or exit.
    """

    def __init__(self, main, skip_intro=False):
        """Initializes the main menu.
        """

        self.intro_duration = 6000
        self.intro_timer = 0 if skip_intro else self.intro_duration  # Přeskoč intro pokud skip_intro=True
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
        play_btn_x = self.main.screen.get_width() // 2
        play_btn_y = self.main.screen.get_height() // 2 - 180

        # --- PLAY button ---
        play_button = MenuButton(
            play_btn_x,
            play_btn_y,
            lambda: self.main.start_game(),
            text="Play",
            play_color=self.title_color
        )
        self.buttons.add(play_button)

        # --- Reset High Score Button (directly under PLAY, same style/size) ---
        def reset_high_score():
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            score_file = os.path.join(base_path, "highscore.txt")
            try:
                with open(score_file, "w") as f:
                    f.write("0")
            except Exception as e:
                print(f"Error resetting high score: {e}")
            self.high_score = 0

        blue_icon = os.path.join(base_path, "tiles/menu/button_round_flat.png")
        if not os.path.exists(blue_icon):
            blue_icon = None  # fallback to default

        reset_btn_x = play_btn_x
        reset_btn_y = play_btn_y + 90
        reset_button = MenuButton(
            reset_btn_x,
            reset_btn_y,
            reset_high_score,
            text="Reset Score",
            play_color=(60, 140, 255),
            icon_idle=blue_icon,
            icon_hover=blue_icon,
            icon_click=blue_icon,
            font_size=48,
            hover_offset=220,
            icon_size=64
        )
        self.buttons.add(reset_button)

        # --- EXIT button (directly under RESET SCORE, same style/size) ---
        exit_btn_x = play_btn_x
        exit_btn_y = reset_btn_y + 90
        exit_icon_red = os.path.join(base_path, "tiles/menu/icon_cross_red.png")
        exit_icon_grey = os.path.join(base_path, "tiles/menu/icon_cross_grey.png")
        exit_button = MenuButton(
            exit_btn_x,
            exit_btn_y,
            lambda: self.main.quit(),
            text="Exit",
            play_color=(220, 40, 40),
            icon_idle=exit_icon_red,
            icon_hover=exit_icon_red,
            icon_click=exit_icon_grey,
            font_size=48,
            hover_offset=100,
            icon_size=58
        )
        self.buttons.add(exit_button)

        self.high_score = self.load_high_score()

    def load_high_score(self):
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        score_file = os.path.join(base_path, "highscore.txt")
        try:
            if os.path.exists(score_file):
                with open(score_file, "r") as f:
                    return int(f.read().strip())
        except Exception as e:
            print(f"Error loading high score: {e}")
        return 0

    def loop(self, dt):
        """Performs the Event, Update, Render cycle.

        Args:
            dt (int): Delta time in milliseconds since the last frame.
        """

        screen = self.main.screen

        # Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.main.quit()
            # Allow skipping intro with mouse click
            elif event.type == pygame.MOUSEBUTTONDOWN and self.intro_timer > 0:
                self.intro_timer = 0
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.main.quit()

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
            studio_surface = studio_font.render("Team 12 - summer 2025", True, (252, 186, 3))
            studio_shadow = studio_font.render("Team 12 - summer 2025", True, (40, 40, 40))
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

            # Show high score below the title
            high_score_font = pygame.font.SysFont(None, 48)
            high_score_text = f"High Score: {self.high_score}"
            high_score_surface = high_score_font.render(high_score_text, True, (255, 255, 255))
            high_score_shadow = high_score_font.render(high_score_text, True, (40, 40, 40))
            high_score_x = (screen.get_width() - high_score_surface.get_width()) // 2
            high_score_y = title_y + title_surface.get_height() + 20
            screen.blit(high_score_shadow, (high_score_x + 2, high_score_y + 2))
            screen.blit(high_score_surface, (high_score_x, high_score_y))

            # --- Update high score in case it was reset ---
            self.high_score = self.load_high_score()

            for button in self.buttons:
                button.draw(screen)

        pygame.display.flip()
