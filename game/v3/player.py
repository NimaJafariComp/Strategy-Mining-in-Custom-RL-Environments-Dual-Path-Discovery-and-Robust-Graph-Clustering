import pygame
from utils import is_walkable

# Lazy image loader
def load_image(path, size):
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.smoothscale(image, size)

class Player(pygame.sprite.Sprite):
    player_image = None  # Class-level attribute to store the player image

    def __init__(self, x, y):
        if Player.player_image is None:
            Player.player_image = load_image("cb.png", (50, 50))
        super().__init__()
        self.image = Player.player_image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 5
        self.last_position = (x, y)
        self.MOVEMENT_THRESHOLD = 2
        self.inventory = []
        self.current_weight = 0  # Track the current weight of the inventory
        self.max_weight = 9999  # Set maximum weight player can carry

    def can_pick_up(self, item):
        """Check if the player can pick up the item without exceeding max weight."""
        return self.current_weight + item.weight <= self.max_weight

    def pick_up(self, item):
        """Add item to inventory if it does not exceed weight limit."""
        if self.can_pick_up(item):
            self.inventory.append(item)
            self.current_weight += item.weight
            print(f"Picked up {item.color} {item.name}. Current weight: {self.current_weight}/{self.max_weight}")
        else:
            print(f"Cannot pick up {item.color} {item.name}. Exceeds weight limit!")

    def update(self, keys, tileheight, tilewidth, tmx_data, player_data, rocks):
        """Update player movement based on key input and ensure exact tile stepping."""
        move_dir = None
        if keys[pygame.K_w]:  # Up
            move_dir = (0, -1)
        elif keys[pygame.K_s]:  # Down
            move_dir = (0, 1)
        elif keys[pygame.K_a]:  # Left
            move_dir = (-1, 0)
        elif keys[pygame.K_d]:  # Right
            move_dir = (1, 0)

        if move_dir:
            dx_tile, dy_tile = move_dir
            new_tile_x = (self.rect.x // tilewidth) + dx_tile
            new_tile_y = (self.rect.y // tileheight) + dy_tile

            if is_walkable(tmx_data, new_tile_x, new_tile_y, rocks):
                self.rect.x = new_tile_x * tilewidth
                self.rect.y = new_tile_y * tileheight

                current_tile = (new_tile_x, new_tile_y)
                if current_tile != self.last_position:
                    player_data.append({
                        "event": "move",
                        "tile": current_tile
                    })
                    self.last_position = current_tile
                    print(f"Moved to tile {current_tile}")

    
    def update_rl(self, action, tileheight, tilewidth, tmx_data, player_data, rocks):
        dx_tile, dy_tile = 0, 0

        if action == 0:      # Up
            dy_tile = -1
        elif action == 1:    # Down
            dy_tile = 1
        elif action == 2:    # Left
            dx_tile = -1
        elif action == 3:    # Right
            dx_tile = 1
        else:
            return

        # Calculate new tile position
        current_tile_x = self.rect.x // tilewidth
        current_tile_y = self.rect.y // tileheight
        new_tile_x = current_tile_x + dx_tile
        new_tile_y = current_tile_y + dy_tile

        # Only move if destination is walkable
        if is_walkable(tmx_data, new_tile_x, new_tile_y, rocks):
            self.rect.x = new_tile_x * tilewidth
            self.rect.y = new_tile_y * tileheight

            current_tile = (new_tile_x, new_tile_y)
            if current_tile != self.last_position:
                player_data.append({
                    "event": "move",
                    "tile": current_tile
                })
                self.last_position = current_tile


