import pygame
import math

class CarSprite(pygame.sprite.Sprite):
    """The car object."""

    def __init__(self, x, y, size=(85, 100)):
        super().__init__()

        self.original_image = pygame.transform.scale(
            pygame.image.load("assets/Car_Ruber.png").convert_alpha(), size
        )
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(x, y))
        
        self.collision_width = size[0] * 0.5
        self.collision_height = size[1] * 0.85


        self.pos = pygame.Vector2(x, y)
        self.angle = 0
        self.speed = 0

        self.max_speed = 5
        self.max_reverse_speed = -2
        self.acceleration = 0.1
        self.brake_strength = 0.3
        self.friction = 0.5

        self.steering_angle = 0
        self.steering_speed = 0.8
        self.max_steering = 5.0
        self.steering_return = 0.5

        self.handbrake_engaged = False
        self.stored_momentum = 0
        self.braking = False

        self.max_fuel = 100
        self.fuel = 100

    def update(self, game, camera_x, camera_y, keys=None):
        if keys is None:
            keys = pygame.key.get_pressed()

        # Steering
        if keys[pygame.K_a]:
            self.steering_angle = min(self.steering_angle + self.steering_speed, self.max_steering)
        elif keys[pygame.K_d]:
            self.steering_angle = max(self.steering_angle - self.steering_speed, -self.max_steering)
        else:
            if self.steering_angle > 0:
                self.steering_angle = max(self.steering_angle - self.steering_return, 0)
            elif self.steering_angle < 0:
                self.steering_angle = min(self.steering_angle + self.steering_return, 0)

        self.braking = keys[pygame.K_x]

        # Movement + Fuel logic
        if not self.handbrake_engaged:
            if self.braking:
                if self.speed > 0:
                    self.speed = max(self.speed - self.brake_strength, 0)
                elif self.speed < 0:
                    self.speed = min(self.speed + self.brake_strength, 0)
            elif keys[pygame.K_w] and self.fuel > 0:
                self.speed = min(self.speed + self.acceleration, self.max_speed)
            elif keys[pygame.K_s] and self.fuel > 0:
                self.speed = max(self.speed - self.acceleration, self.max_reverse_speed)
            else:
                if self.speed > 0:
                    self.speed = max(self.speed - self.friction, 0)
                elif self.speed < 0:
                    self.speed = min(self.speed + self.friction, 0)

        # Move and rotate
        if self.speed != 0:
            self.angle += self.steering_angle * (self.speed / self.max_speed) * 0.5
            rad = math.radians(self.angle)
            dx = -math.sin(rad) * self.speed
            dy = -math.cos(rad) * self.speed

            new_x = self.pos.x + dx
            new_y = self.pos.y + dy

            half_width = self.collision_width / 2
            half_height = self.collision_height / 2

            # Define bounding box collision corners
            collision_points = [
                (new_x - half_width, new_y - half_height),
                (new_x + half_width, new_y - half_height),
                (new_x - half_width, new_y + half_height),
                (new_x + half_width, new_y + half_height),
            ]

            if all(game.is_walkable(px, py) for px, py in collision_points):
                self.pos.x = new_x
                self.pos.y = new_y
            else:
                # Debug: print which corner caused the block
                for i, (px, py) in enumerate(collision_points):
                    if not game.is_walkable(px, py):
                        print(f"[DEBUG] Collision blocked at corner {i}: ({px:.1f}, {py:.1f})")

        # Update image and screen rect
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=(self.pos - pygame.Vector2(camera_x, camera_y)))

        # Fuel usage
        if abs(self.speed) > 0.1 and self.fuel > 0:
            self.fuel -= 0.012
            self.fuel = max(self.fuel, 0)



    def toggle_handbrake(self):
        if not self.handbrake_engaged:
            self.stored_momentum = abs(self.speed)
            self.speed = 0
            self.handbrake_engaged = True
        else:
            direction = 1 if self.angle % 360 < 180 else -1
            self.speed = min(self.stored_momentum + 1.5, self.max_speed) * direction
            self.handbrake_engaged = False
            self.stored_momentum = 0

    def is_handbraking(self):
        return self.handbrake_engaged
