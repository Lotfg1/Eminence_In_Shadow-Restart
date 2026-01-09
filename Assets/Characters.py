import pygame

class CharacterBase:
    def __init__(self, x=0, y=0, width=64, height=64, speed=5, stats=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.moving_left = False
        self.moving_right = False
        self.y_momentum = 0
        self.on_ground = False
        
        # Default stats structure
        if stats is None:
            stats = {}
        
        self.stats = {
            'Current_Health': stats.get('Current_Health', 100),
            'Max_Health': stats.get('Max_Health', 100),
            'Current_Mana': stats.get('Current_Mana', 50),
            'Max_Mana': stats.get('Max_Mana', 50),
            'Attack_Damage': stats.get('Attack_Damage', 10),
            'M_Attack_Damage': stats.get('M_Attack_Damage', 10),
            'Skill_Attack_Damage': stats.get('Skill_Attack_Damage', 15),
            'Defense': stats.get('Defense', 5),
            'M_Defense': stats.get('M_Defense', 5)
        }

    def move(self, rects=None):
        if rects is None:
            rects = []
        # Horizontal movement
        if self.moving_left:
            self.rect.x -= self.speed
            for r in rects:
                if self.rect.colliderect(r):
                    self.rect.left = r.right
        if self.moving_right:
            self.rect.x += self.speed
            for r in rects:
                if self.rect.colliderect(r):
                    self.rect.right = r.left

    def apply_gravity(self, gravity=0.8, max_fall=14, rects=None):
        if rects is None:
            rects = []
        self.y_momentum += gravity
        if self.y_momentum > max_fall:
            self.y_momentum = max_fall
        steps = int(abs(self.y_momentum)) + 1
        step = self.y_momentum / steps
        self.on_ground = False
        for _ in range(steps):
            self.rect.y += step
            for r in rects:
                if self.rect.colliderect(r):
                    if step > 0:
                        self.rect.bottom = r.top
                        self.y_momentum = 0
                        self.on_ground = True
                    elif step < 0:
                        self.rect.top = r.bottom
                        self.y_momentum = 0
    
    def take_damage(self, damage, is_magical=False):
        """Apply damage to the character"""
        defense = self.stats['M_Defense'] if is_magical else self.stats['Defense']
        actual_damage = max(1, damage - defense)  # Minimum 1 damage
        self.stats['Current_Health'] -= actual_damage
        if self.stats['Current_Health'] < 0:
            self.stats['Current_Health'] = 0
        return actual_damage
    
    def heal(self, amount):
        """Heal the character"""
        self.stats['Current_Health'] += amount
        if self.stats['Current_Health'] > self.stats['Max_Health']:
            self.stats['Current_Health'] = self.stats['Max_Health']
        return amount
    
    def use_mana(self, amount):
        """Use mana for a skill"""
        if self.stats['Current_Mana'] >= amount:
            self.stats['Current_Mana'] -= amount
            return True
        return False
    
    def restore_mana(self, amount):
        """Restore mana"""
        self.stats['Current_Mana'] += amount
        if self.stats['Current_Mana'] > self.stats['Max_Mana']:
            self.stats['Current_Mana'] = self.stats['Max_Mana']
        return amount
    
    def is_alive(self):
        """Check if character is alive"""
        return self.stats['Current_Health'] > 0
    
    def get_stat(self, stat_name):
        """Get a specific stat value"""
        return self.stats.get(stat_name, 0)
    
    def set_stat(self, stat_name, value):
        """Set a specific stat value"""
        if stat_name in self.stats:
            self.stats[stat_name] = value
            # Clamp current values to max values
            if stat_name == 'Current_Health':
                self.stats['Current_Health'] = min(self.stats['Current_Health'], self.stats['Max_Health'])
            elif stat_name == 'Current_Mana':
                self.stats['Current_Mana'] = min(self.stats['Current_Mana'], self.stats['Max_Mana'])
    
    def modify_stat(self, stat_name, amount):
        """Modify a stat by a certain amount (can be positive or negative)"""
        if stat_name in self.stats:
            self.stats[stat_name] += amount
            # Clamp current values
            if stat_name == 'Current_Health':
                self.stats['Current_Health'] = max(0, min(self.stats['Current_Health'], self.stats['Max_Health']))
            elif stat_name == 'Current_Mana':
                self.stats['Current_Mana'] = max(0, min(self.stats['Current_Mana'], self.stats['Max_Mana']))


class MainCharacter(CharacterBase):
    def __init__(self, x=0, y=0):
        # Main character stats
        player_stats = {
            'Current_Health': 150,
            'Max_Health': 150,
            'Current_Mana': 30,
            'Max_Mana': 30,
            'Attack_Damage': 15,
            'M_Attack_Damage': 12,
            'Skill_Attack_Damage': 20,
            'Defense': 8,
            'M_Defense': 6
        }
        super().__init__(x, y, 64, 64, speed=10, stats=player_stats)
        
        # Attack system
        self.is_attacking = False
        self.attack_frame = 0
        self.attack_duration = 20  # frames
        self.attack_cooldown = 0
        self.attack_cooldown_max = 30  # frames before next attack
        self.facing_right = True  # Track which direction player is facing
        
        # ATTACK HITBOX CONFIGURATION - Easy to edit!
        self.attack_hitbox_config = {
            'width': 80,           # Width of attack hitbox
            'height': 60,          # Height of attack hitbox
            'offset_x': 70,        # How far in front of player
            'offset_y': 0,         # Vertical offset from player center
            'color': (255, 0, 0),  # Red color for hitbox
            'alpha': 100           # Transparency (0-255, lower = more transparent)
        }
    
    def start_attack(self):
        """Initiate an attack"""
        if self.attack_cooldown == 0 and not self.is_attacking:
            self.is_attacking = True
            self.attack_frame = 0
            self.attack_cooldown = self.attack_cooldown_max
            return True
        return False
    
    def update_attack(self):
        """Update attack animation and cooldown"""
        # Update attack animation
        if self.is_attacking:
            self.attack_frame += 1
            if self.attack_frame >= self.attack_duration:
                self.is_attacking = False
                self.attack_frame = 0
        
        # Update cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
    
    def get_attack_hitbox(self):
        """Get the current attack hitbox rectangle"""
        if not self.is_attacking:
            return None
        
        config = self.attack_hitbox_config
        
        # Calculate hitbox position based on facing direction
        if self.facing_right:
            hitbox_x = self.rect.right + config['offset_x'] - config['width']
        else:
            hitbox_x = self.rect.left - config['offset_x']
        
        hitbox_y = self.rect.centery - config['height'] // 2 + config['offset_y']
        
        return pygame.Rect(hitbox_x, hitbox_y, config['width'], config['height'])
    
    def check_attack_hits(self, entities):
        """Check if attack hits any entities, returns list of hit entities"""
        hitbox = self.get_attack_hitbox()
        if not hitbox:
            return []
        
        hits = []
        for entity in entities:
            if hasattr(entity, 'rect') and hitbox.colliderect(entity.rect):
                hits.append(entity)
        
        return hits
    
    def move(self, rects=None):
        """Override move to track facing direction"""
        if self.moving_left:
            self.facing_right = False
        elif self.moving_right:
            self.facing_right = True
        
        super().move(rects)


class Merchant(CharacterBase):
    def __init__(self, x=0, y=0):
        # Merchant stats (NPCs have stats too, just in case)
        merchant_stats = {
            'Current_Health': 50,
            'Max_Health': 50,
            'Current_Mana': 0,
            'Max_Mana': 0,
            'Attack_Damage': 0,
            'M_Attack_Damage': 0,
            'Skill_Attack_Damage': 0,
            'Defense': 3,
            'M_Defense': 3
        }
        super().__init__(x, y, 32, 48, stats=merchant_stats)

class Enemey_Base(CharacterBase):
    def __init__(self):
        super().__init__(0, 0, 32, 48, stats={})