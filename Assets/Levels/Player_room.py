import pygame
from Assets.Interactables import Wall, Bed

def load_level():
    ground = [pygame.Rect(0, 920-64, 1080, 64)]
    platforms = []
    npcs = []
    interactables = [
        Bed(400, 920-32-64),          # Bed: collidable
        Wall(0, 0, 40, 856, destination_index=True),   # left wall triggers menu
        Wall(1040, 0, 40, 856, destination_index=True) # right wall triggers menu
    ]
    player_start = (100, 920-64-64)
    return {
        "ground": ground,
        "platforms": platforms,
        "npcs": npcs,
        "interactables": interactables,
        "player_start": player_start,
        "infinite": False
    }
