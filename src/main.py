import pygame
from scenes.mainmenu import MainMenu
from scenes.game import Game

class Main():
    def __init__(self):
        self.WIDTH = 800
        self.HEIGHT = 600
        self.FPS = 45

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("My caption of the game")

        self.clock = pygame.time.Clock()
        self.running = False

        self.current_scene = None
        def switch_to_game():
            self.current_scene = Game(self.screen)
        self.current_scene = MainMenu(self.screen, lambda: switch_to_game())
    
    def run(self):
        pygame.init()

        self.running = True

        while self.running:
            # FPS kontrola / jeslti bezi dle rychlosti!
            dt = self.clock.tick(self.FPS)

            if self.current_scene is not None:
                self.current_scene.loop(dt)
                continue

            # Event
            for event in pygame.event.get():
                # print(event) - pokud potrebujete info co se zmacklo.
                if event.type == pygame.QUIT:
                    running = False
            


        pygame.quit()


main = Main()
main.run()