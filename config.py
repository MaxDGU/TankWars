"""
Configuration and constants for TankWars Single-Player Campaign
"""

# Screen settings
SCREEN_WIDTH = 1170
SCREEN_HEIGHT = 510
FPS = 24

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Game states
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_LEVEL_COMPLETE = "level_complete"
STATE_GAME_OVER = "game_over"

# Player settings
PLAYER_START_HEALTH = 40
PLAYER_START_AMMO = 150
PLAYER_START_LIVES = 3
PLAYER_SPEED = 5
PLAYER_TURN_SPEED = 3
PLAYER_FIRE_DELAY = 3

# Enemy types configuration
ENEMY_TYPES = {
    "scout": {
        "health": 10,
        "speed": 6,
        "fire_delay": 40,  # frames between shots
        "accuracy": 0.6,   # 0-1, affects aim randomness
        "points": 100,
        "color": (150, 150, 0),  # yellowish
        "behavior": "patrol"
    },
    "soldier": {
        "health": 20,
        "speed": 4,
        "fire_delay": 30,
        "accuracy": 0.75,
        "points": 200,
        "color": (0, 150, 0),  # greenish
        "behavior": "pursue"
    },
    "heavy": {
        "health": 50,
        "speed": 2,
        "fire_delay": 50,
        "accuracy": 0.5,
        "points": 500,
        "color": (100, 100, 100),  # gray
        "behavior": "patrol",
        "bullet_size": "big"
    },
    "sniper": {
        "health": 15,
        "speed": 0,
        "fire_delay": 60,
        "accuracy": 0.9,
        "points": 300,
        "color": (150, 0, 150),  # purple
        "behavior": "stationary"
    },
    "boss": {
        "health": 200,
        "speed": 3,
        "fire_delay": 20,
        "accuracy": 0.8,
        "points": 2000,
        "color": (200, 0, 0),  # red
        "behavior": "boss",
        "bullet_size": "big"
    }
}

# Level definitions
LEVELS = {
    1: {
        "name": "Desert Outpost",
        "map": "level_01_desert.png",
        "enemies": [("scout", 3)],
        "player_start": (100, 250),
        "objective": "eliminate"
    },
    2: {
        "name": "Desert Fortress",
        "map": "level_02_desert.png",
        "enemies": [("scout", 2), ("soldier", 2)],
        "player_start": (100, 250),
        "objective": "eliminate"
    },
    3: {
        "name": "Urban Warfare",
        "map": "level_03_city.png",
        "enemies": [("soldier", 3), ("scout", 2)],
        "player_start": (100, 250),
        "objective": "eliminate"
    },
    4: {
        "name": "City Siege",
        "map": "level_04_city.png",
        "enemies": [("soldier", 3), ("sniper", 1)],
        "player_start": (100, 250),
        "objective": "eliminate"
    },
    5: {
        "name": "Forest Ambush",
        "map": "level_05_forest.png",
        "enemies": [("scout", 3), ("soldier", 2), ("sniper", 1)],
        "player_start": (100, 250),
        "objective": "eliminate"
    },
    6: {
        "name": "Deep Woods",
        "map": "level_06_forest.png",
        "enemies": [("soldier", 3), ("heavy", 1)],
        "player_start": (100, 250),
        "objective": "eliminate"
    },
    7: {
        "name": "Industrial Zone",
        "map": "level_07_industrial.png",
        "enemies": [("heavy", 2), ("soldier", 2), ("sniper", 1)],
        "player_start": (100, 250),
        "objective": "eliminate"
    },
    8: {
        "name": "Factory Floor",
        "map": "level_08_industrial.png",
        "enemies": [("heavy", 2), ("sniper", 2), ("soldier", 3)],
        "player_start": (100, 250),
        "objective": "eliminate"
    },
    9: {
        "name": "Fortress Approach",
        "map": "level_09_fortress.png",
        "enemies": [("heavy", 3), ("soldier", 4), ("sniper", 2)],
        "player_start": (100, 250),
        "objective": "eliminate"
    },
    10: {
        "name": "Final Battle",
        "map": "level_10_fortress.png",
        "enemies": [("boss", 1), ("heavy", 2)],
        "player_start": (100, 250),
        "objective": "boss"
    }
}

# Power-up types
POWERUP_TYPES = {
    "health": {
        "effect": "restore_health",
        "value": 20,
        "duration": 0,  # instant
        "color": RED,
        "symbol": "+"
    },
    "ammo": {
        "effect": "restore_ammo",
        "value": 50,
        "duration": 0,
        "color": YELLOW,
        "symbol": "A"
    },
    "speed": {
        "effect": "speed_boost",
        "value": 1.5,  # multiplier
        "duration": 240,  # frames (10 seconds at 24 fps)
        "color": BLUE,
        "symbol": "S"
    },
    "shield": {
        "effect": "invulnerability",
        "value": 1,
        "duration": 120,  # 5 seconds
        "color": WHITE,
        "symbol": "O"
    },
    "rapid_fire": {
        "effect": "rapid_fire",
        "value": 0.5,  # fire delay multiplier
        "duration": 192,  # 8 seconds
        "color": (255, 128, 0),  # orange
        "symbol": "R"
    },
    "double_damage": {
        "effect": "double_damage",
        "value": 2,
        "duration": 240,  # 10 seconds
        "color": (255, 0, 255),  # magenta
        "symbol": "D"
    }
}

# Power-up spawn settings
POWERUP_DROP_CHANCE = 0.3  # 30% chance from destroyed enemy
POWERUP_SPAWN_INTERVAL = 600  # frames (25 seconds) for random spawns

# Save file path
SAVE_FILE = "tankwars_save.json"
