# Assets/Combos.py
"""
Combo System - Beat-based directional attacks and combo sequences
All timing is synchronized to the music's BPM
"""

class ComboSystem:
    """Modifies attacks based on directional input and BPM timing"""
    
    # Define attack variants based on direction held (all beat-based)
    COMBO_VARIANTS = {
        "neutral": {
            "name": "Quarter Note Slash",
            "description": "Standard forward attack - Quarter note timing",
            "damage_multiplier": 1.0,
            "knockback_multiplier": 1.0,
            "range": 100,
            "windup_beats": 0.25,    # Wind-up takes 0.25 beats
            "active_beats": 0.5,     # Active for 0.5 beats
            "recovery_beats": 0.25,  # Recovery for 0.25 beats
            "total_beats": 1.0,      # Total attack duration: 1 beat
            "symbol": "N",           # Symbol for combo sequences
        },
        "forward": {
            "name": "Dash Slash",
            "description": "Attack while moving forward - more knockback",
            "damage_multiplier": 1.2,
            "knockback_multiplier": 1.5,
            "range": 120,
            "windup_beats": 0.25,
            "active_beats": 0.5,
            "recovery_beats": 0.25,
            "total_beats": 1.0,
            "symbol": "F",
        },
        "down": {
            "name": "Low Sweep",
            "description": "Low attack - sweeps enemies off their feet",
            "damage_multiplier": 1.1,
            "knockback_multiplier": 0.6,
            "range": 90,
            "angle": "down",
            "windup_beats": 0.25,
            "active_beats": 0.5,
            "recovery_beats": 0.25,
            "total_beats": 1.0,
            "symbol": "D",
        },
    }
    
    # Attack types based on rhythm (can be triggered with different inputs)
    RHYTHM_ATTACKS = {
        "eighth_stab": {
            "name": "Eighth Note Stab",
            "description": "Quick stab - Eighth note (0.5 beat)",
            "damage_multiplier": 0.6,
            "knockback_multiplier": 0.3,
            "range": 80,
            "windup_beats": 0.125,   # Wind-up: 1/8 beat
            "active_beats": 0.25,    # Active: 1/4 beat
            "recovery_beats": 0.125, # Recovery: 1/8 beat
            "total_beats": 0.5,      # Total: 0.5 beats (eighth note)
            "symbol": "E",
        },
        "quarter_slash": {
            "name": "Quarter Note Slash",
            "description": "Standard slash - Quarter note (1 beat)",
            "damage_multiplier": 1.0,
            "knockback_multiplier": 1.0,
            "range": 100,
            "windup_beats": 0.25,
            "active_beats": 0.5,
            "recovery_beats": 0.25,
            "total_beats": 1.0,      # Total: 1 beat (quarter note)
            "symbol": "Q",
        },
        "half_heavy": {
            "name": "Half Note Heavy",
            "description": "Heavy swing - Half note (2 beats)",
            "damage_multiplier": 2.0,
            "knockback_multiplier": 2.5,
            "range": 130,
            "windup_beats": 0.5,     # Wind-up: 0.5 beats
            "active_beats": 1.0,     # Active: 1 beat
            "recovery_beats": 0.5,   # Recovery: 0.5 beats
            "total_beats": 2.0,      # Total: 2 beats (half note)
            "symbol": "H",
        },
    }
    
    # COMBO SEQUENCES - Special attacks triggered by precise timing patterns
    # Format: {"pattern": ["attack_symbols"], "requirements": {...}, "result": {...}}
    COMBO_SEQUENCES = {
        "triple_strike": {
            "name": "Triple Strike",
            "description": "Three quick eighth note stabs in rhythm",
            "pattern": ["E", "E", "E"],  # Three eighth stabs
            "timing_window": 0.1,  # Must hit within 0.1 beats of perfect timing
            "damage_multiplier": 2.5,
            "knockback_multiplier": 3.0,
            "animation": "triple_strike",
            "color": (255, 200, 50),  # Golden flash
        },
        "heavy_finisher": {
            "name": "Heavy Finisher",
            "description": "Two quarter notes followed by a half note",
            "pattern": ["Q", "Q", "H"],  # Quarter, Quarter, Half
            "timing_window": 0.15,
            "damage_multiplier": 3.5,
            "knockback_multiplier": 4.0,
            "animation": "heavy_finisher",
            "color": (255, 50, 50),  # Red flash
        },
        "dash_combo": {
            "name": "Dash Combo",
            "description": "Forward slash into heavy attack",
            "pattern": ["F", "F", "H"],  # Forward, Forward, Heavy
            "timing_window": 0.15,
            "damage_multiplier": 3.0,
            "knockback_multiplier": 5.0,
            "animation": "dash_combo",
            "color": (50, 200, 255),  # Blue flash
        },
        "sweep_launcher": {
            "name": "Sweep Launcher",
            "description": "Down attack into upward slash",
            "pattern": ["D", "N", "N"],  # Down, Neutral, Neutral
            "timing_window": 0.15,
            "damage_multiplier": 2.8,
            "knockback_multiplier": 3.5,
            "animation": "sweep_launcher",
            "color": (150, 50, 255),  # Purple flash
        },
    }
    
    def __init__(self):
        """Initialize combo system with attack history tracking"""
        self.attack_history = []  # List of (symbol, beat_timestamp) tuples
        self.is_comboing = False
        self.last_attack_beat = 0
        self.combo_timeout = 0.5  # seconds after last attack before combo state ends
    
    def record_attack(self, attack_symbol, current_beat):
        """Record an attack in the combo history"""
        self.attack_history.append({
            'symbol': attack_symbol,
            'beat': current_beat,
            'time': __import__('time').time()
        })
        self.last_attack_beat = current_beat
        self.is_comboing = True
        
        # Keep only the last 10 attacks in history
        if len(self.attack_history) > 10:
            self.attack_history.pop(0)
    
    def update_combo_state(self):
        """Update combo state - end combo if timeout exceeded"""
        import time
        if not self.attack_history:
            self.is_comboing = False
            return
        
        # Check if combo timeout has expired
        time_since_last = time.time() - self.attack_history[-1]['time']
        if time_since_last > self.combo_timeout:
            self.is_comboing = False
            self.attack_history.clear()
    
    def check_combo_sequences(self):
        """Check if recent attacks match any combo sequence pattern"""
        if len(self.attack_history) < 2:
            return None
        
        # Check each combo sequence
        for combo_name, combo_data in self.COMBO_SEQUENCES.items():
            pattern = combo_data['pattern']
            timing_window = combo_data['timing_window']
            
            # Check if we have enough attacks in history
            if len(self.attack_history) < len(pattern):
                continue
            
            # Get the last N attacks where N is the pattern length
            recent_attacks = self.attack_history[-len(pattern):]
            
            # Check if symbols match
            symbols_match = all(
                attack['symbol'] == pattern[i] 
                for i, attack in enumerate(recent_attacks)
            )
            
            if not symbols_match:
                continue
            
            # Check timing - attacks should be on beat within timing window
            timing_correct = True
            for i in range(1, len(recent_attacks)):
                beat_diff = recent_attacks[i]['beat'] - recent_attacks[i-1]['beat']
                # Expected beat diff based on the attack type
                expected_diff = self._get_attack_beats(pattern[i-1])
                
                # Check if within timing window
                if abs(beat_diff - expected_diff) > timing_window:
                    timing_correct = False
                    break
            
            if timing_correct:
                # Found a combo! Clear history and return combo data
                self.attack_history.clear()
                return {
                    'name': combo_name,
                    'data': combo_data
                }
        
        return None
    
    def _get_attack_beats(self, symbol):
        """Get the beat duration for an attack symbol"""
        # Check rhythm attacks first
        for attack_data in self.RHYTHM_ATTACKS.values():
            if attack_data.get('symbol') == symbol:
                return attack_data['total_beats']
        
        # Check combo variants
        for attack_data in self.COMBO_VARIANTS.values():
            if attack_data.get('symbol') == symbol:
                return attack_data['total_beats']
        
        return 1.0  # Default to 1 beat
    
    @staticmethod
    def get_attack_variant(moving_left, moving_right, moving_down):
        """Determine which attack variant to use based on movement input"""
        # Determine direction being held during attack
        if moving_down:
            return ComboSystem.COMBO_VARIANTS["down"]
        elif moving_left or moving_right:
            # Attacking while moving forward
            return ComboSystem.COMBO_VARIANTS["forward"]
        else:
            return ComboSystem.COMBO_VARIANTS["neutral"]
    
    @staticmethod
    def get_rhythm_attack(attack_type):
        """Get attack based on rhythm type (eighth, quarter, half)"""
        return ComboSystem.RHYTHM_ATTACKS.get(attack_type, ComboSystem.RHYTHM_ATTACKS["quarter_slash"])
    
    @staticmethod
    def beats_to_frames(beats, bpm, fps=60):
        """Convert beats to frames at given BPM and FPS"""
        seconds_per_beat = 60.0 / bpm
        seconds = beats * seconds_per_beat
        frames = int(seconds * fps)
        return max(1, frames)  # At least 1 frame
    
    @staticmethod
    def frames_to_beats(frames, bpm, fps=60):
        """Convert frames to beats at given BPM and FPS"""
        seconds = frames / fps
        seconds_per_beat = 60.0 / bpm
        beats = seconds / seconds_per_beat
        return beats
    
    @staticmethod
    def apply_combo_modifiers(enemy, damage, knockback, attack_variant):
        """Apply combo variant modifiers to damage and knockback"""
        modified_damage = damage * attack_variant["damage_multiplier"]
        modified_knockback = knockback * attack_variant["knockback_multiplier"]
        return modified_damage, modified_knockback
