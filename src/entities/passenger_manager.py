import pygame
from .passenger import Passenger

class PassengerManager:
    def __init__(self, sprite_sheet):
        self.group = pygame.sprite.Group()
        self.sprite_sheet = sprite_sheet
        self.passenger_sprite = None
        self.visible = False

    def spawn_passenger(self, pixel_x, pixel_y):
        self.passenger_sprite = Passenger(pixel_x, pixel_y, self.sprite_sheet)
        self.group.add(self.passenger_sprite)
        self.visible = True

    def update(self, dt):
        self.group.update(dt)

    def draw(self, screen, camera_x, camera_y):
        for sprite in self.group:
            screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y - camera_y))

    def reset(self):
        self.group.empty()
        self.passenger_sprite = None
        self.visible = False

    def start_entry_animation(self, x, y):
        # Create and add a new passenger at given x, y
        self.passenger = Passenger(x, y, self.sprite_sheet)
        self.group.add(self.passenger)

