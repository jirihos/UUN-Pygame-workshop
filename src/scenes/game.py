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
        self.car = CarSprite(400,500)
        self.sprites.add(self.car)
        self.brake_pressed = False
        self.money = 0 


        base_path = os.path.dirname(os.path.dirname(__file__))

        # Use the same font as in mainmenu.py and menubutton.py
        self.font_path = os.path.join(base_path, "fonts/Kenney_Future.ttf")
        self.font = pygame.font.Font(self.font_path, 36)
        self.font_small = pygame.font.Font(self.font_path, 24)

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

        self.WALKABLE_TILES = [0, 22, 850, 851, 852, 779, 674, 709, 782]

        self.MAP_WIDTH = len(self.tile_map[0]) * self.tile_size
        self.MAP_HEIGHT = len(self.tile_map) * self.tile_size

        # Find pickup and pump tile locations
        self.pickup_tile_locations = []
        self.pump_tile_locations = []
        for y, row in enumerate(self.tile_map):
            for x, tile_id in enumerate(row):
                PICKUP_TILE = 851
                PUMP_TILE = 852
                if tile_id == PICKUP_TILE:
                    self.pickup_tile_locations.append((x, y))
                elif tile_id == PUMP_TILE:
                    self.pump_tile_locations.append((x, y))
        
        self.new_job()

        # === Minimap ===
        self.minimap_scale = 2
        self.minimap_surface = self._create_minimap()

        # Load PNG backgrounds for minimap and dashboard
        self.dashboard_bg_img = pygame.image.load(os.path.join(base_path, "tiles/game/game_board_background.png")).convert_alpha()

        self.show_fps = False  # FPS display toggle

    def new_job(self):
        if len(self.pickup_tile_locations) < 2:
            self.current_job = None
            self.job_state = None
            return
        
        locs = random.sample(self.pickup_tile_locations, 2)
        self.current_job = Job(locs[0], locs[1])
        self.job_state = "pickup"

    def _create_minimap(self):
        """Creates the minimap surface from the tile_map."""
        map_w = len(self.tile_map[0])
        map_h = len(self.tile_map)
        scale = self.minimap_scale
        surf = pygame.Surface((int(map_w * scale), int(map_h * scale)))
        surf.fill((30, 30, 30))
        for y, row in enumerate(self.tile_map):
            for x, tile_id in enumerate(row):
                color = self.tile_colors.get(tile_id, (80, 80, 80))
                rect = pygame.Rect(int(x * scale), int(y * scale), max(1, int(scale)), max(1, int(scale)))
                surf.fill(color, rect)
        return surf

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
                elif event.key == pygame.K_ESCAPE:
                    self.main.quit()
                elif event.key == pygame.K_l:
                    self.show_fps = not self.show_fps  # Toggle FPS display

        camera_x = max(0, min(self.car.pos.x - self.main.WIDTH // 2, self.MAP_WIDTH - self.main.WIDTH))
        camera_y = max(0, min(self.car.pos.y - self.main.HEIGHT // 2, self.MAP_HEIGHT - self.main.HEIGHT))

        keys = pygame.key.get_pressed()
        self.brake_pressed = keys[pygame.K_x]
        self.car.update(self, camera_x, camera_y, keys)

        # === Job Progress Logic ===
        if self.current_job and self.job_state:
            if self.job_state == "pickup":
                if self.is_at_tile(self.current_job.pickup_tile_loc) and self.car.is_handbraking() and abs(self.car.speed) < 0.2:
                    print("[JOB] Passenger picked up.")
                    self.job_state = "dropoff"

            elif self.job_state == "dropoff":
                if self.is_at_tile(self.current_job.delivery_tile_loc) and self.car.is_handbraking() and abs(self.car.speed) < 0.2:
                    print("[JOB] Passenger dropped off. Job complete.")
                    self.money += random.randint(15,25)
                    self.new_job()

        screen.fill((50, 50, 50))

        for y, row in enumerate(self.tile_map):
            for x, tile_id in enumerate(row):
                pos = (x * self.tile_size - camera_x, y * self.tile_size - camera_y)
                tile_img = self.tile_images.get(tile_id)
                if tile_img:
                    screen.blit(tile_img, pos)

                # === Draw red outline for unwalkable tiles (debug) ===
                # if tile_id not in self.WALKABLE_TILES:
                #     pygame.draw.rect(screen, (255, 0, 0), (*pos, self.tile_size, self.tile_size), 2)

        self.sprites.draw(screen)

        small_font = pygame.font.Font(self.font_path, 32)

        # Draw FPS only if toggled on
        if self.show_fps:
            fps_text = f"FPS: {self.main.clock.get_fps():.0f}"
            fps_shadow = small_font.render(fps_text, True, (40, 40, 40))
            fps_surface = small_font.render(fps_text, True, (0, 255, 0))
            screen.blit(fps_shadow, (2, 2))
            screen.blit(fps_surface, (0, 0))

        if self.current_job is not None:
             screen.blit(small_font.render(f"Pickup tile: {self.current_job.pickup_tile_loc}", True, (250, 80, 100)), (200, 0))
             screen.blit(small_font.render(f"Delivery tile: {self.current_job.delivery_tile_loc}", True, (250, 80, 100)), (500, 0))
             screen.blit(small_font.render(f"Job state: {self.job_state}", True, (250, 80, 100)), (900, 0))
    

        self.draw_dashboard()
        self.draw_minimap()  # Draw the minimap

        pygame.display.flip()

    def draw_dashboard(self):

        dash_rect = pygame.Rect(20, self.main.screen.get_height() - 140, 240, 120)
        dash_bg_rect = dash_rect.inflate(24, 32)

        # Scale and draw PNG background for dashboard
        dashboard_bg_scaled = pygame.transform.scale(self.dashboard_bg_img, (dash_bg_rect.width, dash_bg_rect.height))
        self.main.screen.blit(dashboard_bg_scaled, dash_bg_rect.topleft)

        # Center area for content inside the dashboard background
        center_x = dash_bg_rect.x + dash_bg_rect.width // 2

        # === Speed Display ===
        speed_display = int(abs(self.car.speed * 5))
        speed_text = f"{speed_display} km/h"
        fuel_label = "Fuel"

        font_speed = pygame.font.Font(self.font_path, 36)
        font_fuel = pygame.font.Font(self.font_path, 24)

        # Render text surfaces and their shadows
        speed_surface = font_speed.render(speed_text, True, (255, 255, 255))
        speed_shadow = font_speed.render(speed_text, True, (40, 40, 40))
        fuel_surface = font_fuel.render(fuel_label, True, (255, 255, 255))
        fuel_shadow = font_fuel.render(fuel_label, True, (40, 40, 40))

        # Calculate vertical positions for centering
        total_height = speed_surface.get_height() + 8 + fuel_surface.get_height() + 8 + 30  # 30 for fuel gauge
        start_y = dash_bg_rect.y + (dash_bg_rect.height - total_height) // 2

        # Speed text centered
        speed_x = center_x - speed_surface.get_width() // 2
        speed_y = start_y
        self.main.screen.blit(speed_shadow, (speed_x + 2, speed_y + 2))
        self.main.screen.blit(speed_surface, (speed_x, speed_y))

        # Fuel label centered
        fuel_x = center_x - fuel_surface.get_width() // 2
        fuel_y = speed_y + speed_surface.get_height() + 8
        self.main.screen.blit(fuel_shadow, (fuel_x + 2, fuel_y + 2))
        self.main.screen.blit(fuel_surface, (fuel_x, fuel_y))

        # Fuel gauge centered under the fuel label
        blocks = 5
        block_width = 20
        block_height = 30
        spacing = 5
        gauge_width = blocks * block_width + (blocks - 1) * spacing
        gauge_x = center_x - gauge_width // 2
        gauge_y = fuel_y + fuel_surface.get_height() + 8

        fuel_level = max(0, min(self.car.fuel, 100))
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

            rect = pygame.Rect(gauge_x + i * (block_width + spacing), gauge_y, block_width, block_height)
            pygame.draw.rect(self.main.screen, color, rect)
            pygame.draw.rect(self.main.screen, (255, 255, 255), rect, 2)

        if self.brake_pressed:
            pygame.draw.rect(self.main.screen, (200, 0, 0), (dash_rect.x + 10, dash_rect.bottom - 25, 80, 20))
            self._draw_text("BRAKE", dash_rect.x + 15, dash_rect.bottom - 24, (0, 0, 0), size=20)

        # Draw only the red "P" in a circle in the dashboard if handbrake is active
        if self.car.is_handbraking():
            circle_x = dash_rect.right - 30
            circle_y = dash_rect.y + 30
            pygame.draw.circle(self.main.screen, (200, 0, 0), (circle_x, circle_y), 16)
            font_p = pygame.font.Font(self.font_path, 24)
            p_surface = font_p.render("P", True, (255, 255, 255))
            p_shadow = font_p.render("P", True, (40, 40, 40))
            px = circle_x - p_surface.get_width() // 2
            py = circle_y - p_surface.get_height() // 2
            self.main.screen.blit(p_shadow, (px + 2, py + 2))
            self.main.screen.blit(p_surface, (px, py))

        # === Display Cash ===
        cash_text = f"${self.money}"
        font_cash = pygame.font.Font(self.font_path, 36)

        cash_surface = font_cash.render(cash_text, True, (255, 255, 255))
        cash_shadow = font_cash.render(cash_text, True, (40, 40, 40))

        cash_x = 20
        cash_y = 20

        self.main.screen.blit(cash_shadow, (cash_x + 2, cash_y + 2))
        self.main.screen.blit(cash_surface, (cash_x, cash_y))


    def draw_minimap(self):
        """Displays the minimap in the bottom right corner and highlights the car position, pickup and delivery locations."""
        scale = self.minimap_scale
        minimap = self.minimap_surface.copy()
        car_x = int(self.car.pos.x / self.tile_size * scale)
        car_y = int(self.car.pos.y / self.tile_size * scale)
        pygame.draw.circle(minimap, (255, 0, 0), (car_x, car_y), max(3, int(3 * scale)))

        # Draw pickup and delivery locations if job exists
        if self.current_job is not None:
            if self.job_state == "pickup":
                # Show pickup location (blue dot) only if still in pickup phase
                px, py = self.current_job.pickup_tile_loc
                pickup_x = int(px * scale)
                pickup_y = int(py * scale)
                pygame.draw.circle(minimap, (0, 120, 255), (pickup_x, pickup_y), max(3, int(3 * scale)))

            # Always show delivery location (green dot) while job exists
            dx, dy = self.current_job.delivery_tile_loc
            delivery_x = int(dx * scale)
            delivery_y = int(dy * scale)
            pygame.draw.circle(minimap, (0, 200, 0), (delivery_x, delivery_y), max(3, int(3 * scale)))

        minimap_rect = minimap.get_rect()
        minimap_rect.x = self.main.screen.get_width() - minimap_rect.width - 40
        minimap_rect.y = self.main.screen.get_height() - minimap_rect.height - 40

        # Draw a colored filled rectangle with border (same color as text PLAY in menu)
        border_color = (252, 186, 3)
        border_rect = minimap_rect.inflate(16, 16)
        pygame.draw.rect(self.main.screen, border_color, border_rect, border_radius=12)
        pygame.draw.rect(self.main.screen, border_color, border_rect, width=6, border_radius=12)

        # Center minimap inside the border
        minimap_center_x = border_rect.x + (border_rect.width - minimap_rect.width) // 2
        minimap_center_y = border_rect.y + (border_rect.height - minimap_rect.height) // 2
        self.main.screen.blit(minimap, (minimap_center_x, minimap_center_y))

    def tile_to_world(self, tile_pos):
        x, y = tile_pos
        return pygame.Vector2(x * self.tile_size + self.tile_size // 2, y * self.tile_size + self.tile_size // 2)

    def is_at_tile(self, tile_pos, radius=50):
        world_pos = self.tile_to_world(tile_pos)
        return self.car.pos.distance_to(world_pos) <= radius


    def _draw_text(self, text, x, y, color=(255, 255, 255), size=36):
        # Use Kenney_Future font for all text
        font = pygame.font.Font(self.font_path, size)
        surface = font.render(text, True, color)
        self.main.screen.blit(surface, (x, y))
