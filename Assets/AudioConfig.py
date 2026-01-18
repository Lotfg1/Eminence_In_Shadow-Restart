# Assets/AudioConfig.py
"""
EASY AUDIO CONFIGURATION
========================
Add your songs here - BPM will be automatically detected!
The game will automatically play them and display the beat counter.
"""

import pygame
import time
import os
import random

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
        """Calculate beat timing based on BPM - quarter notes"""
        return 60.0 / self.bpm  # Standard quarter note timing
    
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
        bpm=None,  # Auto-detect actual BPM
        time_signature_beats=4,
        auto_detect_bpm=True
    ),
    
    # City theme - peaceful town music
    "city_theme": Song(
        name="City Theme",
        filepath="Assets/Music/City/OxT - HIGHEST.mp3",  # Put your city music here!
        bpm=None,  # Auto-detect actual BPM
        time_signature_beats=4,
        auto_detect_bpm=True
    ),
    
    # Player room - calm ambience
    "calm_theme": Song(
        name="Calm Theme - Player Room",
        filepath="Assets/Music/Player_Room/OxT - HIGHEST.mp3",  # Put your room music here!
        bpm=None,  # Auto-detect actual BPM
        time_signature_beats=4,
        auto_detect_bpm=True
    ),
    
    # Start menu music
    "menu_theme": Song(
        name="Menu Theme",
        filepath="Assets/Music/Start_Menu/OxT - HIGHEST.mp3",  # Put your menu music here!
        bpm=None,  # Auto-detect actual BPM
        time_signature_beats=4,
        auto_detect_bpm=True
    ),
    
    # For backwards compatibility
    "highest": Song(
        name="OxT - HIGHEST",
        filepath="Assets/Music/OxT - HIGHEST.mp3",
        bpm=None,  # Auto-detect actual BPM
        time_signature_beats=4,
        auto_detect_bpm=True
    ),
    
    # Add more songs here - BPM will be detected automatically!
    # Just add: "your_id": Song("Name", "path/to/song.mp3"),
}

# =============================================================================
# TIME SIGNATURE COUNTER DISPLAY CONFIGURATION - EASY TO EDIT!
# =============================================================================

TIME_SIGNATURE_COUNTER_CONFIG = {
    "enabled": True,              # Show time signature counter? True/False
    "position": "bottom_right",   # Options: "bottom_right", "bottom_left", "top_right", "top_left", "center"
    "offset_x": 20,               # Distance from edge (pixels)
    "offset_y": 20,               # Distance from edge (pixels)
    "font_size": 48,              # Size of beat numbers
    "color": (255, 255, 255),     # Color (R, G, B) - white by default
    "highlight_color": (255, 215, 0),  # Color for current beat - gold by default
    # Counter increments: if BPM > 160, count every 2 beats; else every 1 beat
}

def get_beat_increment(bpm):
    """Returns beat increment: 1 for <= 160 BPM, 2 for > 160 BPM"""
    return 2 if bpm > 160 else 1

# =============================================================================
# AUDIO SYSTEM CLASS - Handles playback and beat tracking
# =============================================================================

