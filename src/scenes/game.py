import pygame
import os
import math
import random
from car_sprite import CarSprite
from tiles import tile_dict
from job import Job
from entities.passenger import Passenger
from entities.passenger_manager import PassengerManager


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
        self.tank_session = None  # Track refueling session
        self.hunger = 100
        self.max_hunger = 100
        self.is_eating = False
        self.passenger_group = pygame.sprite.Group()
        self.passenger_sprite = None
        self.passenger_visible = False
        self.accepting_jobs = True  # Whether new jobs are generated automatically

        base_path = os.path.dirname(os.path.dirname(__file__))

        # Use the same font as in mainmenu.py and menubutton.py
        self.font_path = os.path.join(base_path, "fonts/Kenney_Future.ttf")
        self.font = pygame.font.Font(self.font_path, 36)
        self.font_small = pygame.font.Font(self.font_path, 24)
        self.small_font = pygame.font.Font(self.font_path, 32)

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

        self.WALKABLE_TILES = [0, 22, 676, 814, 850, 851, 852, 779, 674, 709, 782] # List of ID's of walkable tiles

        self.MAP_WIDTH = len(self.tile_map[0]) * self.tile_size
        self.MAP_HEIGHT = len(self.tile_map) * self.tile_size

        # Find pickup and pump tile locations
        self.pickup_tile_locations = []
        self.pump_tile_locations = []
        self.food_tile_locations = []
        self.service_tile_locations = []
        for y, row in enumerate(self.tile_map):
            for x, tile_id in enumerate(row):
                PICKUP_TILE = 851
                PUMP_TILE = 852
                FOOD_TILE = 814
                SERVICE_TILE = 676
                if tile_id == PICKUP_TILE:
                    self.pickup_tile_locations.append((x, y))
                elif tile_id == PUMP_TILE:
                    self.pump_tile_locations.append((x, y))
                elif tile_id == FOOD_TILE:
                    self.food_tile_locations.append((x, y))
                elif tile_id == SERVICE_TILE:
                    self.service_tile_locations.append((x, y))
        

        self.current_job = None
        self.job_state = None
        self.new_job()

        # === Minimap ===
        self.minimap_scale = 2
        self.minimap_surface = self._create_minimap()

        # Load PNG backgrounds for minimap and dashboard
        self.dashboard_bg_img = pygame.image.load(os.path.join(base_path, "tiles/game/game_board_background.png")).convert_alpha()

        # Load PNG icon for pump (for minimap)
        self.pump_icon_img = pygame.image.load(os.path.join(base_path, "tiles/game/gas-pump-alt.png")).convert_alpha()
        self.pump_icon_img = pygame.transform.scale(self.pump_icon_img, (18, 18))  # Adjust size as needed

        # Load PNG icon for food (for minimap)
        self.food_icon_img = pygame.image.load(os.path.join(base_path, "tiles/game/apple-whole.png")).convert_alpha()
        self.food_icon_img = pygame.transform.scale(self.food_icon_img, (18, 18))  # Adjust size as needed

        self.show_fps = False  # FPS display toggle

        self.passenger_group = pygame.sprite.Group()
        self.passenger_sprite_sheet = pygame.image.load("src/entities/RPG_assets.png").convert_alpha()
        self.passenger_sprite = None
        self.passenger_visible = False

        self.passenger_manager = PassengerManager(self.passenger_sprite_sheet)

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
        self.pending_job = None
        print(f"[JOB] New job created: {locs}")

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

    def is_on_food_tile(self):
        # Returns True if the car is currently on a food tile
        car_tile_x = int(self.car.pos.x) // self.tile_size
        car_tile_y = int(self.car.pos.y) // self.tile_size
        return (car_tile_x, car_tile_y) in self.food_tile_locations

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
        self.passenger_manager.update(dt)

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
                    self.show_fps = not self.show_fps
                elif event.key == pygame.K_RETURN:
                    # Only toggle accepting_jobs on ENTER
                    self.accepting_jobs = not self.accepting_jobs
                    print(f"[JOB] Accepting jobs: {self.accepting_jobs}")
                    # If switched ON and no job, generate new job
                    if self.accepting_jobs and not self.current_job and not self.pending_job:
                        self.new_job()

        camera_x = max(0, min(self.car.pos.x - self.main.WIDTH // 2, self.MAP_WIDTH - self.main.WIDTH))
        camera_y = max(0, min(self.car.pos.y - self.main.HEIGHT // 2, self.MAP_HEIGHT - self.main.HEIGHT))

        keys = pygame.key.get_pressed()
        self.brake_pressed = keys[pygame.K_x]
        self.car.update(self, camera_x, camera_y, keys)
        self.passenger_group.update(dt)

        # === Job Progress Logic ===
        if self.current_job and self.job_state:
            if self.job_state == "pickup":
                # If at pickup location, handbrake is engaged, and car is stopped, switch to dropoff
                if self.is_at_tile(self.current_job.pickup_tile_loc) and self.car.is_handbraking() and abs(self.car.speed) < 0.2:
                    print("[JOB] Passenger picked up.")
                    self.passenger_manager.remove_passenger()
                    self.job_state = "dropoff"

            elif self.job_state == "dropoff":
                # If at delivery location, handbrake is engaged, and car is stopped, complete job and start new one
                if self.is_at_tile(self.current_job.delivery_tile_loc) and self.car.is_handbraking() and abs(self.car.speed) < 0.2:
                    print("[JOB] Passenger dropped off. Job complete.")

                    # Calculate payment
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

                    # Clean up job
                    self.passenger_manager.remove_passenger()
                    self.job_state = None
                    self.current_job = None
                    if self.accepting_jobs:
                        self.new_job()


        # === Passenger Spawning via PassengerManager ===
        if self.job_state == "pickup" and not self.passenger_manager.visible:
            tile_x, tile_y = self.current_job.pickup_tile_loc
            pixel_x = tile_x * self.tile_size
            pixel_y = tile_y * self.tile_size
            self.passenger_manager.start_entry_animation(pixel_x, pixel_y)

        # Refueling logic (now only allowed when no passenger is in the car)
        self.is_refueling = False
        FUEL_PER_DOLLAR = 2.0  # 2 units per $1
        can_refuel = not (self.current_job and self.job_state == "dropoff")

        # --- Refueling session logic ---
        if can_refuel and self.is_on_pump_tile() and self.car.is_handbraking():
            if keys[pygame.K_f]:
                self.is_refueling = True
                if self.tank_session is None:
                    # Start new refueling session
                    self.tank_session = {"fuel_added": 0.0, "cost": 0.0}
                fuel_needed = self.car.max_fuel - self.car.fuel
                max_affordable_fuel = self.money * FUEL_PER_DOLLAR
                fuel_to_add = min(FUEL_PER_DOLLAR * 0.5, fuel_needed, max_affordable_fuel)
                cost = fuel_to_add / FUEL_PER_DOLLAR
                # Only add fuel if enough money and not full and fuel_to_add > 0
                if self.car.fuel < self.car.max_fuel and self.money >= cost and fuel_to_add > 0:
                    self.car.fuel += fuel_to_add
                    self.money -= cost  # Money is deducted immediately for precise control
                    self.tank_session["fuel_added"] += fuel_to_add
                    self.tank_session["cost"] += cost
                # If can't afford next step or no fuel to add, finish session and show animation
                if fuel_to_add <= 0 or self.money < (0.5 / FUEL_PER_DOLLAR):
                    if self.tank_session and self.tank_session["fuel_added"] > 0:
                        self.cash_animations.append({
                            "text": f"-${int(round(self.tank_session['cost']))}",
                            "color": (255, 40, 40),
                            "pos": pygame.Vector2(self.car.pos.x, self.car.pos.y - 80),
                            "alpha": 200,
                            "lifetime": 0.7
                        })
                    self.tank_session = None
            else:
                # F released or not pressed
                if self.tank_session and self.tank_session["fuel_added"] > 0:
                    self.cash_animations.append({
                        "text": f"-${int(round(self.tank_session['cost']))}",
                        "color": (255, 40, 40),
                        "pos": pygame.Vector2(self.car.pos.x, self.car.pos.y - 80),
                        "alpha": 200,
                        "lifetime": 0.7
                    })
                self.tank_session = None
        else:
            # Not on pump or can't refuel
            if self.tank_session and self.tank_session["fuel_added"] > 0:
                self.cash_animations.append({
                    "text": f"-${int(round(self.tank_session['cost']))}",
                    "color": (255, 40, 40),
                    "pos": pygame.Vector2(self.car.pos.x, self.car.pos.y - 80),
                    "alpha": 200,
                    "lifetime": 0.7
                })
            self.tank_session = None

        # If tank is full during refueling, finish session and show animation
        if self.tank_session and self.car.fuel >= self.car.max_fuel and self.tank_session["fuel_added"] > 0:
            self.cash_animations.append({
                "text": f"-${int(round(self.tank_session['cost']))}",
                "color": (255, 40, 40),
                "pos": pygame.Vector2(self.car.pos.x, self.car.pos.y - 80),
                "alpha": 200,
                "lifetime": 0.7
            })
            self.tank_session = None

        # === Hunger logic ===
        if abs(self.car.speed) > 0.1 and self.hunger > 0:
            self.hunger -= 0.012 / 4  # 4x slower than fuel
            self.hunger = max(self.hunger, 0)

        # === Eating logic (now uses F, only if enough money and no customer in car) ===
        self.is_eating = False
        FOOD_PRICE = 20
        can_eat = (
            self.is_on_food_tile()
            and self.car.is_handbraking()
            and self.money >= FOOD_PRICE
            and not (self.current_job and self.job_state == "dropoff")  # No customer in car
        )
        if can_eat and keys[pygame.K_f]:
            if self.hunger < self.max_hunger:
                self.is_eating = True
                self.hunger = self.max_hunger
                self.money -= FOOD_PRICE
                self.cash_animations.append({
                    "text": f"-${FOOD_PRICE}",
                    "color": (255, 40, 40),
                    "pos": pygame.Vector2(self.car.pos.x, self.car.pos.y - 110),
                    "alpha": 200,
                    "lifetime": 0.7
                })

        # === Out of hunger (starvation) ===
        if self.hunger <= 0:
            self.car.speed = 0  # Stop the car
            # Show "STARVED TO DEATH" message in the center of the screen
            message = "STARVED TO DEATH"
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

            pygame.display.flip()
            return  # Skip rest of loop if dead

        # Draw game map
        screen.fill((50, 50, 50))
        for y, row in enumerate(self.tile_map):
            for x, tile_id in enumerate(row):
                pos = (x * self.tile_size - camera_x, y * self.tile_size - camera_y)
                tile_img = self.tile_images.get(tile_id)
                if tile_img and pos[0] > -self.tile_size and pos[0] < self.main.WIDTH and pos[1] > -self.tile_size and pos[1] < self.main.HEIGHT:
                    screen.blit(tile_img, pos)

        self.sprites.draw(screen)

        # Draw FPS only if toggled on
        if self.show_fps:
            fps_text = f"FPS: {self.main.clock.get_fps():.0f}"
            fps_shadow = self.small_font.render(fps_text, True, (40, 40, 40))
            fps_surface = self.small_font.render(fps_text, True, (0, 255, 0))
            screen.blit(fps_shadow, (2, 2))
            screen.blit(fps_surface, (0, 0))

        self.draw_dashboard()
        self.draw_minimap()  # Draw the minimap

        # === ARROW TO CURRENT JOB TARGET ===
        if self.current_job and self.job_state:
            # Set arrow color to yellow (same as PLAY in menu)
            arrow_color = (252, 186, 3)
            if self.job_state == "pickup":
                target_tile = self.current_job.pickup_tile_loc
            else:
                target_tile = self.current_job.delivery_tile_loc

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

        # === REFUEL & FOOD MESSAGES (above dashboard, English, with all conditions) ===
        FUEL_PER_DOLLAR = 2.0
        FOOD_PRICE = 20

        # Refuel message logic
        if self.is_on_pump_tile() and self.car.is_handbraking():
            if self.current_job and self.job_state == "dropoff":
                message = "Cannot refuel – customer in car"
            elif self.car.fuel < self.car.max_fuel:
                if self.money < (0.5 / FUEL_PER_DOLLAR):
                    message = "Not enough money for refueling"
                else:
                    message = "Hold F to refuel"
            else:
                message = None
            if message:
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

        # Food message logic
        if self.is_on_food_tile() and self.car.is_handbraking():
            if self.current_job and self.job_state == "dropoff":
                message = "Cannot eat – customer in car"
            elif self.hunger < self.max_hunger:
                if self.money >= FOOD_PRICE:
                    message = "Hold F to eat"
                else:
                    message = "Not enough money for food"
            else:
                message = None
            if message:
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

        self.passenger_manager.update(dt)
        self.passenger_manager.draw(screen, camera_x, camera_y)

        # Draw the game objects
        self.sprites.draw(screen)
        self.passenger_group.draw(screen)  # Draw the passenger

        # Render car hitbox for debugging
        if False and self.car.collision_points is not None:
            for point in self.car.collision_points:
                point = point - pygame.Vector2(camera_x, camera_y)
                pygame.draw.circle(screen, (240, 0, 0), point, 5)

        pygame.display.flip()

    def draw_dashboard(self):
        """Draws the lower-left dashboard area of the screen, including:
        - Speed display
        - Fuel level bar
        - Handbrake/brake indicators
        - Cash counter and floating cash animations
        """

        dash_rect = pygame.Rect(20, self.main.screen.get_height() - 220, 240, 200)
        dash_bg_rect = dash_rect.inflate(24, 32)

        dashboard_bg_scaled = pygame.transform.scale(self.dashboard_bg_img, (dash_bg_rect.width, dash_bg_rect.height))
        self.main.screen.blit(dashboard_bg_scaled, dash_bg_rect.topleft)

        center_x = dash_bg_rect.x + dash_bg_rect.width // 2

        # === Speed Display ===
        speed_display = int(abs(self.car.speed * 5))
        speed_text = f"{speed_display} km/h"
        fuel_label = "Fuel"
        hunger_label = "Hunger"

        font_speed = pygame.font.Font(self.font_path, 36)
        font_fuel = pygame.font.Font(self.font_path, 24)
        font_hunger = pygame.font.Font(self.font_path, 24)

        # Render text surfaces and their shadows
        speed_surface = font_speed.render(speed_text, True, (255, 255, 255))
        speed_shadow = font_speed.render(speed_text, True, (40, 40, 40))
        fuel_surface = font_fuel.render(fuel_label, True, (255, 255, 255))
        fuel_shadow = font_fuel.render(fuel_label, True, (40, 40, 40))
        hunger_surface = font_hunger.render(hunger_label, True, (255, 255, 255))
        hunger_shadow = font_hunger.render(hunger_label, True, (40, 40, 40))

        # Calculate vertical positions for centering (now with more space)
        total_height = (
            speed_surface.get_height() + 8 +
            fuel_surface.get_height() + 8 + 30 +  # fuel bar
            hunger_surface.get_height() + 8 + 30  # hunger bar
        )
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

        # Hunger label centered
        hunger_x = center_x - hunger_surface.get_width() // 2
        hunger_y = bar_y + bar_height + 8
        self.main.screen.blit(hunger_shadow, (hunger_x + 2, hunger_y + 2))
        self.main.screen.blit(hunger_surface, (hunger_x, hunger_y))

        # === Hunger progress bar ===
        bar_y2 = hunger_y + hunger_surface.get_height() + 8
        hunger_level = max(0, min(self.hunger, 100))
        fill_width = int(bar_width * (hunger_level / 100))

        # Bar background
        pygame.draw.rect(self.main.screen, (60, 60, 60), (bar_x, bar_y2, bar_width, bar_height), border_radius=8)
        # Bar fill (color changes with level)
        if hunger_level > 60:
            fill_color = (0, 200, 200)
        elif hunger_level > 30:
            fill_color = (255, 200, 0)
        else:
            fill_color = (255, 0, 0)
        pygame.draw.rect(self.main.screen, fill_color, (bar_x, bar_y2, fill_width, bar_height), border_radius=8)
        # Bar border
        pygame.draw.rect(self.main.screen, (255, 255, 255), (bar_x, bar_y2, bar_width, bar_height), 2, border_radius=8)

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

        # === Display Customer Status ===
        if self.current_job and self.job_state == "dropoff":
            customer_status = "Customer: IN CAR"
        else:
            customer_status = "Customer: NONE"
        font_cust = pygame.font.Font(self.font_path, 24)
        cust_surface = font_cust.render(customer_status, True, (255, 255, 255))
        cust_shadow = font_cust.render(customer_status, True, (40, 40, 40))
        cust_x = 20
        cust_y = score_y + score_surface.get_height() + 4
        self.main.screen.blit(cust_shadow, (cust_x + 2, cust_y + 2))
        self.main.screen.blit(cust_surface, (cust_x, cust_y))

        # === Display Accepting Jobs Status ===
        jobs_status = "Accepting jobs: ON" if self.accepting_jobs else "Accepting jobs: OFF"
        jobs_color = (252, 186, 3) if self.accepting_jobs else (180, 60, 60)
        font_jobs = pygame.font.Font(self.font_path, 22)
        jobs_surface = font_jobs.render(jobs_status, True, jobs_color)
        jobs_shadow = font_jobs.render(jobs_status, True, (40, 40, 40))
        jobs_x = 20
        jobs_y = cust_y + cust_surface.get_height() + 4
        self.main.screen.blit(jobs_shadow, (jobs_x + 2, jobs_y + 2))
        self.main.screen.blit(jobs_surface, (jobs_x, jobs_y))

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
        """Displays the minimap in the bottom right corner and highlights the car position, current target, and pump/food icons."""
        scale = self.minimap_scale
        minimap = self.minimap_surface.copy()
        car_x = int(self.car.pos.x / self.tile_size * scale)
        car_y = int(self.car.pos.y / self.tile_size * scale)
        pygame.draw.circle(minimap, (255, 0, 0), (car_x, car_y), max(3, int(3 * scale)))

        # Draw pump icons on minimap
        for tx, ty in self.pump_tile_locations:
            icon_x = int(tx * scale - self.pump_icon_img.get_width() // 2)
            icon_y = int(ty * scale - self.pump_icon_img.get_height() // 2)
            minimap.blit(self.pump_icon_img, (icon_x, icon_y))

        # Draw food icons on minimap
        for tx, ty in self.food_tile_locations:
            icon_x = int(tx * scale - self.food_icon_img.get_width() // 2)
            icon_y = int(ty * scale - self.food_icon_img.get_height() // 2)
            minimap.blit(self.food_icon_img, (icon_x, icon_y))

        # Show only the current target (pickup or dropoff)
        if self.current_job is not None and self.job_state:
            tx, ty = self.current_job.pickup_tile_loc if self.job_state == "pickup" else self.current_job.delivery_tile_loc
            color = (252, 186, 3)  # Yellow for both pickup and dropoff
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
