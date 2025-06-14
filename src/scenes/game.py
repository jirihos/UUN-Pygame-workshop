import pygame
import os
from car_sprite import CarSprite
from tiles import tile_dict

class Game:
    def __init__(self, main):
        self.main = main
        self.sprites = pygame.sprite.Group()
        self.car = CarSprite(self.main.screen.get_width() // 2, self.main.screen.get_height() // 2)
        self.sprites.add(self.car)
        self.font = pygame.font.SysFont(None, 36)

        # Definujte base_path zde:
        base_path = os.path.dirname(os.path.dirname(__file__))  # path to src
        self.sprite_sheet = pygame.image.load(os.path.join(base_path, "tiles/game/tilemap_packed.png")).convert_alpha()

        self.SPRITE_TILE_SIZE = 16     # velikost jedné dlaždice v obrázku
        self.TILE_SPACING = 1          # mezera mezi dlaždicemi
        self.TILE_MARGIN = 0           # okraje kolem sprite sheetu
        self.tile_size = 64            # velikost dlaždice na obrazovce

        def get_tile(x, y):
            px = self.TILE_MARGIN + x * (self.SPRITE_TILE_SIZE + self.TILE_SPACING)
            py = self.TILE_MARGIN + y * (self.SPRITE_TILE_SIZE + self.TILE_SPACING)
            rect = pygame.Rect(px, py, self.SPRITE_TILE_SIZE, self.SPRITE_TILE_SIZE)
            return self.sprite_sheet.subsurface(rect)

        self.tile_images = {
            i: pygame.transform.scale(get_tile(*coords), (self.tile_size, self.tile_size))
            for i, (coords, _) in tile_dict.items()
        }

        # === Barvy pro minimapu===
        self.tile_colors = {
            i: (100 + i * 10 % 155, 100 + i * 20 % 155, 100 + i * 30 % 155)
            for i in tile_dict.keys()
        }

        def load_tile_map(path):
            tile_map = []
            with open(path, "r") as f:
                for line in f:
                    row = [int(tile) for tile in line.strip().split(",")]
                    tile_map.append(row)
            return tile_map

        # === Načtení mapy ===
        map_filepath = os.path.join(os.path.dirname(base_path), "editor/tile_map.txt")
        self.tile_map = load_tile_map(map_filepath)  # mapa vygenerovaná editorem

        # === Průchodnost ===
        self.WALKABLE_TILES = [ 1, 2, 3, 4, 5, 15, 16, 17, 18, 19, 20, 21, 22, 23]

        self.MAP_WIDTH = len(self.tile_map[0]) * self.tile_size
        self.MAP_HEIGHT = len(self.tile_map) * self.tile_size

    def is_walkable(self, x, y):
        tile_x = int(x) // self.tile_size
        tile_y = int(y) // self.tile_size
        if 0 <= tile_y < len(self.tile_map) and 0 <= tile_x < len(self.tile_map[0]):
            tile = self.tile_map[tile_y][tile_x]
            return tile in self.WALKABLE_TILES
        return False

    def loop(self, dt):
        screen = self.main.screen

        # Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.main.quit()

        # Update

        # Kamera sleduje hráče
        camera_x = max(0, min(self.car.pos.x - self.main.WIDTH // 2, self.MAP_WIDTH - self.main.WIDTH))
        camera_y = max(0, min(self.car.pos.y - self.main.HEIGHT // 2, self.MAP_HEIGHT - self.main.HEIGHT))

        keys = pygame.key.get_pressed()
        self.car.update(self, camera_x, camera_y, keys)

        font = pygame.font.SysFont("None", 50)
        fps_text = font.render(f"FPS: {self.main.clock.get_fps():.0f}", True, (250, 80, 100))

        # Render
        screen.fill((255, 255, 255))
        # === Vykreslení mapy ===
        for y, row in enumerate(self.tile_map):
            for x, tile_id in enumerate(row):
                pos = (x * self.tile_size - camera_x, y * self.tile_size - camera_y)
                tile_img = self.tile_images.get(tile_id)
                if tile_img:
                    screen.blit(tile_img, pos)
        self.sprites.draw(screen)

        # === Minimapka ===
        def draw_minimap():
            map_w = len(self.tile_map[0])
            map_h = len(self.tile_map)
        
            max_size = 200  # maximální šířka/výška minimapy v pixelech
            mini_tile = max(1, min(max_size // map_w, max_size // map_h))
        
            offset_x = self.main.WIDTH - map_w * mini_tile - 5
            offset_y = self.main.HEIGHT - map_h * mini_tile - 5
        
            # pozadí minimapy (volitelné)
            pygame.draw.rect(screen, (40, 40, 40), (offset_x - 2, offset_y - 2, map_w * mini_tile + 4, map_h * mini_tile + 4))
        
            # vykreslení minimapy
            for y, row in enumerate(self.tile_map):
                for x, tile_id in enumerate(row):
                    color = self.tile_colors.get(tile_id, (100, 100, 100))
                    rect = pygame.Rect(offset_x + x * mini_tile, offset_y + y * mini_tile, mini_tile, mini_tile)
                    pygame.draw.rect(screen, color, rect)
        
            # hráč na minimapě
            px = int(self.car.pos.x // self.tile_size)
            py = int(self.car.pos.y // self.tile_size)
            pygame.draw.rect(
                screen,
                (255, 0, 0),
                pygame.Rect(offset_x + px * mini_tile, offset_y + py * mini_tile, mini_tile, mini_tile)
        )

        # draw_minimap()

        screen.blit(fps_text, (0, 0))

        pygame.display.flip()
