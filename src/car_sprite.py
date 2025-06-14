import pygame
import math

class CarSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, size=(150, 200)):
        super().__init__()
        original_image = pygame.image.load("assets/Car_Ruber.png").convert_alpha()
        self.original_image = pygame.transform.scale(original_image, size)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))

        self.pos = pygame.Vector2(x, y)
        self.angle = 0
        self.speed = 0

        self.max_speed = 6
        self.acceleration = 0.2
        self.brake_strength = 1.0
        self.friction = 0.05

        self.steering_angle = 0
        self.steering_speed = 0.3
        self.max_steering = 3
        self.steering_return = 0.1

    def update(self, keys=None):
        if keys is None:
            keys = pygame.key.get_pressed()

        # Steering input
        if keys[pygame.K_a]:
            self.steering_angle = min(self.steering_angle + self.steering_speed, self.max_steering)
        elif keys[pygame.K_d]:
            self.steering_angle = max(self.steering_angle - self.steering_speed, -self.max_steering)
        else:
            if self.steering_angle > 0:
                self.steering_angle = max(self.steering_angle - self.steering_return, 0)
            elif self.steering_angle < 0:
                self.steering_angle = min(self.steering_angle + self.steering_return, 0)

        # Acceleration
        if keys[pygame.K_w]:
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_s]:
            self.speed = max(self.speed - self.acceleration, -2)
        else:
            if self.speed > 0:
                self.speed = max(self.speed - self.friction, 0)
            elif self.speed < 0:
                self.speed = min(self.speed + self.friction, 0)

        # Apply turning
        if self.speed != 0:
            self.angle += self.steering_angle * (self.speed / self.max_speed) * 0.5

            rad = math.radians(self.angle)
            dx = -math.sin(rad) * self.speed
            dy = -math.cos(rad) * self.speed
            self.pos.x += dx
            self.pos.y += dy

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.pos)