class AudioSystem:
    """Manages music playback and beat synchronization"""
    
    def __init__(self, settings=None):
        pygame.mixer.init()
        self.current_song = None
        self.font = pygame.font.SysFont(None, TIME_SIGNATURE_COUNTER_CONFIG["font_size"])
        self.info_font = pygame.font.SysFont(None, 24)

        # Volume controls (0.0 - 1.0)
        self.master_volume = 1.0
        self.music_volume = 1.0
        self.sfx_volume = 1.0

        # Pending crossfade state
        self._pending_song = None
        self._pending_start_time = 0.0
        self._pending_fade_in_ms = 0

        if settings:
            audio_cfg = settings.audio
            self.set_volumes(
                audio_cfg.get("master_volume", 1.0),
                audio_cfg.get("music_volume", 1.0),
                audio_cfg.get("sfx_volume", 1.0)
            )
        else:
            self._apply_music_volume()
    
    def play_song(self, song_or_path, fade_out_ms=600, fade_in_ms=600):
        """Play a song by ID from SONGS or by direct file path, with fade."""
        # Resolve song target
        song = None
        if isinstance(song_or_path, Song):
            song = song_or_path
        elif isinstance(song_or_path, str):
            if song_or_path in SONGS:
                song = SONGS[song_or_path]
            else:
                # Treat as a direct filepath; create a lightweight Song
                name = os.path.splitext(os.path.basename(song_or_path))[0]
                song = Song(name=name, filepath=song_or_path, bpm=None, auto_detect_bpm=True)
        else:
            print("Warning: Invalid song identifier provided to play_song")
            return False

        # Skip if same file already playing
        if self.current_song and self.current_song.is_playing:
            if os.path.abspath(self.current_song.filepath) == os.path.abspath(song.filepath):
                return True
            # Fade out current and schedule next
            try:
                pygame.mixer.music.fadeout(int(fade_out_ms))
            except Exception:
                pygame.mixer.music.stop()
            self.current_song.is_playing = False
            self._pending_song = song
            self._pending_start_time = time.time() + (fade_out_ms / 1000.0)
            self._pending_fade_in_ms = int(fade_in_ms)
            return True
        else:
            # Play immediately with optional fade-in
            try:
                pygame.mixer.music.load(song.filepath)
                self._apply_music_volume()
                pygame.mixer.music.play(-1, fade_ms=int(fade_in_ms))
                song.is_playing = True
                song.start_time = time.time()
                song.last_beat_time = song.start_time
                song.current_beat = 0
                self.current_song = song
                return True
            except Exception as e:
                print(f"Error: Could not load '{song.filepath}': {e}")
                return False
    
    def stop_song(self):
        """Stop the currently playing song (fade out)"""
        try:
            pygame.mixer.music.fadeout(500)
        except Exception:
            pygame.mixer.music.stop()
        if self.current_song:
            self.current_song.is_playing = False
        self.current_song = None
    
    def update(self):
        """Update beat counter and handle pending crossfades - call every frame"""
        # Handle scheduled song start after fade-out
        if self._pending_song and time.time() >= self._pending_start_time:
            try:
                pygame.mixer.music.load(self._pending_song.filepath)
                self._apply_music_volume()
                pygame.mixer.music.play(-1, fade_ms=self._pending_fade_in_ms)
                self._pending_song.is_playing = True
                self._pending_song.start_time = time.time()
                self._pending_song.last_beat_time = self._pending_song.start_time
                self._pending_song.current_beat = 0
                self.current_song = self._pending_song
            except Exception as e:
                print(f"Error: Could not load '{self._pending_song.filepath}': {e}")
                self.current_song = None
            finally:
                self._pending_song = None
                self._pending_start_time = 0.0
                self._pending_fade_in_ms = 0

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
    
    def get_nearest_beat_time(self):
        """Get the timestamp of the nearest beat (past or future)"""
        if not self.current_song or not self.current_song.is_playing:
            return time.time()
        
        current_time = time.time()
        elapsed = current_time - self.current_song.last_beat_time
        next_beat_time = self.current_song.last_beat_time + self.current_song.seconds_per_beat
        
        # If we're closer to the last beat, return that; otherwise next beat
        if elapsed < self.current_song.seconds_per_beat / 2:
            return self.current_song.last_beat_time
        else:
            return next_beat_time
    
    @property
    def beat_progress(self):
        """Get progress to next beat (0.0 to 1.0)"""
        if not self.current_song or not self.current_song.is_playing:
            return 0.0
        
        current_time = time.time()
        elapsed = current_time - self.current_song.last_beat_time
        return min(1.0, elapsed / self.current_song.seconds_per_beat)
    
    @property
    def current_beat(self):
        """Get current beat number"""
        if not self.current_song:
            return 1
        return self.current_song.current_beat
    
    def draw_time_signature_counter(self, screen, display_beat, beat_increment=1):
        """Draw the time signature counter on screen
        
        Shows a simple beat count based on time signature.
        If BPM > 160, counter increments every 2 beats; else every 1 beat.
        
        Args:
            screen: Surface to draw on
            display_beat: Current display beat number
            beat_increment: How much to increment per beat (1 or 2)
        """
        if not TIME_SIGNATURE_COUNTER_CONFIG["enabled"]:
            return
        
        if not self.current_song or not self.current_song.is_playing:
            return
        
        song = self.current_song
        
        # Calculate position
        pos_x, pos_y = self._get_time_sig_position(screen)
        
        # Draw main beat number (large)
        color = TIME_SIGNATURE_COUNTER_CONFIG["highlight_color"]
        beat_surface = self.font.render(str(display_beat % 5), True, color)
        screen.blit(beat_surface, (pos_x, pos_y))
    
    def _get_time_sig_position(self, screen):
        """Calculate time signature counter position based on config"""
        screen_w = screen.get_width()
        screen_h = screen.get_height()
        offset_x = TIME_SIGNATURE_COUNTER_CONFIG["offset_x"]
        offset_y = TIME_SIGNATURE_COUNTER_CONFIG["offset_y"]
        
        position = TIME_SIGNATURE_COUNTER_CONFIG["position"]
        
        if position == "bottom_right":
            return (screen_w - 100 - offset_x, screen_h - 80 - offset_y)
        elif position == "bottom_left":
            return (offset_x, screen_h - 80 - offset_y)
        elif position == "top_right":
            return (screen_w - 100 - offset_x, offset_y)
        elif position == "top_left":
            return (offset_x, offset_y)
        elif position == "center":
            return (screen_w // 2 - 50, screen_h // 2)
        else:
            return (screen_w - 100 - offset_x, screen_h - 80 - offset_y)

    # ==================== VOLUME HELPERS ====================
    def set_volumes(self, master_volume, music_volume, sfx_volume):
        """Apply volume settings and push them to the mixer"""
        self.master_volume = self._clamp(master_volume)
        self.music_volume = self._clamp(music_volume)
        self.sfx_volume = self._clamp(sfx_volume)
        self._apply_music_volume()

    def get_sfx_volume(self):
        return self.master_volume * self.sfx_volume

    def apply_sfx_volume(self, sound):
        try:
            sound.set_volume(self.get_sfx_volume())
        except Exception:
            pass

    def _apply_music_volume(self):
        try:
            pygame.mixer.music.set_volume(self.master_volume * self.music_volume)
        except Exception:
            pass

    @staticmethod
    def _clamp(value):
        return max(0.0, min(1.0, float(value)))

# =============================================================================
# USAGE EXAMPLE
# =============================================================================
"""
In your main game file:

from Assets.AudioConfig import AudioSystem, MusicManager

# Initialize
audio_system = AudioSystem()
music_manager = MusicManager()

# Get random song for a level
song_id = music_manager.get_random_song("dark_forest")
audio_system.play_song(song_id)

# In your game update loop
audio_system.update()

# In your game draw loop
audio_system.draw_beat_counter(screen)

# To stop music
audio_system.stop_song()
"""


# ============================================================================
# MUSIC MANAGER - Handle song selection per level
# ============================================================================

class MusicManager:
    """Manages song selection and organization by level"""
    
    # Level to music folder mappings
    LEVEL_MUSIC_FOLDERS = {
        "dark_forest": "Assets/Music/Dark_Forest",
        "city": "Assets/Music/City",
        "player_room": "Assets/Music/Player_Room",
        "start_menu": "Assets/Music/Start_Menu",
    }
    
    # Cache of loaded songs per level
    _music_cache = {}
    
    # Level to song ID mappings - all songs per level
    LEVEL_MUSIC = {
        "dark_forest": ["battle_theme"],
        "city": ["city_theme"],
        "player_room": ["calm_theme"],
        "start_menu": ["menu_theme"],
    }
    
    # Default fallback songs
    DEFAULT_MUSIC = {
        "menu": "menu_theme",
        "combat": "battle_theme",
        "exploration": "city_theme",
    }
    
    @staticmethod
    def _get_music_files_from_folder(folder_path):
        """Get all music files from a folder"""
        audio_extensions = {'.mp3', '.wav', '.ogg', '.flac'}
        music_files = []
        
        try:
            if os.path.exists(folder_path):
                for filename in os.listdir(folder_path):
                    if os.path.splitext(filename)[1].lower() in audio_extensions:
                        full_path = os.path.join(folder_path, filename)
                        music_files.append(full_path)
        except Exception as e:
            print(f"Error reading music folder {folder_path}: {e}")
        
        return music_files
    
    @staticmethod
    def get_random_song_from_level(level_id):
        """Get a random song file from the level's music folder"""
        # Check cache first
        if level_id in MusicManager._music_cache:
            files = MusicManager._music_cache[level_id]
            if files:
                return random.choice(files)
        
        # Get folder path for this level
        folder_path = MusicManager.LEVEL_MUSIC_FOLDERS.get(level_id, "Assets/Music")
        
        # Get all music files from the folder
        music_files = MusicManager._get_music_files_from_folder(folder_path)
        
        # Cache the results
        MusicManager._music_cache[level_id] = music_files
        
        # Return a random file, or fallback
        if music_files:
            return random.choice(music_files)
        else:
            # Fallback to old system if folder doesn't exist
            return MusicManager.get_random_song(level_id)
    
    @staticmethod
    def get_random_song(level_name):
        """Get a random song ID for the given level; fallback to any SONGS."""
        songs = MusicManager.LEVEL_MUSIC.get(level_name)
        if songs:
            return random.choice(songs)
        # Fallback: choose any registered song
        if SONGS:
            return random.choice(list(SONGS.keys()))
        return MusicManager.DEFAULT_MUSIC["exploration"]
    
    @staticmethod
    def get_song_for_level(level_name):
        """Get the primary song for a level (first in list)"""
        songs = MusicManager.LEVEL_MUSIC.get(level_name)
        return songs[0] if songs else MusicManager.DEFAULT_MUSIC["exploration"]
    
    @staticmethod
    def add_level_music(level_name, song_id):
        """Add a song ID to a level's music pool"""
        if level_name not in MusicManager.LEVEL_MUSIC:
            MusicManager.LEVEL_MUSIC[level_name] = []
        if song_id not in MusicManager.LEVEL_MUSIC[level_name]:
            MusicManager.LEVEL_MUSIC[level_name].append(song_id)
