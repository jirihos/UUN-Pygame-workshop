import pygame
from entities.passenger import Passenger

class PassengerManager:
    """Manages the passenger sprite and its animations."""

    def __init__(self, sprite_sheet):
        """Initializes the PassengerManager with a sprite sheet.
        
        Args:
            sprite_sheet: The sprite sheet containing passenger animations.
        """

        self.sprite_sheet = sprite_sheet
        self.group = pygame.sprite.Group()
        self.sprite = None
        self.visible = False
        self.animating = False

    def start_entry_animation(self, x, y):
        """Starts the entry animation for a passenger at the given coordinates.
        
        Args:
            x: The x-coordinate where the passenger should appear.
            y: The y-coordinate where the passenger should appear.
        """

        self.sprite = Passenger(x, y, self.sprite_sheet)
        self.group.add(self.sprite)
        self.visible = True
        self.animating = True

    def remove_passenger(self):
        """Removes the passenger sprite from the group and stops its animation."""
        
        if self.sprite:
            self.sprite.kill()
            self.sprite = None
        self.visible = False
        self.animating = False

    def update(self, dt):
        """Updates the passenger sprite and its animations.

        Args:
            dt: The time delta since the last update.
        """

        self.group.update(dt)

    def draw(self, screen, camera_x, camera_y):
        """Draws the passenger sprite on the screen.

        Args:
            screen: The screen surface to draw on.
            camera_x: The x-coordinate of the camera.
            camera_y: The y-coordinate of the camera.
        """
        
        if self.sprite:
            screen.blit(
                self.sprite.image,
                (self.sprite.rect.x - camera_x, self.sprite.rect.y - camera_y)
        )

