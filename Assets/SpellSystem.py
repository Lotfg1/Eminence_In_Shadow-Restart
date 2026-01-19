# Assets/SpellSystem.py
"""
Spell Casting System - Hold Shift + Type words on beat
Features shaky text display with Grape Soda font
"""

import pygame
import math
import random
import os
import time

# Font path
GRAPE_SODA_PATH = os.path.join("Assets", "Fonts", "GrapeSoda.ttf")


def get_grape_font(size):
    """Get Grape Soda font if available"""
    return pygame.font.Font(GRAPE_SODA_PATH if os.path.exists(GRAPE_SODA_PATH) else None, size)


class Spell:
    """Individual spell definition"""
    def __init__(self, spell_id, name, word, beats_allowed, mana_percent, damage_per_mana, description, effect_type):
        self.spell_id = spell_id
        self.name = name
        self.word = word.upper()  # The word to type
        self.beats_allowed = beats_allowed  # How many beats to complete
        self.mana_percent = mana_percent  # Percentage of max mana to use
        self.damage_per_mana = damage_per_mana  # Damage dealt per mana spent
        self.description = description
        self.effect_type = effect_type  # "atomic", "sneak", "dash"
        self.cooldown = 2.0  # Cooldown in seconds
        self.last_used = 0
    
    def get_mana_cost(self, player):
        """Calculate mana cost based on player's max mana"""
        max_mana = player.stats.get('Max_Mana', 100)
        raw_cost = max_mana * (self.mana_percent / 100.0)
        # Round: up if 0.5 or more, down if less
        return round(raw_cost)
    
    def get_damage(self, mana_used, player):
        """Calculate damage based on mana used and skill attack"""
        skill_attack = player.stats.get('Skill_Attack_Damage', 0)
        multiplier = 1 + 0.01 * skill_attack
        return int(self.damage_per_mana * mana_used * multiplier)


# Define the three spells
SPELLS = {
    "atomic": Spell(
        "atomic",
        "Atomic",
        "ATOMIC",
        4,    # 4 beats to type
        50,   # 50% of max mana
        2,    # 2 damage per mana
        "Type ATOMIC within 4 beats. Creates a massive screen-wide explosion.",
        "atomic"
    ),
    "sneak": Spell(
        "sneak",
        "Sneak Attack",
        "FEINT",
        6,    # 6 beats window
        10,   # 10% of max mana
        3,    # 3 damage per mana
        "Type FEINT and stand still. Counter-attack when hit, taking no damage.",
        "sneak"
    ),
    "dash": Spell(
        "dash",
        "Mana Burst",
        "DASH",
        3,    # 3 beats to type
        20,   # 20% of max mana
        1,    # 1 damage per mana
        "Type DASH within 3 beats. Teleport behind the furthest enemy.",
        "dash"
    )
}


