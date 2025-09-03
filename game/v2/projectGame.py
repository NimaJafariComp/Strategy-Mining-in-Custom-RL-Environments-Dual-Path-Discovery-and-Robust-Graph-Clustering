import pygame
import sys
import random
import json
import os
import pytmx

#static layouts 
STATIC_LAYOUT = {
    "player": (5, 5),
    "keys": [
        {"pos": (3, 7), "color": "blue"},
    ],
    "explosives": [
        {"pos": (7, 8), "color": "red"},
        {"pos": (14, 4), "color": "red"},
    ],
    "doors": [
        {"pos": (6, 5), "color": "blue"},
    ],
    "rocks": [
        {"pos": (8, 9), "color": "red"},
        {"pos": (8, 12), "color": "red"}
    ],
    "coins": [
        (2, 3), (4, 4), (6, 6)
    ]
}

# Initialize Pygame
pygame.init()

# Screen dimensions and settings
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Game Title")

# Load the Tiled map
tmx_data = pytmx.load_pygame(r'C:\Users\nimam\Desktop\untitled.tmx')
# Check if the map has loaded correctly
if tmx_data:
    print("Map loaded successfully!")
    visible_layers = list(tmx_data.layers)
    print(f"Number of layers: {len(visible_layers)}")
else:
    print("Failed to load the map.")

# Lazy image loader
script_dir = os.path.dirname(__file__)
def load_image(path):
    image_path = os.path.join(script_dir, path)
    image = pygame.image.load(image_path).convert_alpha()
    return pygame.transform.smoothscale(image, (int(41.6 * 1), int(41.6 * 1)))

# Now import other modules
from item import Key, Explosive
from player import Player
from interactable import Door, Rock
from coin import Coin

# Constants
FPS = 60
INTERACTION_DISTANCE = 40  # Distance for interactions
SCALING_FACTOR = 1.2
# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)  # Highlight selected item
RED = (255, 0, 0)    # Quit button color

# Sprite groups
all_sprites = pygame.sprite.Group()
items = pygame.sprite.Group()
doors = pygame.sprite.Group()
rocks = pygame.sprite.Group()
coins = pygame.sprite.Group()


# Clock
clock = pygame.time.Clock()

# Player data for logging
player_data = []

import os

# Function to save player data
def save_player_data():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create a "game_data" folder within the script's directory
    save_directory = os.path.join(script_dir, "game_data")
    os.makedirs(save_directory, exist_ok=True)
    
    # Save the data to the file
    save_path = os.path.join(save_directory, "player_data.json")
    with open(save_path, "w") as f:
        json.dump(player_data, f, indent=4)
        

def save_screenshot():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create a "game_data" folder within the script's directory
    save_directory = os.path.join(script_dir, "game_data")
    os.makedirs(save_directory, exist_ok=True)
    # Get the next screenshot index
    index = 1
    while True:
        screenshot_name = os.path.join(save_directory, f"screenshot{index}.png")
        if not os.path.exists(screenshot_name):
            break
        index += 1

    # Capture the screen
    pygame.image.save(pygame.display.get_surface(), screenshot_name)
    print(f"Screenshot saved as {screenshot_name}")
        
        

def is_tile_occupied(x, y, layer_index):
    """Check if the given tile is occupied (not empty)."""
    return tmx_data.get_tile_gid(x, y, layer_index) != 0


def can_place_in_tight_path(x, y, layer_index):
    """Check if rocks and doors can be placed in a tight path."""
    # Check left and right tiles
    left_occupied = is_tile_occupied(x - 1, y, layer_index)
    right_occupied = is_tile_occupied(x + 1, y, layer_index)

    # Check top and bottom tiles
    top_occupied = is_tile_occupied(x, y - 1, layer_index)
    bottom_occupied = is_tile_occupied(x, y + 1, layer_index)

    # Return True if either left/right or top/bottom are occupied
    return (left_occupied and right_occupied) or (top_occupied and bottom_occupied)
        

# Function to generate random positions
def random_position(sprite_width, sprite_height):
    x = random.randint(0, SCREEN_WIDTH - sprite_width)
    y = random.randint(0, SCREEN_HEIGHT - sprite_height)
    return x, y

