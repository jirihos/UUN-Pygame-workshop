import pygame

from scenes.mainmenu import MainMenu
from scenes.game import Game

class Main():
    """The main class that initializes Pygame"""
    def __init__(self):
        self.WIDTH = 1920
        self.HEIGHT = 1080
        self.FPS = 60

        pygame.init()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.WIDTH, self.HEIGHT = self.screen.get_size()
        pygame.display.set_caption("Ruber Taxi Service")

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