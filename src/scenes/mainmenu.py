import pygame
from menubutton import MenuButton

class MainMenu():
    def __init__(self, screen: pygame.Surface, switch_to_game):
        self.intro_timer = 1000
        self.screen = screen
        self.buttons = pygame.sprite.Group()
        self.buttons.add(MenuButton(self.screen.get_width()/2, self.screen.get_height()/2, 100, 50, lambda: self.start_game()))
        self.switch_to_game = switch_to_game

    def start_game(self):
        self.switch_to_game()

    def loop(self, dt):
        # Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                # TODO
        
        # Update
        self.intro_timer -= dt

        myfont = pygame.font.SysFont("None", 50)
        text = myfont.render(f"Car game", True, (250,80,100))

        intro = self.intro_timer > 0
        menu = not intro

        self.buttons.update()

        # Render
        self.screen.fill((0, 0, 0))
        if intro:
            self.screen.blit(text, (self.screen.get_width()/2, self.screen.get_height()/2))
        
        if menu:
            self.buttons.draw(self.screen)


        pygame.display.flip()