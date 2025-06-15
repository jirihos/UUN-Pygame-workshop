import pygame
from car_sprite import CarSprite

class Game:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.sprites = pygame.sprite.Group()
        self.car = CarSprite(screen.get_width() // 2, screen.get_height() // 2)
        self.sprites.add(self.car)
        self.font = pygame.font.SysFont(None, 36)
        self.brake_pressed = False

    def loop(self, dt):
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.car.toggle_handbrake()

        self.brake_pressed = keys[pygame.K_x]
        self.car.update(keys)

        self.screen.fill((30, 30, 30))
        self.sprites.draw(self.screen)

        # --- UI Indicators ---
        if self.car.is_handbraking():
            self._draw_text("Handbrake ON", 20, 20, (255, 100, 100))
        if self.brake_pressed:
            self._draw_text("Brake ON", 20, 60, (255, 255, 100))

        pygame.display.flip()

    def _draw_text(self, text, x, y, color=(255, 255, 255)):
        surface = self.font.render(text, True, color)
        self.screen.blit(surface, (x, y))
