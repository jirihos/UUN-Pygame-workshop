"""
Editor

l - load
q - save

šipky = pohyb kamery
y, x nebo [ a ] = výběr dlaždice
a, d, w, s = posun výběru mezi sloupci a řádky (v tilesetu)
levé tlačítko = kreslení
pravé tlačítko = mazání (tile 0)
"""

import pygame
import os
import sys
from tiles import tile_dict  # použit tiles.py se 35×26 dlaždicemi

# === Inicializace Pygame ===
pygame.init()

# === Konfigurace sprite sheetu ===
SPRITE_TILE_SIZE = 16
TILE_SPACING = 1
TILE_MARGIN = 0

# === Velikost zobrazení ===
TILE_SIZE = 20
VISIBLE_WIDTH = 1600
VISIBLE_HEIGHT = 900
MAP_WIDTH, MAP_HEIGHT = 150, 150

# === Pygame okno ===
screen = pygame.display.set_mode((VISIBLE_WIDTH, VISIBLE_HEIGHT))
pygame.display.set_caption("Tilemap Editor")
font = pygame.font.SysFont(None, 24)

# === Načtení sprite sheetu ===
base_path = os.path.dirname(__file__)
sprite_sheet = pygame.image.load(os.path.join(base_path, "tilemap.png")).convert_alpha()

map_filepath = os.path.join(base_path, "tile_map.txt")

def get_tile(x, y):
    px = TILE_MARGIN + x * (SPRITE_TILE_SIZE + TILE_SPACING)
    py = TILE_MARGIN + y * (SPRITE_TILE_SIZE + TILE_SPACING)
    rect = pygame.Rect(px, py, SPRITE_TILE_SIZE, SPRITE_TILE_SIZE)
    return sprite_sheet.subsurface(rect)

# === Bezpečné načtení dlaždic ===
tile_images = {}
tile_descriptions = {}
coords_to_id = {}
id_to_coords = {}

max_x_tiles = sprite_sheet.get_width() // (SPRITE_TILE_SIZE + TILE_SPACING)
max_y_tiles = sprite_sheet.get_height() // (SPRITE_TILE_SIZE + TILE_SPACING)

for i, (coords, desc) in tile_dict.items():
    x, y = coords
    if 0 <= x < max_x_tiles and 0 <= y < max_y_tiles:
        try:
            tile_images[i] = get_tile(x, y)
            tile_descriptions[i] = desc
            coords_to_id[(x, y)] = i
            id_to_coords[i] = (x, y)
        except ValueError:
            print(f"Výřez mimo rozsah: {i} → ({x}, {y})")
    else:
        print(f"Souřadnice mimo rozsah: {i} → ({x}, {y})")

# === Výběr dlaždice ===
valid_tile_ids = sorted(tile_images.keys())
selected_index = 0
selected_tile = valid_tile_ids[selected_index]

# === Mapa ===
tile_map = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

# === Kamera ===
camera_x = 0
camera_y = 0
camera_speed = 10

