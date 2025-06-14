import pygame
import os

class MenuButton(pygame.sprite.Sprite):
    def __init__(self, x, y, callback, play_color=(252, 186, 3)):
        super().__init__()
        base_path = os.path.dirname(__file__)  # path to src
        font_path = os.path.join(base_path, "fonts/Kenney_Future.ttf")

        self.image_idle = pygame.image.load(os.path.join(base_path, "tiles/menu/arrow_decorative_e_green.png")).convert_alpha()
        self.image_hover = pygame.image.load(os.path.join(base_path, "tiles/menu/arrow_decorative_e_yellow.png")).convert_alpha()
        self.image_click = pygame.image.load(os.path.join(base_path, "tiles/menu/arrow_decorative_e_grey.png")).convert_alpha()

        self.image = self.image_idle
        self.rect = self.image.get_rect(center=(x, y))

        self.callback = callback
        self.clicked = False
        self.hovered = False  # Track hover state

        # Font for "Play" text
        self.font = pygame.font.Font(font_path, 48)
        self.text_surface = self.font.render("Play", True, play_color)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        if self.rect.collidepoint(mouse_pos):
            self.hovered = True
            if mouse_pressed:
                self.image = self.image_click
                if not self.clicked:
                    self.clicked = True
                    self.callback()
            else:
                self.image = self.image_hover
                self.clicked = False
        else:
            self.image = self.image_idle
            self.clicked = False
            self.hovered = False

    def draw(self, surface):
        offset = 100 if self.hovered else 0
        arrow_pos = (self.rect.x + offset, self.rect.y)
        if self.hovered:
            # Draw "Play" text with shadow to the left of the arrow
            text_x = arrow_pos[0] - self.text_surface.get_width() - 10
            text_y = arrow_pos[1] + (self.image.get_height() - self.text_surface.get_height()) // 2
            # Shadow
            shadow_surface = self.font.render("Play", True, (40, 40, 40))
            surface.blit(shadow_surface, (text_x + 2, text_y + 2))
            surface.blit(self.text_surface, (text_x, text_y))
        surface.blit(self.image, arrow_pos)
        # If not hovered, draw arrow in original position (already handled by the image.blit call)
