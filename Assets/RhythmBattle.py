# Assets/RhythmBattle.py
"""
RHYTHM BATTLE SYSTEM
====================
Ties combat to music beats - attacks are stronger when timed on beat!

Features:
- Beat timing windows (Perfect/Good/Miss)
- Visual feedback for rhythm accuracy
- Combo chains that build with good timing
- Damage multipliers based on timing
- Attack animations synchronized to beats
"""

import pygame
import math
from Assets.Combos import ComboSystem

class RhythmTiming:
    """Defines timing windows for rhythm accuracy"""
    # Timing windows (in seconds from perfect beat)
    PERFECT_WINDOW = 0.04   # ±40ms = Perfect hit (stricter)
    GOOD_WINDOW = 0.08      # ±80ms = Good hit (stricter)
    MISS_THRESHOLD = 0.15   # ±150ms = Still registers but "Miss"
    
    # Damage multipliers based on timing
    PERFECT_MULTIPLIER = 1.5   # 50% bonus damage
    GOOD_MULTIPLIER = 1.2      # 20% bonus damage
    MISS_MULTIPLIER = 0.8      # 20% damage penalty
    
    # Combo bonuses (stacks with timing multiplier)
    COMBO_MULTIPLIER_PER_HIT = 0.1  # +10% per combo hit (max 5 hits)
    MAX_COMBO_BONUS = 0.5           # Max +50% from combo
    
    # Combo timing threshold for high BPM
    HIGH_BPM_THRESHOLD = 100  # If BPM > this, use half note timing for combos
    
    # Visual feedback colors
    PERFECT_COLOR = (255, 215, 0)   # Gold
    GOOD_COLOR = (100, 255, 100)    # Green
    MISS_COLOR = (255, 100, 100)    # Red


class RhythmAttack:
    """Represents a single attack with rhythm timing"""
    def __init__(self, attack_type, direction, timestamp, beat_time):
        self.attack_type = attack_type       # "neutral", "forward", "down", etc.
        self.direction = direction           # Direction held during attack
        self.timestamp = timestamp           # When attack was pressed
        self.beat_time = beat_time          # Nearest beat time
        self.accuracy = self._calculate_accuracy()
        self.multiplier = self._get_multiplier()
        
        # Visual feedback
        self.feedback_timer = 0.5  # Show feedback for 0.5 seconds
        self.feedback_text = self._get_feedback_text()
        self.feedback_color = self._get_feedback_color()
    
    def _calculate_accuracy(self):
        """Calculate how close the attack was to the beat"""
        time_diff = abs(self.timestamp - self.beat_time)
        
        if time_diff <= RhythmTiming.PERFECT_WINDOW:
            return "PERFECT"
        elif time_diff <= RhythmTiming.GOOD_WINDOW:
            return "GOOD"
        elif time_diff <= RhythmTiming.MISS_THRESHOLD:
            return "MISS"
        else:
            return "LATE"
    
    def _get_multiplier(self):
        """Get damage multiplier based on accuracy"""
        if self.accuracy == "PERFECT":
            return RhythmTiming.PERFECT_MULTIPLIER
        elif self.accuracy == "GOOD":
            return RhythmTiming.GOOD_MULTIPLIER
        else:
            return RhythmTiming.MISS_MULTIPLIER
    
    def _get_feedback_text(self):
        """Get text to display for feedback"""
        return self.accuracy
    
    def _get_feedback_color(self):
        """Get color for feedback"""
        if self.accuracy == "PERFECT":
            return RhythmTiming.PERFECT_COLOR
        elif self.accuracy == "GOOD":
            return RhythmTiming.GOOD_COLOR
        else:
            return RhythmTiming.MISS_COLOR


