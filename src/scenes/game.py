import pygame
from car_sprite import CarSprite

class Game:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.sprites = pygame.sprite.Group()
        self.car = CarSprite(screen.get_width() // 2, screen.get_height() // 2)
        self.sprites.add(self.car)
        self.font = pygame.font.SysFont(None, 36)

    def loop(self, dt):
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                # TODO

        self.car.update(keys)
        self.screen.fill((30, 30, 30))
        self.sprites.draw(self.screen)

        pygame.display.flip()
