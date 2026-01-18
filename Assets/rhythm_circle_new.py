"""
Rhythm Battle Circle Drawing Function (Cleaned & Fixed)
========================================================
This is the refactored draw_beat_indicators method with proper indentation,
imports, and detailed comments. Copy this into RhythmBattle.py to replace
the existing draw_beat_indicators method in the RhythmBattleSystem class.

REQUIREMENTS:
- Add to RhythmBattle.py imports: import pygame
- Add to RhythmBattle.py class RhythmBattleSystem:
- Requires: self.audio_system, self.circle_last_time, self.outer_radius_state, self.prev_beat_in_cycle
"""

import pygame
from Assets.RhythmBattle import RhythmTiming  # Timing windows (PERFECT/GOOD/MISS) and BPM threshold


def draw_beat_indicators(self, screen, font):
    """
    Draw a tiny Osu-style rhythm indicator circle in the top-right corner.
    
    The circle uses an approach mechanic where the outer circle shrinks toward
    the inner circle, reaching it exactly at each beat. Visual feedback is color-coded
    based on timing accuracy (perfect/good/miss windows).
    
    Args:
        screen (pygame.Surface): Screen surface to draw on
        font (pygame.font.Font): Font for text rendering (unused but kept for API consistency)
    
    Returns:
        None
    """
    # Exit early if no song is playing (audio system not ready)
    if not self.audio_system.current_song:
        return
    

    
    # ===== BEAT CYCLE CONFIGURATION =====
    # Determine beat cycle length based on BPM (higher BPM = faster timing)
    bpm = self.audio_system.current_song.bpm
    is_high_bpm = bpm > RhythmTiming.HIGH_BPM_THRESHOLD  # 100 BPM threshold
    
    # Use half-note (2 beats) for high BPM tracks, quarter-note (1 beat) for slower tracks
    beat_cycle_length = 2.0 if is_high_bpm else 1.0
    
    # Calculate current position within beat cycle (0.0 = start, 1.0 = next beat)
    current_beat = self.audio_system.current_beat
    beat_in_cycle = (current_beat % beat_cycle_length) / beat_cycle_length
    
    # ===== CIRCLE POSITIONING =====
    # Position circle 40px from right edge, 40px from top (tiny indicator in corner)
    center_x = screen.get_width() - 40
    center_y = 40
    
    # ===== CIRCLE SIZING =====
    # Inner radius: static target circle (8px for tiny indicator)
    inner_radius = 8
    # Outer radius: approach circle that shrinks from max to inner (22px starting size)
    max_outer_radius = 22
    
    # Calculate timing for beat synchronization
    beat_seconds = beat_cycle_length * 60.0 / bpm  # Duration of one beat cycle in seconds
    shrink_per_sec = (max_outer_radius - inner_radius) / max(beat_seconds, 0.001)  # Shrink rate
    
    # ===== TIME-BASED SHRINK LOGIC =====
    # Track frame-by-frame timing to achieve smooth animation independent of beat calculations
    now = pygame.time.get_ticks() / 1000.0  # Current time in seconds
    if self.circle_last_time is None:
        self.circle_last_time = now
    
    dt = now - self.circle_last_time  # Delta time since last frame
    self.circle_last_time = now
    
    # Reset to max radius at start of new beat cycle (when beat_in_cycle wraps from ~1.0 to ~0.0)
    if self.outer_radius_state is None or beat_in_cycle < self.prev_beat_in_cycle:
        self.outer_radius_state = max_outer_radius
    
    # Continuously shrink outer radius toward inner radius over beat duration
    self.outer_radius_state = max(inner_radius, self.outer_radius_state - shrink_per_sec * dt)
    outer_radius = int(self.outer_radius_state)
    self.prev_beat_in_cycle = beat_in_cycle
    
    # ===== CIRCLE RENDERING SETUP =====
    # Create transparent 60x60px surface for drawing circles (accounts for stroke width)
    surface_size = (60, 60)
    circle_surface = pygame.Surface(surface_size, pygame.SRCALPHA)
    center_offset = (30, 30)  # Center point within the 60x60 surface
    
    # ===== TIMING ACCURACY COLOR CODING =====
    # Calculate how far current beat is from perfect timing (0 = perfect, 1 = far away)
    time_from_beat_percent = abs(beat_in_cycle - 1.0)
    
    # Determine outer circle color based on timing window (perfect/good/miss)
    if time_from_beat_percent <= (RhythmTiming.PERFECT_WINDOW / (beat_cycle_length * 60 / bpm)):
        # Within perfect window (±40ms): bright gold indicator
        outer_color = (255, 215, 0, 220)
    elif time_from_beat_percent <= (RhythmTiming.GOOD_WINDOW / (beat_cycle_length * 60 / bpm)):
        # Within good window (±80ms): green indicator
        outer_color = (100, 255, 100, 200)
    elif time_from_beat_percent <= (RhythmTiming.MISS_THRESHOLD / (beat_cycle_length * 60 / bpm)):
        # Within miss window (±150ms): red indicator
        outer_color = (255, 100, 100, 180)
    else:
        # Beyond any timing window: gray (too early/late)
        outer_color = (150, 150, 150, 120)
    
    # ===== DRAW CIRCLE ELEMENTS =====
    # Draw outer approach circle (2px stroke for tiny version)
    pygame.draw.circle(circle_surface, outer_color, center_offset, outer_radius, 2)
    
    # Draw inner static target circle (1px stroke for definition)
    pygame.draw.circle(circle_surface, (200, 200, 200, 220), center_offset, inner_radius, 1)
    
    # Draw filled center of inner circle (dark gray, subtle)
    pygame.draw.circle(circle_surface, (80, 80, 80, 100), center_offset, max(1, inner_radius - 2), 0)
    
    # ===== OPTIONAL: GLOW EFFECT =====
    # Add a subtle glow during the last 15% of beat cycle (visual feedback for imminent beat)
    if beat_in_cycle > 0.85:
        # Glow strength increases as beat approaches (0 = weak, 1 = strong)
        glow_strength = (beat_in_cycle - 0.85) / 0.15
        # Glow expands outward from inner circle
        glow_size = int(3 * glow_strength)
        # Glow fades in as beat approaches
        glow_alpha = int(120 * glow_strength)
        # Draw glowing aura (1px stroke)
        pygame.draw.circle(circle_surface, (255, 215, 0, glow_alpha), center_offset, inner_radius + glow_size, 1)
    
    # ===== DISPLAY ON SCREEN =====
    # Blit 60x60 surface to screen at top-right position (adjusted for center_offset)
    screen.blit(circle_surface, (center_x - 30, center_y - 30))
