"""
Map generator for TankWars Single-Player Campaign
Creates procedural level maps as PNG images
"""

import os

try:
    from PIL import Image
except ImportError:
    # Fallback - try pygame
    import pygame
    pygame.init()
    USE_PYGAME = True
else:
    USE_PYGAME = False

# Map dimensions (in tiles)
MAP_WIDTH = 39   # 1170 / 30
MAP_HEIGHT = 17  # 510 / 30

# Colors
WALL = (255, 0, 0)      # Red = wall
FLOOR = (100, 100, 100)  # Gray = floor


def create_map_image(width, height):
    """Create a blank map image"""
    if USE_PYGAME:
        return pygame.Surface((width, height))
    else:
        return Image.new('RGB', (width, height), FLOOR)


def set_pixel(img, x, y, color):
    """Set a pixel in the image"""
    if USE_PYGAME:
        img.set_at((x, y), color)
    else:
        img.putpixel((x, y), color)


def save_image(img, path):
    """Save image to file"""
    if USE_PYGAME:
        pygame.image.save(img, path)
    else:
        img.save(path)


def add_border(img):
    """Add border walls around the map"""
    for x in range(MAP_WIDTH):
        set_pixel(img, x, 0, WALL)
        set_pixel(img, x, MAP_HEIGHT - 1, WALL)
    for y in range(MAP_HEIGHT):
        set_pixel(img, 0, y, WALL)
        set_pixel(img, MAP_WIDTH - 1, y, WALL)


def add_horizontal_wall(img, y, x_start, x_end):
    """Add a horizontal wall"""
    for x in range(x_start, x_end + 1):
        if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
            set_pixel(img, x, y, WALL)


def add_vertical_wall(img, x, y_start, y_end):
    """Add a vertical wall"""
    for y in range(y_start, y_end + 1):
        if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
            set_pixel(img, x, y, WALL)


def add_box(img, x, y, width, height):
    """Add a rectangular box wall"""
    for dx in range(width):
        for dy in range(height):
            if 0 <= x + dx < MAP_WIDTH and 0 <= y + dy < MAP_HEIGHT:
                set_pixel(img, x + dx, y + dy, WALL)


def generate_desert_1():
    """Level 1: Desert Outpost - Simple open layout"""
    img = create_map_image(MAP_WIDTH, MAP_HEIGHT)
    if not USE_PYGAME:
        img.paste(FLOOR, (0, 0, MAP_WIDTH, MAP_HEIGHT))
    add_border(img)

    # Few scattered obstacles
    add_box(img, 12, 4, 2, 3)
    add_box(img, 12, 10, 2, 3)
    add_box(img, 25, 6, 3, 2)
    add_box(img, 25, 10, 3, 2)

    return img


def generate_desert_2():
    """Level 2: Desert Fortress - More cover"""
    img = create_map_image(MAP_WIDTH, MAP_HEIGHT)
    if not USE_PYGAME:
        img.paste(FLOOR, (0, 0, MAP_WIDTH, MAP_HEIGHT))
    add_border(img)

    # Central barrier
    add_vertical_wall(img, 19, 4, 12)

    # Side obstacles
    add_box(img, 8, 3, 2, 2)
    add_box(img, 8, 12, 2, 2)
    add_box(img, 28, 5, 3, 3)
    add_box(img, 28, 9, 3, 3)

    return img


def generate_city_1():
    """Level 3: Urban Warfare - Building blocks"""
    img = create_map_image(MAP_WIDTH, MAP_HEIGHT)
    if not USE_PYGAME:
        img.paste(FLOOR, (0, 0, MAP_WIDTH, MAP_HEIGHT))
    add_border(img)

    # Buildings
    add_box(img, 6, 2, 4, 4)
    add_box(img, 6, 11, 4, 4)

    add_box(img, 16, 5, 3, 3)
    add_box(img, 16, 9, 3, 3)

    add_box(img, 26, 2, 5, 3)
    add_box(img, 26, 12, 5, 3)
    add_box(img, 32, 6, 3, 5)

    return img


def generate_city_2():
    """Level 4: City Siege - More complex urban"""
    img = create_map_image(MAP_WIDTH, MAP_HEIGHT)
    if not USE_PYGAME:
        img.paste(FLOOR, (0, 0, MAP_WIDTH, MAP_HEIGHT))
    add_border(img)

    # Street layout with buildings
    add_box(img, 5, 2, 3, 5)
    add_box(img, 5, 10, 3, 5)

    add_horizontal_wall(img, 8, 10, 15)

    add_box(img, 20, 3, 4, 3)
    add_box(img, 20, 11, 4, 3)

    add_vertical_wall(img, 28, 2, 6)
    add_vertical_wall(img, 28, 10, 14)

    add_box(img, 33, 5, 3, 7)

    return img


def generate_forest_1():
    """Level 5: Forest Ambush - Scattered trees"""
    img = create_map_image(MAP_WIDTH, MAP_HEIGHT)
    if not USE_PYGAME:
        img.paste(FLOOR, (0, 0, MAP_WIDTH, MAP_HEIGHT))
    add_border(img)

    # Tree clusters (small boxes)
    positions = [
        (5, 4), (7, 8), (6, 12),
        (12, 3), (14, 7), (13, 11), (11, 14),
        (20, 5), (22, 9), (19, 13),
        (27, 3), (29, 7), (26, 11), (30, 14),
        (34, 5), (33, 10)
    ]

    for x, y in positions:
        add_box(img, x, y, 2, 2)

    return img


