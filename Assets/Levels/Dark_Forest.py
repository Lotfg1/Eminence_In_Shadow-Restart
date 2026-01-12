import pygame
import random
from Assets.Interactables import Wall, Merchant, Tent, Rock
from Assets.Characters import SmallBandit, LargeBandit

SEGMENT_WIDTH = 768
SCREEN_HEIGHT = 920

GROUND_STEP = 50
HEIGHT_CHANGE_MIN = 2000
HEIGHT_CHANGE_MAX = 3000

# Natural occurrence configuration
MERCHANT_CHANCE = 0.01  # 1% chance per segment
MERCHANT_COOLDOWN = 50  # Can't spawn for 50 segments after appearing
TENT_CHANCE = 0.05      # 5% chance per segment
ROCK_CHANCE = 0.08      # 8% chance per segment
ENEMY_CHANCE = 0.1      # 10% chance per segment to spawn enemy group

# Platform density configuration
MAX_PLATFORMS_PER_SEGMENT = 1  # Adjust this for fewer/more platforms


def load_level():
    # INTERACTABLE WALL
    wall = Wall(
        x=-40,
        y=0,
        width=40,
        height=SCREEN_HEIGHT,
        destination_index=True
    )

    ground = []
    platforms = []
    npcs = []
    interactables = [wall]
    natural_objects = []  # Tents and rocks
    tents = []
    rocks = []
    coins = []  # No coins in Dark Forest
    enemies = []  # Enemy list

    segments = {}

    current_ground_y = SCREEN_HEIGHT - 64
    distance_since_change = 0
    next_height_change = random.randint(
        HEIGHT_CHANGE_MIN,
        HEIGHT_CHANGE_MAX
    )

    # Merchant tracking
    last_merchant_segment = -1000

    # --- Helper function to prevent tent spawning under platforms ---
    def platform_above_x(segment_platforms, x, width, ground_y):
        # Tent rect extending upwards to check for overlap
        tent_rect = pygame.Rect(x, ground_y - 400, width, 400)
        for p in segment_platforms:
            if p.colliderect(tent_rect):
                return True
        return False

    # --- Segment generation ---
    def generate_segment(index):
        nonlocal current_ground_y, distance_since_change, next_height_change, last_merchant_segment

        if index in segments:
            return

        segment_x = index * SEGMENT_WIDTH
        distance_since_change += SEGMENT_WIDTH

        # Change height every 2000-3000 px
        if distance_since_change >= next_height_change:
            current_ground_y += random.choice([-GROUND_STEP, GROUND_STEP])
            current_ground_y = max(
                300,
                min(current_ground_y, SCREEN_HEIGHT - 64)
            )
            distance_since_change = 0
            next_height_change = random.randint(
                HEIGHT_CHANGE_MIN,
                HEIGHT_CHANGE_MAX
            )

        # Ground fills to bottom of screen
        ground_rect = pygame.Rect(
            segment_x,
            current_ground_y,
            SEGMENT_WIDTH,
            SCREEN_HEIGHT - current_ground_y
        )

        # Generate platforms (Option 2: controlled density)
        segment_platforms = []
        platform_count = random.randint(0, MAX_PLATFORMS_PER_SEGMENT)

        for _ in range(platform_count):
            # maximum width the platform can have given the margins
            max_platform_width = SEGMENT_WIDTH - 200 - 200
            if max_platform_width < 200:
                break  # cannot place any platform in this segment

            w = random.randint(200, min(400, max_platform_width))
            x_min = 200
            x_max = SEGMENT_WIDTH - w - 200

            if x_max >= x_min:
                x = segment_x + random.randint(x_min, x_max)
                y = current_ground_y - random.randint(220, 320)
                segment_platforms.append(pygame.Rect(x, y, w, 16))
            # if x_max < x_min, skip this platform
        # Generate natural occurrences
        segment_natural = []
        segment_tents = []
        segment_rocks = []
        segment_interactables = []

        # MERCHANT - Rare spawn with cooldown
        if (index - last_merchant_segment) >= MERCHANT_COOLDOWN:
            if random.random() < MERCHANT_CHANCE:
                merchant_x = segment_x + random.randint(200, SEGMENT_WIDTH - 200)
                merchant = Merchant(merchant_x, current_ground_y - 48)
                segment_interactables.append(merchant)
                last_merchant_segment = index

        # TENTS - Large sloped polygons (must NOT spawn under platforms)
        if random.random() < TENT_CHANCE:
            tent_x = segment_x + random.randint(150, SEGMENT_WIDTH - 350)
            tent_width = 200  # adjust to Tent actual width if needed
            if not platform_above_x(segment_platforms, tent_x, tent_width, current_ground_y):
                tent = Tent(tent_x, current_ground_y)
                segment_tents.append(tent)
                segment_natural.append(tent)

        # ROCKS - Small sloped polygons
        if random.random() < ROCK_CHANCE:
            rock_x = segment_x + random.randint(100, SEGMENT_WIDTH - 200)
            rock = Rock(rock_x, current_ground_y)
            segment_rocks.append(rock)
            segment_natural.append(rock)
        
        # ENEMIES - Spawn groups of 2-4 bandits
        segment_enemies = []
        if random.random() < ENEMY_CHANCE:
            num_enemies = random.randint(2, 4)
            for i in range(num_enemies):
                enemy_x = segment_x + random.randint(150, SEGMENT_WIDTH - 150)
                enemy_y = current_ground_y
                # More large bandits in the Dark Forest (50/50 split)
                if random.random() < 0.5:
                    segment_enemies.append(SmallBandit(enemy_x, enemy_y))
                else:
                    segment_enemies.append(LargeBandit(enemy_x, enemy_y))

        # Save segment data
        segments[index] = {
            "ground": ground_rect,
            "platforms": segment_platforms,
            "natural_objects": segment_natural,
            "tents": segment_tents,
            "rocks": segment_rocks,
            "interactables": segment_interactables,
            "enemies": segment_enemies
        }

        # Extend global lists
        ground.append(ground_rect)
        platforms.extend(segment_platforms)
        natural_objects.extend(segment_natural)
        tents.extend(segment_tents)
        rocks.extend(segment_rocks)
        interactables.extend(segment_interactables)
        enemies.extend(segment_enemies)

    # Pre-generate starting area
    for i in range(-4, 6):
        generate_segment(i)

    player_start = (200, current_ground_y - 64)

    return {
        "ground": ground,
        "platforms": platforms,
        "segments": segments,
        "generate_segment": generate_segment,
        "npcs": npcs,
        "interactables": interactables,
        "natural_objects": natural_objects,
        "tents": tents,
        "rocks": rocks,
        "coins": coins,
        "enemies": enemies,
        "player_start": player_start,
        "infinite": True,
        "level_id": "dark_forest",
        "music": "battle_theme"
    }