# === Hlavní smyčka ===
running = True
while running:
    screen.fill((50, 50, 50))

    # === Pohyb kamery ===
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        camera_x = max(0, camera_x - camera_speed)
    if keys[pygame.K_RIGHT]:
        camera_x = min(MAP_WIDTH * TILE_SIZE - VISIBLE_WIDTH, camera_x + camera_speed)
    if keys[pygame.K_UP]:
        camera_y = max(0, camera_y - camera_speed)
    if keys[pygame.K_DOWN]:
        camera_y = min(MAP_HEIGHT * TILE_SIZE - (VISIBLE_HEIGHT - 40), camera_y + camera_speed)

    # === Vykreslení mapy ===
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            tile_id = tile_map[y][x]
            img = tile_images.get(tile_id)
            if img:
                pos_x = x * TILE_SIZE - camera_x
                pos_y = y * TILE_SIZE - camera_y
                if 0 <= pos_x < VISIBLE_WIDTH and 0 <= pos_y < VISIBLE_HEIGHT - 40:
                    scaled = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                    screen.blit(scaled, (pos_x, pos_y))
                    pygame.draw.rect(screen, (0, 0, 0), (pos_x, pos_y, TILE_SIZE, TILE_SIZE), 1)

    # === GUI panel ===
    pygame.draw.rect(screen, (30, 30, 30), (0, VISIBLE_HEIGHT - 40, VISIBLE_WIDTH, 40))
    desc = tile_descriptions.get(selected_tile, "?")
    label = font.render(f"Vybraná dlaždice: {selected_tile} ({desc}) ←/→, WASD, Q: uložit, L: načíst", True, (255, 255, 255))
    screen.blit(label, (10, VISIBLE_HEIGHT - 30))
    preview_tile = tile_images.get(selected_tile)
    if preview_tile:
        preview = pygame.transform.scale(preview_tile, (TILE_SIZE, TILE_SIZE))
        screen.blit(preview, (VISIBLE_WIDTH - TILE_SIZE - 10, VISIBLE_HEIGHT - TILE_SIZE - 5))

    # === Události ===
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            tx = (mx + camera_x) // TILE_SIZE
            ty = (my + camera_y) // TILE_SIZE
            if 0 <= tx < MAP_WIDTH and 0 <= ty < MAP_HEIGHT:
                if event.button == 1:
                    tile_map[ty][tx] = selected_tile
                elif event.button == 3:
                    tile_map[ty][tx] = 0

        elif event.type == pygame.KEYDOWN:
            # Posun indexu v platných tile ID
            if event.key == pygame.K_y or event.key == pygame.K_LEFTBRACKET:
                selected_index = (selected_index - 1) % len(valid_tile_ids)
                selected_tile = valid_tile_ids[selected_index]
            elif event.key == pygame.K_x or event.key == pygame.K_RIGHTBRACKET:
                selected_index = (selected_index + 1) % len(valid_tile_ids)
                selected_tile = valid_tile_ids[selected_index]

            # Posun po souřadnicích dlaždic
            elif event.key in (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s):
                if selected_tile in id_to_coords:
                    x, y = id_to_coords[selected_tile]
                    if event.key == pygame.K_a:
                        x -= 1
                    elif event.key == pygame.K_d:
                        x += 1
                    elif event.key == pygame.K_w:
                        y -= 1
                    elif event.key == pygame.K_s:
                        y += 1
                    if (x, y) in coords_to_id:
                        selected_tile = coords_to_id[(x, y)]
                        selected_index = valid_tile_ids.index(selected_tile)

            elif event.key == pygame.K_SPACE:
                selected_tile = 0
                selected_index = valid_tile_ids.index(0)

            elif event.key == pygame.K_q:
                with open(map_filepath, "w") as f:
                    for row in tile_map:
                        f.write(",".join(map(str, row)) + "\n")
                print("Mapa uložena jako tile_map.txt")

            elif event.key == pygame.K_l:
                try:
                    with open(map_filepath, "r") as f:
                        tile_map = [list(map(int, line.strip().split(","))) for line in f]
                    MAP_HEIGHT = len(tile_map)
                    MAP_WIDTH = len(tile_map[0]) if MAP_HEIGHT > 0 else 0
                    print("Mapa načtena ze souboru.")
                except Exception as e:
                    print("Chyba při načítání:", e)

    # === Malování při držení tlačítek ===
    mouse_buttons = pygame.mouse.get_pressed()
    if mouse_buttons[0] or mouse_buttons[2]:
        mx, my = pygame.mouse.get_pos()
        if my < VISIBLE_HEIGHT - 40:
            tx = (mx + camera_x) // TILE_SIZE
            ty = (my + camera_y) // TILE_SIZE
            if 0 <= tx < MAP_WIDTH and 0 <= ty < MAP_HEIGHT:
                if mouse_buttons[0]:
                    tile_map[ty][tx] = selected_tile
                elif mouse_buttons[2]:
                    tile_map[ty][tx] = 0

    pygame.display.flip()

pygame.quit()
sys.exit()
