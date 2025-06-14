import pygame
from car_sprite import CarSprite

class Game:
    def __init__(self, main):
        self.main = main
        self.sprites = pygame.sprite.Group()
        self.car = CarSprite(self.main.screen.get_width() // 2, self.main.screen.get_height() // 2)
        self.sprites.add(self.car)
        self.font = pygame.font.SysFont(None, 36)

    def loop(self, dt):
        screen = self.main.screen

        # Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.main.quit()

        # Update
        keys = pygame.key.get_pressed()
        self.car.update(keys)

        font = pygame.font.SysFont("None", 50)
        fps_text = font.render(f"FPS: {self.main.clock.get_fps():.0f}", True, (250, 80, 100))

        # Render
        screen.fill((30, 30, 30))
        self.sprites.draw(screen)

        screen.blit(fps_text, (0, 0))

        pygame.display.flip()