class SpellCastingSystem:
    """
    Handles spell input while holding Shift.
    Displays shaky text with underscore cursor.
    """
    
    def __init__(self, audio_system):
        self.audio_system = audio_system
        
        # Input state
        self.shift_held = False
        self.typed_text = ""
        self.casting_start_beat = None
        self.casting_start_time = None
        
        # Sneak attack state
        self.sneak_active = False
        self.sneak_start_beat = None
        self.sneak_start_time = None
        self.player_sneak_pos = None  # Position when sneak started
        
        # Visual effects
        self.atomic_effect_active = False
        self.atomic_effect_timer = 0
        self.atomic_effect_phase = None  # "shrink" or "expand"
        self.atomic_effect_radius = 0
        
        self.dash_effect_active = False
        self.dash_effect_timer = 0
        self.dash_target_pos = None
        
        # Fonts
        self.font = get_grape_font(48)
        self.small_font = get_grape_font(24)
        
        # Shake animation
        self.shake_timer = 0
        
        # Spell result message
        self.result_message = ""
        self.result_timer = 0
        
        # Spell cooldowns
        self.cooldowns = {spell_id: 0 for spell_id in SPELLS}
    
    def get_current_beat(self):
        """Get current beat from audio system"""
        if self.audio_system and self.audio_system.current_song:
            return self.audio_system.current_beat
        return 0
    
    def get_bpm(self):
        """Get current BPM"""
        if self.audio_system and self.audio_system.current_song:
            return self.audio_system.current_song.bpm
        return 120  # Default
    
    def handle_event(self, event, player):
        """Handle keyboard events for spell casting"""
        if event.type == pygame.KEYDOWN:
            # Check for Shift press
            if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                self.shift_held = True
                self.typed_text = ""
                self.casting_start_beat = self.get_current_beat()
                self.casting_start_time = time.time()
                return True
            
            # If shift is held, capture letter keys
            if self.shift_held:
                if event.key == pygame.K_BACKSPACE:
                    self.typed_text = self.typed_text[:-1]
                elif event.key == pygame.K_ESCAPE:
                    # Cancel spell casting
                    self.shift_held = False
                    self.typed_text = ""
                elif event.unicode.isalpha():
                    self.typed_text += event.unicode.upper()
                    # Check if we completed a spell
                    self._check_spell_completion(player)
                return True  # Consume the event
        
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                self.shift_held = False
                # Don't clear typed text immediately for visual feedback
        
        return False
    
    def _check_spell_completion(self, player):
        """Check if typed text matches a spell"""
        current_beat = self.get_current_beat()
        beats_elapsed = current_beat - self.casting_start_beat if self.casting_start_beat else 0
        
        for spell_id, spell in SPELLS.items():
            if self.typed_text == spell.word:
                # Check if within beat window
                if beats_elapsed <= spell.beats_allowed:
                    # Calculate mana cost based on max mana
                    mana_cost = spell.get_mana_cost(player)
                    # Check mana
                    if player.stats.get('Current_Mana', 0) >= mana_cost:
                        # Check cooldown
                        if time.time() - self.cooldowns.get(spell_id, 0) >= spell.cooldown:
                            self._cast_spell(spell, player, mana_cost)
                            return
                        else:
                            self.result_message = f"{spell.name} on cooldown!"
                            self.result_timer = 1.5
                    else:
                        self.result_message = f"Not enough mana! Need {mana_cost}"
                        self.result_timer = 1.5
                else:
                    self.result_message = "Too slow!"
                    self.result_timer = 1.5
                
                # Reset input
                self.typed_text = ""
                self.shift_held = False
                return
    
    def _cast_spell(self, spell, player, mana_cost):
        """Execute a spell"""
        # Deduct mana
        player.stats['Current_Mana'] = max(0, player.stats['Current_Mana'] - mana_cost)
        
        # Set cooldown
        self.cooldowns[spell.spell_id] = time.time()
        
        # Calculate damage based on mana spent and skill attack
        final_damage = spell.get_damage(mana_cost, player)
        
        # Handle spell effects
        if spell.effect_type == "atomic":
            self._start_atomic_effect(player, final_damage)
            self.result_message = f"ATOMIC! {final_damage} damage! ({mana_cost} mana)"
        
        elif spell.effect_type == "sneak":
            self._start_sneak_effect(player, final_damage)
            self.result_message = f"Sneak Attack ready! ({final_damage} dmg)"
        
        elif spell.effect_type == "dash":
            # Dash is handled in update with enemies
            self.dash_effect_active = True
            self.dash_damage = final_damage
            self.result_message = f"Mana Burst! {final_damage} damage!"
        
        self.result_timer = 2.0
        
        # Reset casting state
        self.typed_text = ""
        self.shift_held = False
    
    def _start_atomic_effect(self, player, damage):
        """Start the atomic explosion effect"""
        self.atomic_effect_active = True
        self.atomic_effect_timer = 0
        self.atomic_effect_phase = "shrink"
        self.atomic_effect_radius = 2000  # Start from outside screen
        self.atomic_damage = damage
        self.atomic_center = (player.rect.centerx, player.rect.centery)
    
    def _start_sneak_effect(self, player, damage):
        """Start sneak attack counter mode"""
        self.sneak_active = True
        self.sneak_start_beat = self.get_current_beat()
        self.sneak_start_time = time.time()
        self.sneak_damage = damage
        self.player_sneak_pos = (player.rect.x, player.rect.y)
    
    def update(self, dt, player, enemies, screen_rect):
        """Update spell effects and timers"""
        self.shake_timer += dt * 10  # Shake animation timer
        
        # Update result message timer
        if self.result_timer > 0:
            self.result_timer -= dt
        
        # Update atomic effect
        if self.atomic_effect_active:
            self._update_atomic_effect(dt, player, enemies, screen_rect)
        
        # Update sneak attack
        if self.sneak_active:
            self._update_sneak_effect(dt, player, enemies)
        
        # Update dash effect
        if self.dash_effect_active:
            self._update_dash_effect(dt, player, enemies, screen_rect)
    
    def _update_atomic_effect(self, dt, player, enemies, screen_rect):
        """Update atomic explosion animation"""
        self.atomic_effect_timer += dt
        speed = 3000  # pixels per second
        
        if self.atomic_effect_phase == "shrink":
            # Circle shrinks from outside to player
            self.atomic_effect_radius -= speed * dt
            if self.atomic_effect_radius <= 0:
                self.atomic_effect_phase = "expand"
                self.atomic_effect_radius = 0
                # Deal damage to all enemies on screen
                for enemy in enemies:
                    if enemy.is_alive():
                        enemy.take_damage(self.atomic_damage)
        
        elif self.atomic_effect_phase == "expand":
            # Circle expands out again
            self.atomic_effect_radius += speed * 1.5 * dt
            if self.atomic_effect_radius > 2000:
                self.atomic_effect_active = False
    
    def _update_sneak_effect(self, dt, player, enemies):
        """Update sneak attack counter"""
        current_beat = self.get_current_beat()
        beats_elapsed = current_beat - self.sneak_start_beat if self.sneak_start_beat else 0
        
        # Check if player moved
        if self.player_sneak_pos:
            dx = abs(player.rect.x - self.player_sneak_pos[0])
            dy = abs(player.rect.y - self.player_sneak_pos[1])
            if dx > 5 or dy > 5:
                # Player moved, cancel sneak
                self.sneak_active = False
                self.result_message = "Sneak cancelled - you moved!"
                self.result_timer = 1.5
                return
        
        # Check if time expired
        if beats_elapsed > 6:
            self.sneak_active = False
            self.result_message = "Sneak expired"
            self.result_timer = 1.0
    
    def check_sneak_counter(self, player, attacker):
        """
        Called when an enemy attacks the player.
        Returns True if sneak counter activates (player takes no damage).
        """
        if self.sneak_active:
            self.sneak_active = False
            # Counter attack!
            attacker.take_damage(self.sneak_damage)
            self.result_message = f"Counter! {self.sneak_damage} damage!"
            self.result_timer = 2.0
            return True  # Player takes no damage
        return False
    
    def _update_dash_effect(self, dt, player, enemies, screen_rect):
        """Execute mana burst dash"""
        if not enemies:
            self.dash_effect_active = False
            return
        
        # Find furthest enemy on screen
        furthest_enemy = None
        max_dist = 0
        player_x = player.rect.centerx
        
        for enemy in enemies:
            if enemy.is_alive():
                dist = abs(enemy.rect.centerx - player_x)
                if dist > max_dist:
                    max_dist = dist
                    furthest_enemy = enemy
        
        if furthest_enemy:
            # Teleport behind the enemy
            if furthest_enemy.rect.centerx > player_x:
                # Enemy is to the right, teleport to right of enemy
                player.rect.x = furthest_enemy.rect.right + 20
            else:
                # Enemy is to the left, teleport to left of enemy
                player.rect.x = furthest_enemy.rect.left - player.rect.width - 20
            
            player.rect.y = furthest_enemy.rect.y
            
            # Deal damage
            furthest_enemy.take_damage(self.dash_damage)
        
        self.dash_effect_active = False
    
    def draw(self, screen, camera_x=0, camera_y=0):
        """Draw spell casting UI and effects"""
        screen_w, screen_h = screen.get_size()
        
        # Draw atomic effect
        if self.atomic_effect_active:
            self._draw_atomic_effect(screen, camera_x, camera_y)
        
        # Draw spell input display
        if self.shift_held or self.typed_text:
            self._draw_spell_input(screen)
        
        # Draw sneak attack indicator
        if self.sneak_active:
            self._draw_sneak_indicator(screen)
        
        # Draw result message
        if self.result_timer > 0 and self.result_message:
            alpha = min(255, int(self.result_timer * 255))
            self._draw_shaky_text(screen, self.result_message, 
                                  screen_w // 2, screen_h // 2 - 100,
                                  (255, 200, 50), center=True, alpha=alpha)
    
    def _draw_atomic_effect(self, screen, camera_x, camera_y):
        """Draw the atomic explosion circle"""
        if not self.atomic_effect_active:
            return
        
        screen_w, screen_h = screen.get_size()
        center_x = int(self.atomic_center[0] - camera_x)
        center_y = int(self.atomic_center[1] - camera_y)
        
        # Draw white circle
        radius = max(1, int(self.atomic_effect_radius))
        
        # Create surface for the circle with alpha
        if radius < 2000:
            circle_surf = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
            
            # Draw multiple rings for glow effect
            for i in range(5):
                r = radius + i * 3
                alpha = max(0, 255 - i * 50)
                if r > 0:
                    pygame.draw.circle(circle_surf, (255, 255, 255, alpha), 
                                      (center_x, center_y), r, max(1, 8 - i))
            
            screen.blit(circle_surf, (0, 0))
    
    def _draw_spell_input(self, screen):
        """Draw the spell input with shaky text and underscore"""
        screen_w, screen_h = screen.get_size()
        
        # Position at bottom center
        y_pos = screen_h - 120
        
        # Build display text: typed text + underscore cursor
        display_text = self.typed_text + "_"
        
        # Draw with shake effect
        self._draw_shaky_text(screen, display_text, screen_w // 2, y_pos, 
                              (255, 255, 100), center=True)
        
        # Draw hint text below
        hint = "Hold SHIFT + Type spell"
        hint_surf = self.small_font.render(hint, True, (180, 180, 180))
        screen.blit(hint_surf, (screen_w // 2 - hint_surf.get_width() // 2, y_pos + 50))
    
    def _draw_sneak_indicator(self, screen):
        """Draw sneak attack ready indicator"""
        screen_w, screen_h = screen.get_size()
        
        # Calculate remaining beats
        current_beat = self.get_current_beat()
        beats_elapsed = current_beat - self.sneak_start_beat if self.sneak_start_beat else 0
        beats_remaining = max(0, 6 - beats_elapsed)
        
        text = f"SNEAK READY ({beats_remaining:.1f} beats)"
        self._draw_shaky_text(screen, text, screen_w // 2, 80, (100, 255, 100), center=True)
    
    def _draw_shaky_text(self, screen, text, x, y, color, center=False, alpha=255):
        """Draw text with shake effect"""
        # Render each character with slight offset
        total_width = 0
        char_surfaces = []
        
        for i, char in enumerate(text):
            # Calculate shake offset for this character
            shake_x = math.sin(self.shake_timer + i * 0.5) * 2
            shake_y = math.cos(self.shake_timer * 1.3 + i * 0.7) * 2
            
            char_surf = self.font.render(char, True, color)
            char_surfaces.append((char_surf, shake_x, shake_y))
            total_width += char_surf.get_width()
        
        # Calculate starting x position
        if center:
            start_x = x - total_width // 2
        else:
            start_x = x
        
        # Draw each character with shake
        current_x = start_x
        for char_surf, shake_x, shake_y in char_surfaces:
            if alpha < 255:
                char_surf.set_alpha(alpha)
            screen.blit(char_surf, (current_x + shake_x, y + shake_y))
            current_x += char_surf.get_width()
    
    def is_casting(self):
        """Check if player is currently casting a spell"""
        return self.shift_held
    
    def get_spell_list(self):
        """Get list of all spells for UI display"""
        return list(SPELLS.values())