def generate_forest_2():
    """Level 6: Deep Woods - Maze-like paths"""
    img = create_map_image(MAP_WIDTH, MAP_HEIGHT)
    if not USE_PYGAME:
        img.paste(FLOOR, (0, 0, MAP_WIDTH, MAP_HEIGHT))
    add_border(img)

    # Winding path walls
    add_horizontal_wall(img, 5, 5, 15)
    add_vertical_wall(img, 15, 5, 8)

    add_horizontal_wall(img, 11, 8, 20)

    add_vertical_wall(img, 24, 3, 7)
    add_horizontal_wall(img, 3, 24, 32)

    add_vertical_wall(img, 32, 3, 11)
    add_horizontal_wall(img, 11, 26, 32)

    add_vertical_wall(img, 10, 10, 14)

    return img


def generate_industrial_1():
    """Level 7: Industrial Zone - Narrow corridors"""
    img = create_map_image(MAP_WIDTH, MAP_HEIGHT)
    if not USE_PYGAME:
        img.paste(FLOOR, (0, 0, MAP_WIDTH, MAP_HEIGHT))
    add_border(img)

    # Long walls creating corridors
    add_horizontal_wall(img, 4, 1, 12)
    add_horizontal_wall(img, 12, 1, 12)

    add_vertical_wall(img, 16, 1, 15)

    add_horizontal_wall(img, 4, 20, 30)
    add_horizontal_wall(img, 12, 20, 30)

    add_box(img, 33, 6, 3, 5)

    return img


def generate_industrial_2():
    """Level 8: Factory Floor - Complex industrial"""
    img = create_map_image(MAP_WIDTH, MAP_HEIGHT)
    if not USE_PYGAME:
        img.paste(FLOOR, (0, 0, MAP_WIDTH, MAP_HEIGHT))
    add_border(img)

    # Machinery blocks
    add_box(img, 5, 3, 4, 4)
    add_box(img, 5, 10, 4, 4)

    add_vertical_wall(img, 13, 2, 6)
    add_vertical_wall(img, 13, 10, 14)

    add_box(img, 18, 6, 3, 5)

    add_horizontal_wall(img, 3, 24, 33)
    add_horizontal_wall(img, 13, 24, 33)

    add_box(img, 28, 6, 4, 5)

    add_box(img, 34, 3, 3, 3)
    add_box(img, 34, 11, 3, 3)

    return img


def generate_fortress_1():
    """Level 9: Fortress Approach - Defensive positions"""
    img = create_map_image(MAP_WIDTH, MAP_HEIGHT)
    if not USE_PYGAME:
        img.paste(FLOOR, (0, 0, MAP_WIDTH, MAP_HEIGHT))
    add_border(img)

    # Layered defenses
    add_vertical_wall(img, 10, 2, 6)
    add_vertical_wall(img, 10, 10, 14)

    add_box(img, 16, 4, 2, 3)
    add_box(img, 16, 10, 2, 3)

    add_vertical_wall(img, 22, 1, 5)
    add_vertical_wall(img, 22, 11, 16)

    add_box(img, 28, 6, 3, 5)

    add_vertical_wall(img, 34, 2, 6)
    add_vertical_wall(img, 34, 10, 14)

    return img


def generate_fortress_2():
    """Level 10: Final Battle - Boss arena"""
    img = create_map_image(MAP_WIDTH, MAP_HEIGHT)
    if not USE_PYGAME:
        img.paste(FLOOR, (0, 0, MAP_WIDTH, MAP_HEIGHT))
    add_border(img)

    # Arena with cover positions
    add_box(img, 8, 4, 3, 3)
    add_box(img, 8, 10, 3, 3)

    # Central pillars
    add_box(img, 18, 3, 2, 2)
    add_box(img, 18, 12, 2, 2)
    add_box(img, 18, 7, 2, 3)

    # Boss area cover
    add_box(img, 28, 5, 2, 2)
    add_box(img, 28, 10, 2, 2)

    add_box(img, 34, 7, 2, 3)

    return img


def main():
    """Generate all level maps"""
    maps_dir = os.path.join(os.path.dirname(__file__), "maps")
    os.makedirs(maps_dir, exist_ok=True)

    generators = [
        ("level_01_desert.png", generate_desert_1),
        ("level_02_desert.png", generate_desert_2),
        ("level_03_city.png", generate_city_1),
        ("level_04_city.png", generate_city_2),
        ("level_05_forest.png", generate_forest_1),
        ("level_06_forest.png", generate_forest_2),
        ("level_07_industrial.png", generate_industrial_1),
        ("level_08_industrial.png", generate_industrial_2),
        ("level_09_fortress.png", generate_fortress_1),
        ("level_10_fortress.png", generate_fortress_2),
    ]

    for filename, generator in generators:
        img = generator()
        filepath = os.path.join(maps_dir, filename)
        save_image(img, filepath)
        print(f"Generated: {filepath}")

    print(f"\nAll {len(generators)} maps generated in {maps_dir}/")


if __name__ == "__main__":
    main()
