import pygame

class Job:
    """A class representing a job."""
    
    def __init__(self, pickup_tile_loc, delivery_tile_loc, is_timed=False, time_limit=None):
        """
        Initializes a job with pickup and delivery tile locations.

        Args:
            pickup_tile_loc (tuple): The tile location for pickup (x, y).
            delivery_tile_loc (tuple): The tile location for delivery (x, y).
            is_timed (bool): Whether the job is a timed job.
            time_limit (float): The number of seconds the player has to complete the job.
        """
        self.pickup_tile_loc = pickup_tile_loc
        self.delivery_tile_loc = delivery_tile_loc
        self.is_timed = is_timed
        self.time_limit = time_limit
        self.time_remaining = time_limit if is_timed else None
        self.completed_in_time = True if is_timed else None 


    def distance(self, tile_size):
        """Calculates the Euclidean distance between pickup and delivery locations in pixels.

        Args:
            tile_size (int): The size of each tile in pixels.

        Returns:
            float: The pixel-based Euclidean distance between pickup and delivery locations.
        """
        px, py = self.pickup_tile_loc
        dx, dy = self.delivery_tile_loc
        pickup_vec = pygame.Vector2(px * tile_size + tile_size // 2, py * tile_size + tile_size // 2)
        delivery_vec = pygame.Vector2(dx * tile_size + tile_size // 2, dy * tile_size + tile_size // 2)
        return pickup_vec.distance_to(delivery_vec)
