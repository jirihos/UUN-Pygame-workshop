import pygame

class Game():
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    def loop(self, dt):
        myfont = pygame.font.SysFont("None", 50)
        text = myfont.render("Game", True, (250, 80, 100))

        self.screen.fill((0, 0, 0))
        self.screen.blit(text, (self.screen.get_width() // 2 - 50, self.screen.get_height() // 2))

        pygame.display.flip()
