import pygame
import random

from Assets.GameBalance import PLAYER, ENEMY, SMALL_BANDIT, LARGE_BANDIT, EXPERIENCE, get_enemy_stats, get_player_level_stats
from Assets.AttackConfig import AttackConfig

class CharacterBase:
    def __init__(self, x=0, y=0, width=64, height=64, speed=5, stats=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.velocity_x = 0  # Smooth horizontal velocity
        self.acceleration = 1.2  # How fast we speed up
        self.friction = 0.85  # How fast we slow down
        self.moving_left = False
        self.moving_right = False
        self.y_momentum = 0
        self.on_ground = False
        
        # Knockback system
        self.is_stunned = False
        self.stun_timer = 0  # Time remaining in stun
        self.x_momentum = 0  # Momentum-based horizontal knockback
        
        # Default stats structure
        if stats is None:
            self.stats = {
                'Max_Health': 100,
                'Current_Health': 100,
                'Max_Mana': 50,
                'Current_Mana': 50,
                'Attack_Damage': 10,
                'Defense': 5,
                'Speed': speed
            }
        else:
            self.stats = stats.copy()

    def move(self, rects=None):
        """Handle horizontal movement with acceleration/deceleration"""
        if self.is_stunned:
            # Clear movement flags when stunned so they can be restored after
            self.moving_left = False
            self.moving_right = False
            return
        
        # Acceleration based movement
        if self.moving_left:
            self.velocity_x -= self.acceleration
            self.velocity_x = max(self.velocity_x, -self.speed)
        elif self.moving_right:
            self.velocity_x += self.acceleration
            self.velocity_x = min(self.velocity_x, self.speed)
        else:
            # Apply friction when not actively moving
            self.velocity_x *= self.friction
            if abs(self.velocity_x) < 0.1:
                self.velocity_x = 0
        
        # Apply horizontal movement
        if self.velocity_x != 0:
            self.rect.x += self.velocity_x
            
            # Handle horizontal collisions
            if rects:
                for rect in rects:
                    if self.rect.colliderect(rect):
                        if self.velocity_x > 0:  # Moving right
                            self.rect.right = rect.left
                        else:  # Moving left
                            self.rect.left = rect.right
                        self.velocity_x = 0

    def apply_gravity(self, gravity=0.8, max_fall=14, rects=None):
        """Apply gravity and handle vertical collisions"""
        self.on_ground = False
        self.y_momentum += gravity
        if self.y_momentum > max_fall:
            self.y_momentum = max_fall
        
        self.rect.y += self.y_momentum
        
        if rects:
            for rect in rects:
                if self.rect.colliderect(rect):
                    if self.y_momentum > 0:  # Falling
                        self.rect.bottom = rect.top
                        self.y_momentum = 0
                        self.on_ground = True
                    elif self.y_momentum < 0:  # Rising
                        self.rect.top = rect.bottom
                        self.y_momentum = 0
    
    def teleport_jump(self, rects, distance):
        """Teleport upward by distance pixels, stopping at obstacles"""
        if not self.on_ground:
            return
        
        original_y = self.rect.y
        target_y = self.rect.y - distance
        step = 10
        
        # Move upward in steps, checking for collisions
        while self.rect.y > target_y:
            self.rect.y -= step
            
            # Check for ceiling collision
            if rects:
                for rect in rects:
                    if self.rect.colliderect(rect):
                        # Hit ceiling, stop here
                        self.rect.bottom = rect.bottom
                        self.y_momentum = 0
                        return
            
            # Don't go above target
            if self.rect.y < target_y:
                self.rect.y = target_y
                break
        
        # Set upward momentum after teleport
        self.y_momentum = -5
    
    def apply_knockback(self, knockback_x, knockback_y, stun_duration=0.3, major=False):
        """Apply knockback force and stun the character"""
        self.x_momentum = knockback_x
        self.y_momentum = knockback_y
        self.is_stunned = True
        self.stun_timer = stun_duration
    
    def update_stun_and_knockback(self, dt, rects):
        """Update stun state and apply knockback momentum"""
        if self.is_stunned:
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.is_stunned = False
                self.stun_timer = 0
                
                # Restore movement input when stun ends
                keys = pygame.key.get_pressed()
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    self.moving_left = True
                if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    self.moving_right = True
        
        # Apply horizontal knockback momentum
        if abs(self.x_momentum) > 0.1:
            old_x = self.rect.x
            self.rect.x += self.x_momentum
            
            # Check horizontal collisions
            if rects:
                for rect in rects:
                    if self.rect.colliderect(rect):
                        self.rect.x = old_x
                        self.x_momentum = 0
                        break
            
            # Apply friction to knockback
            self.x_momentum *= 0.92
            if abs(self.x_momentum) < 0.1:
                self.x_momentum = 0
    
    def take_damage(self, damage, is_magical=False):
        """Take damage and reduce health"""
        defense = self.stats.get('M_Defense' if is_magical else 'Defense', 0)
        actual_damage = max(1, damage - defense)
        self.stats['Current_Health'] -= actual_damage
        if self.stats['Current_Health'] < 0:
            self.stats['Current_Health'] = 0
    
    def heal(self, amount):
        """Restore health"""
        self.stats['Current_Health'] += amount
        max_health = self.stats.get('Max_Health', 100)
        if self.stats['Current_Health'] > max_health:
            self.stats['Current_Health'] = max_health
    
    def use_mana(self, amount):
        """Use mana for abilities"""
        if self.stats['Current_Mana'] >= amount:
            self.stats['Current_Mana'] -= amount
            return True
        return False
    
    def restore_mana(self, amount):
        """Restore mana"""
        self.stats['Current_Mana'] += amount
        max_mana = self.stats.get('Max_Mana', 50)
        if self.stats['Current_Mana'] > max_mana:
            self.stats['Current_Mana'] = max_mana
    
    def is_alive(self):
        """Check if character is alive"""
        return self.stats['Current_Health'] > 0
    
    def get_stat(self, stat_name):
        """Get a stat value"""
        return self.stats.get(stat_name, 0)
    
    def set_stat(self, stat_name, value):
        """Set a stat value with bounds checking"""
        if stat_name in self.stats:
            self.stats[stat_name] = value
            # Apply bounds for health/mana
            if stat_name == 'Current_Health':
                self.stats['Current_Health'] = max(0, min(self.stats['Current_Health'], self.stats['Max_Health']))
            elif stat_name == 'Current_Mana':
                self.stats['Current_Mana'] = max(0, min(self.stats['Current_Mana'], self.stats['Max_Mana']))
    
    def modify_stat(self, stat_name, amount):
        """Modify a stat by an amount"""
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
        
        # Keep facing direction for movement
        self.facing_right = True
        
        # Block system
        self.is_blocking = False
        self.block_frame = 0
        self.block_duration = 30  # frames
        
        # Hit stun system
        self.hit_stun_frames = 0
        self.hit_flash_timer = 0
        
        # Attack system
        self.current_attack = None
        self.attack_frame = 0
        self.attack_start_beat = 0
        self.attack_windup_beats = 0
        self.attack_active_beats = 0
        self.attack_recovery_beats = 0
        self.current_attack_variant = None
        self.last_attack_time = 0
        self.combo_timeout = 0.5
        self.is_comboing = False
        self.active_combo_sequence = None
        self.combo_flash_timer = 0
        
        # Stat allocation system
        self.free_stat_points = 0
        
        # Gold system
        self.gold = 0
    
    def gain_experience(self, amount):
        """Gain experience points and level up if enough"""
        self.experience += amount
        while self.experience >= self.exp_for_next_level:
            self.level_up()
    
    def level_up(self):
        """Level up the player and increase stats"""
        self.experience -= self.exp_for_next_level
        self.level += 1
        
        # Get stat increases for this level
        level_stats = get_player_level_stats(self.level)
        
        # Update player stats
        for stat_name, new_value in level_stats.items():
            self.stats[stat_name.replace('_', ' ').title().replace(' ', '_')] = new_value
        
        # Grant free stat points for allocation
        self.free_stat_points += 3
        
        # Full heal on level up
        self.stats['Current_Health'] = self.stats['Max_Health']
        self.stats['Current_Mana'] = self.stats['Max_Mana']
        
        # Increase exp needed for next level
        self.exp_for_next_level = int(self.exp_for_next_level * 1.2)
        
        print(f"Level up! Now level {self.level}. Gained 3 stat points!")
        self.stats['Current_Health'] = self.stats['Max_Health']
        self.stats['Current_Mana'] = self.stats['Max_Mana']
        
        # Increase exp needed for next level
        self.exp_for_next_level = int(self.exp_for_next_level * 1.2)
        
        print(f"Level up! Now level {self.level}")
    
    def start_block(self):
        """Start blocking"""
        if not self.is_stunned:
            self.is_blocking = True
    
    def perform_attack(self, attack_type, rhythm_multiplier=1.0):
        """Perform an attack with rhythm-based damage
        
        Args:
            attack_type: Type of attack ("neutral", "forward", "down")
            rhythm_multiplier: Damage multiplier from rhythm system
        """
        # Get attack config
        attack_reach = AttackConfig.get_reach(attack_type)
        attack_damage_mod = AttackConfig.get_damage_multiplier(attack_type)
        
        # Calculate base damage
        base_damage = self.stats.get('Attack_Damage', 3)
        
        # Apply config multiplier
        config_damage = base_damage * attack_damage_mod
        
        # Apply rhythm multiplier (from timing and combo)
        final_damage = int(config_damage * rhythm_multiplier)
        
        # Store attack data for collision detection
        self.current_attack = {
            "damage": final_damage,
            "knockback_x": 12,
            "knockback_y": -2,
            "range": attack_reach,
            "type": attack_type,
            "active": True
        }
        
        return final_damage
    
    def take_damage(self, damage, is_magical=False):
        """Take damage with blocking consideration"""
        # Check if blocking
        if self.is_blocking:
            damage = max(1, damage // 4)  # Block reduces damage to 25%
        
        # Apply damage
        super().take_damage(damage, is_magical)
        self.hit_stun_frames = 30  # Brief stun
        self.hit_flash_timer = 0
    
    def move(self, rects=None):
        """Enhanced movement for player"""
        # Don't move if blocking
        if self.is_blocking:
            self.moving_left = False
            self.moving_right = False
        
        # Update facing direction
        if self.moving_right:
            self.facing_right = True
        elif self.moving_left:
            self.facing_right = False
        
        # Call parent movement (no attack-related slowdown)
        super().move(rects)


class Merchant(CharacterBase):
    def __init__(self, x=0, y=0):
        super().__init__(x, y, 48, 48, speed=0)  # Merchants don't move
        

class EnemyBase(CharacterBase):
    def __init__(self, x=0, y=0, width=48, height=48, speed=5, stats=None):
        super().__init__(x, y, width, height, speed, stats)
        
        # AI state
        self.ai_state = "patrol"  # patrol, chase
        self.detection_range = 200
        self.patrol_center = x
        self.patrol_range = 100
        self.patrol_direction = random.choice([-1, 1])
        
        # Health bar
        self.max_health = stats['Max_Health'] if stats else 50
        self.health_bar_timer = 0
        self.health_bar_duration = 3.0  # Show health bar for 3 seconds after taking damage
    
    def update_ai(self, player, collision_rects, gravity=0.7, max_fall=12, dt=0.016, current_beat=1, current_frame=0):
        """Update enemy AI behavior"""
        if self.is_stunned:
            self.update_stun_and_knockback(dt, collision_rects)
            self.apply_gravity(gravity, max_fall, collision_rects)
            return
        
        # Calculate distance to player
        distance_to_player = abs(self.rect.centerx - player.rect.centerx)
        
        # State machine - only patrol and chase, no attacking
        if distance_to_player <= self.detection_range:
            self.ai_state = "chase"
        else:
            self.ai_state = "patrol"
        
        # Execute state behavior
        if self.ai_state == "patrol":
            self._patrol()
        elif self.ai_state == "chase":
            self._chase_player(player, collision_rects, gravity, max_fall)
        
        # Update health bar timer
        if self.health_bar_timer > 0:
            self.health_bar_timer -= dt
        
        # Apply physics
        self.apply_gravity(gravity, max_fall, collision_rects)
    
    def _patrol(self):
        """Simple patrol behavior"""
        # Move towards patrol bounds
        if self.rect.centerx < self.patrol_center - self.patrol_range:
            self.patrol_direction = 1
        elif self.rect.centerx > self.patrol_center + self.patrol_range:
            self.patrol_direction = -1
        
        # Move in patrol direction
        if self.patrol_direction > 0:
            self.moving_right = True
            self.moving_left = False
        else:
            self.moving_left = True
            self.moving_right = False
    
    def _chase_player(self, player, collision_rects, gravity, max_fall):
        """Chase the player"""
        if player.rect.centerx > self.rect.centerx:
            self.moving_right = True
            self.moving_left = False
        else:
            self.moving_left = True
            self.moving_right = False
        
        # Move towards player
        self.move(collision_rects)
    
    def take_damage(self, damage, is_magical=False):
        """Take damage and show health bar"""
        super().take_damage(damage, is_magical)
        self.health_bar_timer = self.health_bar_duration
        
        # Simple knockback when taking damage
        knockback_x = random.choice([-5, 5])
        self.apply_knockback(knockback_x, -2, 0.1)
    
    def draw(self, screen, camera_x, camera_y, color, config=None):
        """Draw enemy with health bar if recently damaged"""
        # Draw enemy
        screen_rect = self.rect.move(-camera_x, -camera_y)
        pygame.draw.rect(screen, color, screen_rect)
        
        # Draw health bar if recently damaged
        if self.health_bar_timer > 0:
            bar_width = 40
            bar_height = 4
            bar_x = screen_rect.centerx - bar_width // 2
            bar_y = screen_rect.top - 10
            
            # Background
            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            
            # Health bar
            health_percentage = self.stats['Current_Health'] / self.max_health
            health_width = int(bar_width * health_percentage)
            health_color = (255, 0, 0) if health_percentage < 0.3 else (255, 255, 0) if health_percentage < 0.6 else (0, 255, 0)
            pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height))


