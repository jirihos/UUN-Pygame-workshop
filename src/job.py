import pygame

class Job:
    def __init__(self, pickup_tile_loc, delivery_tile_loc):
        self.pickup_tile_loc = pickup_tile_loc
        self.delivery_tile_loc = delivery_tile_loc

    def distance(self, tile_size):
        # Returns pixel-based Euclidean distance between pickup and dropoff
        px, py = self.pickup_tile_loc
        dx, dy = self.delivery_tile_loc
        pickup_vec = pygame.Vector2(px * tile_size + tile_size // 2, py * tile_size + tile_size // 2)
        delivery_vec = pygame.Vector2(dx * tile_size + tile_size // 2, dy * tile_size + tile_size // 2)
        return pickup_vec.distance_to(delivery_vec)
