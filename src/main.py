import pygame

from scenes.mainmenu import MainMenu
from scenes.game import Game

class Main():
    def __init__(self):
        self.WIDTH = 1200
        self.HEIGHT = 800
        self.FPS = 60

        pygame.init()

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Ruber Car Game")

        self.clock = pygame.time.Clock()
        self.running = False

        self.current_scene = MainMenu(self)
    
    def start_game(self):
        self.current_scene = Game(self)

    def run(self):
        self.running = True

        while self.running:
            dt = self.clock.tick(self.FPS)

            if self.current_scene is not None:
                self.current_scene.loop(dt)

        pygame.quit()
    
    def quit(self):
        self.running = False

if __name__ == "__main__":
    main = Main()
    main.run()