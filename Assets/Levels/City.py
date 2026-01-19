import pygame
from Assets.Interactables import Merchant
from Assets.Interactables import Wall

def load_level():
    # Background-aligned metrics
    bg_width = 1024
    bg_height = 863
    ground_height = 32
    ground_y = 815  # Align with visible street/floor in city.jpg

    # Floor aligned to background bottom
    ground = [pygame.Rect(0, ground_y, bg_width, ground_height)]
    # Add a small ledge/platform on the left building
    platforms = [pygame.Rect(120, 640, 220, 24)]

    # No platforms
    # (platforms defined above)

    # NPCs
    npcs = []

    # Interactables (merchant)
    interactables = [
        Merchant(x=500, y=ground_y - 64),  # Place on ground
        Wall(0, 0, 40, ground_y, destination_index=True),   # left wall triggers menu
        Wall(bg_width - 40, 0, 40, ground_y, destination_index=True) # right wall triggers menu
    ]

    # Player start
    player_start = (100, ground_y - 64)

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
        "world_width": bg_width,
        "world_height": bg_height,
        "level_id": "city",
        "music_category": "city"
    }