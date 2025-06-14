import pygame
import os

class MenuButton(pygame.sprite.Sprite):
    def __init__(self, x, y, callback):
        super().__init__()
        base_path = os.path.dirname(__file__)
        self.image_idle = pygame.image.load(os.path.join(base_path, "tiles/menu/arrow_decorative_e_green.png")).convert_alpha()
        self.image_hover = pygame.image.load(os.path.join(base_path, "tiles/menu/arrow_decorative_e_yellow.png")).convert_alpha()
        self.image_click = pygame.image.load(os.path.join(base_path, "tiles/menu/arrow_decorative_e_grey.png")).convert_alpha()

        self.image = self.image_idle
        self.rect = self.image.get_rect(center=(x, y))

        self.callback = callback
        self.clicked = False

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        if self.rect.collidepoint(mouse_pos):
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
