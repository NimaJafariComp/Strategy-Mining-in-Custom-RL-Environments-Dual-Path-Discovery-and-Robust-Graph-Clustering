import pygame
import pytmx
SCALING_FACTOR = 1.2
def is_walkable(tmx_data, tile_x, tile_y, rocks):
    """
    tmx_data: pytmx.TiledMap
    tile_x, tile_y: integer tile coordinates
    rocks: iterable of rock sprites
    """
    # 1) Out of bounds
    if tile_x < 0 or tile_y < 0 or tile_x >= tmx_data.width or tile_y >= tmx_data.height:
        return False

    # 2) Rock collision
    tw = int(tmx_data.tilewidth * SCALING_FACTOR)
    th = int(tmx_data.tileheight * SCALING_FACTOR)
    for rock in rocks:
        rx = rock.rect.centerx // tw
        ry = rock.rect.centery  // th
        if rx == tile_x and ry == tile_y:
            return False

    # 3) Floor collision: only gid==0 is empty/unwalkable
    #    your map’s floor layer should have gid>0 for actual floor tiles
    gid = tmx_data.get_tile_gid(tile_x, tile_y, 0)  # layer 0
    if gid == 0:
        return True

    return False



