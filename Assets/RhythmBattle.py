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
    GOOD_WINDOW = 0.15      # ±150ms = Good hit (more lenient)
    MISS_THRESHOLD = 0.25   # ±250ms = Still registers but "Miss"
    
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
        self.combo_system = ComboSystem()
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
        self.combo_finisher_bonus = 1.0
        self.combo_finisher_timer = 0.0
        
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
        
        # Determine rhythm attack tier based on BPM (fast → shorter attacks)
        rhythm_type = "quarter_slash"
        seconds_per_beat = 0.5
        bpm = 120
        if self.audio_system.current_song:
            bpm = self.audio_system.current_song.bpm
            seconds_per_beat = self.audio_system.current_song.seconds_per_beat
        if bpm >= 150:
            rhythm_type = "eighth_stab"
        elif bpm <= 100:
            rhythm_type = "half_heavy"
        else:
            rhythm_type = "quarter_slash"

        rhythm_attack = ComboSystem.get_rhythm_attack(rhythm_type)

        # Set cooldown from rhythm attack total beats, 0.2s faster
        self.attack_cooldown = max(0.05, rhythm_attack["total_beats"] * seconds_per_beat - 0.2)

        # Record attack in combo system using rhythm symbol and check sequences
        self.combo_system.record_attack(rhythm_attack["symbol"], self.audio_system.current_beat)
        combo_hit = self.combo_system.check_combo_sequences()
        if combo_hit:
            data = combo_hit["data"]
            # Apply a temporary finisher bonus multiplier
            self.combo_finisher_bonus = data.get("damage_multiplier", 1.0)
            self.combo_finisher_timer = 0.5
            # Visual feedback for combo
            self.feedback_displays.append({
                "text": data.get("name", "COMBO"),
                "color": data.get("color", (255, 255, 255)),
                "timer": 0.6,
                "y_offset": -10
            })
        
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
        finisher_mult = self.combo_finisher_bonus
        return timing_mult * combo_mult * finisher_mult
    
    def update(self, dt, current_time):
        """Update rhythm system"""
        # Update combo timeout based on current song
        self._update_combo_timeout()
        
        # Update cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown = max(0, self.attack_cooldown - dt)
        # Decay finisher bonus after short duration
        if self.combo_finisher_timer > 0:
            self.combo_finisher_timer = max(0, self.combo_finisher_timer - dt)
            if self.combo_finisher_timer == 0:
                self.combo_finisher_bonus = 1.0
        
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
        """Draw Osu-style rhythm circle - bottom-center; hits inner exactly on beat"""
        if not self.audio_system.current_song:
            return
        import time
        bpm = self.audio_system.current_song.bpm
        seconds_per_beat = self.audio_system.current_song.seconds_per_beat
        last_beat = self.audio_system.current_song.last_beat_time
        now = time.time()
        elapsed = max(0.0, now - last_beat)
        time_until_next = max(0.0, seconds_per_beat - elapsed)
        ratio = time_until_next / max(seconds_per_beat, 1e-6)  # 1.0 right after beat, 0.0 at the beat

        # Bottom-center position
        center_x = screen.get_width() // 2
        center_y = screen.get_height() - 40

        inner_radius = 8
        max_outer_radius = 22
        outer_radius = int(inner_radius + (max_outer_radius - inner_radius) * ratio)

        surface_size = (60, 60)
        circle_surface = pygame.Surface(surface_size, pygame.SRCALPHA)
        center_offset = (30, 30)

        # Color feedback based on closeness to beat
        # Near the beat (ratio ~ 0) → Perfect/Good/Miss windows
        time_to_beat = time_until_next
        if time_to_beat <= RhythmTiming.PERFECT_WINDOW:
            outer_color = (255, 215, 0, 220)
        elif time_to_beat <= RhythmTiming.GOOD_WINDOW:
            outer_color = (100, 255, 100, 200)
        elif time_to_beat <= RhythmTiming.MISS_THRESHOLD:
            outer_color = (255, 100, 100, 180)
        else:
            outer_color = (150, 150, 150, 120)

        pygame.draw.circle(circle_surface, outer_color, center_offset, outer_radius, 2)
        pygame.draw.circle(circle_surface, (200, 200, 200, 220), center_offset, inner_radius, 1)
        pygame.draw.circle(circle_surface, (80, 80, 80, 100), center_offset, max(1, inner_radius - 2), 0)

        # Subtle glow when within last 15% of time to beat
        if ratio < 0.15:
            glow_strength = (0.15 - ratio) / 0.15
            glow_size = int(3 * glow_strength)
            glow_alpha = int(120 * glow_strength)
            pygame.draw.circle(circle_surface, (255, 215, 0, glow_alpha), center_offset, inner_radius + glow_size, 1)

        screen.blit(circle_surface, (center_x - 30, center_y - 30))
    
    def reset_combo(self):
        """Reset combo chain (e.g., when hit by enemy)"""
        self.combo_chain.clear()
        self.combo_count = 0
    
    def reset_beat_tracking(self):
        """Reset rhythm circle beat tracking when song changes"""
        self.outer_radius_state = None
        self.prev_beat_in_cycle = 0.0
        self.circle_last_time = None