def init_game_objects():
    for x, y, gid in tmx_data.layers[0]:
        if gid:  # If there's a tile
            pygame.draw.rect(screen, (255, 0, 0, 100), 
                             pygame.Rect(x * tmx_data.tilewidth, y * tmx_data.tileheight, 
                                         tmx_data.tilewidth, tmx_data.tileheight))

    print("Map width:", tmx_data.width)
    print("Map height:", tmx_data.height)
    
    # List visible layers for debugging
    for layer in tmx_data.visible_layers:
        print("Layer name:", layer.name)

    global player
    # Create player
    player_spawned = False
    layer_index = 0  # Since you have only one layer
    while not player_spawned:
        # Randomly select a tile coordinate
        x = random.randint(0, tmx_data.width - 1)
        y = random.randint(0, tmx_data.height - 1)
        # Check if the tile is empty (no tile means it's walkable)
        if tmx_data.get_tile_gid(x, y, layer_index) == 0:  # Use layer index
            # Calculate scaled position
            player_x = (x * tmx_data.tilewidth)
            player_y = (y * tmx_data.tileheight)
            player = Player(player_x * SCALING_FACTOR, player_y * SCALING_FACTOR)
            all_sprites.add(player)
            player_spawned = True
            

    # Spawn 3 keys
    key_images = {
    "blue": load_image("key_blue.png"),
    "red": load_image("key_red.png"),
    "green": load_image("key_green.png"),
    "purple": load_image("key_purple.png")
    }
    keys_spawned = 0
    while keys_spawned < 5:
        key_x = random.randint(0, tmx_data.width - 1)
        key_y = random.randint(0, tmx_data.height - 1)
        if tmx_data.get_tile_gid(key_x, key_y, layer_index) == 0:  # Check for empty tile
            key_position_x = key_x * tmx_data.tilewidth
            key_position_y = key_y * tmx_data.tileheight
    
            # Choose a random color
            key_color = random.choice(list(key_images.keys()))
            key_image = key_images[key_color]
            
            key = Key(key_position_x * SCALING_FACTOR, key_position_y * SCALING_FACTOR, key_image, "key", 1, key_color)
            items.add(key)
            all_sprites.add(key)
            keys_spawned += 1  # Increase count

    # Spawn 3 explosives
    explosive_image = load_image("explosive.png")
    explosives_spawned = 0
    while explosives_spawned < 5:
        explosive_x = random.randint(0, tmx_data.width - 1)
        explosive_y = random.randint(0, tmx_data.height - 1)
        if tmx_data.get_tile_gid(explosive_x, explosive_y, layer_index) == 0:
            explosive_position_x = explosive_x * tmx_data.tilewidth
            explosive_position_y = explosive_y * tmx_data.tileheight
            explosive = Explosive(explosive_position_x * SCALING_FACTOR, explosive_position_y * SCALING_FACTOR, explosive_image, "explosive", 4, "red")
            items.add(explosive)
            all_sprites.add(explosive)
            explosives_spawned += 1  # Increase count

    # Spawn 3 doors
    door_images = {
    "blue": load_image("blue_door.png"),
    "red": load_image("red_door.png"),
    "green": load_image("green_door.png"),
    "purple": load_image("purple_door.png")
    }
    doors_spawned = 0
    while doors_spawned < 4:
        door_x = random.randint(0, tmx_data.width - 1)
        door_y = random.randint(0, tmx_data.height - 1)
        if tmx_data.get_tile_gid(door_x, door_y, layer_index) == 0 and can_place_in_tight_path(door_x, door_y, layer_index):
            door_position_x = door_x * tmx_data.tilewidth
            door_position_y = door_y * tmx_data.tileheight

            # Choose a random color
            door_color = random.choice(list(door_images.keys()))
            door_image = door_images[door_color]

            door = Door(door_position_x * SCALING_FACTOR, door_position_y * SCALING_FACTOR, door_image, door_color, "door")
            doors.add(door)
            all_sprites.add(door)
            doors_spawned += 1  # Increase count

    # Spawn 3 rocks
    rocks_spawned = 0
    while rocks_spawned < 4:
        rock_x = random.randint(0, tmx_data.width - 1)
        rock_y = random.randint(0, tmx_data.height - 1)
        if tmx_data.get_tile_gid(rock_x, rock_y, layer_index) == 0 and can_place_in_tight_path(rock_x, rock_y, layer_index):
            rock_position_x = rock_x * tmx_data.tilewidth
            rock_position_y = rock_y * tmx_data.tileheight
            rock = Rock(rock_position_x * SCALING_FACTOR, rock_position_y * SCALING_FACTOR, load_image("rock.png"), "red", "rock")
            rocks.add(rock)
            all_sprites.add(rock)
            rocks_spawned += 1  # Increase count
    
    #spawn coins
    coins_spawned = 0
    while coins_spawned < 6:
        coin_x = random.randint(0, tmx_data.width - 1)
        coin_y = random.randint(0, tmx_data.height - 1)
        if tmx_data.get_tile_gid(coin_x, coin_y, layer_index) == 0 and can_place_in_tight_path(coin_x, coin_y, layer_index):
            coin_position_x = coin_x * tmx_data.tilewidth
            coin_position_y = coin_y * tmx_data.tileheight
            coin = Coin(coin_position_x * SCALING_FACTOR, coin_position_y * SCALING_FACTOR, load_image("coin_image.png"))
            coins.add(coin)
            all_sprites.add(coin)
            coins_spawned += 1  # Increase count



