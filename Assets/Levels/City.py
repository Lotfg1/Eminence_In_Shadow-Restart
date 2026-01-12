import pygame
from Assets.Interactables import Merchant
from Assets.Interactables import Wall

def load_level():
    # Floor
    ground = [pygame.Rect(0, 920-64, 1080, 64)]

    # No platforms
    platforms = []

    # NPCs
    npcs = []

    # Interactables (merchant)
    interactables = [
        Merchant(x=500, y=920-48-64),  # 48 tall, just above floor
        Wall(0, 0, 40, 856, destination_index=True),   # left wall triggers menu
        Wall(1040, 0, 40, 856, destination_index=True) # right wall triggers menu
    ]

    # Player start
    player_start = (100, 920-64-64)

    # No enemies in city
    enemies = []

    return {
        "ground": ground,
        "platforms": platforms,
        "npcs": npcs,
        "interactables": interactables,
        "coins": [],  # No coins in city
        "enemies": enemies,
        "player_start": player_start,
        "infinite": False,
        "world_width": 1080,
        "level_id": "city",
        "music": "city_theme"
    }