class SmallBandit(EnemyBase):
    """Small Bandit - Level 1-5"""
    def __init__(self, x=0, y=0):
        stats = get_enemy_stats("small")
        super().__init__(x, y, SMALL_BANDIT['width'], SMALL_BANDIT['height'], stats['speed'], stats)


class LargeBandit(EnemyBase):
    """Large Bandit - Level 6-10"""
    def __init__(self, x=0, y=0):
        stats = get_enemy_stats("large")
        super().__init__(x, y, LARGE_BANDIT['width'], LARGE_BANDIT['height'], stats['speed'], stats)
        self.speed = speed
        self.velocity_x = 0  # Smooth horizontal velocity
        self.acceleration = 1.2  # How fast we speed up
        self.friction = 0.85  # How fast we slow down
        self.moving_left = False
        self.moving_right = False
        self.y_momentum = 0
        self.on_ground = False
        
        # Knockback system
        self.is_stunned = False
        self.stun_timer = 0  # Time remaining in stun
        self.stun_timer = 0
        self.x_momentum = 0  # Momentum-based horizontal knockback
        
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
        
        # Smooth acceleration-based movement
        if self.moving_left:
            self.velocity_x -= self.acceleration
        elif self.moving_right:
            self.velocity_x += self.acceleration
        else:
            # Apply friction when not moving
            self.velocity_x *= self.friction
            # Stop completely when very slow
            if abs(self.velocity_x) < 0.1:
                self.velocity_x = 0
        
        # Clamp velocity to max speed
        if self.velocity_x > self.speed:
            self.velocity_x = self.speed
        elif self.velocity_x < -self.speed:
            self.velocity_x = -self.speed
        
        # Apply horizontal movement
        self.rect.x += self.velocity_x
        for r in rects:
            if self.rect.colliderect(r):
                if self.velocity_x > 0:
                    self.rect.right = r.left
                elif self.velocity_x < 0:
                    self.rect.left = r.right
                self.velocity_x = 0

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
    
    def apply_knockback(self, knockback_x, knockback_y, stun_duration=0.3, major=False):
        """Apply momentum-based knockback to character"""
        # Set horizontal momentum (how fast to push character, will decelerate naturally)
        self.x_momentum = knockback_x * 0.5  # Subtle momentum, will slow down each frame
        
        # Stun the character during knockback
        self.is_stunned = True
        self.stun_timer = stun_duration  # Track stun time remaining
    
    def update_stun_and_knockback(self, dt, rects):
        # Update stun timer
        if self.is_stunned and hasattr(self, 'stun_timer'):
            self.stun_timer -= dt
            if self.stun_timer <= 0:
                self.is_stunned = False
                self.stun_timer = 0
        
        # Apply x_momentum knockback (natural deceleration each frame)
        if abs(self.x_momentum) > 0.1:
            self.rect.x += self.x_momentum
            
            # Platform collision checks
            for r in rects:
                if self.rect.colliderect(r):
                    if self.x_momentum > 0:
                        self.rect.right = r.left
                    else:
                        self.rect.left = r.right
                    self.x_momentum = 0
                    break
            
            # Friction: gradually slow down
            self.x_momentum *= 0.92
    
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
        
        # Store original speed for rhythm boosts
        self.original_speed = PLAYER['base_speed']
        
        # RHYTHM SYSTEM - All actions tied to musical beats
        self.rhythm_system = {
            'last_beat_action': 0,      # Last beat when an action was performed
            'beat_window': 0.2,         # How close to beat you need to be (±0.2 beats)
            'perfect_window': 0.1,      # Perfect timing window (±0.1 beats)
            'action_queue': [],         # Queue of pending rhythm actions
            'combo_count': 0,           # Current rhythm combo count
            'last_action_type': None,   # Last action performed
        }
        
        # Keep facing direction for movement
        self.facing_right = True
        
        # Block/Counter system
        self.is_blocking = False
        self.block_frame = 0
        self.block_duration = 30  # frames
        self.can_counter = False
        self.counter_window = 30  # frames to counter after enemy telegraph
        self.last_enemy_telegraph_frame = -999
        
        # Hit stun system
        self.hit_stun_frames = 0
        self.hit_flash_timer = 0
        
        # ATTACK HITBOX CONFIGURATION - Easy to edit!
        self.attack_hitbox_config = {
            'width': 80,           # Width of attack hitbox
            'height': 60,          # Height of attack hitbox
            'offset_x': 70,        # How far in front of player
            'offset_y': 0,         # Vertical offset from player center
            'color': (255, 0, 0),  # Red color for hitbox
            'alpha': 100           # Transparency (0-255, lower = more transparent)
        }
    
    def update_attack(self, current_beat, bpm, dt=0.016):
        """Update attack animation with beat-based timing
        
        Args:
            current_beat: Current musical beat (float)
            bpm: Current BPM of the music
            dt: Delta time since last frame in seconds
        """
        import time
        
        # Update hit stun
        if self.hit_stun_frames > 0:
            self.hit_stun_frames -= 1
            self.hit_flash_timer += 1
        
        # Update blocking
        if self.is_blocking:
            self.block_frame += 1
            if self.block_frame >= self.block_duration:
                self.is_blocking = False
                self.block_frame = 0
        
        # Update combo state
        time_since_last_attack = time.time() - self.last_attack_time
        if time_since_last_attack > self.combo_timeout:
            self.is_comboing = False
        
        # Update combo flash effect
        if self.active_combo_sequence:
            self.combo_flash_timer += 1
            if self.combo_flash_timer > 30:  # Flash for 30 frames
                self.active_combo_sequence = None
                self.combo_flash_timer = 0
        
        # Update attack animation (beat-based)
        if self.is_attacking:
            self.attack_frame += 1  # Still increment for visual effects
            beats_elapsed = current_beat - self.attack_start_beat
            total_beats = self.attack_windup_beats + self.attack_active_beats + self.attack_recovery_beats
            
            # Safety check: if beat counter reset or went backward, use frame-based timeout
            if beats_elapsed < 0 or current_beat == 0:
                # Fall back to frame-based timing (60 FPS)
                max_frames = int(total_beats * 60)  # Assume ~1 beat per second at average BPM
                if self.attack_frame >= max_frames:
                    self.is_attacking = False
                    self.attack_frame = 0
                    self.current_attack_variant = None
            else:
                # Convert beats to frames for visual effects
                seconds_per_beat = 60.0 / bpm
                total_seconds = total_beats * seconds_per_beat
                total_frames = int(total_seconds * 60)  # 60 FPS
                
                # End attack when total beat duration is reached
                if beats_elapsed >= total_beats:
                    self.is_attacking = False
                    self.attack_frame = 0
                    self.current_attack_variant = None
                
                # Also set legacy frame-based timings for visual effects
                self.attack_windup_frames = int(self.attack_windup_beats * seconds_per_beat * 60)
                self.attack_active_frames = int(self.attack_active_beats * seconds_per_beat * 60)
                self.attack_recovery_frames = int(self.attack_recovery_beats * seconds_per_beat * 60)
    
    def can_attack(self, current_beat):
        """Check if player can attack on this beat"""
        # Can't attack if already attacking, hit stunned, or blocking
        if self.is_attacking or self.hit_stun_frames > 0 or self.is_blocking:
            return False
        
        # Main character has no cooldown - can attack anytime they're not busy
        return True
    
    def start_attack(self, current_beat, attack_data=None):
        """Start a new attack
        
        Args:
            current_beat: Current musical beat
            attack_data: Optional dictionary with attack properties
        """
        import time
        
        # Default attack data if none provided
        if attack_data is None:
            attack_data = {
                "name": "Slash",
                "damage_multiplier": 1.0,
                "knockback_multiplier": 1.0,
                "range": 100,
                "windup_beats": 0.25,
                "active_beats": 0.5,
                "recovery_beats": 0.25,
                "total_beats": 1.0,
            }
        
        # Set attack properties from attack_data
        self.is_attacking = True
        self.attack_frame = 0
        self.attack_start_beat = current_beat
        self.current_attack_variant = attack_data
        self.attack_type = attack_data.get('name', 'Slash')
        
        # Set beat-based timing
        self.attack_windup_beats = attack_data.get('windup_beats', 0.25)
        self.attack_active_beats = attack_data.get('active_beats', 0.5)
        self.attack_recovery_beats = attack_data.get('recovery_beats', 0.25)
        
        # Main character has no attack cooldown - can attack immediately after previous attack ends
        
        # Update combo state
        self.is_comboing = True
        self.last_attack_time = time.time()
    
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
    
    def get_attack_hitbox(self, current_beat):
        """Get the current attack hitbox rectangle (only during active phase)
        
        Args:
            current_beat: Current musical beat
        """
        if not self.is_attacking:
            return None
        
        # Calculate which phase we're in
        beats_elapsed = current_beat - self.attack_start_beat
        
        # If beat timing is unreliable (negative or too small), use frame-based timing instead
        if beats_elapsed < 0 or (beats_elapsed == 0 and self.attack_frame > 5):
            # Fallback to frame-based timing
            windup_frames = max(5, int(self.attack_windup_beats * 60))  # At least 5 frames windup
            active_frames = max(10, int(self.attack_active_beats * 60))  # At least 10 frames active
            
            if self.attack_frame < windup_frames:
                return None  # Still winding up
            if self.attack_frame >= windup_frames + active_frames:
                return None  # Recovery phase
        else:
            # Use beat-based timing
            # Only show hitbox during active phase (after wind-up)
            if beats_elapsed < self.attack_windup_beats:
                return None  # Still winding up
            if beats_elapsed >= self.attack_windup_beats + self.attack_active_beats:
                return None  # Recovery phase
        
        # If we have an active combo sequence, use larger hitbox
        if self.active_combo_sequence:
            config = {
                'width': 120,
                'height': 80,
                'offset_x': 90,
                'offset_y': 0,
            }
        else:
            config = self.attack_hitbox_config
        
        # Calculate hitbox position based on facing direction and attack type
        if self.current_attack_variant and self.current_attack_variant.get('angle') == 'down':
            # Down attack - hitbox below player
            hitbox_x = self.rect.centerx - config['width'] // 2
            hitbox_y = self.rect.bottom - 10
        else:
            # Forward attack - hitbox in front based on facing direction
            if self.facing_right:
                hitbox_x = self.rect.right + config['offset_x'] - config['width']
            else:
                hitbox_x = self.rect.left - config['offset_x']
            hitbox_y = self.rect.centery - config['height'] // 2 + config.get('offset_y', 0)
        
        # Debug: Print hitbox info
        hitbox = pygame.Rect(hitbox_x, hitbox_y, config['width'], config['height'])
        # print(f"Hitbox created: x={hitbox_x}, y={hitbox_y}, w={config['width']}, h={config['height']}")
        
        return hitbox
    
    def check_attack_hits(self, entities, current_beat):
        """Check if attack hits any entities, returns list of hit entities"""
        hitbox = self.get_attack_hitbox(current_beat)
        if not hitbox:
            return []
        
        hits = []
        for entity in entities:
            if hasattr(entity, 'rect') and hitbox.colliderect(entity.rect):
                hits.append(entity)
        
        return hits
    
    def start_block(self):
        """Start blocking"""
        if not self.is_attacking and self.hit_stun_frames <= 0:
            self.is_blocking = True
            self.block_frame = 0
    
    def take_damage(self, damage, is_magical=False):
        """Override to add hit stun"""
        # Check if blocking
        if self.is_blocking:
            # Blocked! No damage, no stun
            return 0
        
        # Take damage normally
        actual_damage = super().take_damage(damage, is_magical)
        
        # Add hit stun
        self.hit_stun_frames = 15  # Stunned for 15 frames (~0.25 seconds at 60fps)
        self.is_attacking = False  # Cancel current attack
        self.attack_frame = 0
        
        return actual_damage
    
    def register_enemy_telegraph(self, frame_number):
        """Register when an enemy starts telegraphing an attack"""
        self.last_enemy_telegraph_frame = frame_number
    
    def attempt_counter(self, current_frame):
        """Try to counter an incoming attack"""
        # Check if within counter window
        frames_since_telegraph = current_frame - self.last_enemy_telegraph_frame
        if 0 <= frames_since_telegraph <= self.counter_window and self.is_blocking:
            return True  # Successful counter!
        return False
    
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
        self.chase_speed_multiplier = ENEMY.get('chase_speed_multiplier', 0.33)
        self.patrol_speed_multiplier = ENEMY.get('patrol_speed_multiplier', 0.15)
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
        self.attack_cooldown_max = 2.0  # Seconds between attacks
        
        # Attack telegraph and wind-up
        self.is_telegraphing = False
        self.telegraph_frame = 0
        self.telegraph_duration = 20  # frames before attack (telegraph)
        self.attack_windup_frames = 15  # frames to wind up attack
        self.attack_active_frames = 10  # frames attack hitbox is active
        self.is_executing_attack = False
        self.attack_execution_frame = 0
        
        # Hit stun (can't attack when hit)
        self.hit_stun_frames = 0
        self.hit_flash_timer = 0
    
    def update_ai(self, player, collision_rects, gravity=0.7, max_fall=12, dt=0.016, current_beat=1, current_frame=0):
        """Simple AI: Chase player when within 500px, patrol otherwise"""
        if not self.is_alive():
            self.state = "dead"
            return
        
        # Update stun and knockback
        self.update_stun_and_knockback(dt, collision_rects)
        
        # Don't act when stunned
        if self.is_stunned:
            self.moving_left = False
            self.moving_right = False
            self.apply_gravity(gravity, max_fall, collision_rects)
            self.move(collision_rects)
            return
        
        # Simple AI decision: Chase if player is within 500 pixels
        distance_to_player = abs(player.rect.centerx - self.rect.centerx)
        
        if distance_to_player < 500:
            self.state = "chase"
            self._chase_player(player, collision_rects, gravity, max_fall)
        else:
            self.state = "patrol"
            self._patrol()
        
        # Attack if player is in range
        self.update_attack_system(player, dt, current_beat)
        
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
            self.speed = 5 * self.patrol_speed_multiplier  # Use slower patrol speed
        else:
            self.moving_left = True
            self.moving_right = False
            self.facing_right = False
            self.speed = 5 * self.patrol_speed_multiplier  # Use slower patrol speed
    
    def _chase_player(self, player, collision_rects, gravity, max_fall):
        """Chase player at 0.3x their speed, slowing down as we get closer"""
        player_x = player.rect.centerx
        enemy_x = self.rect.centerx
        player_speed = 7  # Config.PLAYER_SPEED
        
        # Calculate distance to player
        distance_to_player = abs(player_x - enemy_x)
        
        # Speed reduces as we get closer (careful approach)
        # Full speed at 400+ px, half speed at 150-400 px, quarter speed at 0-150 px
        if distance_to_player > 400:
            chase_speed = player_speed * 0.3  # Full chase speed
        elif distance_to_player > 150:
            chase_speed = player_speed * 0.15  # Half chase speed (getting close)
        else:
            chase_speed = player_speed * 0.08  # Quarter speed (very close, careful)
        
        # Horizontal chase
        if player_x > enemy_x:
            self.moving_right = True
            self.moving_left = False
            self.facing_right = True
            self.speed = chase_speed
        elif player_x < enemy_x:
            self.moving_left = True
            self.moving_right = False
            self.facing_right = False
            self.speed = chase_speed
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
    
    def update_attack_system(self, player, dt, current_beat, current_frame=0):
        """Attack system with telegraph and wind-up"""
        # Update hit stun
        if self.hit_stun_frames > 0:
            self.hit_stun_frames -= 1
            self.hit_flash_timer += 1
            return  # Can't attack while stunned
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        
        # Handle telegraph phase
        if self.is_telegraphing:
            self.telegraph_frame += 1
            if self.telegraph_frame >= self.telegraph_duration:
                # Telegraph done, start attack execution
                self.is_telegraphing = False
                self.is_executing_attack = True
                self.attack_execution_frame = 0
            return
        
        # Handle attack execution
        if self.is_executing_attack:
            self.attack_execution_frame += 1
            
            # Wind-up phase
            if self.attack_execution_frame < self.attack_windup_frames:
                return  # Still winding up
            
            # Active attack phase - hit player once
            if self.attack_execution_frame == self.attack_windup_frames:
                # Check if player countered
                if hasattr(player, 'attempt_counter') and player.attempt_counter(current_frame):
                    # Player countered! Enemy takes damage and gets stunned
                    self.take_damage(player.stats['Attack_Damage'] * 1.5, is_magical=False)
                    self.is_executing_attack = False
                    self.attack_execution_frame = 0
                    self.attack_cooldown = self.attack_cooldown_max
                    return
                
                # Normal attack execution
                attack_type = "stab" if random.random() < 0.7 else "uppercut"
                self._execute_attack(player, attack_type)
            
            # Check if attack is complete
            if self.attack_execution_frame >= self.attack_windup_frames + self.attack_active_frames:
                self.is_executing_attack = False
                self.attack_execution_frame = 0
                self.attack_cooldown = self.attack_cooldown_max
            return
        
        # Check if should start new attack
        distance_to_player = abs(player.rect.centerx - self.rect.centerx)
        if distance_to_player < self.attack_range and self.attack_cooldown <= 0:
            # Start telegraph
            self.is_telegraphing = True
            self.telegraph_frame = 0
            # Notify player for counter window
            if hasattr(player, 'register_enemy_telegraph'):
                player.register_enemy_telegraph(current_frame)
    
    def take_damage(self, damage, is_magical=False):
        """Override to add hit stun and cancel attacks"""
        actual_damage = super().take_damage(damage, is_magical)
        
        # Add hit stun - can't attack for a bit
        self.hit_stun_frames = 20  # Stunned for 20 frames
        
        # Cancel any ongoing attacks
        self.is_telegraphing = False
        self.is_executing_attack = False
        self.telegraph_frame = 0
        self.attack_execution_frame = 0
        
        return actual_damage
    
    def _execute_attack(self, player, attack_type):
        distance = abs(player.rect.centerx - self.rect.centerx)
        if distance > ENEMY['attack_range']:
            return
        
        damage = self.stats['Attack_Damage']
        if hasattr(player, 'take_damage'):
            player.take_damage(damage, is_magical=False)
        
        knockback_dir = 1 if self.facing_right else -1
        
        if attack_type == "stab":
            # Minor attack: brief stun with light knockback
            kb_config = ENEMY['stab_knockback']
            player.apply_knockback(knockback_dir * kb_config['x'], kb_config['y'], 
                                  stun_duration=ENEMY['stab_stun'], major=False)
        elif attack_type == "uppercut":
            # Major attack: stronger knockback with longer stun
            kb_config = ENEMY['uppercut_knockback']
            player.apply_knockback(knockback_dir * kb_config['x'], kb_config['y'], 
                                  stun_duration=ENEMY['uppercut_stun'], major=False)
    
    def draw(self, screen, camera_x, camera_y, color, config=None):
        screen_rect = self.rect.move(-camera_x, -camera_y)
        
        # Flash when hit
        if self.hit_stun_frames > 0 and self.hit_flash_timer % 4 < 2:
            # Draw white when hit
            pygame.draw.rect(screen, (255, 255, 255), screen_rect)
        else:
            pygame.draw.rect(screen, color, screen_rect)
        
        # Draw telegraph indicator (red glow) when telegraphing attack
        if self.is_telegraphing:
            telegraph_progress = self.telegraph_frame / self.telegraph_duration
            glow_size = int(10 + telegraph_progress * 40)
            glow_alpha = int(50 + telegraph_progress * 150)
            glow_surf = pygame.Surface((screen_rect.width + glow_size, screen_rect.height + glow_size), pygame.SRCALPHA)
            glow_color = (255, 50, 50, glow_alpha)  # Red glow that intensifies
            pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=8)
            screen.blit(glow_surf, (screen_rect.x - glow_size//2, screen_rect.y - glow_size//2))
        
        # Draw wind-up indicator (orange) when executing attack wind-up
        if self.is_executing_attack and self.attack_execution_frame < self.attack_windup_frames:
            windup_progress = self.attack_execution_frame / self.attack_windup_frames
            glow_size = int(15 + windup_progress * 35)
            glow_surf = pygame.Surface((screen_rect.width + glow_size, screen_rect.height + glow_size), pygame.SRCALPHA)
            glow_color = (255, 150, 0, int(120 * windup_progress))  # Orange glow
            pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=8)
            screen.blit(glow_surf, (screen_rect.x - glow_size//2, screen_rect.y - glow_size//2))
        
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