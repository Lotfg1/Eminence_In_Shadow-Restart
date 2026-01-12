import pygame
from Assets.Interactables import Wall, Bed, Coin

def load_level():
    ground = [pygame.Rect(0, 920-64, 1080, 64)]
    platforms = []
    npcs = []
    interactables = [
        Bed(400, 920-32-64),          # Bed: collidable
        Wall(0, 0, 40, 856, destination_index=True),   # left wall triggers menu
        Wall(1040, 0, 40, 856, destination_index=True) # right wall triggers menu
    ]
    
    # Add coin that animates every 5 seconds
    coins = [
        Coin(x=700, y=920-64-40, width=32, height=32)  # Coin floating above ground
    ]
    
    # No enemies in player room
    enemies = []
    
    player_start = (100, 920-64-64)
    
    return {
        "ground": ground,
        "platforms": platforms,
        "npcs": npcs,
        "interactables": interactables,
        "coins": coins,
        "enemies": enemies,
        "player_start": player_start,
        "infinite": False,
        "world_width": 1080,
        "level_id": "player_room",  # Identifier for music system
        "music": "calm_theme"  # Which song to play
    }