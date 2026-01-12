# Assets/AudioConfig.py
"""
EASY AUDIO CONFIGURATION
========================
Add your songs here - BPM will be automatically detected!
The game will automatically play them and display the beat counter.
"""

import pygame
import time

class Song:
    """Represents a song with rhythm information"""
    def __init__(self, name, filepath, bpm=None, time_signature_beats=4, time_signature_note=4, auto_detect_bpm=True):
        """
        Args:
            name: Display name of the song
            filepath: Path to the MP3 file (e.g., "Assets/Audio/song.mp3")
            bpm: Beats per minute (e.g., 120, 250) - if None and auto_detect_bpm=True, will auto-detect
            time_signature_beats: Top number of time signature (e.g., 4 in 4/4)
            time_signature_note: Bottom number of time signature (e.g., 4 in 4/4)
            auto_detect_bpm: If True and bpm is None, will attempt to detect BPM automatically (lazy-loaded)
        """
        self.name = name
        self.filepath = filepath
        self.time_signature_beats = time_signature_beats
        self.time_signature_note = time_signature_note
        self.auto_detect_bpm = auto_detect_bpm
        self._bpm = bpm  # Store initial BPM (may be None)
        self._bpm_detected = False  # Track if we've run detection yet
        
        # Runtime variables
        self.is_playing = False
        self.start_time = 0
        self.current_beat = 1
        self.last_beat_time = 0
    
    @property
    def bpm(self):
        """Lazy-load BPM detection only when accessed"""
        if self._bpm is None and self.auto_detect_bpm and not self._bpm_detected:
            self._bpm = self._detect_bpm(self.filepath)
            self._bpm_detected = True
        elif self._bpm is None:
            self._bpm = 120  # Default
        return self._bpm
    
    @property
    def seconds_per_beat(self):
        """Calculate beat timing based on BPM"""
        return 60.0 / self.bpm
    
    def _detect_bpm(self, filepath):
        """Automatically detect BPM from audio file"""
        try:
            import librosa
            print(f"Detecting BPM for {self.name}... (this may take a moment)")
            y, sr = librosa.load(filepath)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            print(f"Auto-detected BPM for {self.name}: {tempo:.1f}")
            return float(tempo)
        except ImportError:
            print(f"Warning: librosa not installed. Install with 'pip install librosa' for auto BPM detection.")
            print(f"Using default BPM of 120 for {self.name}")
            return 120.0
        except FileNotFoundError:
            print(f"Warning: Audio file not found: {filepath}")
            print(f"Using default BPM of 120 for {self.name}")
            return 120.0
        except Exception as e:
            print(f"Error detecting BPM for {filepath}: {e}")
            print(f"Using default BPM of 120 for {self.name}")
            return 120.0

# =============================================================================
# ADD YOUR SONGS HERE - EXTREMELY EASY TO EDIT!
# =============================================================================

SONGS = {
    # Main battle theme - plays in Dark Forest
    "battle_theme": Song(
        name="Battle Theme - Dark Forest",
        filepath="Assets/Music/Dark_Forest/OxT - HIGHEST.mp3",  # Put your battle music here!
        bpm=180,  # Adjust to match your music
        time_signature_beats=4,
        auto_detect_bpm=False
    ),
    
    # City theme - peaceful town music
    "city_theme": Song(
        name="City Theme",
        filepath="Assets/Music/City/OxT - HIGHEST.mp3",  # Put your city music here!
        bpm=120,  # Slower, calmer
        time_signature_beats=4,
        auto_detect_bpm=False
    ),
    
    # Player room - calm ambience
    "calm_theme": Song(
        name="Calm Theme - Player Room",
        filepath="Assets/Music/Player_Room/OxT - HIGHEST.mp3",  # Put your room music here!
        bpm=90,  # Very slow and calm
        time_signature_beats=4,
        auto_detect_bpm=False
    ),
    
    # Start menu music
    "menu_theme": Song(
        name="Menu Theme",
        filepath="Assets/Music/Start_Menu/OxT - HIGHEST.mp3",  # Put your menu music here!
        bpm=140,
        time_signature_beats=4,
        auto_detect_bpm=False
    ),
    
    # For backwards compatibility
    "highest": Song(
        name="OxT - HIGHEST",
        filepath="Assets/Music/OxT - HIGHEST.mp3",
        bpm=180,
        time_signature_beats=4,
        auto_detect_bpm=False
    ),
    
    # Add more songs here - BPM will be detected automatically!
    # Just add: "your_id": Song("Name", "path/to/song.mp3"),
}

# =============================================================================
# BEAT COUNTER DISPLAY CONFIGURATION - EASY TO EDIT!
# =============================================================================

BEAT_COUNTER_CONFIG = {
    "enabled": True,              # Show beat counter? True/False
    "position": "bottom_right",   # Options: "bottom_right", "bottom_left", "top_right", "top_left", "center"
    "offset_x": 20,               # Distance from edge (pixels)
    "offset_y": 20,               # Distance from edge (pixels)
    "font_size": 48,              # Size of beat numbers
    "color": (255, 255, 255),     # Color (R, G, B) - white by default
    "highlight_color": (255, 215, 0),  # Color for current beat - gold by default
    "show_bpm": True,             # Show BPM info? True/False
    "show_time_sig": True,        # Show time signature? True/False
}

