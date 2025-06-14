import pygame

from scenes.mainmenu import MainMenu
from scenes.game import Game

class Main():
    def __init__(self):
        self.WIDTH = 768
        self.HEIGHT = 768
        self.FPS = 45

        pygame.init()

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Ruber Car Game")

        self.clock = pygame.time.Clock()
        self.running = False

        self.current_scene = None

        def switch_to_game():
            self.current_scene = Game(self.screen)
        self.current_scene = MainMenu(self.screen, switch_to_game)

    def run(self):
        self.running = True

        while self.running:
            dt = self.clock.tick(self.FPS)

            # --- Event handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif hasattr(self.current_scene, "handle_event"):
                    self.current_scene.handle_event(event)

            # --- Scene logic and rendering ---
            if self.current_scene is not None:
                self.current_scene.loop(dt)

        pygame.quit()

if __name__ == "__main__":
    main = Main()
    main.run()