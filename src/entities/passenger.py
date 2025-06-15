import pygame

class Passenger(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_sheet):
        super().__init__()
        self.sprite_sheet = sprite_sheet  # <- make sure this is passed and stored
        self.sprite_sheet = self.sprite_sheet.subsurface(pygame.Rect(16, 16, 96, 96))  # Ensure the sprite sheet is loaded correctly
        background_color = (77, 253, 252)
        self.sprite_sheet.set_colorkey(background_color)
        self.frames = []
        self.load_frames()
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_timer = 0
        self.animation_speed = 150  # milliseconds

    def load_frames(self):
        sprite_width, sprite_height = 16, 16
        for i in range(3):  # Walking down
            frame = self.sprite_sheet.subsurface(pygame.Rect(0, i * sprite_height, sprite_width, sprite_height))
            self.frames.append(frame)

    def update(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]