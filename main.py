# ============================================================================
# EMINENCE IN SHADOW - RESTART
# ============================================================================
# A simple 2D platformer game.
#
# Main flow:
#  1. Config class: All game settings in one place
#  2. Game class: Main game object that handles everything
#  3. update(): Called every frame - update positions, physics, etc
#  4. draw(): Called every frame - render everything on screen
#  5. run(): Main loop that ties it all together
#
# ============================================================================
import pygame
import sys
import time
import math
import random
import json
import importlib.util
import os
import numpy as np
from Assets.Settings import Settings
from Assets.Characters import MainCharacter
from Assets.Menus import StartMenu, PauseMenu, MerchantMenu, TravelMenu, SettingsMenu, StatusMenu, ScrollableLayout, InventoryMenu, EquipmentMenu
from Assets.AudioConfig import AudioSystem, MusicManager
from Assets.RhythmBattle import RhythmBattleSystem
from Assets.AttackConfig import AttackConfig
from Assets.SpellSystem import SpellCastingSystem

# ==================== CONFIGURATION ====================
class Config:
    """Central configuration for the game"""
    # Display - Original dimensions (2x zoom handled differently)
    SCREEN_WIDTH = 1080
    SCREEN_HEIGHT = 920
    FPS = 60
    WINDOW_TITLE = "Eminence in Shadow: Restart"
    
    # Visual Settings
    ZOOM_SCALE = 1.5
    AVAILABLE_ZOOM_LEVELS = [1.0, 1.25, 1.5, 1.75, 2.0]  # Zoom options in settings
    
    # Camera
    LOOK_AHEAD_MAX = 90
    LOOK_AHEAD_ACCEL = 6
    LOOK_AHEAD_RETURN = 8
    CAMERA_SMOOTHING = 0.25  # Faster camera response to knockback
    
    # Level
    SEGMENT_WIDTH = 768
    
    # Player
    PLAYER_WIDTH = 64
    PLAYER_HEIGHT = 64
    PLAYER_SPEED = 7
    PLAYER_JUMP_STRENGTH = -24  # Not used anymore
    PLAYER_TELEPORT_DISTANCE = 300  # How far up to teleport
    GRAVITY = 0.7
    MAX_FALL_SPEED = 12
    
    # Interaction
    INTERACTION_BOX_INFLATE = (80, 40)
    ICON_OFFSET_Y = 25  # How far above object to show icon
    
    # Transition
    TRANSITION_SPEED = 40
    
    # Go Back Timer
    GO_BACK_TIMER_DURATION = 5.0  # 5 seconds
    FADE_SPEED = 10  # Alpha change per frame
    GO_BACK_CANCEL_DISTANCE = 30  # Pixels moved to cancel timer
    
    # Colors - All configurable for easy transparency
    COLOR_SKY = (30, 30, 80)
    COLOR_GROUND = (100, 100, 100)
    COLOR_PLATFORM = (160, 82, 45)
    COLOR_INTERACTABLE = (200, 100, 200)
    COLOR_PLAYER = (0, 255, 0)
    COLOR_TRANSITION = (0, 0, 0)
    COLOR_COLORKEY = (255, 0, 255)
    COLOR_TIMER_BG = (0, 0, 0)
    COLOR_TIMER_TEXT = (255, 255, 255)
    COLOR_MERCHANT = (200, 100, 200)
    COLOR_BED = (150, 75, 0)
    COLOR_WALL = (80, 80, 80)
    COLOR_TENT = (120, 80, 60)
    COLOR_TENT_BASE = (90, 60, 40)
    COLOR_TENT_OUTLINE = (80, 50, 30)
    COLOR_ROCK = (70, 70, 70)
    COLOR_ROCK_OUTLINE = (50, 50, 50)
    
    # Alpha values (0-255, 0 = fully transparent, 255 = fully opaque)
    ALPHA_GROUND = 255
    ALPHA_PLATFORM = 255
    ALPHA_INTERACTABLE = 255
    ALPHA_PLAYER = 255
    ALPHA_MERCHANT = 255
    ALPHA_BED = 255
    ALPHA_WALL = 255
    ALPHA_TENT = 255
    ALPHA_ROCK = 255
    
    # Image/Sprite Settings
    USE_IMAGES = False  # Set to True to use images instead of rectangles
    PLAYER_IMAGE_PATH = "Assets/Photos/Player.png"
    GROUND_IMAGE_PATH = "Assets/Photos/Ground.png"
    PLATFORM_IMAGE_PATH = "Assets/Photos/Platform.png"
    MERCHANT_IMAGE_PATH = "Assets/Photos/Merchant.png"
    BED_IMAGE_PATH = "Assets/Photos/Bed.png"
    WALL_IMAGE_PATH = "Assets/Photos/Wall.png"
    TENT_IMAGE_PATH = "Assets/Photos/Tent.png"
    ROCK_IMAGE_PATH = "Assets/Photos/Rock.png"
    CITY_BACKGROUND_PATH = "Assets/Photos/city.jpg"
    
    # Paths
    LEVEL_PATHS = [
        "Assets/Levels/Player_Room.py",
        "Assets/Levels/City.py",
        "Assets/Levels/Dark_Forest.py"
    ]
    INTERACT_ICON_PATH = "Assets/Photos/Key_Placeholder_Image.png"
    COIN_IMAGE_PATH = "Assets/Photos/Coin.png"
    COIN_ANIMATION_PATH = "Assets/Animations/Coin.gif"
    SETTINGS_PATH = "Assets/settings.json"

