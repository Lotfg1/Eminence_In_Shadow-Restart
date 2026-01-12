import pygame

from Assets.ComboConfig import ComboTracker
from Assets.GameBalance import PLAYER, ENEMY, SMALL_BANDIT, LARGE_BANDIT, EXPERIENCE, COMBO_BALANCE, ENEMY_COMBOS, get_enemy_stats, get_player_level_stats

class CharacterBase:
    def __init__(self, x=0, y=0, width=64, height=64, speed=5, stats=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.moving_left = False
        self.moving_right = False
        self.y_momentum = 0
        self.on_ground = False
        
        # Stun and knockback system
        self.is_stunned = False
        self.stun_timer = 0
        self.knockback_x = 0  # Horizontal knockback velocity
        self.knockback_y = 0  # Vertical knockback velocity
        
        # Bounce system (for major knockback)
        self.is_bouncing = False
        self.bounce_count = 0
        self.bounce_velocity = 0  # Upward velocity for bounces
        
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
    
    def teleport_jump(self, rects, distance):
        if not self.on_ground:
            return False
        
        # Calculate target position
        target_y = self.rect.y - distance
        
        # Check for platforms in the way
        check_rect = pygame.Rect(self.rect.x, target_y, self.rect.width, distance)
        
        # Find the lowest platform that blocks the teleport
        blocking_platform = None
        for r in rects:
            if check_rect.colliderect(r):
                # Only consider platforms above us
                if r.bottom <= self.rect.top:
                    if blocking_platform is None or r.bottom > blocking_platform.bottom:
                        blocking_platform = r
        
        # Teleport to position
        if blocking_platform:
            # Stop just BELOW the platform (above it, but with negative velocity to fall)
            self.rect.bottom = blocking_platform.top - 1
            # Give player upward momentum to hit the platform
            self.y_momentum = -12  # Upward momentum
        else:
            # Teleport full distance and give upward momentum
            self.rect.y = target_y
            self.y_momentum = -12  # Upward momentum
        
        self.on_ground = False
        return True
    
    def apply_knockback(self, knockback_x, knockback_y, stun_duration=0.5, major=False):
        self.knockback_x = knockback_x
        self.knockback_y = knockback_y
        self.is_stunned = True
        self.stun_timer = stun_duration
        
        # Major knockback triggers bouncing
        if major:
            self.is_bouncing = True
            self.bounce_count = 0
            self.bounce_velocity = knockback_y
    
    def update_stun_and_knockback(self, dt, rects):
        if self.is_stunned:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.is_stunned = False
                self.stun_timer = 0
        
        # Handle bouncing (for major knockback)
        if self.is_bouncing:
            self.bounce_velocity += 0.7  # Gravity during bounce
            self.rect.y += self.bounce_velocity
            
            # Check for ground collision during bounce
            for r in rects:
                if self.rect.colliderect(r) and self.bounce_velocity > 0:
                    self.rect.bottom = r.top
                    self.bounce_count += 1
                    
                    # Reverse velocity and reduce it each bounce (dampening)
                    self.bounce_velocity = -self.bounce_velocity * 0.6
                    
                    # Stop bouncing after 3 bounces
                    if self.bounce_count >= 3:
                        self.is_bouncing = False
                        self.bounce_velocity = 0
                        self.on_ground = True
                    break
        
        # Apply knockback (minor)
        if abs(self.knockback_x) > 0.1 or abs(self.knockback_y) > 0.1:
            self.rect.x += self.knockback_x
            for r in rects:
                if self.rect.colliderect(r):
                    if self.knockback_x > 0:
                        self.rect.right = r.left
                    else:
                        self.rect.left = r.right
                    self.knockback_x = 0
            
            self.rect.y += self.knockback_y
            for r in rects:
                if self.rect.colliderect(r):
                    if self.knockback_y > 0:
                        self.rect.bottom = r.top
                        self.knockback_y = 0
                        self.on_ground = True
                    elif self.knockback_y < 0:
                        self.rect.top = r.bottom
                        self.knockback_y = 0
            
            self.knockback_x *= 0.85
            self.knockback_y += 0.5
    
    def take_damage(self, damage, is_magical=False):
        """Apply damage to the character"""
        defense = self.stats['M_Defense'] if is_magical else self.stats['Defense']
        actual_damage = max(1, damage - defense)
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
        # Level and experience system
        self.level = 1
        self.experience = 0
        self.exp_for_next_level = EXPERIENCE["exp_curve"]
        
        # Main character stats using GameBalance config
        player_stats = get_player_level_stats(self.level)
        player_stats.update({
            'Current_Health': player_stats['max_health'],
            'Max_Health': player_stats['max_health'],
            'Current_Mana': player_stats['max_mana'],
            'Max_Mana': player_stats['max_mana'],
            'M_Attack_Damage': PLAYER['m_attack_damage'],
            'Skill_Attack_Damage': PLAYER['skill_attack_damage'],
            'M_Defense': PLAYER['m_defense']
        })
        
        super().__init__(x, y, PLAYER['width'], PLAYER['height'], speed=PLAYER['base_speed'], stats=player_stats)
        
        # Invulnerability after hitting enemies
        self.invulnerable = False
        self.invuln_timer = 0
        self.invuln_duration = PLAYER['invuln_duration_beats']
        self.invuln_flash = False  # For visual flash effect
        
        # Attack system
        self.is_attacking = False
        self.attack_frame = 0
        self.attack_duration = 20  # frames
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
        
        # Combo system
        self.combo_tracker = ComboTracker()
    
    def start_attack(self, beat_number=1):
        """Initiate an attack - beat_number is which beat (1-4) this attack is on"""
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_frame = 0
            
            # Track attack for combo system
            import time
            self.combo_tracker.add_hit(time.time(), beat_number)
            
            return True
        return False
    
    def update_attack(self):
        """Update attack animation"""
        # Update attack animation
        if self.is_attacking:
            self.attack_frame += 1
            if self.attack_frame >= self.attack_duration:
                self.is_attacking = False
                self.attack_frame = 0
    
    def gain_experience(self, amount):
        """Gain experience and level up if needed
        
        Args:
            amount: Experience amount to gain
        """
        self.experience += amount
        
        # Check for level up
        while self.experience >= self.exp_for_next_level:
            self.level_up()
    
    def level_up(self):
        """Level up the player and increase stats"""
        self.experience -= self.exp_for_next_level
        self.level += 1
        self.exp_for_next_level = EXPERIENCE["exp_curve"] * self.level
        
        # Get new stats for this level
        new_stats = get_player_level_stats(self.level)
        
        # Increase health
        health_gain = new_stats['max_health'] - self.stats['Max_Health']
        self.stats['Max_Health'] = new_stats['max_health']
        self.stats['Current_Health'] += health_gain
        
        # Increase mana
        mana_gain = new_stats['max_mana'] - self.stats['Max_Mana']
        self.stats['Max_Mana'] = new_stats['max_mana']
        self.stats['Current_Mana'] += mana_gain
        
        # Increase attack
        self.stats['Attack_Damage'] = new_stats['attack_damage']
        
        # Increase defense
        self.stats['Defense'] = new_stats['defense']
    
    def set_invulnerable(self, beat_count=None):
        """Make player invulnerable for a number of beats
        
        Args:
            beat_count: Number of beats to be invulnerable (uses config default if None)
        """
        if beat_count is None:
            beat_count = PLAYER['invuln_duration_beats']
        
        self.invulnerable = True
        self.invuln_timer = beat_count  # Will be decremented by beat counter in main.py
        self.invuln_flash = False
    
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

class EnemyBase(CharacterBase):
    def __init__(self, x=0, y=0, width=48, height=48, speed=5, stats=None):
        super().__init__(x, y, width, height, speed, stats)
        
        # AI system
        self.patrol_left = x - 100
        self.patrol_right = x + 100
        self.patrol_direction = 1  # 1 for right, -1 for left
        
        self.detection_range = 200  # How far to detect player
        self.chase_speed_multiplier = 1.2  # Chase speed multiplier (reduced from 1.5)
        self.jump_height_threshold = 100  # If player is this high above, try to jump
        self.state = "patrol"  # patrol, chase, dead
        
        self.facing_right = True
        self.is_jumping = False
        
        # Jump delay system
        self.player_jumped_recently = False
        self.jump_delay_timer = 0
        self.jump_delay = 0.15  # 0.15 second delay
        self.jump_strength = -18  # Normal jump strength
        
        # Random jump system
        self.random_jump_timer = 0
        self.random_jump_cooldown = 2.0  # Time between random jumps
        
        # Attack system for enemies
        self.attack_range = 80  # How close to attack
        self.attack_cooldown = 0
        self.attack_cooldown_max = 2.0  # 2 seconds between combo starts
        self.current_attack = None  # "stab" or "uppercut"
        self.attack_timer = 0
        self.combo_state = 0  # 0 = not attacking, 1+ = attacking
        self.combo_index = 0  # Current position in note pattern
        self.combo_pattern = []  # The note pattern being executed
        self.last_executed_note = -1  # Track which note we've already executed
    
    def update_ai(self, player, collision_rects, gravity=0.7, max_fall=12, dt=0.016, current_beat=1):
        if not self.is_alive():
            self.state = "dead"
            return
        
        # Update stun and knockback
        self.update_stun_and_knockback(dt, collision_rects)
        
        # Don't act when stunned
        if self.is_stunned:
            self.apply_gravity(gravity, max_fall, collision_rects)
            return
        
        # Freeze completely during player invulnerability
        if player.invulnerable:
            # Stop all movement
            self.moving_left = False
            self.moving_right = False
            self.state = "patrol"
            # Still apply gravity but don't move or attack
            self.apply_gravity(gravity, max_fall, collision_rects)
            self.move(collision_rects)
            return
        
        # Normal AI behavior when player is not invulnerable
        distance_to_player = abs(player.rect.centerx - self.rect.centerx)
        
        # Decide state
        if distance_to_player < self.detection_range:
            self.state = "chase"
        else:
            self.state = "patrol"
        
        # Track if player jumped (went from on_ground to not on_ground)
        if not player.on_ground and player.y_momentum < -5:
            self.player_jumped_recently = True
            self.jump_delay_timer = self.jump_delay
        
        # Update jump delay timer
        if self.jump_delay_timer > 0:
            self.jump_delay_timer -= dt
        
        # Update random jump timer
        if self.random_jump_timer > 0:
            self.random_jump_timer -= dt
        
        # Update attack system (combo attacks on beats)
        self.update_attack_system(player, dt, current_beat)
        
        # Execute state behavior
        if self.state == "chase":
            self._chase_player(player, collision_rects, gravity, max_fall)
        elif self.state == "patrol":
            self._patrol()
        
        # Apply physics
        self.apply_gravity(gravity, max_fall, collision_rects)
        self.move(collision_rects)
    
    def _patrol(self):
        if self.rect.centerx <= self.patrol_left:
            self.patrol_direction = 1
        elif self.rect.centerx >= self.patrol_right:
            self.patrol_direction = -1
        
        if self.patrol_direction == 1:
            self.moving_right = True
            self.moving_left = False
            self.facing_right = True
        else:
            self.moving_left = True
            self.moving_right = False
            self.facing_right = False
    
    def _chase_player(self, player, collision_rects, gravity, max_fall):
        import random
        
        player_x = player.rect.centerx
        enemy_x = self.rect.centerx
        
        # Horizontal chase
        if player_x > enemy_x:
            self.moving_right = True
            self.moving_left = False
            self.facing_right = True
            self.speed = 5 * self.chase_speed_multiplier
        elif player_x < enemy_x:
            self.moving_left = True
            self.moving_right = False
            self.facing_right = False
            self.speed = 5 * self.chase_speed_multiplier
        else:
            self.moving_left = False
            self.moving_right = False
        
        # Try to jump if player is above and we saw them jump (with delay)
        player_above = player.rect.centery < self.rect.centery - self.jump_height_threshold
        if player_above and self.on_ground and self.player_jumped_recently and self.jump_delay_timer <= 0:
            self.y_momentum = self.jump_strength
            self.on_ground = False
            self.player_jumped_recently = False
        
        # Random jumping while chasing
        if self.on_ground and self.random_jump_timer <= 0:
            # 30% chance to jump when timer expires
            if random.random() < 0.3:
                self.y_momentum = self.jump_strength
                self.on_ground = False
                self.random_jump_timer = self.random_jump_cooldown + random.uniform(0, 1.0)  # 2-3 seconds
            else:
                self.random_jump_timer = 0.5  # Check again soon
    
    def update_attack_system(self, player, dt, current_beat):
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        # Check if player is in attack range
        distance_to_player = abs(player.rect.centerx - self.rect.centerx)
        
        # Start combo if close enough and cooldown is ready
        if distance_to_player < self.attack_range and self.attack_cooldown <= 0 and self.combo_state == 0:
            self.combo_state = 1
            self.combo_index = 0  # Track position in note pattern
            self.attack_cooldown = self.attack_cooldown_max
            # Get the note pattern for this enemy's combo
            self.combo_pattern = ENEMY_COMBOS["standard"]["pattern"]
            self.last_executed_note = -1  # Track which note we've executed
        
        # Execute combo based on note pattern
        if self.combo_state > 0 and self.combo_index < len(self.combo_pattern):
            current_note = self.combo_pattern[self.combo_index]
            
            # Determine which beats this note should execute on
            # Q (Quarter) notes execute on beats 1 or 3
            # E (Eighth) notes execute on beats 2 or 4
            should_execute = False
            attack_type = "stab"  # Default to stab
            
            if current_note == "Q" and current_beat in [1, 3]:
                should_execute = True
                # Alternate between stab and uppercut
                attack_type = "stab" if self.combo_index % 2 == 0 else "uppercut"
            elif current_note == "E" and current_beat in [2, 4]:
                should_execute = True
                # Eighths tend to be lighter attacks
                attack_type = "stab"
            
            # Execute the attack if conditions are met and we haven't already done this note
            if should_execute and self.last_executed_note != self.combo_index:
                self._execute_attack(player, attack_type)
                self.last_executed_note = self.combo_index
                self.combo_index += 1
                
                # If we've executed all notes in the pattern, reset
                if self.combo_index >= len(self.combo_pattern):
                    self.combo_state = 0
    
    def _execute_attack(self, player, attack_type):
        if player.invulnerable:
            return
        
        distance = abs(player.rect.centerx - self.rect.centerx)
        if distance > ENEMY['attack_range']:
            return
        
        damage = self.stats['Attack_Damage']
        if hasattr(player, 'take_damage'):
            player.take_damage(damage, is_magical=False)
        
        knockback_dir = 1 if self.facing_right else -1
        
        if attack_type == "stab":
            # Minor attack: stun and start combo (1-2 beats)
            kb_config = ENEMY['stab_knockback']
            player.apply_knockback(knockback_dir * kb_config['x'], kb_config['y'], 
                                  stun_duration=ENEMY['stab_stun'], major=False)
        elif attack_type == "uppercut":
            # Major attack: bouncing knockback effect (like Street Fighter)
            kb_config = ENEMY['uppercut_knockback']
            player.apply_knockback(knockback_dir * kb_config['x'], kb_config['y'], 
                                  stun_duration=ENEMY['uppercut_stun'], major=True)
    
    def draw(self, screen, camera_x, camera_y, color, config=None):
        screen_rect = self.rect.move(-camera_x, -camera_y)
        pygame.draw.rect(screen, color, screen_rect)
        
        # Draw health bar above enemy
        health_bar_width = 40
        health_bar_height = 4
        health_ratio = self.stats['Current_Health'] / self.stats['Max_Health']
        
        bar_x = screen_rect.centerx - health_bar_width // 2
        bar_y = screen_rect.top - 8
        
        # Background (red)
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, health_bar_width, health_bar_height))
        # Foreground (green)
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, int(health_bar_width * health_ratio), health_bar_height))


