# Assets/AttackConfig.py
"""
Attack Configuration System
Defines reach, damage, and visual properties for each attack type
"""

class AttackConfig:
    """Configuration for different attack types"""
    
    # Attack type configurations: reach (pixels), damage multiplier, hitbox height
    ATTACKS = {
        "neutral": {
            "name": "Standard Slash",
            "reach": 50,           # How far the attack extends
            "damage_multiplier": 0.8,  # Base damage x this = attack damage
            "width": 80,
            "height": 60,
            "offset_x": 70,
            "offset_y": -10,
        },
        "forward": {
            "name": "Dash Attack",
            "reach": 80,          # Reaches further
            "damage_multiplier": 0.95,
            "width": 120,
            "height": 80,
            "offset_x": 100,
            "offset_y": -15,
        },
        "down": {
            "name": "Low Sweep",
            "reach": 60,          # Wide sweep
            "damage_multiplier": 0.85,
            "width": 100,
            "height": 40,
            "offset_x": 80,
            "offset_y": 20,
        },
    }
    
    @staticmethod
    def get_attack(attack_type):
        """Get attack config by type"""
        return AttackConfig.ATTACKS.get(attack_type, AttackConfig.ATTACKS["neutral"])
    
    @staticmethod
    def get_reach(attack_type):
        """Get reach for an attack type"""
        return AttackConfig.get_attack(attack_type)["reach"]
    
    @staticmethod
    def get_damage_multiplier(attack_type):
        """Get damage multiplier for an attack type"""
        return AttackConfig.get_attack(attack_type)["damage_multiplier"]
    
    @staticmethod
    def get_hitbox(attack_type):
        """Get hitbox dimensions for an attack type"""
        config = AttackConfig.get_attack(attack_type)
        return {
            "width": config["width"],
            "height": config["height"],
            "offset_x": config["offset_x"],
            "offset_y": config["offset_y"],
        }