# GAME CLASS
class Game:
    def __init__(self):
        pygame.init()
        self.config = Config()
        self.settings = Settings(self.config.SETTINGS_PATH)
        
        # Display setup - create a scaled surface for zoom
        self.display_surface = pygame.display.set_mode((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        pygame.display.set_caption(self.config.WINDOW_TITLE)
        
        # Internal screen based on zoom scale (smaller = more zoomed in)
        internal_width = int(self.config.SCREEN_WIDTH / self.config.ZOOM_SCALE)
        internal_height = int(self.config.SCREEN_HEIGHT / self.config.ZOOM_SCALE)
        self.screen = pygame.Surface((internal_width, internal_height))
        
        self.clock = pygame.time.Clock()
        # Use Cavalhatriz font if available
        self.font_path = os.path.join("Assets", "Fonts", "Cavalhatriz.ttf")
        self.font = pygame.font.Font(self.font_path if os.path.exists(self.font_path) else None, 32)
        self.font_large = pygame.font.Font(self.font_path if os.path.exists(self.font_path) else None, 48)
        self.timer_font = pygame.font.Font(self.font_path if os.path.exists(self.font_path) else None, 48)
        self.hint_font = pygame.font.Font(self.font_path if os.path.exists(self.font_path) else None, 22)

        # Player
        self.player = MainCharacter()
        self.saved_y_momentum = 0  # Store y_momentum when menu opens
        
        # Frame counter
        self.frame_counter = 0

        # Camera - adjusted for zoom
        self.camera_x = 0
        self.camera_y = 0
        self.look_offset_x = 0
        
        # Jump cooldown (frame-based instead of time.sleep)
        self.jump_cooldown = 0
        self.jump_cooldown_max = 12  # 12 frames = 0.2 seconds at 60 FPS

        # Level management
        self.level_files = self.config.LEVEL_PATHS
        self.current_level_index = 0
        self.level_data = {}
        
        # Drops (flying loot on enemy death)
        self.drops = []
        
        # Audio system - simple background music
        self.audio_system = AudioSystem(self.settings)
        # Start with menu theme
        self.audio_system.play_song("menu_theme")
        
        # Rhythm battle system
        self.rhythm_system = RhythmBattleSystem(self.audio_system)
        
        # Spell casting system
        self.spell_system = SpellCastingSystem(self.audio_system)
        
        # Track player health for damage detection (screen shake)
        self.last_player_health = self.player.stats.get('Current_Health', 100)
        
        # Load the starting level
        self.load_level(self.level_files[self.current_level_index])

        # Ensure zoom level exists
        if "zoom_level" not in self.settings.display:
            self.settings.display["zoom_level"] = self.config.ZOOM_SCALE
            self.settings.save()
        
        # Apply zoom from settings
        self.apply_zoom(self.settings.display["zoom_level"])
        
        self._initialize_menus()
        self.previous_menu = None  # Track menu navigation

        # Interaction
        self.interact_icon = pygame.image.load(self.config.INTERACT_ICON_PATH)

        # Transition system
        self._initialize_transition()
        self.apply_audio_settings()
        
        # Go Back timer system
        self.go_back_active = False
        self.go_back_timer = 0.0
        self.go_back_fade_phase = None  # None, "fade_out", "fade_in"
        self.go_back_fade_alpha = 0
        self.go_back_start_pos = (0, 0)  # Store player position when timer starts
        
        # Load images if enabled
        self.images = {}
        if self.config.USE_IMAGES:
            self._load_images()
        else:
            # Still load city background even if sprites use rectangles
            self.images['city_bg'] = pygame.image.load(self.config.CITY_BACKGROUND_PATH).convert() if os.path.exists(self.config.CITY_BACKGROUND_PATH) else None
        
        # Screen shake system
        self.shake_intensity = 0.0  # Current shake intensity (0.0-1.0)
        self.shake_duration = 0.0   # Remaining shake duration in seconds
        self.shake_offset_x = 0     # Current shake offset
        self.shake_offset_y = 0

    def _load_images(self):
        """Load all images for sprites"""
        try:
            self.images['player'] = pygame.image.load(self.config.PLAYER_IMAGE_PATH)
            self.images['ground'] = pygame.image.load(self.config.GROUND_IMAGE_PATH)
            self.images['platform'] = pygame.image.load(self.config.PLATFORM_IMAGE_PATH)
            self.images['merchant'] = pygame.image.load(self.config.MERCHANT_IMAGE_PATH)
            self.images['bed'] = pygame.image.load(self.config.BED_IMAGE_PATH)
            self.images['wall'] = pygame.image.load(self.config.WALL_IMAGE_PATH)
            self.images['tent'] = pygame.image.load(self.config.TENT_IMAGE_PATH)
            self.images['rock'] = pygame.image.load(self.config.ROCK_IMAGE_PATH)
            # Optional city background image
            if os.path.exists(self.config.CITY_BACKGROUND_PATH):
                self.images['city_bg'] = pygame.image.load(self.config.CITY_BACKGROUND_PATH).convert()
            else:
                self.images['city_bg'] = None
        except:
            print("Warning: Some images could not be loaded, falling back to rectangles")
            self.config.USE_IMAGES = False
    
    def draw_text_with_shadow(self, text, font, color, x, y, shadow_offset=2):
        """Draw text with a shadow for better readability"""
        # Draw shadow
        shadow_surface = font.render(text, True, (0, 0, 0))
        self.screen.blit(shadow_surface, (x + shadow_offset, y + shadow_offset))
        # Draw main text
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))
        return text_surface
    
    def apply_zoom(self, zoom_level):
        """Smoothly transition to zoom level"""
        # Store target zoom instead of applying immediately
        if not hasattr(self, 'target_zoom'):
            self.target_zoom = self.config.ZOOM_SCALE
            self.zoom_speed = 0.01  # Very slow smooth zoom
        
        self.target_zoom = zoom_level

    def apply_audio_settings(self):
        """Sync saved audio settings to the mixer and sounds"""
        volumes = self.settings.audio
        self.audio_system.set_volumes(
            volumes.get("master_volume", 1.0),
            volumes.get("music_volume", 1.0),
            volumes.get("sfx_volume", 1.0),
        )

        if hasattr(self, "travel_sound"):
            self.audio_system.apply_sfx_volume(self.travel_sound)

    def trigger_screen_shake(self, intensity=0.5, duration=0.2):
        """Trigger a screen shake effect
        
        Args:
            intensity: How strong the shake is (0.0-1.0, multiplied by 5 pixels)
            duration: How long the shake lasts in seconds
        """
        self.shake_intensity = min(1.0, max(0.0, intensity))
        self.shake_duration = duration

    def _initialize_menus(self):
        """Initialize all menu objects"""
        from Assets.Menus import KeyBindsMenu
        self.menus = {
            "start": StartMenu(self.font, self.settings),
            "pause": PauseMenu(self.font, self.screen.get_width(), self.settings),
            "merchant": MerchantMenu(self.font, self.settings),
            "settings": SettingsMenu(self.font, self.settings, self.config),
            "status": StatusMenu(self.font, self.player, self.settings),
            "keybinds": KeyBindsMenu(self.font, self.settings),
            "inventory": InventoryMenu(self.player, self.settings),
            "equipment": EquipmentMenu(self.player, self.settings)
        }
        self.active_menu = "start"
        self.travel_menu = None
        self.pause_player_physics()
    
    def _initialize_transition(self):
        """Initialize transition system"""
        self.transitioning = False
        self.transition_radius = 0
        self.transition_phase = None
        self.transition_target = None
        self.transition_destination_name = ""
        self.destination_fade_alpha = 255
        # Use internal screen size for transition (calculated dynamically)
        internal_width = int(self.config.SCREEN_WIDTH / self.config.ZOOM_SCALE)
        internal_height = int(self.config.SCREEN_HEIGHT / self.config.ZOOM_SCALE)
        self.transition_max = int((internal_width ** 2 + internal_height ** 2) ** 0.5)
        self.transition_surface = pygame.Surface((internal_width, internal_height))
        self.transition_surface.set_colorkey(self.config.COLOR_COLORKEY)
        # Load travel sound
        self.travel_sound = pygame.mixer.Sound("Assets/Music/SFXs/Travel_noise.mp3")

    # ==================== LEVEL MANAGEMENT ====================
    def load_level(self, filepath):
        """Load a new level from a Python file"""
        # Import the level file as a Python module
        spec = importlib.util.spec_from_file_location("level_module", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.level_data = module.load_level()  # Get level data (enemies, platforms, etc)
        
        # Reset player to starting position
        self.player.rect.topleft = self.level_data["player_start"]
        self.player.y_momentum = 0
        self.player.on_ground = False
        
        # Reset camera to center
        self.camera_x = 0
        self.camera_y = 0
        self.look_offset_x = 0
        
        # For infinite levels, generate starting segments
        if self.level_data.get("infinite", False):
            seg = self.player.rect.centerx // self.config.SEGMENT_WIDTH
            for i in range(seg - 2, seg + 3):
                self.level_data["generate_segment"](i)
        
        # Clear any leftover drops from previous level
        self.drops.clear()
        
        # Change music based on level - use registered songs for correct BPM
        level_id = self.level_data.get("level_id", "exploration")
        level_music = MusicManager.get_random_song(level_id)
        
        # Play the song ID (which has correct BPM set)
        try:
            self.audio_system.play_song(level_music)
            # Reset rhythm circle BPM when song changes
            if hasattr(self.rhythm_system, 'reset_beat_tracking'):
                self.rhythm_system.reset_beat_tracking()
        except Exception as e:
            print(f"Error loading music: {e}")
            # Fallback to menu theme if song fails to load
            try:
                self.audio_system.play_song("menu_theme")
            except:
                pass
    
    def save_game(self):
        """Save current game state to a JSON file"""
        save_data = {
            "player": {
                "position": [self.player.rect.x, self.player.rect.y],
                "level": self.player.level,
                "exp": self.player.experience,
                "exp_for_next_level": self.player.exp_for_next_level,
                "stats": self.player.stats.copy()
            },
            "current_level_index": self.current_level_index,
            "current_level": self.level_files[self.current_level_index]
        }
        
        try:
            with open("save_data.json", "w") as f:
                json.dump(save_data, f, indent=2)
            print("Game saved successfully!")
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self):
        """Load game state from save file"""
        try:
            with open("save_data.json", "r") as f:
                save_data = json.load(f)
            
            # Load player data
            player_data = save_data["player"]
            self.player.level = player_data["level"]
            self.player.experience = player_data["exp"]
            self.player.exp_for_next_level = player_data["exp_for_next_level"]
            self.player.stats = player_data["stats"].copy()
            
            # Load level
            level_index = save_data["current_level_index"]
            if level_index < len(self.level_files):
                self.current_level_index = level_index
                self.load_level(self.level_files[self.current_level_index])
                # Set player position after level load
                self.player.rect.x, self.player.rect.y = player_data["position"]

            # After loading, ensure nothing spawns too close to player
            self._prune_spawn_safe_radius(500)
            
            print("Game loaded successfully!")
            return True
        except FileNotFoundError:
            print("No save file found.")
            return False
        except Exception as e:
            print(f"Error loading game: {e}")
            return False

    def get_collision_rects(self):
        """Get list of all solid objects player can collide with"""
        rects = [
            *self.level_data.get("ground", []),  # Solid ground
            *self.level_data.get("platforms", [])  # Floating platforms
        ]
        # Add interactables that are solid
        rects += [o.rect for o in self.level_data.get("interactables", []) if getattr(o, "collidable", True)]
        # Add slopes (tents and rocks)
        rects += [t.get_collision_rect() for t in self.level_data.get("tents", [])]
        rects += [r.get_collision_rect() for r in self.level_data.get("rocks", [])]
        # Add coins
        rects += [c.rect for c in self.level_data.get("coins", []) if hasattr(c, "rect")]
        # For infinite levels, add all current segment collisions
        if self.level_data.get("infinite", False):
            for seg in self.level_data["segments"].values():
                g = seg["ground"]
                rects += [g] if isinstance(g, pygame.Rect) else g
                rects += seg["platforms"]
        return rects

    # ==================== CAMERA SYSTEM ====================
    def update_camera(self):
        """Position camera to follow player with smooth movement"""
        # Get the screen size (in game coordinates)
        internal_width = int(self.config.SCREEN_WIDTH / self.config.ZOOM_SCALE)
        internal_height = int(self.config.SCREEN_HEIGHT / self.config.ZOOM_SCALE)
        
        # Always center camera on player (even during combos)
        target_x = self.player.rect.centerx - (internal_width // 2)
        target_y = self.player.rect.centery - (internal_height // 2)
        
        keys = pygame.key.get_pressed()
        
        # Look-ahead: if player is moving, show a bit more in that direction
        if self.level_data.get("infinite", False):
            self._update_look_ahead(keys)
            target_x += self.look_offset_x
        else:
            self.look_offset_x = 0
        
        # Don't scroll past level boundaries
        target_x = self._clamp_camera_target_x(target_x, internal_width)
        target_y = self._clamp_camera_target_y(target_y, internal_height)
        
        # Smoothly move camera to target (not instant)
        self.camera_x += (target_x - self.camera_x) * self.config.CAMERA_SMOOTHING
        self.camera_y += (target_y - self.camera_y) * self.config.CAMERA_SMOOTHING
        
        # Apply screen shake offset
        self.camera_x += self.shake_offset_x
        self.camera_y += self.shake_offset_y

    def _update_look_ahead(self, keys):
        """Update camera look-ahead offset based on player movement"""
        if keys[self.settings.keybinds["MoveRight"]]:
            self.look_offset_x += self.config.LOOK_AHEAD_ACCEL
        elif keys[self.settings.keybinds["MoveLeft"]]:
            self.look_offset_x -= self.config.LOOK_AHEAD_ACCEL
        else:
            # Return to center
            if self.look_offset_x > 0:
                self.look_offset_x -= self.config.LOOK_AHEAD_RETURN
            elif self.look_offset_x < 0:
                self.look_offset_x += self.config.LOOK_AHEAD_RETURN
        
        self.look_offset_x = max(-self.config.LOOK_AHEAD_MAX, 
                                 min(self.config.LOOK_AHEAD_MAX, self.look_offset_x))

    def _clamp_camera_target_x(self, target_x, internal_width):
        """Clamp camera target X to level boundaries"""
        target_x = max(0, target_x)
        
        if not self.level_data.get("infinite", False):
            world_width = self.level_data.get("world_width", self.config.SCREEN_WIDTH)
            if world_width <= internal_width:
                target_x = -(internal_width - world_width) // 2
            else:
                target_x = min(target_x, world_width - internal_width)
        
        return target_x
    
    def _clamp_camera_target_y(self, target_y, internal_height):
        """Clamp camera target Y to level boundaries"""
        world_height = self.level_data.get("world_height", 920) if self.level_data else 920  # Allow per-level height
        
        # Keep camera from going too high or too low
        target_y = max(0, target_y)
        target_y = min(target_y, world_height - internal_height)
        
        return target_y

    def _clamp_camera_position(self, camera_x):
        """Clamp final camera position - not used anymore"""
        return camera_x

    # ==================== INTERACTION SYSTEM ====================
    def handle_interactions(self):
        """Check if player is touching an interactable object"""
        # Create a box around the player (larger than player for easier interaction)
        box = self.player.rect.inflate(*self.config.INTERACTION_BOX_INFLATE)
        
        # Check each interactable object in the level
        for obj in self.level_data.get("interactables", []):
            if box.colliderect(obj.rect):  # If player touches it
                # Call the object's interact function
                if hasattr(obj, "interact"):
                    obj.interact(self.player, self)
    
    
    def _prune_spawn_safe_radius(self, radius=500):
        """Remove spawned objects that are too close to the player (future segments only)."""
        px = self.player.rect.centerx
        player_seg = px // self.config.SEGMENT_WIDTH

        def keep_obj(obj):
            # Always keep level blockers
            if hasattr(obj, "destination_index"):
                return True
            cx = None
            if hasattr(obj, "rect"):
                cx = obj.rect.centerx
            elif isinstance(obj, pygame.Rect):
                cx = obj.centerx
            if cx is None:
                return True
            # Keep everything in the player's current segment
            obj_seg = cx // self.config.SEGMENT_WIDTH
            if obj_seg == player_seg:
                return True
            # Remove only if within the safety radius
            return abs(cx - px) > radius

        # Filter global lists
        for key in ["platforms", "natural_objects", "tents", "rocks", "enemies", "interactables"]:
            if key in self.level_data:
                self.level_data[key] = [o for o in self.level_data[key] if keep_obj(o)]

        # Filter per-segment lists to keep future lookups consistent
        if "segments" in self.level_data:
            for seg in self.level_data["segments"].values():
                for key in ["platforms", "natural_objects", "tents", "rocks", "interactables", "enemies"]:
                    if key in seg:
                        seg[key] = [o for o in seg[key] if keep_obj(o)]

    def _clear_first_segment_objects(self):
        """Remove objects from the first segment (segment index 0) except blockers/walls."""
        def in_first_seg(obj):
            cx = None
            if hasattr(obj, "rect"):
                cx = obj.rect.centerx
            elif isinstance(obj, pygame.Rect):
                cx = obj.centerx
            if cx is None:
                return False
            return (cx // self.config.SEGMENT_WIDTH) == 0

        def keep_obj(obj):
            if hasattr(obj, "destination_index"):
                return True
            return not in_first_seg(obj)

        for key in ["platforms", "natural_objects", "tents", "rocks", "enemies", "interactables"]:
            if key in self.level_data:
                self.level_data[key] = [o for o in self.level_data[key] if keep_obj(o)]

        if "segments" in self.level_data and 0 in self.level_data["segments"]:
            seg = self.level_data["segments"][0]
            for key in ["platforms", "natural_objects", "tents", "rocks", "interactables", "enemies"]:
                if key in seg:
                    seg[key] = [o for o in seg[key] if keep_obj(o)]

    def get_nearby_interactables(self):
        """Get all interactables near the player"""
        box = self.player.rect.inflate(*self.config.INTERACTION_BOX_INFLATE)
        nearby = []
        for obj in self.level_data.get("interactables", []):
            if box.colliderect(obj.rect):
                nearby.append(obj)
        return nearby

    # PLAYER PHYSICS PAUSE/RESUME
    def pause_player_physics(self):
        """Pause player movement and save momentum when opening menu"""
        self.player.moving_left = False
        self.player.moving_right = False
        self.saved_y_momentum = self.player.y_momentum
        self.player.y_momentum = 0
    
    def resume_player_physics(self):
        """Resume player physics when closing menu"""
        self.player.y_momentum = self.saved_y_momentum
        self.saved_y_momentum = 0

    # MENU SYSTEM
    def handle_menu_input(self, event):
        """Handle input for active menu"""
        menu = self.travel_menu if self.active_menu == "travel" else self.menus[self.active_menu]
        result = menu.handle_input(event)
        self.player.moving_left = False
        self.player.moving_right = False
        if result is None:
            return
        
        if result in ("close", "resume"):
            # Handle back navigation
            if self.active_menu == "settings" and self.previous_menu:
                self.active_menu = self.previous_menu
                self.previous_menu = None
            elif self.active_menu == "status" and self.previous_menu:
                self.active_menu = self.previous_menu
                self.previous_menu = None
            elif self.active_menu == "inventory" and self.previous_menu:
                self.active_menu = self.previous_menu
                self.previous_menu = None
            elif self.active_menu == "equipment" and self.previous_menu:
                self.active_menu = self.previous_menu
                self.previous_menu = None
            else:
                self.resume_player_physics()
                self.active_menu = None
                self.previous_menu = None
        elif result == "quit":
            pygame.quit()
            sys.exit()
        elif result == "start":
            self.resume_player_physics()
            self.active_menu = None
            self.previous_menu = None
        elif result == "continue":
            # Load saved game
            if self.load_game():
                self.resume_player_physics()
                self.active_menu = None
                self.previous_menu = None
            else:
                # If load fails, just start new game
                self.resume_player_physics()
                self.active_menu = None
                self.previous_menu = None
        elif result == "save_game":
            # Save the game
            self.save_game()
            # Stay in pause menu
        elif result == "settings":
            self.previous_menu = self.active_menu
            self.active_menu = "settings"
        elif result == "keybinds":
            self.previous_menu = self.active_menu
            self.active_menu = "keybinds"
        elif result == "Status":
            self.previous_menu = self.active_menu
            self.active_menu = "status"
        elif result == "inventory":
            self.previous_menu = self.active_menu
            self.active_menu = "inventory"
        elif result == "equipment":
            self.previous_menu = self.active_menu
            self.active_menu = "equipment"
        elif result == "go_back":
            self.resume_player_physics()
            self.start_go_back_timer()
        elif result == "audio_changed":
            self.apply_audio_settings()
        elif result == "zoom_changed":
            # Apply zoom immediately
            new_zoom = self.settings.display.get("zoom_level", 1.5)
            self.apply_zoom(new_zoom)
        elif isinstance(result, int):
            self.start_transition(result)

    def start_go_back_timer(self):
        """Start the 5-second timer for going back to level start"""
        self.go_back_active = True
        self.go_back_timer = self.config.GO_BACK_TIMER_DURATION
        self.go_back_start_pos = (self.player.rect.x, self.player.rect.y)
        self.active_menu = None
        self.previous_menu = None

    def update_go_back_timer(self, dt):
        """Update the go back timer"""
        if not self.go_back_active:
            return
        
        # Check if player has moved to cancel timer (allow movement anytime)
        distance_moved = ((self.player.rect.x - self.go_back_start_pos[0]) ** 2 + 
                        (self.player.rect.y - self.go_back_start_pos[1]) ** 2) ** 0.5
        if distance_moved > self.config.GO_BACK_CANCEL_DISTANCE:
            self.go_back_active = False
            self.go_back_timer = 0
            self.go_back_fade_phase = None
            return
        
        # Check if any enemy is in combo state (attacking) - cancel timer
        any_enemy_in_combo = any(getattr(e, "combo_state", 0) > 0 for e in self.level_data.get("enemies", []))
        if any_enemy_in_combo:
            self.go_back_active = False
            self.go_back_timer = 0
            self.go_back_fade_phase = None
            return
        
        # Handle fade phases
        if self.go_back_fade_phase == "fade_out":
            self.go_back_fade_alpha += self.config.FADE_SPEED
            if self.go_back_fade_alpha >= 255:
                self.go_back_fade_alpha = 255
                self.player.rect.topleft = self.level_data["player_start"]
                self.player.y_momentum = 0
                self.player.on_ground = False
                self.camera_x = 0
                self.camera_y = 0
                self.look_offset_x = 0
                self.go_back_fade_phase = "fade_in"
        elif self.go_back_fade_phase == "fade_in":
            self.go_back_fade_alpha -= self.config.FADE_SPEED
            if self.go_back_fade_alpha <= 0:
                self.go_back_fade_alpha = 0
                self.go_back_active = False
                self.go_back_fade_phase = None
        else:
            # Count down timer
            self.go_back_timer -= dt
            if self.go_back_timer <= 0:
                self.go_back_timer = 0
                self.go_back_fade_phase = "fade_out"
                self.go_back_fade_alpha = 0

    # TRANSITION SYSTEM
    def start_transition(self, target_level_index):
        """Begin transition to a new level"""
        self.transitioning = True
        self.transition_phase = "expand"
        self.transition_radius = 0
        self.transition_target = target_level_index
        # Get destination name from file path
        filepath = self.level_files[target_level_index]
        level_name = filepath.split('/')[-1].replace('.py', '')
        self.transition_destination_name = level_name.replace("_", " ")
        self.destination_fade_alpha = 255
        # Play travel sound
        try:
            self.travel_sound.play()
        except:
            pass  # Sound file might not load, continue anyway

    def update_transition(self):
        """Update transition animation"""
        if self.transition_phase == "expand":
            self.transition_radius += self.config.TRANSITION_SPEED
            if self.transition_radius >= self.transition_max:
                self.load_level(self.level_files[self.transition_target])
                self.current_level_index = self.transition_target
                self.active_menu = None
                self.travel_menu = None
                self.previous_menu = None
                self.transition_phase = "collapse"
        
        elif self.transition_phase == "collapse":
            self.transition_radius -= self.config.TRANSITION_SPEED
            if self.transition_radius <= 0:
                self.transition_phase = "show_destination"
                self.destination_fade_alpha = 255
        
        elif self.transition_phase == "show_destination":
            # Fade out destination text
            self.destination_fade_alpha -= 300 * (1.0 / self.config.FPS)  # Fade over ~1.7 seconds
            if self.destination_fade_alpha <= 0:
                self.transitioning = False
                self.transition_phase = None
                self.destination_fade_alpha = 0

    def update_bed_fade(self, dt):
        """Update bed fade animation - delegates to Bed class"""
        for obj in self.level_data.get("interactables", []):
            if hasattr(obj, 'update_fade'):
                obj.update_fade(dt, self.player, self)
                
                # Check if tent spawning should occur after rest
                if hasattr(obj, 'bed_interaction_active') and not obj.fade_active:
                    for tent in self.level_data.get("interactables", []):
                        if hasattr(tent, "spawn_bandits_after_rest") and tent.spawn_bandits_after_rest:
                            # Spawn 3 bandits near the tent
                            from Assets.Characters import SmallBandit
                            bandits = [SmallBandit(tent.x + 40 * i, tent.y - 100) for i in range(3)]
                            self.level_data.get("enemies", []).extend(bandits)
                            tent.spawn_bandits_after_rest = False

    # ==================== INPUT HANDLING ====================
    def handle_input(self):
        """Listen for keyboard/quit events and respond"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Player closed the window
                pygame.quit()
                sys.exit()
            
            # If a menu is open, send events to the menu
            if self.active_menu:
                self.handle_menu_input(event)
                continue
            
            # Handle spell casting input (Shift + typing)
            if self.spell_system.handle_event(event, self.player):
                continue  # Spell system consumed the event
            
            # Otherwise handle normal game input
            if not self.go_back_active:
                if event.type == pygame.KEYDOWN:
                    self._handle_keydown(event)
                elif event.type == pygame.KEYUP:
                    self._handle_keyup(event)

    def _handle_keydown(self, event):
        """Handle when a key is pressed down"""
        kb = self.settings.keybinds  # Shorthand for keybinds
        
        # Check which key was pressed and respond
        if event.key == kb["Pause"]:
            # Open pause menu
            self.pause_player_physics()
            self.active_menu = "pause"
        
        elif event.key == kb["MoveLeft"]:
            # Start moving left
            if self.player.hit_stun_frames <= 0:
                self.player.moving_left = True
        
        elif event.key == kb["MoveRight"]:
            # Start moving right
            if self.player.hit_stun_frames <= 0:
                self.player.moving_right = True
        
        elif event.key == kb["Jump"] and self.player.on_ground:
            # Teleport upward (only if on ground)
            if self.player.on_ground and self.jump_cooldown <= 0:
                self.player.teleport_jump(self.get_collision_rects(), self.config.PLAYER_TELEPORT_DISTANCE)
                self.jump_cooldown = self.jump_cooldown_max
        
        elif event.key == kb["Interact"]:
            # Try to interact with nearby objects
            self.handle_interactions()
        
        elif event.key == kb.get("Block", 102):  # F key
            # Start blocking
            self.player.start_block()
        
        elif event.key == kb.get("Attack", 32):  # SPACE key
            # Process rhythm-based attack
            current_time = time.time()
            
            # Determine direction based on keys held
            direction = "neutral"
            if self.player.moving_left or self.player.moving_right:
                direction = "forward"
            elif pygame.key.get_pressed()[self.settings.keybinds.get("MoveDown", 115)]:  # S key
                direction = "down"
            
            # Process attack through rhythm system
            attack = self.rhythm_system.process_attack_input(direction, current_time)
            
            if attack:
                # Apply attack to player (with rhythm multiplier)
                self.player.perform_attack(
                    attack.attack_type,
                    self.rhythm_system.get_total_multiplier()
                )

    def _handle_keyup(self, event):
        """Handle when a key is released"""
        kb = self.settings.keybinds
        
        # Stop moving when left/right keys are released
        if event.key == kb["MoveLeft"]:
            self.player.moving_left = False
        elif event.key == kb["MoveRight"]:
            self.player.moving_right = False
        elif event.key == kb.get("Block", 102):  # F key
            self.player.is_blocking = False

    # SLOPE PHYSICS
    def handle_slope_physics(self):
        """Handle special physics for sloped polygons (tents and rocks)"""
        for tent in self.level_data.get("tents", []):
            if tent.handle_tent_collision(self.player):
                return
        
        for rock in self.level_data.get("rocks", []):
            if rock.handle_rock_collision(self.player):
                return

    # GAME LOOP 
    def update(self):
        """Update game state - runs every frame (60 times per second)"""
        # dt = "delta time" = time since last frame in seconds
        dt = self.clock.get_time() / 1000.0
        
        # Increment frame counter
        self.frame_counter += 1
        
        if self.transitioning:
            # Keep audio system running for crossfades and song switches
            self.audio_system.update()
            # Continue updating rhythm system during transitions for song consistency
            self.rhythm_system.update(dt, time.time())
            self.update_transition()
            return
        
        # Check if any bed is active
        bed_active = any(hasattr(obj, 'fade_active') and obj.fade_active 
                        for obj in self.level_data.get("interactables", []))
        if bed_active:
            # Keep audio system running during fades
            self.audio_system.update()
            self.update_bed_fade(dt)
            return
        
        if self.go_back_active:
            self.update_go_back_timer(dt)
            if self.go_back_fade_phase:
                # Keep audio system running during go-back fade
                self.audio_system.update()
                return
        
        if self.active_menu:
            # Still update audio for scheduled song changes
            self.audio_system.update()
            return  # Pause game while menu is open
        
        # Update jump cooldown
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1
        
        # ========== Update Game Objects ==========
        # Update coins (collect animations, etc)
        for coin in self.level_data.get("coins", []):
            if hasattr(coin, "update"):
                coin.update(dt)
        
        # Update drops (physics, fading, removal)
        self._update_drops(dt)
        
        # Update audio system
        self.audio_system.update()
        
        # Update rhythm battle system
        self.rhythm_system.update(dt, time.time())
        
        # Update spell system
        enemies = self.level_data.get("enemies", [])
        screen_rect = self.screen.get_rect()
        self.spell_system.update(dt, self.player, enemies, screen_rect)
        
        # Update player attack state (cooldown, stun decay)
        if self.audio_system.current_song:
            bpm = self.audio_system.current_song.bpm
        else:
            bpm = 120  # Default fallback

        # Protect against missing method in case of stale class definitions
        if hasattr(self.player, "update_attack"):
            self.player.update_attack(self.audio_system.current_beat, bpm, dt)
        
        # ========== Update Enemies ==========
        rects = self.get_collision_rects()
        
        # Track health before enemy updates for sneak attack detection
        health_before_enemies = self.player.stats.get('Current_Health', 0)
        
        for enemy in self.level_data.get("enemies", []):
            if hasattr(enemy, "update_ai"):
                # Update enemy AI (behavior, movement, attacks)
                enemy.update_ai(self.player, rects, self.config.GRAVITY, self.config.MAX_FALL_SPEED, dt, 0, self.frame_counter)
        
        # Check if player took damage during enemy updates - trigger sneak counter
        health_after_enemies = self.player.stats.get('Current_Health', 0)
        if health_after_enemies < health_before_enemies and self.spell_system.sneak_active:
            # Find the attacking enemy (closest one in attack range)
            for enemy in self.level_data.get("enemies", []):
                if enemy.is_alive() and abs(enemy.rect.centerx - self.player.rect.centerx) < 80:
                    # Sneak counter activates!
                    damage_taken = health_before_enemies - health_after_enemies
                    self.player.stats['Current_Health'] = health_before_enemies  # Restore health
                    if self.spell_system.check_sneak_counter(self.player, enemy):
                        break
        
        # ========== Check Player Attacks on Enemies ==========
        if hasattr(self.player, 'current_attack') and self.player.current_attack and self.player.current_attack.get('active'):
            attack_type = self.player.current_attack.get('type', 'neutral')
            hitbox = self._get_attack_hitbox(attack_type)
            
            # Calculate attack rect with player facing direction
            if self.player.facing_right:
                attack_x = self.player.rect.centerx + hitbox['offset_x']
            else:
                attack_x = self.player.rect.centerx - hitbox['offset_x'] - hitbox['width']
            
            attack_rect = pygame.Rect(
                attack_x,
                self.player.rect.centery + hitbox['offset_y'],
                hitbox['width'],
                hitbox['height']
            )
            
            for enemy in self.level_data.get("enemies", []):
                if attack_rect.colliderect(enemy.rect):
                    # Hit the enemy!
                    enemy.take_damage(self.player.current_attack['damage'])
                    enemy.apply_knockback(
                        self.player.current_attack['knockback_x'] * (1 if self.player.facing_right else -1),
                        self.player.current_attack['knockback_y'],
                        stun_duration=0.3
                    )
                    
                    # Screen shake on finisher combo (5 hits = max combo)
                    if self.rhythm_system.combo_count >= 5:
                        self.trigger_screen_shake(intensity=0.8, duration=0.15)
            
            # Deactivate attack after one frame
            self.player.current_attack['active'] = False
        
        # Update screen shake effect
        if self.shake_duration > 0:
            self.shake_duration -= dt
            if self.shake_duration <= 0:
                self.shake_intensity = 0.0
                self.shake_offset_x = 0
                self.shake_offset_y = 0
            else:
                # Apply screen shake with random offset
                shake_amount = self.shake_intensity * 5  # Max 5 pixels shake
                self.shake_offset_x = random.randint(int(-shake_amount), int(shake_amount))
                self.shake_offset_y = random.randint(int(-shake_amount), int(shake_amount))
        
        # Check if player took damage and trigger screen shake
        if self.player.stats['Current_Health'] < self.last_player_health:
            self.trigger_screen_shake(intensity=0.6, duration=0.2)
        self.last_player_health = self.player.stats['Current_Health']
        enemies_to_remove = []
        for enemy in self.level_data.get("enemies", []):
            if not enemy.is_alive():
                enemies_to_remove.append(enemy)
                # Spawn loot drops
                self._spawn_enemy_drops(enemy)
        for enemy in enemies_to_remove:
            self.level_data["enemies"].remove(enemy)
        
        # Generate new map sections for infinite levels
        if self.level_data.get("infinite", False):
            seg = self.player.rect.centerx // self.config.SEGMENT_WIDTH
            for i in range(seg - 2, seg + 3):
                if i not in self.level_data["segments"]:
                    self.level_data["generate_segment"](i)
        
        # ========== Update Player Physics ==========
        rects = self.get_collision_rects()
        
        # Handle stun and knockback
        self.player.update_stun_and_knockback(dt, rects)
        
        # Update player position (only if not stunned)
        if not self.player.is_stunned:
            # Check if we just came out of stun - restore held movement keys
            if hasattr(self.player, '_was_stunned_last_frame') and self.player._was_stunned_last_frame:
                # Check current key states and restore movement if keys are held
                keys = pygame.key.get_pressed()
                kb = self.settings.keybinds
                if keys[kb["MoveLeft"]] and self.player.hit_stun_frames <= 0:
                    self.player.moving_left = True
                if keys[kb["MoveRight"]] and self.player.hit_stun_frames <= 0:
                    self.player.moving_right = True
            
            # Apply gravity
            self.player.apply_gravity(self.config.GRAVITY, self.config.MAX_FALL_SPEED, rects)
            
            # Handle slopes (tents, rocks with special physics)
            self.handle_slope_physics()
            
            # Move player left/right
            self.player.move(rects)
        else:
            # Still fall while stunned (can't prevent gravity)
            self.player.apply_gravity(self.config.GRAVITY, self.config.MAX_FALL_SPEED, rects)
        
        # ========== Update Camera ==========
        # Position camera to follow player
        self.update_camera()

    def _get_attack_hitbox(self, attack_type):
        """Get attack hitbox dimensions based on attack type - from AttackConfig
        
        Returns:
            dict with 'width', 'height', 'offset_x', 'offset_y' for the attack
        """
        return AttackConfig.get_hitbox(attack_type)
    
    # ==================== RENDERING ====================
    def draw(self):
        """Draw everything on screen - runs every frame"""
        # Clear screen to sky color
        self.screen.fill(self.config.COLOR_SKY)
        
        # Draw city background image if in City level
        self._draw_city_background()

        # City-specific transparency overrides (show background art)
        is_city = self.level_data.get('level_id') == 'city' if self.level_data else False
        orig_ground_alpha = self.config.ALPHA_GROUND
        orig_wall_alpha = self.config.ALPHA_WALL
        if is_city:
            self.config.ALPHA_GROUND = 0
            self.config.ALPHA_WALL = 0
        
        # ========== Draw all game objects ==========
        # Draw in order: ground, platforms, objects, coins, drops, enemies, player
        # (Order matters: things drawn first appear behind things drawn last)
        self._draw_ground()
        self._draw_platforms()
        self._draw_natural_objects()
        self._draw_interactables()
        self._draw_coins()
        self._draw_drops()
        
        self._draw_enemies()
        self._draw_player()
        
        # Draw UI elements
        self._draw_interaction_icons()
        self._draw_go_back_timer()
        self._draw_health_mana_bars()  # Health and mana bars
        self._draw_rhythm_feedback()  # Rhythm battle feedback
        self._draw_controls_overlay()
        self._draw_menus()
        self._draw_transition()
        self._draw_go_back_fade()
        self._draw_bed_fade()

        # Restore alphas
        if is_city:
            self.config.ALPHA_GROUND = orig_ground_alpha
            self.config.ALPHA_WALL = orig_wall_alpha
        
        # Scale the internal screen to display surface with smooth scaling for better visuals
        scaled = pygame.transform.smoothscale(self.screen, (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        self.display_surface.blit(scaled, (0, 0))
        
        pygame.display.flip()

    def _draw_city_background(self):
        """Draw the city background image scaled to screen when in the City level"""
        try:
            if self.level_data and self.level_data.get('level_id') == 'city':
                bg = self.images.get('city_bg')
                if bg:
                    scaled_bg = pygame.transform.smoothscale(bg, (self.screen.get_width(), self.screen.get_height()))
                    offset_x = int(self.camera_x * 0.1)
                    w = scaled_bg.get_width()
                    # Tile across the viewport to avoid gaps when scrolling
                    for dx in (-w, 0, w):
                        self.screen.blit(scaled_bg, ((-offset_x % w) + dx, 0))
        except Exception:
            # Fail silently if background isn't available
            pass

    def _draw_with_alpha(self, surface, color, rect, alpha):
        """Helper to draw rectangles with alpha transparency"""
        if alpha < 255:
            temp_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            temp_surface.fill((*color, alpha))
            surface.blit(temp_surface, rect.topleft)
        else:
            pygame.draw.rect(surface, color, rect)

    def _draw_ground(self):
        """Draw ground rectangles"""
        for g in self.level_data.get("ground", []):
            screen_rect = g.move(-self.camera_x, -self.camera_y)
            self._draw_with_alpha(self.screen, self.config.COLOR_GROUND, screen_rect, self.config.ALPHA_GROUND)

    def _draw_platforms(self):
        """Draw platform rectangles"""
        for p in self.level_data.get("platforms", []):
            screen_rect = p.move(-self.camera_x, -self.camera_y)
            self._draw_with_alpha(self.screen, self.config.COLOR_PLATFORM, screen_rect, self.config.ALPHA_PLATFORM)

    def _draw_natural_objects(self):
        """Draw natural objects (rocks, tents, slopes)"""
        for obj in self.level_data.get("natural_objects", []):
            if hasattr(obj, "draw"):
                obj.draw(self.screen, self.camera_x, self.camera_y, self.config)

    def _draw_interactables(self):
        """Draw interactable objects"""
        for obj in self.level_data.get("interactables", []):
            if hasattr(obj, "draw"):
                obj.draw(self.screen, self.camera_x, self.camera_y, self.config)
            else:
                screen_rect = obj.rect.move(-self.camera_x, -self.camera_y)
                self._draw_with_alpha(self.screen, self.config.COLOR_INTERACTABLE, screen_rect, self.config.ALPHA_INTERACTABLE)

    def _draw_coins(self):
        """Draw coins"""
        for coin in self.level_data.get("coins", []):
            if hasattr(coin, "draw"):
                coin.draw(self.screen, self.camera_x, self.camera_y)

    def _spawn_enemy_drops(self, enemy, count=5):
        """Spawn coins that fan out on enemy death"""
        from Assets.Interactables import Coin
        
        # Calculate experience based on enemy level
        exp_table = {
            1: 1, 2: 2, 3: 4, 4: 6, 5: 10,
            6: 13, 7: 16, 8: 20, 9: 24, 10: 30
        }
        enemy_level = enemy.stats.get('Level', 1)
        exp_reward = exp_table.get(enemy_level, 5)
        
        # Give experience to player
        self.player.gain_experience(exp_reward)
        print(f"Enemy level {enemy_level} defeated! Gained {exp_reward} experience.")
        
        # Create coins that spray outward in a fan pattern
        for i in range(count):
            # Spread coins in a fan (mostly upward and sideways)
            angle = random.uniform(-math.pi * 0.7, -math.pi * 0.3)  # Spray upward-ish
            # Vary speed for visual variety
            speed = random.uniform(300, 500)
            
            # Create a coin at the enemy center
            coin = Coin(
                x=int(enemy.rect.centerx),
                y=int(enemy.rect.centery),
                gold_value=random.randint(1, 3)  # Each coin worth 1-3 gold
            )
            
            # Add initial velocity (spraying outward)
            coin.vx = math.cos(angle) * speed
            coin.vy = math.sin(angle) * speed
            coin.life = 3.0  # Lives for 3 seconds before disappearing
            
            # Add to drops for physics simulation
            self.drops.append(coin)

    def _update_drops(self, dt):
        """Update all drops - apply physics and remove expired ones"""
        if not self.drops:
            return  # No drops to update
        
        from Assets.Interactables import Coin
        
        # Physics constants
        gravity = 800  # Strong gravity for satisfying arc
        damping = 0.92 ** (dt * 60)  # Slight air resistance
        
        # Keep only drops that are still alive
        alive = []
        for drop in self.drops:
            # Handle Coin objects
            if isinstance(drop, Coin):
                # Handle collection animation (float to player)
                if drop.is_collecting:
                    # Move towards player
                    dx = drop.collect_target_x - drop.rect.centerx
                    dy = drop.collect_target_y - drop.rect.centery
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance < 10:
                        # Coin reached player - collect it
                        self.player.gold += drop.gold_value
                        print(f"Picked up {drop.gold_value} gold! Total: {self.player.gold}")
                        # Don't add to alive list (removes coin)
                    else:
                        # Move towards player
                        move_amount = drop.collect_speed * dt
                        if distance > 0:
                            drop.rect.centerx += (dx / distance) * move_amount
                            drop.rect.centery += (dy / distance) * move_amount
                        alive.append(drop)
                else:
                    # Normal physics
                    drop.vy += gravity * dt  # Gravity pulls down
                    drop.vx *= damping  # Slow down horizontal movement
                    drop.vy *= damping  # Slow down vertical movement
                    
                    # Move the coin
                    drop.rect.x += drop.vx * dt
                    drop.rect.y += drop.vy * dt
                    
                    # Update the original_y for bobbing animation (keeps it grounded while moving)
                    drop.original_y = drop.rect.y
                    
                    # Count down lifetime
                    drop.life -= dt
                    
                    # Check coin pickup collision with player
                    if self.player.rect.colliderect(drop.rect):
                        # Start collection animation
                        drop.is_collecting = True
                        drop.collect_target_x = self.player.rect.centerx
                        drop.collect_target_y = self.player.rect.centery
                        drop.vx = 0  # Stop physics
                        drop.vy = 0
                        alive.append(drop)
                    elif drop.life > 0:
                        # Keep coin if not picked up and still alive
                        alive.append(drop)
            else:
                # Legacy dict-based drops (for backwards compatibility)
                drop["vy"] += gravity * dt  # Gravity pulls down
                drop["vx"] *= damping  # Slow down horizontal movement
                drop["vy"] *= damping  # Slow down vertical movement
                drop["x"] += drop["vx"] * dt
                drop["y"] += drop["vy"] * dt
                drop["life"] -= dt
                if drop["life"] > 0:
                    alive.append(drop)
        
        # Replace drop list with only alive drops
        self.drops = alive

    def _draw_drops(self):
        """Draw all drop circles on screen"""
        from Assets.Interactables import Coin
        for drop in self.drops:
            # If it's a Coin object, use its draw method
            if isinstance(drop, Coin):
                drop.draw(self.screen, self.camera_x, self.camera_y)
            else:
                # Legacy dict-based drops
                # Convert world position to screen position (accounting for camera)
                screen_x = int(drop["x"] - self.camera_x)
                screen_y = int(drop["y"] - self.camera_y)
                screen_pos = (screen_x, screen_y)
                
                # Pulse effect based on lifetime
                pulse = abs(math.sin(drop["life"] * 5)) * 0.3 + 0.7
                radius = int(drop["radius"] * pulse)
                
                # Draw the drop as a filled circle with glow
                pygame.draw.circle(self.screen, drop["color"], screen_pos, radius)
                # Outer glow
                glow_color = (255, 255, 150, 128)
                pygame.draw.circle(self.screen, drop["color"], screen_pos, radius + 2, 1)

    def _draw_enemies(self):
        """Draw enemies"""
        for enemy in self.level_data.get("enemies", []):
            if hasattr(enemy, "draw"):
                enemy.draw(self.screen, self.camera_x, self.camera_y, enemy.color, self.config)

    def _draw_player(self):
        """Draw player character"""
        # Don't draw player during jump animation (0.3s)
        if False:
            return
        
        screen_rect = self.player.rect.move(-self.camera_x, -self.camera_y)
        
        # Flash when hit
        if self.player.hit_stun_frames > 0:
            if self.player.hit_flash_timer % 4 < 2:  # Flash every 4 frames
                alpha = 128  # Semi-transparent when hit
            else:
                alpha = self.config.ALPHA_PLAYER
        else:
            alpha = self.config.ALPHA_PLAYER
        
        # Draw player with normal rendering
        self._draw_with_alpha(self.screen, self.config.COLOR_PLAYER, screen_rect, alpha)
        
        # Draw blue shield when blocking
        if self.player.is_blocking:
            shield_surf = pygame.Surface((screen_rect.width + 20, screen_rect.height + 20), pygame.SRCALPHA)
            shield_color = (100, 150, 255, 120)  # Blue transparent
            pygame.draw.rect(shield_surf, shield_color, shield_surf.get_rect(), border_radius=8)
            self.screen.blit(shield_surf, (screen_rect.x - 10, screen_rect.y - 10))
        
        # Draw attack slash effect
        if hasattr(self.player, 'current_attack') and self.player.current_attack and self.player.current_attack.get('active'):
            attack_type = self.player.current_attack.get('type', 'neutral')
            hitbox = self._get_attack_hitbox(attack_type)
            
            # Calculate screen position
            if self.player.facing_right:
                attack_x = self.player.rect.centerx + hitbox['offset_x']
            else:
                attack_x = self.player.rect.centerx - hitbox['offset_x'] - hitbox['width']
            
            attack_rect = pygame.Rect(
                attack_x - self.camera_x,
                self.player.rect.centery + hitbox['offset_y'] - self.camera_y,
                hitbox['width'],
                hitbox['height']
            )
            
            # Draw slash effect based on attack type
            if attack_type == "down":
                color = (255, 100, 100, 150)  # Red for down attack
            elif attack_type == "forward":
                color = (255, 215, 0, 150)  # Gold for forward attack
            else:
                color = (200, 200, 255, 150)  # Blue for neutral attack
            
            slash_surf = pygame.Surface((attack_rect.width, attack_rect.height), pygame.SRCALPHA)
            pygame.draw.ellipse(slash_surf, color, slash_surf.get_rect())
            self.screen.blit(slash_surf, (attack_rect.x, attack_rect.y))

    def _draw_interaction_icons(self):
        """Draw interaction icons above nearby objects"""
        nearby = self.get_nearby_interactables()
        for obj in nearby:
            icon_x = obj.rect.centerx - self.camera_x - self.interact_icon.get_width() // 2
            icon_y = self.player.rect.top - self.camera_y - self.config.ICON_OFFSET_Y
            self.screen.blit(self.interact_icon, (icon_x, icon_y))

    def _draw_go_back_timer(self):
        """Draw the countdown timer above player's head"""
        if self.go_back_active and not self.go_back_fade_phase:
            timer_text = f"{int(self.go_back_timer) + 1}"
            text_surface = self.timer_font.render(timer_text, True, self.config.COLOR_TIMER_TEXT)
            
            player_screen_x = self.player.rect.centerx - self.camera_x
            player_screen_y = self.player.rect.top - self.camera_y - 90
            
            bg_rect = pygame.Rect(
                player_screen_x - text_surface.get_width() // 2 - 10,
                player_screen_y - 10,
                text_surface.get_width() + 20,
                text_surface.get_height() + 20
            )
            pygame.draw.rect(self.screen, self.config.COLOR_TIMER_BG, bg_rect)
            pygame.draw.rect(self.screen, self.config.COLOR_TIMER_TEXT, bg_rect, 2)
            
            self.screen.blit(text_surface, (player_screen_x - text_surface.get_width() // 2, player_screen_y))
            
            cancel_text = self.font.render("Move to cancel", True, (200, 200, 200))
            cancel_y = player_screen_y + text_surface.get_height() + 5
            self.screen.blit(cancel_text, (player_screen_x - cancel_text.get_width() // 2, cancel_y))

    def _draw_rhythm_combat(self):
        """Legacy method - no longer used"""
        pass
    
    def _draw_rhythm_feedback(self):
        """Draw rhythm battle system feedback"""
        if not self.active_menu:  # Only show during gameplay
            # Check if any enemies are nearby (within 400 pixels)
            enemies_nearby = False
            for enemy in self.level_data.get("enemies", []):
                distance = abs(enemy.rect.centerx - self.player.rect.centerx)
                if distance < 400:
                    enemies_nearby = True
                    break
            
            # Draw feedback text above player (PERFECT/GOOD/MISS)
            self.rhythm_system.draw_feedback(
                self.screen,
                self.player.rect.centerx,
                self.player.rect.centery,
                self.camera_x,
                self.camera_y,
                self.font
            )
            
            # Draw combo counter (top right)
            self.rhythm_system.draw_combo_counter(self.screen, self.font)

    def _draw_controls_overlay(self):
        """Draw a small controls hint for clarity."""
        lines = [
            "Move: A / D",
            "Jump: W",
            "Attack: Space",
            "Block: F",
            "Interact: E",
            "Pause / Menu: Esc",
        ]
        padding = 8
        line_height = 20
        width = 180
        height = padding * 2 + line_height * len(lines)
        panel = pygame.Surface((width, height), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 140))
        for i, text in enumerate(lines):
            rendered = self.hint_font.render(text, True, (230, 230, 230))
            panel.blit(rendered, (padding, padding + i * line_height))
        self.screen.blit(panel, (10, 10))
            
        # Draw beat timing bar (bottom center) - only when enemies nearby
        self.rhythm_system.draw_beat_indicators(self.screen, self.font)
        
        # Draw spell casting UI and effects
        self.spell_system.draw(self.screen, self.camera_x, self.camera_y)
    
    def _draw_health_mana_bars(self):
        """Draw health and mana bars in top-left corner"""
        # Bar dimensions
        bar_width = 200
        bar_height = 20
        bar_x = 10
        health_y = 10
        mana_y = 35
        
        # ===== HEALTH BAR =====
        # Calculate how full the health bar is (0.0 to 1.0)
        health_ratio = self.player.stats['Current_Health'] / self.player.stats['Max_Health']
        health_ratio = max(0, min(1, health_ratio))  # Keep between 0 and 1
        
        # Draw background (dark red)
        shadow_offset = 2
        pygame.draw.rect(self.screen, (0, 0, 0), 
                        (bar_x + shadow_offset, health_y + shadow_offset, bar_width, bar_height), 
                        border_radius=5)
        pygame.draw.rect(self.screen, (60, 10, 10), (bar_x, health_y, bar_width, bar_height), border_radius=5)
        
        # Draw foreground (bright red) with gradient
        if health_ratio > 0:
            filled_width = int(bar_width * health_ratio)
            for i in range(filled_width):
                progress = i / bar_width
                r = int(255 - (progress * 40))
                g = int(30 * progress)
                color = (r, g, 0)
                pygame.draw.rect(self.screen, color, (bar_x + i, health_y + 2, 1, bar_height - 4))
        
        # Draw glossy highlight
        highlight = pygame.Surface((bar_width - 4, bar_height // 3), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 40))
        self.screen.blit(highlight, (bar_x + 2, health_y + 2))
        
        # Draw white border
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, health_y, bar_width, bar_height), 2, border_radius=5)
        
        # Draw health text
        health_text = f"HP: {int(self.player.stats['Current_Health'])}/{int(self.player.stats['Max_Health'])}"
        self.draw_text_with_shadow(health_text, self.font, (255, 255, 255), bar_x + 8, health_y + 4)
        
        # ===== MANA BAR =====
        # Calculate how full the mana bar is (0.0 to 1.0)
        mana_ratio = self.player.stats['Current_Mana'] / self.player.stats['Max_Mana']
        mana_ratio = max(0, min(1, mana_ratio))  # Keep between 0 and 1
        
        # Draw background (dark blue)
        shadow_offset = 2
        pygame.draw.rect(self.screen, (0, 0, 0), 
                        (bar_x + shadow_offset, mana_y + shadow_offset, bar_width, bar_height),
                        border_radius=5)
        pygame.draw.rect(self.screen, (10, 10, 60), (bar_x, mana_y, bar_width, bar_height), border_radius=5)
        
        # Draw foreground (bright blue) with gradient
        if mana_ratio > 0:
            filled_width = int(bar_width * mana_ratio)
            for i in range(filled_width):
                progress = i / bar_width
                b = int(255 - (progress * 40))
                g = int(120 + (progress * 40))
                color = (0, g, b)
                pygame.draw.rect(self.screen, color, (bar_x + i, mana_y + 2, 1, bar_height - 4))
        
        # Draw glossy highlight
        highlight = pygame.Surface((bar_width - 4, bar_height // 3), pygame.SRCALPHA)
        highlight.fill((255, 255, 255, 40))
        self.screen.blit(highlight, (bar_x + 2, mana_y + 2))
        
        # Draw white border
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, mana_y, bar_width, bar_height), 2, border_radius=5)
        
        # Draw mana text
        mana_text = f"MP: {int(self.player.stats['Current_Mana'])}/{int(self.player.stats['Max_Mana'])}"
        self.draw_text_with_shadow(mana_text, self.font, (255, 255, 255), bar_x + 8, mana_y + 4)
        
        # ===== EXPERIENCE BAR =====
        exp_bar_width = 200
        exp_bar_height = 15
        exp_y = 60
        
        # Draw experience text
        exp_text = f"Exp: {self.player.experience} / {self.player.exp_for_next_level}"
        exp_text_surface = self.font.render(exp_text, True, (200, 200, 200))
        self.screen.blit(exp_text_surface, (bar_x, exp_y))
        
        # Calculate and draw exp bar
        exp_ratio = self.player.experience / max(1, self.player.exp_for_next_level)
        exp_ratio = max(0, min(1, exp_ratio))
        
        # Background (dark yellow)
        pygame.draw.rect(self.screen, (100, 100, 0), (bar_x, exp_y + 20, exp_bar_width, exp_bar_height))
        # Foreground (bright yellow)
        pygame.draw.rect(self.screen, (255, 255, 0), (bar_x, exp_y + 20, int(exp_bar_width * exp_ratio), exp_bar_height))
        # Border
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, exp_y + 20, exp_bar_width, exp_bar_height), 1)

    def _draw_go_back_fade(self):
        """Draw fade effect for go back"""
        if self.go_back_fade_phase:
            fade_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.go_back_fade_alpha)
            self.screen.blit(fade_surface, (0, 0))

    def _draw_bed_fade(self):
        """Draw bed fade effect and text - delegates to Bed class"""
        for obj in self.level_data.get("interactables", []):
            if hasattr(obj, 'draw_fade'):
                obj.draw_fade(self.screen)

    def _draw_menus(self):
        """Draw active menu"""
        if self.active_menu:
            menu = self.travel_menu if self.active_menu == "travel" else self.menus[self.active_menu]
            menu.draw(self.screen)

    def _draw_transition(self):
        """Draw transition effect"""
        if self.transitioning:
            self.transition_surface.fill(self.config.COLOR_COLORKEY)
            # Draw circle at the center of the screen (player stays centered due to camera)
            center_x = self.transition_surface.get_width() // 2
            center_y = self.transition_surface.get_height() // 2
            
            # During expand and collapse phases, draw black circle with "Travelling to..." text
            if self.transition_phase in ["expand", "collapse"]:
                pygame.draw.circle(self.transition_surface, (0, 0, 0),
                                 (center_x, center_y), int(self.transition_radius))
                
                # Show "Travelling to..." text during expand phase
                if self.transition_phase == "expand":
                    travelling_text = self.font.render("Travelling to...", True, (255, 255, 255))
                    text_x = center_x - travelling_text.get_width() // 2
                    text_y = center_y - travelling_text.get_height() // 2
                    self.transition_surface.blit(travelling_text, (text_x, text_y))
            
            # During show_destination phase, fade out the destination name
            elif self.transition_phase == "show_destination":
                # Draw destination name with fade
                # Use Cavalhatriz font for destination display if available
                dest_font = pygame.font.Font(self.font_path if os.path.exists(self.font_path) else None, 96)
                dest_text = dest_font.render(self.transition_destination_name, True, (255, 255, 255))
                dest_text.set_alpha(int(self.destination_fade_alpha))
                text_x = center_x - dest_text.get_width() // 2
                text_y = center_y - dest_text.get_height() // 2
                self.transition_surface.blit(dest_text, (text_x, text_y))
            
            self.screen.blit(self.transition_surface, (0, 0))

    def run(self):
        """Main game loop"""
        # Draw initial frame to prevent black screen
        self.draw()
        
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(self.config.FPS)


Game().run()