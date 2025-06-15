import pygame
import os
import math
import random
from car_sprite import CarSprite
from tiles import tile_dict
from job import Job

class Game:
    def __init__(self, main):
        self.main = main
        self.sprites = pygame.sprite.Group()
        self.car = CarSprite(400, 500)  # Manual spawn position
        self.sprites.add(self.car)
        self.font = pygame.font.SysFont(None, 36)
        self.brake_pressed = False

        base_path = os.path.dirname(os.path.dirname(__file__))

        self.SPRITE_TILE_SIZE = 16
        self.TILE_SPACING = 1
        self.TILE_MARGIN = 0

        self.tile_size = 40

        self.sprite_sheet = pygame.image.load(os.path.join(base_path, "tiles/game/tilemap.png")).convert_alpha()

        def get_tile(x, y):
            px = self.TILE_MARGIN + x * (self.SPRITE_TILE_SIZE + self.TILE_SPACING)
            py = self.TILE_MARGIN + y * (self.SPRITE_TILE_SIZE + self.TILE_SPACING)
            rect = pygame.Rect(px, py, self.SPRITE_TILE_SIZE, self.SPRITE_TILE_SIZE)
            return self.sprite_sheet.subsurface(rect)

        self.tile_images = {
            i: pygame.transform.scale(get_tile(*coords), (self.tile_size, self.tile_size))
            for i, (coords, _) in tile_dict.items()
        }

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

        map_filepath = os.path.join(os.path.dirname(base_path), "editor/tile_map.txt")
        self.tile_map = load_tile_map(map_filepath)

        self.WALKABLE_TILES = [0, 22, 850, 851, 779, 674, 709]

        self.MAP_WIDTH = len(self.tile_map[0]) * self.tile_size
        self.MAP_HEIGHT = len(self.tile_map) * self.tile_size

        # find pickup tile locations
        self.pickup_tile_locations = []
        for y, row in enumerate(self.tile_map):
            for x, tile_id in enumerate(row):
                PICKUP_TILE = 851
                if tile_id == PICKUP_TILE:
                    self.pickup_tile_locations.append((x, y))
        
        self.new_job()

    def new_job(self):
        if len(self.pickup_tile_locations) < 2:
            self.current_job = None
            return
        
        locs = random.sample(self.pickup_tile_locations, 2)
        self.current_job = Job(locs[0], locs[1])

    def is_walkable(self, x, y): 
        tile_x = int(x) // self.tile_size
        tile_y = int(y) // self.tile_size
        if 0 <= tile_y < len(self.tile_map) and 0 <= tile_x < len(self.tile_map[0]):
            tile = self.tile_map[tile_y][tile_x]
            return tile in self.WALKABLE_TILES
        return False

    def loop(self, dt):
        screen = self.main.screen

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.main.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.car.toggle_handbrake()

        camera_x = max(0, min(self.car.pos.x - self.main.WIDTH // 2, self.MAP_WIDTH - self.main.WIDTH))
        camera_y = max(0, min(self.car.pos.y - self.main.HEIGHT // 2, self.MAP_HEIGHT - self.main.HEIGHT))

        keys = pygame.key.get_pressed()
        self.brake_pressed = keys[pygame.K_x]
        self.car.update(self, camera_x, camera_y, keys)

        screen.fill((255, 255, 255))

        for y, row in enumerate(self.tile_map):
            for x, tile_id in enumerate(row):
                pos = (x * self.tile_size - camera_x, y * self.tile_size - camera_y)
                tile_img = self.tile_images.get(tile_id)
                if tile_img:
                    screen.blit(tile_img, pos)

                # === Draw red outline for unwalkable tiles (debug) ===
                if tile_id not in self.WALKABLE_TILES:
                    pygame.draw.rect(screen, (255, 0, 0), (*pos, self.tile_size, self.tile_size), 2)

        self.sprites.draw(screen)

        self.draw_dashboard()

        # for debugging
        screen.blit(self.font.render(f"FPS: {self.main.clock.get_fps():.0f}", True, (250, 80, 100)), (0, 0))
        if self.current_job is not None:
            screen.blit(self.font.render(f"Pickup tile: {self.current_job.pickup_tile_loc}", True, (250, 80, 100)), (200, 0))
            screen.blit(self.font.render(f"Delivery tile: {self.current_job.delivery_tile_loc}", True, (250, 80, 100)), (700, 0))

        pygame.display.flip()

    def draw_dashboard(self):
        dash_rect = pygame.Rect(20, self.main.HEIGHT - 100, 240, 80)
        pygame.draw.rect(self.main.screen, (20, 20, 20), dash_rect, border_radius=10)
        pygame.draw.rect(self.main.screen, (80, 80, 80), dash_rect, 3, border_radius=10)

        speed_display = int(abs(self.car.speed * 5))  # scaled up display
        self._draw_text(f"{speed_display} km/h", dash_rect.x + 20, dash_rect.y + 20, (255, 255, 255), size=36)

        fuel_level = max(0, min(self.car.fuel, 100))  # clamp to [0,100]
        blocks = 5
        block_width = 20
        block_height = 30
        spacing = 5
        start_x = dash_rect.right - (blocks * (block_width + spacing)) - 10
        y = dash_rect.y + 20

        for i in range(blocks):
            threshold = (i + 1) * (100 / blocks)
            color = (100, 100, 100)
            if fuel_level >= threshold:
                if i >= 3:
                    color = (0, 200, 0)
                elif i == 2:
                    color = (255, 200, 0)
                else:
                    color = (255, 0, 0)

            rect = pygame.Rect(start_x + i * (block_width + spacing), y, block_width, block_height)
            pygame.draw.rect(self.main.screen, color, rect)
            pygame.draw.rect(self.main.screen, (255, 255, 255), rect, 2)

        if self.brake_pressed:
            pygame.draw.rect(self.main.screen, (200, 0, 0), (dash_rect.x + 10, dash_rect.bottom - 25, 80, 20))
            self._draw_text("BRAKE", dash_rect.x + 15, dash_rect.bottom - 24, (0, 0, 0), size=20)

        if self.car.is_handbraking():
            pygame.draw.circle(self.main.screen, (200, 0, 0), (dash_rect.right - 20, dash_rect.bottom - 20), 10)
            self._draw_text("P", dash_rect.right - 25, dash_rect.bottom - 28, (0, 0, 0), size=20)

    def _draw_text(self, text, x, y, color=(255, 255, 255), size=36):
        font = pygame.font.SysFont(None, size)
        surface = font.render(text, True, color)
        self.main.screen.blit(surface, (x, y))
