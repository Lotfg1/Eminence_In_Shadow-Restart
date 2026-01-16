# Assets/GameBalance.py

# =============================================================================
# PLAYER STATS
# =============================================================================

PLAYER = {
    "width": 32,
    "height": 64,
    "base_speed": 6,
    
    # Combat
    "attack_damage": 3,
    "m_attack_damage": 2,
    "skill_attack_damage": 4,
    "defense": 8,
    "m_defense": 6,
    
    # Health/Mana
    "max_health": 150,
    "max_mana": 30,
    
    # Invulnerability after hitting enemies
    "invuln_duration_beats": 4,  # How many beats of invulnerability
    "invuln_flash_speed": 0.1,   # How fast to flash during invulnerability
}

# =============================================================================
# ENEMY STATS
# =============================================================================

ENEMY = {
    # Speed multiplier (player speed * this)
    "speed_multiplier": 1.0 / 3.0,  # 1/3 of player speed
    "chase_speed_multiplier": 0.08,  # Chase a bit faster than before
    "patrol_speed_multiplier": 0.02,  # Patrol extremely slowly
    
    # Attack timing (on half notes = one attack per beat)
    "stab_beats": [1, 2],
    "uppercut_beats": [3, 4],
    
    # Attack properties
    "attack_range": 80,
    "attack_cooldown": 2.0,  # Seconds between combo attempts
    "attack_duration": 0.3,   # How long attack hitbox shows (seconds)
    
    # Knockback (platformer-style with gravity)
    "stab_knockback": {"x": 8, "y": -2},    # Minor stun (reduced Y)
    "uppercut_knockback": {"x": 12, "y": -6},  # Major knockback (reduced Y)
    "uppercut_stun": 0.3,
    "stab_stun": 0.8,  # 1-2 beats at 120 BPM
}

# =============================================================================
# SMALL BANDIT (Level 1-5)
# =============================================================================

SMALL_BANDIT = {
    "width": 40,
    "height": 48,
    "max_health": 15,
    "attack_damage": 5,
    "defense": 2,
    "level": 1,
    "exp_value": 25,
    "color": (150, 100, 150),
}

# =============================================================================
# LARGE BANDIT (Level 6-10)
# =============================================================================

LARGE_BANDIT = {
    "width": 56,
    "height": 56,
    "max_health": 40,
    "attack_damage": 10,
    "defense": 4,
    "level": 6,
    "exp_value": 50,
    "color": (200, 80, 80),
}

# =============================================================================
# EXPERIENCE AND LEVELING
# =============================================================================

EXPERIENCE = {
    # Exp gained = enemy_exp_value * player_level / enemy_level
    # (or use a flat value per kill)
    "gain_method": "scaled",  # "scaled" or "flat"
    "flat_exp_per_level": 100,  # If using flat method
    
    # Stat growth per level
    "health_per_level": 20,
    "mana_per_level": 5,
    "attack_per_level": 2,
    "defense_per_level": 1,
    
    # Starting exp for each level (roughly)
    "exp_curve": 100,  # Each level needs this much more exp
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_enemy_stats(enemy_type):
    """Get balanced stats for an enemy type
    
    Args:
        enemy_type: "small" or "large"
    
    Returns:
        Dictionary of enemy stats
    """
    if enemy_type == "small":
        stats = SMALL_BANDIT.copy()
    else:
        stats = LARGE_BANDIT.copy()
    
    # Apply speed multiplier
    stats["speed"] = PLAYER["base_speed"] * ENEMY["speed_multiplier"]
    
    return stats


def get_player_level_stats(level):
    """Get player stats for a given level
    
    Args:
        level: Player level (starts at 1)
    
    Returns:
        Dictionary of stats at this level
    """
    level_offset = level - 1
    return {
        "max_health": PLAYER["max_health"] + (EXPERIENCE["health_per_level"] * level_offset),
        "max_mana": PLAYER["max_mana"] + (EXPERIENCE["mana_per_level"] * level_offset),
        "attack_damage": PLAYER["attack_damage"] + (EXPERIENCE["attack_per_level"] * level_offset),
        "defense": PLAYER["defense"] + (EXPERIENCE["defense_per_level"] * level_offset),
    }


def get_exp_for_level(current_level):
    """Get total exp needed to reach a level
    
    Args:
        current_level: Current player level
    
    Returns:
        Total exp required
    """
    return current_level * EXPERIENCE["exp_curve"]