# =============================================================================
# AUDIO SYSTEM CLASS - Handles playback and beat tracking
# =============================================================================

class AudioSystem:
    """Manages music playback and beat synchronization"""
    
    def __init__(self):
        pygame.mixer.init()
        self.current_song = None
        self.font = pygame.font.SysFont(None, BEAT_COUNTER_CONFIG["font_size"])
        self.info_font = pygame.font.SysFont(None, 24)
    
    def play_song(self, song_id):
        """Start playing a song by its ID"""
        if song_id not in SONGS:
            print(f"Warning: Song '{song_id}' not found!")
            return False
        
        song = SONGS[song_id]
        
        try:
            pygame.mixer.music.load(song.filepath)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            song.is_playing = True
            song.start_time = time.time()
            song.last_beat_time = song.start_time
            song.current_beat = 1
            self.current_song = song
            return True
        except:
            print(f"Error: Could not load '{song.filepath}'")
            return False
    
    def stop_song(self):
        """Stop the currently playing song"""
        pygame.mixer.music.stop()
        if self.current_song:
            self.current_song.is_playing = False
        self.current_song = None
    
    def update(self):
        """Update beat counter - call this every frame"""
        if not self.current_song or not self.current_song.is_playing:
            return
        
        current_time = time.time()
        elapsed = current_time - self.current_song.last_beat_time
        
        # Check if we've hit the next beat
        if elapsed >= self.current_song.seconds_per_beat:
            self.current_song.current_beat += 1
            if self.current_song.current_beat > self.current_song.time_signature_beats:
                self.current_song.current_beat = 1
            self.current_song.last_beat_time = current_time
    
    def draw_beat_counter(self, screen, current_level_id=None):
        """Draw the beat counter on screen
        
        Args:
            screen: Surface to draw on
            current_level_id: Current level identifier (only show BPM in dark_forest)
        """
        if not BEAT_COUNTER_CONFIG["enabled"]:
            return
        
        # Only show beat counter in dark forest
        if current_level_id != "dark_forest":
            return
        
        if not self.current_song or not self.current_song.is_playing:
            return
        
        song = self.current_song
        
        # Calculate position
        pos_x, pos_y = self._get_position(screen)
        
        # Draw beat numbers (e.g., "1 2 3 4" with current beat highlighted)
        beat_text = ""
        for i in range(1, song.time_signature_beats + 1):
            beat_text += str(i) + " "
        
        # Draw all beats
        y_offset = 0
        for i in range(1, song.time_signature_beats + 1):
            color = BEAT_COUNTER_CONFIG["highlight_color"] if i == song.current_beat else BEAT_COUNTER_CONFIG["color"]
            beat_surface = self.font.render(str(i), True, color)
            screen.blit(beat_surface, (pos_x + (i - 1) * 40, pos_y + y_offset))
        
        # Draw BPM info
        if BEAT_COUNTER_CONFIG["show_bpm"]:
            bpm_text = f"BPM: {song.bpm}"
            bpm_surface = self.info_font.render(bpm_text, True, (200, 200, 200))
            screen.blit(bpm_surface, (pos_x, pos_y - 30))
        
        # Draw time signature
        if BEAT_COUNTER_CONFIG["show_time_sig"]:
            sig_text = f"{song.time_signature_beats}/{song.time_signature_note}"
            sig_surface = self.info_font.render(sig_text, True, (200, 200, 200))
            screen.blit(sig_surface, (pos_x + 150, pos_y - 30))
    
    def _get_position(self, screen):
        """Calculate beat counter position based on config"""
        screen_w = screen.get_width()
        screen_h = screen.get_height()
        offset_x = BEAT_COUNTER_CONFIG["offset_x"]
        offset_y = BEAT_COUNTER_CONFIG["offset_y"]
        
        position = BEAT_COUNTER_CONFIG["position"]
        
        if position == "bottom_right":
            return (screen_w - 200 - offset_x, screen_h - 80 - offset_y)
        elif position == "bottom_left":
            return (offset_x, screen_h - 80 - offset_y)
        elif position == "top_right":
            return (screen_w - 200 - offset_x, offset_y)
        elif position == "top_left":
            return (offset_x, offset_y)
        elif position == "center":
            return (screen_w // 2 - 100, screen_h // 2)
        else:
            return (screen_w - 200 - offset_x, screen_h - 80 - offset_y)  # Default to bottom right

# =============================================================================
# USAGE EXAMPLE
# =============================================================================
"""
In your main game file:

from Assets.AudioConfig import AudioSystem

# Initialize
audio_system = AudioSystem()

# In game start or level load
audio_system.play_song("battle_theme")

# In your game update loop
audio_system.update()

# In your game draw loop
audio_system.draw_beat_counter(screen)

# To stop music
audio_system.stop_song()
"""