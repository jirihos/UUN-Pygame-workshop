import pygame
import os
import math
import random
from car_sprite import CarSprite
from tiles import tile_dict
from job import Job

class Game:
    """The actual game. Renders the map, HUD, and contains the main game logic.
    
    Handles player input, car movement, job management, and rendering of the game scene.
    Attributes:
        main: Reference to the main controller (provides screen, clock, etc.)
        sprites: Group of all game sprites.
        car: The player's car sprite.
        brake_pressed: Boolean indicating if the brake is pressed.
        money: Player's current cash amount.
        is_refueling: Boolean indicating if the player is currently refueling.
        cash_animations: List of cash animations for floating money effects.
        pending_job: Job that is available to be accepted by the player.
    """

    def __init__(self, main):
        """Initializes the Game object, loads map and resources, sets up the player, 
        and prepares all game logic structures.
        
        Args:
            main: Reference to the main controller (provides screen, clock, etc.)
        """

        self.main = main
        self.sprites = pygame.sprite.Group()
        self.car = CarSprite(400,500)
        self.sprites.add(self.car)
        self.brake_pressed = False
        self.money = 0 
        self.is_refueling = False
        self.cash_animations = []
        self.pending_job = None
        self.customers_served = 0  # Track number of delivered customers (score)

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
            """Returns a tile image from the sprite sheet based on its coordinates.
            
            Args:
                x: The x-coordinate of the tile in the sprite sheet.
                y: The y-coordinate of the tile in the sprite sheet.
            
            Returns:
                A pygame.Surface object representing the tile.
            """

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
            """Loads the tile map from a text file.
            """

            tile_map = []
            with open(path, "r") as f:
                for line in f:
                    row = [int(tile) for tile in line.strip().split(",")]
                    tile_map.append(row)
            return tile_map

        map_filepath = os.path.join(os.path.dirname(base_path), "editor/tile_map.txt")
        self.tile_map = load_tile_map(map_filepath)

        self.WALKABLE_TILES = [0, 22, 814, 850, 851, 852, 779, 674, 709, 782] # List of ID's of walkable tiles

        self.MAP_WIDTH = len(self.tile_map[0]) * self.tile_size
        self.MAP_HEIGHT = len(self.tile_map) * self.tile_size

        # Find pickup and pump tile locations
        self.pickup_tile_locations = []
        self.pump_tile_locations = []
        self.food_tile_locations = []
        for y, row in enumerate(self.tile_map):
            for x, tile_id in enumerate(row):
                PICKUP_TILE = 851
                PUMP_TILE = 852
                FOOD_TILE = 814
                if tile_id == PICKUP_TILE:
                    self.pickup_tile_locations.append((x, y))
                elif tile_id == PUMP_TILE:
                    self.pump_tile_locations.append((x, y))
                elif tile_id == FOOD_TILE:
                    self.food_tile_locations.append((x, y))
        
        self.new_job()

        # === Minimap ===
        self.minimap_scale = 2
        self.minimap_surface = self._create_minimap()

        # Load PNG backgrounds for minimap and dashboard
        self.dashboard_bg_img = pygame.image.load(os.path.join(base_path, "tiles/game/game_board_background.png")).convert_alpha()

        self.show_fps = False  # FPS display toggle

    def new_job(self):
        """Creates a new job by randomly selecting two pickup locations."""

        # If there are not enough pickup locations, do not create a job
        if len(self.pickup_tile_locations) < 2:
            self.current_job = None
            self.job_state = None
            return
        
        # Randomly select two different pickup locations for pickup and delivery
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
        """Determines if a given world coordinate (x, y) is on a walkable tile.

        Args:
            x (float): X coordinate in world space.
            y (float): Y coordinate in world space.

        Returns:
            bool: True if the tile is walkable, otherwise False.
        """

        tile_x = int(x) // self.tile_size
        tile_y = int(y) // self.tile_size
        if 0 <= tile_y < len(self.tile_map) and 0 <= tile_x < len(self.tile_map[0]):
            tile = self.tile_map[tile_y][tile_x]
            return tile in self.WALKABLE_TILES
        return False

    def is_on_pump_tile(self):
        """Checks if the car is currently located on a pump tile.

        Returns:
            bool: True if car is on a pump tile, False otherwise.
        """

        car_tile_x = int(self.car.pos.x) // self.tile_size
        car_tile_y = int(self.car.pos.y) // self.tile_size
        return (car_tile_x, car_tile_y) in self.pump_tile_locations

    def get_nearest_pump_tile(self):
        """Finds the nearest fuel pump to the car's current position.

        Returns:
            pygame.Vector2: World coordinates of the nearest pump tile.
        """
        
        car_pos = self.car.pos
        min_dist = float('inf')
        nearest = None
        for x, y in self.pump_tile_locations:
            pump_pos = pygame.Vector2(x * self.tile_size + self.tile_size // 2, y * self.tile_size + self.tile_size // 2)
            dist = car_pos.distance_to(pump_pos)
            if dist < min_dist:
                min_dist = dist
                nearest = pump_pos
        return nearest

    def loop(self, dt):
        """Runs the main game loop logic for a single frame.
        Handles events, updates game state, renders the game scene and HUD.

        Args:
            dt (float): Time delta since last frame (for smooth updates).
        """

        screen = self.main.screen

        # Handle events (quit, handbrake, menu, FPS toggle, job accept)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.main.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.car.toggle_handbrake()
                elif event.key == pygame.K_ESCAPE:
                    from scenes.mainmenu import MainMenu
                    self.main.current_scene = MainMenu(self.main, skip_intro=True)
                elif event.key == pygame.K_l:
                    self.show_fps = not self.show_fps  # Toggle FPS display
            if self.pending_job and event.key == pygame.K_RETURN:
                self.current_job = self.pending_job
                self.job_state = "pickup"
                self.pending_job = None
                print("[JOB] Accepted new job.")

        # Calculate camera position to center the car
        camera_x = max(0, min(self.car.pos.x - self.main.WIDTH // 2, self.MAP_WIDTH - self.main.WIDTH))
        camera_y = max(0, min(self.car.pos.y - self.main.HEIGHT // 2, self.MAP_HEIGHT - self.main.HEIGHT))

        keys = pygame.key.get_pressed()
        self.brake_pressed = keys[pygame.K_x]
        self.car.update(self, camera_x, camera_y, keys)

        # === Job Progress Logic ===
        if self.current_job and self.job_state:
            if self.job_state == "pickup":
                # If at pickup location, handbrake is engaged, and car is stopped, switch to dropoff
                if self.is_at_tile(self.current_job.pickup_tile_loc) and self.car.is_handbraking() and abs(self.car.speed) < 0.2:
                    print("[JOB] Passenger picked up.")
                    self.job_state = "dropoff"

            elif self.job_state == "dropoff":
                # If at delivery location, handbrake is engaged, and car is stopped, complete job and start new one
                if self.is_at_tile(self.current_job.delivery_tile_loc) and self.car.is_handbraking() and abs(self.car.speed) < 0.2:
                    print("[JOB] Passenger dropped off. Job complete.")
                    base_rate = 0.5  
                    distance = self.current_job.distance(self.tile_size) / 100
                    earned = int(base_rate * distance)
                    self.money += earned
                    self.customers_served += 1  # Increment score
                    self.cash_animations.append({
                        "text":f"+${earned}",
                        "color": (0, 255, 100),  # green for earning
                        "pos": pygame.Vector2(self.car.pos.x, self.car.pos.y - 50),
                        "alpha": 255,
                        "lifetime": 1.0 
                    })

                    if len(self.cash_animations) > 5:
                        self.cash_animations.pop(0)

                    self.new_job()
                    self.job_state = "pickup"  # Immediately set to pickup for the new job

        if self.pending_job and event.key == pygame.K_RETURN:
            self.current_job = self.pending_job
            self.job_state = "pickup"
            self.pending_job = None
            print("[JOB] Accepted new job.")


        # Refueling logic (now only allowed when no passenger is in the car)
        self.is_refueling = False
        FUEL_PRICE = 2  # price per unit of fuel
        can_refuel = not (self.current_job and self.job_state == "dropoff")  # Only allow refuel if not in dropoff phase (no passenger)
        if can_refuel and self.is_on_pump_tile() and self.car.is_handbraking():
            if keys[pygame.K_f]:
                self.is_refueling = True
                fuel_needed = self.car.max_fuel - self.car.fuel
                if self.car.fuel < self.car.max_fuel and self.money >= FUEL_PRICE * 0.5:
                    fuel_to_add = min(0.5, fuel_needed)
                    cost = FUEL_PRICE * fuel_to_add
                    if self.money >= cost:
                        self.car.fuel = min(self.car.fuel + fuel_to_add, self.car.max_fuel)
                        self.money -= cost
                        self.cash_animations.append({
                            "text":f"-${int(cost)}",
                            "color": (255, 40, 40),  # red for spending
                            "pos": pygame.Vector2(self.car.pos.x, self.car.pos.y - 80),
                            "alpha": 200,
                            "lifetime": 0.7 
                        })

        # Draw game map
        screen.fill((50, 50, 50))
        for y, row in enumerate(self.tile_map):
            for x, tile_id in enumerate(row):
                pos = (x * self.tile_size - camera_x, y * self.tile_size - camera_y)
                tile_img = self.tile_images.get(tile_id)
                if tile_img:
                    screen.blit(tile_img, pos)

                # Draw red outline for unwalkable tiles (debug)
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

        # self.current_job debug info (optional)
        # if self.current_job is not None:
        #     screen.blit(small_font.render(f"Pickup tile: {self.current_job.pickup_tile_loc}", True, (250, 80, 100)), (200, 0))
        #     screen.blit(small_font.render(f"Delivery tile: {self.current_job.delivery_tile_loc}", True, (250, 80, 100)), (500, 0))
        #     screen.blit(small_font.render(f"Job state: {self.job_state}", True, (250, 80, 100)), (900, 0))

        self.draw_dashboard()
        self.draw_minimap()  # Draw the minimap

        # === ARROW TO CURRENT JOB TARGET ===
        if self.current_job and self.job_state:
            # Set arrow color to match minimap dot color
            if self.job_state == "pickup":
                target_tile = self.current_job.pickup_tile_loc
                arrow_color = (0, 120, 255)  # Blue for pickup
            else:
                target_tile = self.current_job.delivery_tile_loc
                arrow_color = (0, 200, 0)    # Green for dropoff

            target_pos = self.tile_to_world(target_tile)
            car_screen_x = self.car.pos.x - camera_x
            car_screen_y = self.car.pos.y - camera_y
            target_screen_x = target_pos.x - camera_x
            target_screen_y = target_pos.y - camera_y
            dir_vec = pygame.Vector2(target_screen_x - car_screen_x, target_screen_y - car_screen_y)
            if dir_vec.length() > 1:
                dir_vec = dir_vec.normalize()
                arrow_center = pygame.Vector2(car_screen_x, car_screen_y) + dir_vec * 120
                angle = math.degrees(math.atan2(-dir_vec.y, dir_vec.x))
                arrow_size = 36
                points = [
                    (arrow_center.x + math.cos(math.radians(angle)) * arrow_size,
                     arrow_center.y - math.sin(math.radians(angle)) * arrow_size),
                    (arrow_center.x + math.cos(math.radians(angle + 140)) * (arrow_size // 2),
                     arrow_center.y - math.sin(math.radians(angle + 140)) * (arrow_size // 2)),
                    (arrow_center.x + math.cos(math.radians(angle - 140)) * (arrow_size // 2),
                     arrow_center.y - math.sin(math.radians(angle - 140)) * (arrow_size // 2)),
                ]
                shadow_points = [(x+3, y+3) for x, y in points]
                pygame.draw.polygon(screen, (40, 40, 40), shadow_points)
                pygame.draw.polygon(screen, arrow_color, points)

        # OUT OF FUEL MESSAGE
        if self.car.fuel <= 0:
            # Show "OUT OF FUEL" message in the center of the screen
            message = "OUT OF FUEL"
            font = pygame.font.Font(self.font_path, 64)
            text_color = (255, 255, 255)
            shadow_color = (40, 40, 40)
            text_surface = font.render(message, True, text_color)
            shadow_surface = font.render(message, True, shadow_color)
            screen_rect = self.main.screen.get_rect()
            text_rect = text_surface.get_rect(center=screen_rect.center)
            shadow_rect = text_rect.copy()
            shadow_rect.x += 4
            shadow_rect.y += 4

            bg_width = text_rect.width + 80
            bg_height = text_rect.height + 60
            bg_img = pygame.transform.scale(self.dashboard_bg_img, (bg_width, bg_height))
            bg_rect = bg_img.get_rect(center=screen_rect.center)
            self.main.screen.blit(bg_img, bg_rect)

            self.main.screen.blit(shadow_surface, shadow_rect)
            self.main.screen.blit(text_surface, text_rect)

        # REFUEL MESSAGE
        if can_refuel and self.is_on_pump_tile() and self.car.is_handbraking() and self.car.fuel < self.car.max_fuel:
            # Show "Hold F to refuel" message above the dashboard
            message = "Hold F to refuel"
            font = pygame.font.Font(self.font_path, 40)
            text_color = (255, 255, 255)
            shadow_color = (40, 40, 40)
            text_surface = font.render(message, True, text_color)
            shadow_surface = font.render(message, True, shadow_color)
            screen_rect = self.main.screen.get_rect()
            text_rect = text_surface.get_rect()
            group_center = (screen_rect.centerx, screen_rect.height - 60)
            text_rect.center = group_center
            shadow_rect = text_rect.copy()
            shadow_rect.x += 4
            shadow_rect.y += 4

            bg_width = text_rect.width + 60
            bg_height = text_rect.height + 30
            bg_img = pygame.transform.scale(self.dashboard_bg_img, (bg_width, bg_height))
            bg_rect = bg_img.get_rect()
            bg_rect.center = group_center
            self.main.screen.blit(bg_img, bg_rect)

            self.main.screen.blit(shadow_surface, shadow_rect)
            self.main.screen.blit(text_surface, text_rect)

        # FUEL ARROW TO PUMP
        if 0 < self.car.fuel < 30 and self.pump_tile_locations:
            # Show arrow to nearest pump if fuel is low
            nearest_pump = self.get_nearest_pump_tile()
            if nearest_pump:
                car_screen_x = self.car.pos.x - camera_x
                car_screen_y = self.car.pos.y - camera_y
                # Pump position on screen
                pump_screen_x = nearest_pump.x - camera_x
                pump_screen_y = nearest_pump.y - camera_y
                # Direction vector
                dir_vec = pygame.Vector2(pump_screen_x - car_screen_x, pump_screen_y - car_screen_y)
                if dir_vec.length() > 1:
                    dir_vec = dir_vec.normalize()
                    # Arrow will be 80 pixels from the car towards the pump
                    arrow_center = pygame.Vector2(car_screen_x, car_screen_y) + dir_vec * 80
                    angle = math.degrees(math.atan2(-dir_vec.y, dir_vec.x))
                    # Draw arrow (triangle)
                    arrow_size = 36
                    points = [
                        (arrow_center.x + math.cos(math.radians(angle)) * arrow_size,
                         arrow_center.y - math.sin(math.radians(angle)) * arrow_size),
                        (arrow_center.x + math.cos(math.radians(angle + 140)) * (arrow_size // 2),
                         arrow_center.y - math.sin(math.radians(angle + 140)) * (arrow_size // 2)),
                        (arrow_center.x + math.cos(math.radians(angle - 140)) * (arrow_size // 2),
                         arrow_center.y - math.sin(math.radians(angle - 140)) * (arrow_size // 2)),
                    ]
                    # Draw shadow under the arrow first
                    shadow_points = [(x+3, y+3) for x, y in points]
                    pygame.draw.polygon(screen, (40, 40, 40), shadow_points)
                    # Then draw the red arrow
                    pygame.draw.polygon(screen, (220, 40, 40), points)

        if self.pending_job:
            # Show notification for new job
            self._draw_text("New Job Available! Press ENTER to accept.", 40, 60, (255, 255, 255), size=30)



        pygame.display.flip()

    def draw_dashboard(self):
        """Draws the lower-left dashboard area of the screen, including:
        - Speed display
        - Fuel level bar
        - Handbrake/brake indicators
        - Cash counter and floating cash animations
        """

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

        # === Fuel progress bar ===
        bar_width = 140
        bar_height = 24
        bar_x = center_x - bar_width // 2
        bar_y = fuel_y + fuel_surface.get_height() + 8

        fuel_level = max(0, min(self.car.fuel, 100))
        fill_width = int(bar_width * (fuel_level / 100))

        # Bar background
        pygame.draw.rect(self.main.screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=8)
        # Bar fill (color changes with level)
        if fuel_level > 60:
            fill_color = (0, 200, 0)
        elif fuel_level > 30:
            fill_color = (255, 200, 0)
        else:
            fill_color = (255, 0, 0)
        pygame.draw.rect(self.main.screen, fill_color, (bar_x, bar_y, fill_width, bar_height), border_radius=8)
        # Bar border
        pygame.draw.rect(self.main.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=8)

        if self.brake_pressed:
            # Show brake indicator if brake is pressed
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
        cash_text = f"${int(self.money)}"
        font_cash = pygame.font.Font(self.font_path, 36)

        cash_surface = font_cash.render(cash_text, True, (255, 255, 255))
        cash_shadow = font_cash.render(cash_text, True, (40, 40, 40))

        cash_x = 20
        cash_y = 20

        self.main.screen.blit(cash_shadow, (cash_x + 2, cash_y + 2))
        self.main.screen.blit(cash_surface, (cash_x, cash_y))

        # === Display Score (Customers Served) ===
        score_text = f"Score: {self.customers_served}"
        font_score = pygame.font.Font(self.font_path, 28)
        score_surface = font_score.render(score_text, True, (252, 186, 3))
        score_shadow = font_score.render(score_text, True, (40, 40, 40))
        score_x = 20
        score_y = cash_y + cash_surface.get_height() + 8
        self.main.screen.blit(score_shadow, (score_x + 2, score_y + 2))
        self.main.screen.blit(score_surface, (score_x, score_y))

        # === Floating Money Animation ===
        for anim in self.cash_animations[:]:
            font_float = pygame.font.Font(self.font_path, 28)
            # Use color from animation dict, fallback to green if not present
            color = anim.get("color", (0, 255, 100))
            surface = font_float.render(anim["text"], True, color)
            surface.set_alpha(anim["alpha"])
            screen_x = anim["pos"].x - self.car.pos.x + self.main.WIDTH // 2
            screen_y = anim["pos"].y - self.car.pos.y + self.main.HEIGHT // 2
            self.main.screen.blit(surface, (screen_x, screen_y))

            # Animate upward
            anim["pos"].y -= 0.5
            anim["lifetime"] -= 1 / 60
            anim["alpha"] = max(0, int(anim["alpha"] - 5))

            if anim["lifetime"] <= 0 or anim["alpha"] <= 0:
                self.cash_animations.remove(anim)

    def draw_minimap(self):
        """Displays the minimap in the bottom right corner and highlights the car position and current target only."""
        
        scale = self.minimap_scale
        minimap = self.minimap_surface.copy()
        car_x = int(self.car.pos.x / self.tile_size * scale)
        car_y = int(self.car.pos.y / self.tile_size * scale)
        pygame.draw.circle(minimap, (255, 0, 0), (car_x, car_y), max(3, int(3 * scale)))

        # Show only the current target (pickup or dropoff)
        if self.current_job is not None and self.job_state:
            if self.job_state == "pickup":
                tx, ty = self.current_job.pickup_tile_loc
                color = (0, 120, 255)  # Blue for pickup
            else:
                tx, ty = self.current_job.delivery_tile_loc
                color = (0, 200, 0)    # Green for dropoff
            target_x = int(tx * scale)
            target_y = int(ty * scale)
            pygame.draw.circle(minimap, color, (target_x, target_y), max(4, int(4 * scale)))

        minimap_rect = minimap.get_rect()
        minimap_rect.x = self.main.screen.get_width() - minimap_rect.width - 40
        minimap_rect.y = self.main.screen.get_height() - minimap_rect.height - 40

        # Draw a colored filled rectangle with border (same color as PLAY in menu)
        border_color = (252, 186, 3)
        border_rect = minimap_rect.inflate(16, 16)
        pygame.draw.rect(self.main.screen, border_color, border_rect, border_radius=12)
        pygame.draw.rect(self.main.screen, border_color, border_rect, width=6, border_radius=12)

        # Center minimap inside the border
        minimap_center_x = border_rect.x + (border_rect.width - minimap_rect.width) // 2
        minimap_center_y = border_rect.y + (border_rect.height - minimap_rect.height) // 2
        self.main.screen.blit(minimap, (minimap_center_x, minimap_center_y))

    def tile_to_world(self, tile_pos):
        """Converts tile coordinates (x, y) into pixel-based world coordinates.

        Args:
            tile_pos (tuple[int, int]): The (x, y) tile position.

        Returns:
            pygame.Vector2: World coordinates at the tile center.
        """

        x, y = tile_pos
        return pygame.Vector2(x * self.tile_size + self.tile_size // 2, y * self.tile_size + self.tile_size // 2)

    def is_at_tile(self, tile_pos, radius=50):
        """Checks if the car is within a certain radius of the center of a specific tile.

        Args:
            tile_pos (tuple[int, int]): Tile coordinates (x, y).
            radius (float): Maximum distance to consider "at tile".

        Returns:
            bool: True if the car is within the radius of the tile center.
        """

        world_pos = self.tile_to_world(tile_pos)
        return self.car.pos.distance_to(world_pos) <= radius

    def _draw_text(self, text, x, y, color=(255, 255, 255), size=36):
        """Utility function to render and draw text on the screen at a given position.

        Args:
            text (str): The text to render.
            x (int): X position.
            y (int): Y position.
            color (tuple[int, int, int], optional): RGB color. Defaults to white.
            size (int, optional): Font size. Defaults to 36.
        """

        # Use Kenney_Future font for all text
        font = pygame.font.Font(self.font_path, size)
        surface = font.render(text, True, color)
        self.main.screen.blit(surface, (x, y))