# Inventory display function
def display_inventory(selected_item):
    font = pygame.font.Font(None, 36)
    inventory_surface = pygame.Surface((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    inventory_surface.fill(WHITE)
    pygame.draw.rect(inventory_surface, BLACK, inventory_surface.get_rect(), 5)  # Add a border
    rect = inventory_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    # Define spacing and starting position
    padding = 10  # Space between items
    x_offset = padding
    y_offset = padding
    item_rects = []  # Track item rectangles for selection
    selected_item_rect = None  # Rectangle for the selected item
    max_items_per_row = (SCREEN_WIDTH // 2 - 2 * padding) // 80  # Calculate how many items can fit in one row

    for i, item in enumerate(player.inventory):
        
        item_image = item.image
        
        if item_image:
            inventory_surface.blit(item_image, (x_offset, y_offset))
            item_rect = pygame.Rect(rect.left + x_offset, rect.top + y_offset, 80, 80)
            item_rects.append((item_rect, item))

            # Draw selection rectangle if this item is selected
            if selected_item == item:
                selected_item_rect = item_rect.copy()  # Store the rect of the selected item

            x_offset += 80 + padding  # Move to the right for the next item
            # Wrap to the next line if the current row is full
            if (i + 1) % max_items_per_row == 0:
                x_offset = padding  # Reset x_offset
                y_offset += 80 + padding  # Move down to the next row

    screen.blit(inventory_surface, rect.topleft)

    # Return the rectangles for items and the selected item rectangle
    return item_rects, selected_item_rect

# Main Menu Function
def main_menu():
    menu_running = True
    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        screen.fill(WHITE)

        # Draw buttons
        font = pygame.font.Font(None, 74)
        start_button = font.render("Start Game", True, BLACK)
        quit_button = font.render("Quit", True, RED)

        # Button positions
        start_button_rect = start_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        quit_button_rect = quit_button.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

        # Draw buttons
        screen.blit(start_button, start_button_rect)
        screen.blit(quit_button, quit_button_rect)

        # Check for mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if start_button_rect.collidepoint(mx, my):
                menu_running = False  # Start the game
                return "start"
            elif quit_button_rect.collidepoint(mx, my):
                pygame.quit()
                sys.exit()

        pygame.display.flip()


def game_loop():
    tilewidth = int(tmx_data.tilewidth * SCALING_FACTOR)
    tileheight = int(tmx_data.tileheight * SCALING_FACTOR)
    player_coin_count = 0
    global player_data
    # Calculate offsets to center the map
    map_width = tmx_data.width * tilewidth
    map_height = tmx_data.height * tileheight
    global offset_x
    global offset_y
    offset_x = (SCREEN_WIDTH - map_width) // 2
    offset_y = (SCREEN_HEIGHT - map_height) // 2

    init_game_objects()

    running = True
    inventory_open = False
    selected_item = None
    item_rects = []  # Store clickable inventory items
    selected_item_rect = None  # Rectangle for the selected item

    quit_button_rect = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 50)  # Adjust the button's position and size
    
    last_position = None  # Track the last logged position
    
    def draw_map():
        
        tile_width = int(tmx_data.tilewidth * SCALING_FACTOR)
        tile_height = int(tmx_data.tileheight * SCALING_FACTOR)
        
        # Draw the map
        for layer in tmx_data.visible_layers:
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    # Scale the tile and blit it to the screen
                    scaled_tile = pygame.transform.scale(tile, (tile_width, tile_height))
                    screen.blit(scaled_tile, (x * tilewidth + offset_x, y * tileheight + offset_y))
    
    def draw_coin_score():
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Coins: {player_coin_count}", True, (184, 134, 11))  # Gold color
        screen.blit(score_text, (30, 30))

                    
                    
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Open inventory with 'V'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    inventory_open = True
                    item_rects, selected_item_rect = display_inventory(selected_item)

                # Close inventory with 'ESC'
                if event.key == pygame.K_ESCAPE and inventory_open:
                    inventory_open = False
                    selected_item = None  # Reset selected item when closing inventory
                    selected_item_rect = None  # Reset selected item rectangle

            # Handle mouse clicks for inventory
            if inventory_open and event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for rect, item in item_rects:
                    if rect.collidepoint(mx, my):
                        selected_item = item  # Store the name of the selected item
                        print(f"Selected {selected_item.color} {selected_item.name} from inventory.")
                        break  # Exit loop after selecting an item

            # Check for quit button click
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if quit_button_rect.collidepoint(mx, my):
                    save_player_data()
                    running = False  # Exit game loop
            
            if event.type == pygame.KEYDOWN:  # Ensure it's a keyboard event
                if event.key == pygame.K_g:
                    print("G key pressed")  # Debugging
                    mods = pygame.key.get_mods()
                    if (mods & pygame.KMOD_CTRL) and (mods & pygame.KMOD_ALT):
                        print("Ctrl + Alt detected")
                        save_screenshot()



        # Get pressed keys
        keys = pygame.key.get_pressed()

        # Update player
        if not inventory_open:# Disable movement when inventory is open
            player.update(keys, tileheight, tilewidth, tmx_data, player_data, rocks)
       
        # Collect items with 'E'
        if not inventory_open and keys[pygame.K_e]:
            collected_items = pygame.sprite.spritecollide(player, items, True)
            collected_coins = pygame.sprite.spritecollide(player, coins, True)
            player_coin_count += len(collected_coins)
            print(player_coin_count)
            for item in collected_items:
                player.pick_up(item)  # Use the new pick_up method
                player_data.append({"event": "collect_item", "item": (item.name, item.color), "position": player.rect.topleft})
            for coin in collected_coins:
                player_data.append({"event": "collect_coin", "name": (coin.name, coin.color), "total_collected": player_coin_count, "position": player.rect.topleft})

        # Interact with doors or rocks with 'F' (when inventory is open)
        if inventory_open and keys[pygame.K_f] and selected_item:  # Use 'F' to interact when inventory is open
            # Check distance to door
            for door in doors:
                if player.rect.colliderect(door.rect.inflate(INTERACTION_DISTANCE, INTERACTION_DISTANCE)):
                    print(f"Interacting with {door.color} door. Selected item: {selected_item.color} {selected_item.name}")
                    if isinstance(selected_item, Key) and selected_item.color == door.color:
                        door.interact(player, selected_item)  # Call interact method on door
                        player_data.append({"event": "interact", "type": "door", "color": door.color, "item": (selected_item.name, selected_item.color), "position": player.rect.topleft})  # Log interaction
                    else:
                        print(f"Failed, door requires a {door.color} key.")
                        player_data.append({"event": "failed_interact", "type": "door", "color": door.color, "item": (selected_item.name, selected_item.color), "position": player.rect.topleft, "reason": "wrong_item"})
                    selected_item = None  # Reset selected item after interaction
                    inventory_open = False  # Close inventory after use
                    break  # Only check one door at a time

            # Check distance to rock
            for rock in rocks:
                if player.rect.colliderect(rock.rect.inflate(INTERACTION_DISTANCE, INTERACTION_DISTANCE)):
                    print(f"Interacting with {rock.color} rock. Selected item: {selected_item.color} {selected_item.name}")
                    if isinstance(selected_item, Explosive) and selected_item.color == rock.color:
                        rock.interact(player, selected_item)  # Call interact method on rock
                        player_data.append({"event": "interact", "type": "rock", "color": rock.color, "item": (selected_item.name, selected_item.color), "position": player.rect.topleft})  # Log interaction
                    else:
                        print(f"Failed, Rock requires an {rock.color} explosive.")
                        player_data.append({"event": "failed_interact", "type": "rock", "color": rock.color, "item": (selected_item.name, selected_item.color), "position": player.rect.topleft, "reason": "wrong_item"})
                    selected_item = None  # Reset selected item after interaction
                    inventory_open = False  # Close inventory after use
                    break  # Only check one rock at a time



        # Draw everything
        screen.fill(WHITE)
        draw_map()  # Call the draw_map function here
        draw_coin_score()

        
        #all_sprites.draw(screen)
        for sprite in all_sprites:
            screen.blit(sprite.image, (sprite.rect.x + offset_x, sprite.rect.y + offset_y))

        # Draw inventory if open
        if inventory_open:
            item_rects, selected_item_rect = display_inventory(selected_item)
            if selected_item_rect:
                pygame.draw.rect(screen, GREEN, selected_item_rect, 5)  # Highlight selected item

        # Draw quit button
        pygame.draw.rect(screen, RED, quit_button_rect)  # Draw quit button
        quit_button_text = pygame.font.Font(None, 36).render("Quit", True, WHITE)
        screen.blit(quit_button_text, (quit_button_rect.x + 10, quit_button_rect.y + 10))

        pygame.display.flip()
        clock.tick(FPS)
        
    save_player_data()
    pygame.quit()

# Main entry point
if __name__ == "__main__":
    main_menu()  # Start with the main menu
    game_loop()  # Then enter the game loop



