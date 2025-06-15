import pygame
from entities.passenger import Passenger

class PassengerManager:
    def __init__(self, sprite_sheet):
        self.sprite_sheet = sprite_sheet
        self.group = pygame.sprite.Group()
        self.sprite = None
        self.visible = False
        self.animating = False

    def start_entry_animation(self, x, y):
        self.sprite = Passenger(x, y, self.sprite_sheet)
        self.group.add(self.sprite)
        self.visible = True
        self.animating = True

    def remove_passenger(self):
        if self.sprite:
            self.sprite.kill()
            self.sprite = None
        self.visible = False
        self.animating = False

    def update(self, dt):
        self.group.update(dt)

    def draw(self, screen, camera_x, camera_y):
        if self.sprite:
            screen.blit(
                self.sprite.image,
                (self.sprite.rect.x - camera_x, self.sprite.rect.y - camera_y)
        )

