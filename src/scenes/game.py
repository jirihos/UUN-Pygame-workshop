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
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.main.quit()

        self.car.update(keys)
        screen.fill((30, 30, 30))
        self.sprites.draw(screen)

        pygame.display.flip()
