import pygame

class Passenger(pygame.sprite.Sprite):
    """Represents a passenger sprite with animations."""

    def __init__(self, x, y, sprite_sheet):
        """Initializes the Passenger sprite with a position and a sprite sheet.
        
        Args:
            x: The x-coordinate where the passenger should appear.
            y: The y-coordinate where the passenger should appear.
            sprite_sheet: The sprite sheet containing passenger animations.
        """

        super().__init__()
        self.sprite_sheet = sprite_sheet  # <- make sure this is passed and stored
        self.sprite_sheet = self.sprite_sheet.subsurface(pygame.Rect(16, 16, 96, 96))  # Ensure the sprite sheet is loaded correctly
        self.background_color = (77, 253, 252)
        self.sprite_sheet.set_colorkey(self.background_color)
        self.frames = []
        self.load_frames()
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_timer = 0
        self.animation_speed = 150  # milliseconds

    def load_frames(self):
        """Loads the frames for the passenger sprite from the sprite sheet."""

        sprite_width, sprite_height = 16, 16
        for i in range(3):  # Walking down
            frame = self.sprite_sheet.subsurface(pygame.Rect(0, i * sprite_height, sprite_width, sprite_height))
            frame = pygame.transform.scale(frame, (32, 32))
            frame.set_colorkey(self.background_color)
            self.frames.append(frame)

    def update(self, dt):
        """Updates the passenger sprite's animation based on the time delta.
        
        Args:
            dt: The time delta since the last update.
        """
        
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]