class RhythmBattleSystem:
    """Main rhythm battle system - integrates with game"""
    def __init__(self, audio_system):
        self.audio_system = audio_system
        self.combo_chain = []           # List of recent attacks
        self.combo_count = 0            # Current combo count
        self.last_attack_time = 0       # Time of last attack
        self.combo_timeout = 2.0        # Combo breaks after 2 seconds (updated dynamically)
        self._update_combo_timeout()    # Set initial timeout based on BPM
        
        # Visual feedback
        self.feedback_displays = []     # Active feedback to show
        self.beat_indicators = []       # Visual beat indicators
        
        # Attack state
        self.current_attack = None
        self.attack_cooldown = 0
        
        # Combo sequences (for special moves)
        self.input_buffer = []          # Track recent inputs for combos
        self.buffer_max_time = 4.0      # Clear buffer after 4 seconds

        # Osu approach circle state
        self.outer_radius_state = None
        self.prev_beat_in_cycle = 0.0
        self.circle_last_time = None
    
    def process_attack_input(self, direction="neutral", current_time=0):
        """Process an attack button press with rhythm timing
        
        Args:
            direction: Direction held ("neutral", "forward", "down", "up")
            current_time: Current game time in seconds
        
        Returns:
            RhythmAttack object or None if on cooldown
        """
        if self.attack_cooldown > 0:
            return None
        
        # Get nearest beat time
        beat_time = self.audio_system.get_nearest_beat_time()
        
        # Create attack
        attack = RhythmAttack(
            attack_type=direction,
            direction=direction,
            timestamp=current_time,
            beat_time=beat_time
        )
        
        # Add to combo chain
        self._update_combo_chain(attack, current_time)
        
        # Add visual feedback
        self.feedback_displays.append({
            "text": attack.feedback_text,
            "color": attack.feedback_color,
            "timer": attack.feedback_timer,
            "y_offset": 0
        })
        
        # Set cooldown based on attack type
        variant = ComboSystem.COMBO_VARIANTS.get(direction, ComboSystem.COMBO_VARIANTS["neutral"])
        if self.audio_system.current_song:
            seconds_per_beat = self.audio_system.current_song.seconds_per_beat
            self.attack_cooldown = variant["total_beats"] * seconds_per_beat
        else:
            self.attack_cooldown = variant["total_beats"] * 0.5  # Default 0.5 seconds per beat
        
        self.current_attack = attack
        return attack
    
    def _update_combo_timeout(self):
        """Update combo timeout based on current song BPM"""
        if not self.audio_system.current_song:
            self.combo_timeout = 2.0
            return
        
        bpm = self.audio_system.current_song.bpm
        seconds_per_beat = self.audio_system.current_song.seconds_per_beat
        
        # If BPM > 100, use half notes (2 beats) for combo timing
        if bpm > RhythmTiming.HIGH_BPM_THRESHOLD:
            self.combo_timeout = seconds_per_beat * 2.0  # Half note
        else:
            self.combo_timeout = seconds_per_beat * 1.5  # Quarter + eighth
    
    def _update_combo_chain(self, attack, current_time):
        """Update combo chain with new attack"""
        # Break combo if too much time passed
        if current_time - self.last_attack_time > self.combo_timeout:
            self.combo_chain.clear()
            self.combo_count = 0
        
        # Add attack to chain
        self.combo_chain.append(attack)
        
        # Increase combo count only on good timing
        if attack.accuracy in ["PERFECT", "GOOD"]:
            self.combo_count += 1
        else:
            # Reset combo on miss
            self.combo_count = 0
            self.combo_chain.clear()
        
        # Keep only last 5 attacks
        if len(self.combo_chain) > 5:
            self.combo_chain.pop(0)
        
        self.last_attack_time = current_time
    
    def get_combo_multiplier(self):
        """Get total damage multiplier from combo chain"""
        if self.combo_count == 0:
            return 1.0
        
        combo_bonus = min(
            self.combo_count * RhythmTiming.COMBO_MULTIPLIER_PER_HIT,
            RhythmTiming.MAX_COMBO_BONUS
        )
        return 1.0 + combo_bonus
    
    def get_total_multiplier(self):
        """Get total multiplier including combo and timing"""
        if not self.current_attack:
            return 1.0
        
        timing_mult = self.current_attack.multiplier
        combo_mult = self.get_combo_multiplier()
        
        return timing_mult * combo_mult
    
    def update(self, dt, current_time):
        """Update rhythm system"""
        # Update combo timeout based on current song
        self._update_combo_timeout()
        
        # Update cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown = max(0, self.attack_cooldown - dt)
        
        # Update feedback displays
        for feedback in self.feedback_displays[:]:
            feedback["timer"] -= dt
            feedback["y_offset"] -= 60 * dt  # Float upward
            if feedback["timer"] <= 0:
                self.feedback_displays.remove(feedback)
        
        # Clear old attacks from chain
        if current_time - self.last_attack_time > self.combo_timeout:
            self.combo_chain.clear()
            self.combo_count = 0
    
    def draw_feedback(self, screen, player_x, player_y, camera_x, camera_y, font):
        """Draw rhythm feedback above player"""
        screen_x = player_x - camera_x
        screen_y = player_y - camera_y
        
        # Draw feedback text
        for i, feedback in enumerate(self.feedback_displays):
            alpha = int(255 * (feedback["timer"] / 0.5))  # Fade out
            text = font.render(feedback["text"], True, feedback["color"])
            text.set_alpha(alpha)
            
            # Position above player
            y_pos = screen_y - 80 + feedback["y_offset"] - (i * 25)
            text_rect = text.get_rect(center=(screen_x, y_pos))
            screen.blit(text, text_rect)
    
    def draw_combo_counter(self, screen, font):
        """Draw combo counter in corner"""
        if self.combo_count == 0:
            return
        
        # Draw combo count
        combo_text = f"{self.combo_count} HIT COMBO"
        multiplier_text = f"x{self.get_combo_multiplier():.1f} DAMAGE"
        
        # Position in top right
        x = screen.get_width() - 20
        y = 80
        
        # Combo count
        text = font.render(combo_text, True, (255, 215, 0))
        text_rect = text.get_rect(topright=(x, y))
        
        # Background
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(screen, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(screen, (255, 215, 0), bg_rect, 2)
        
        screen.blit(text, text_rect)
        
        # Multiplier
        mult_text = font.render(multiplier_text, True, (255, 255, 100))
        mult_rect = mult_text.get_rect(topright=(x, y + 30))
        screen.blit(mult_text, mult_rect)
    
    def draw_beat_indicators(self, screen, font, enemies_nearby=False):
        """Draw Osu-style rhythm circle - outer circle approaches inner circle like Osu approach circles
        
        Args:
            screen: Surface to draw on
            font: Font for text
            enemies_nearby: Only show circle when enemies are near
        """
        if not self.audio_system.current_song:
            return
        
        # Only show circle when enemies are nearby
        if not enemies_nearby:
            return
        
        # Get current beat info and determine beat cycle duration
        bpm = self.audio_system.current_song.bpm
        is_high_bpm = bpm > 100
        
        # Use 2-beat cycle for high BPM, 1-beat cycle for normal BPM
        beat_cycle_length = 2.0 if is_high_bpm else 1.0
        
        # Get beat progress within the current cycle (0.0 to 1.0)
        current_beat = self.audio_system.current_beat
        beat_in_cycle = (current_beat % beat_cycle_length) / beat_cycle_length
        
        # Circle design - Osu-style hit mechanics
        center_x = screen.get_width() // 2
        center_y = screen.get_height() - 100
        
        inner_radius = 50  # Static target circle (hitcircle)
        max_outer_radius = 140  # Starting size for outer circle (approach circle)
        beat_seconds = beat_cycle_length * 60.0 / bpm
        shrink_per_sec = (max_outer_radius - inner_radius) / max(beat_seconds, 0.001)

        # Time delta for smooth shrinking
        now = pygame.time.get_ticks() / 1000.0
        if self.circle_last_time is None:
            self.circle_last_time = now
        dt = now - self.circle_last_time
        self.circle_last_time = now

        # Reset at the start of a new beat cycle
        if self.outer_radius_state is None or beat_in_cycle < self.prev_beat_in_cycle:
            self.outer_radius_state = max_outer_radius

        # Shrink radius over time until it reaches the inner radius
        self.outer_radius_state = max(inner_radius, self.outer_radius_state - shrink_per_sec * dt)
        outer_radius = int(self.outer_radius_state)
        self.prev_beat_in_cycle = beat_in_cycle
        
        # Create transparent surface for circles
        surface_size = (int(max_outer_radius * 2.5), int(max_outer_radius * 2.5))
        circle_surface = pygame.Surface(surface_size, pygame.SRCALPHA)
        center_offset = (surface_size[0] // 2, surface_size[1] // 2)
        
        # Determine color based on timing accuracy
        # Map beat_in_cycle to timing window - when outer circle is close to inner (perfect window)
        time_from_beat_percent = abs(beat_in_cycle - 1.0)  # 0 when beat hits, 1 when far
        
        if time_from_beat_percent <= (RhythmTiming.PERFECT_WINDOW / (beat_cycle_length * 60 / bpm)):
            # Perfect window - gold (bright)
            outer_color = (255, 215, 0, 220)
        elif time_from_beat_percent <= (RhythmTiming.GOOD_WINDOW / (beat_cycle_length * 60 / bpm)):
            # Good window - green
            outer_color = (100, 255, 100, 200)
        elif time_from_beat_percent <= (RhythmTiming.MISS_THRESHOLD / (beat_cycle_length * 60 / bpm)):
            # Miss window - red
            outer_color = (255, 100, 100, 180)
        else:
            # Too far - gray
            outer_color = (150, 150, 150, 120)
        
        # Draw outer approach circle (THICKER - 6px stroke)
        pygame.draw.circle(circle_surface, outer_color, center_offset, outer_radius, 6)
        
        # Draw inner static hitcircle (3px stroke for definition)
        pygame.draw.circle(circle_surface, (200, 200, 200, 220), center_offset, inner_radius, 3)
        
        # Draw filled center of hitcircle (subtle)
        pygame.draw.circle(circle_surface, (80, 80, 80, 100), center_offset, inner_radius - 12, 0)
        
        # Glow/highlight on hitcircle when close to perfect (just before hit)
        if beat_in_cycle > 0.85:  # Last 15% of cycle
            glow_strength = (beat_in_cycle - 0.85) / 0.15  # 0 to 1
            glow_size = int(15 * glow_strength)
            glow_alpha = int(120 * glow_strength)
            pygame.draw.circle(circle_surface, (255, 215, 0, glow_alpha), center_offset, inner_radius + glow_size, 2)
        
        # Blit to screen
        blit_x = center_x - center_offset[0]
        blit_y = center_y - center_offset[1]
        screen.blit(circle_surface, (blit_x, blit_y))
    
    def reset_combo(self):
        """Reset combo chain (e.g., when hit by enemy)"""
        self.combo_chain.clear()
        self.combo_count = 0
