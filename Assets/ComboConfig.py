# Assets/ComboConfig.py
import time
from Assets.GameBalance import COMBOS, COMBO_BALANCE

# =============================================================================
# COMBO SYSTEM CONFIGURATION
# =============================================================================

COMBO_CONFIG = {
    # Timing windows
    "beat_window": 0.15,  # How many seconds before/after beat counts as "on beat"
    "max_combo_time": 8.0,  # Max seconds to complete a combo (2 bars of 4/4 at 120 BPM)
    
    # Visual effects
    "combo_zoom": 2.0,  # Zoom level during combos
    "combo_zoom_speed": 0.15,  # How fast to zoom in/out (0-1, higher = faster)
    "normal_zoom": 1.5,  # Normal gameplay zoom
    
    # Combo detection
    "min_hits_for_combo": 2,  # Minimum hits to trigger combo mode
    "combo_reset_time": 1.0,  # Seconds without hitting to reset combo
    
    # Display
    "show_combo_name": True,  # Show combo name on screen
    "show_hit_count": True,  # Show hit counter
    "combo_text_color": (255, 215, 0),  # Gold
    "hit_text_color": (255, 255, 255),  # White
}

# =============================================================================
# COMBO TRACKER CLASS
# =============================================================================

# =============================================================================
# COMBO TRACKER CLASS
# =============================================================================

class ComboTracker:
    """Tracks player combos and matches them to note patterns"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset combo state"""
        self.active = False
        self.in_combo = False  # Only true when hitting enemies
        self.hit_count = 0
        self.hits = []  # List of (time, note_type) tuples where note_type is "Q" or "E"
        self.last_hit_time = 0
        self.combo_start_time = 0
        self.matched_combo = None
        self.total_damage_dealt = 0
        self.enemies_hit = set()
        self.target_zoom = 1.5
        self.current_zoom = 1.5
        self.invalid_combo = False
    
    def add_hit(self, current_time, beat_number, hit_enemy=False, seconds_per_beat=0.5):
        """Record a hit with timing-based note detection
        
        Args:
            current_time: Current timestamp
            beat_number: Which beat (1-4) this attack is on
            hit_enemy: Whether this attack actually hit an enemy
            seconds_per_beat: Duration of one beat (calculated from BPM)
        """
        # Determine note type based on TIMING since last hit
        if not self.active:
            # First hit is always a quarter note
            note_type = "Q"
            self.active = True
            self.combo_start_time = current_time
        else:
            # Calculate time since last hit
            time_since_last = current_time - self.last_hit_time
            
            # Tolerance for timing (beats can be slightly off)
            quarter_threshold = seconds_per_beat * 0.75  # 75% of a beat
            eighth_threshold = (seconds_per_beat * 0.5) * 0.75  # 75% of half beat
            half_threshold = (seconds_per_beat * 2) * 0.75  # 75% of two beats
            
            # Check if it's a half note (held for ~2 beats)
            if time_since_last >= half_threshold:
                note_type = "H"  # Half note
            # Check if it's an eighth note (~0.5 beats)
            elif time_since_last <= eighth_threshold:
                note_type = "E"  # Eighth note
            # Otherwise it's a quarter note (~1 beat)
            else:
                note_type = "Q"  # Quarter note
        
        self.hit_count += 1
        self.hits.append((current_time, note_type))
        self.last_hit_time = current_time
        
        # Only enter combo mode if we hit an enemy
        if hit_enemy:
            self.in_combo = True
        
        # Try to match pattern
        self._update_pattern_match()
    
    def update(self, current_time):
        """Update combo state based on time"""
        if not self.active:
            return
        
        # Check if combo should timeout
        time_since_hit = current_time - self.last_hit_time
        if time_since_hit > 2.0:  # 2 seconds without hitting
            self.reset()
            return
        
        # Update zoom
        if self.should_zoom():
            self.target_zoom = 2.0
        else:
            self.target_zoom = 1.5
        
        # Smoothly interpolate zoom
        zoom_diff = self.target_zoom - self.current_zoom
        self.current_zoom += zoom_diff * 0.15
    
    def _update_pattern_match(self):
        """Check if current hit pattern matches any defined combos"""
        self.matched_combo = None
        self.invalid_combo = False
        
        # Convert hits to pattern string
        current_pattern = [hit[1] for hit in self.hits]
        
        # Check exact matches
        for combo_id, combo_data in COMBOS.items():
            if current_pattern == combo_data["pattern"]:
                self.matched_combo = combo_id
                return
        
        # Check if we could still match something
        for combo_id, combo_data in COMBOS.items():
            pattern = combo_data["pattern"]
            # Check if current pattern is a prefix of any combo
            is_valid_prefix = True
            for i, note in enumerate(current_pattern):
                if i >= len(pattern) or note != pattern[i]:
                    is_valid_prefix = False
                    break
            
            if is_valid_prefix:
                # Still building toward this combo
                return
        
        # If we have 2+ hits and don't match anything, it's invalid
        if len(current_pattern) >= 2:
            self.invalid_combo = True
    
    def get_damage_multiplier(self):
        """Get damage multiplier for current combo"""
        if self.matched_combo and self.matched_combo in COMBOS:
            return COMBOS[self.matched_combo]["damage_multiplier"]
        return 1.0
    
    def get_combo_name(self):
        """Get name of current combo"""
        if self.matched_combo and self.matched_combo in COMBOS:
            return COMBOS[self.matched_combo]["name"]
        return "Combo"
    
    def should_zoom(self):
        """Check if we should be in combo zoom mode"""
        return self.in_combo and self.hit_count >= 2
    
    def get_pattern_string(self):
        """Get current pattern as string for display"""
        return "".join([hit[1] for hit in self.hits])
