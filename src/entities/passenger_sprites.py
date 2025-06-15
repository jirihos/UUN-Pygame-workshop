import pygame
import os

class PassengerSpriteLoader:
    def __init__(self):
        base_path = os.path.dirname(__file__)
        sprite_path = os.path.join(base_path, "..", "assets", "passengers", "e131d11a-b1e6-4d1d-9135-887f90b5c282.png")
        self.sheet = pygame.image.load(sprite_path).convert_alpha()
        self.sprite_size = 16
        self.sprites = self.load_all_sprites()

    def load_all_sprites(self):
        sprites = []
        for col in range(5):  # 5 characters horizontally
            for row in range(1):  # Only 1 row of unique characters for now
                x = col * self.sprite_size
                y = row * self.sprite_size * 4  # 4 animation frames (up, left, down, right)
                frame_surface = pygame.Surface((self.sprite_size, self.sprite_size), pygame.SRCALPHA)
                frame_surface.blit(self.sheet, (0, 0), (x, y + self.sprite_size * 2, self.sprite_size, self.sprite_size))  # Down-facing
                sprites.append(frame_surface)
        return sprites