class SmallBandit(EnemyBase):
    """Small Bandit - Level 1-5"""
    def __init__(self, x=0, y=0):
        stats_config = SMALL_BANDIT.copy()
        small_bandit_stats = {
            'Current_Health': stats_config['max_health'],
            'Max_Health': stats_config['max_health'],
            'Current_Mana': 0,
            'Max_Mana': 0,
            'Attack_Damage': stats_config['attack_damage'],
            'M_Attack_Damage': 2,
            'Skill_Attack_Damage': 8,
            'Defense': stats_config['defense'],
            'M_Defense': 1
        }
        speed = PLAYER['base_speed'] * ENEMY['speed_multiplier']
        super().__init__(x, y, stats_config['width'], stats_config['height'], speed=speed, stats=small_bandit_stats)
        
        # Small bandit specific
        self.level = stats_config['level']
        self.experience_value = stats_config['exp_value']
        self.color = stats_config['color']
        self.detection_range = 180
        self.chase_speed_multiplier = 1.2


class LargeBandit(EnemyBase):
    """Large Bandit - Level 6-10"""
    def __init__(self, x=0, y=0):
        stats_config = LARGE_BANDIT.copy()
        large_bandit_stats = {
            'Current_Health': stats_config['max_health'],
            'Max_Health': stats_config['max_health'],
            'Current_Mana': 0,
            'Max_Mana': 0,
            'Attack_Damage': stats_config['attack_damage'],
            'M_Attack_Damage': 5,
            'Skill_Attack_Damage': 15,
            'Defense': stats_config['defense'],
            'M_Defense': 2
        }
        speed = PLAYER['base_speed'] * ENEMY['speed_multiplier']
        super().__init__(x, y, stats_config['width'], stats_config['height'], speed=speed, stats=large_bandit_stats)
        
        # Large bandit specific
        self.level = stats_config['level']
        self.experience_value = stats_config['exp_value']
        self.color = stats_config['color']
        self.detection_range = 220
        self.chase_speed_multiplier = 1.1
        self.jump_height_threshold = 120