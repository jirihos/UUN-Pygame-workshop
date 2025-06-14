import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Sprite Example")

# Load car image
car_image = pygame.image.load("assets/Car_Ruber.png").convert_alpha()
car_rect = car_image.get_rect(center=(WIDTH // 2, HEIGHT // 2))

# Main loop
clock = pygame.time.Clock()
running = True

while running:
    screen.fill((30, 30, 30))  # Background color

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw car
    screen.blit(car_image, car_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
