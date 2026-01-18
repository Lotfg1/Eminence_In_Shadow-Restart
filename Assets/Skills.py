# Assets/Skills.py
"""
Skill System - Rhythm-based special abilities
Skills require specific input patterns timed to the beat
"""

class Skill:
    """Base skill class"""
    def __init__(self, skill_id, name, description, skill_type, challenge, damage_multiplier, mana_cost, cooldown):
        self.skill_id = skill_id
        self.name = name
        self.description = description
        self.skill_type = skill_type  # "word" or "arrows" or other types
        self.challenge = challenge  # What the player needs to do
        self.damage_multiplier = damage_multiplier  # Damage multiplier if successful
        self.mana_cost = mana_cost
        self.cooldown = cooldown  # Cooldown in seconds
        self.last_used = 0  # Timestamp of last use


class SkillSystem:
    """Manages all available skills"""
    
    SKILLS = {
        "basic_attack": Skill(
            "basic_attack",
            "Basic Attack",
            "A simple rhythm-based slash attack",
            "rhythm",
            {"type": "beat_hit", "beats": 1},  # Hit on the beat
            1.0,  # Base damage (1x)
            0,    # No mana cost
            0.5   # 0.5 second cooldown
        ),
        "power_slash": Skill(
            "power_slash",
            "Power Slash",
            "Type 'SLASH' in rhythm to unleash a powerful attack",
            "word",
            {"type": "word", "word": "SLASH", "time_window": 2.0},  # 2 beat window
            2.5,  # 2.5x damage
            20,   # 20 mana
            3.0   # 3 second cooldown
        ),
        "combo_strike": Skill(
            "combo_strike",
            "Combo Strike",
            "Press UP UP DOWN in rhythm with the beat",
            "arrows",
            {"type": "arrow_sequence", "sequence": ["up", "up", "down"], "time_per_input": 0.5},
            2.0,  # 2x damage
            15,   # 15 mana
            2.5   # 2.5 second cooldown
        ),
        "whirlwind": Skill(
            "whirlwind",
            "Whirlwind",
            "Type 'SPIN' repeatedly to build momentum",
            "word",
            {"type": "rapid_word", "word": "SPIN", "count": 3, "time_window": 3.0},
            3.0,  # 3x damage
            30,   # 30 mana
            4.0   # 4 second cooldown
        ),
        "sonic_thrust": Skill(
            "sonic_thrust",
            "Sonic Thrust",
            "Press LEFT RIGHT LEFT in rapid succession",
            "arrows",
            {"type": "arrow_sequence", "sequence": ["left", "right", "left"], "time_per_input": 0.3},
            2.8,  # 2.8x damage
            25,   # 25 mana
            3.5   # 3.5 second cooldown
        ),
    }
    
    @staticmethod
    def get_skill(skill_id):
        """Get a skill by ID"""
        return SkillSystem.SKILLS.get(skill_id)
    
    @staticmethod
    def get_all_skills():
        """Get all available skills"""
        return list(SkillSystem.SKILLS.values())
    
    @staticmethod
    def is_skill_ready(skill_id, current_time):
        """Check if a skill is off cooldown"""
        skill = SkillSystem.get_skill(skill_id)
        if skill is None:
            return False
        return (current_time - skill.last_used) >= skill.cooldown
    
    @staticmethod
    def use_skill(skill_id, current_time):
        """Mark a skill as used (start cooldown)"""
        skill = SkillSystem.get_skill(skill_id)
        if skill:
            skill.last_used = current_time
