# ============================================================================
# EMINENCE IN SHADOW - RESTART
# ============================================================================
# A rhythm-based 2D action game where you attack on musical beats to deal
# extra damage and unlock powerful combos.
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
import importlib.util
from Assets.Settings import Settings
from Assets.Characters import MainCharacter
from Assets.Menus import StartMenu, PauseMenu, MerchantMenu, TravelMenu, SettingsMenu, StatusMenu
from Assets.AudioConfig import AudioSystem
from Assets.ComboConfig import COMBO_CONFIG

# ==================== CONFIGURATION ====================
class Config:
    """Central configuration for the game"""
    # Display - Original dimensions (2x zoom handled differently)
    SCREEN_WIDTH = 1080
    SCREEN_HEIGHT = 920
    FPS = 60
    WINDOW_TITLE = "Eminence in Shadow"
    
    # Visual Settings
    ZOOM_SCALE = 1.5
    AVAILABLE_ZOOM_LEVELS = [1.0, 1.25, 1.5, 1.75, 2.0]  # Zoom options in settings
    
    # Camera
    LOOK_AHEAD_MAX = 90
    LOOK_AHEAD_ACCEL = 6
    LOOK_AHEAD_RETURN = 8
    CAMERA_SMOOTHING = 0.12
    
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
    INTERACTION_BOX_INFLATE = (40, 20)
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
    
    # Attack Keybind (if not in settings file)
    DEFAULT_ATTACK_KEY = pygame.K_SPACE

# GAME CLASS
class Game:
    def __init__(self):
        pygame.init()
        self.config = Config()
        
        # Display setup - create a scaled surface for zoom
        self.display_surface = pygame.display.set_mode((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        pygame.display.set_caption(self.config.WINDOW_TITLE)
        
        # Internal screen based on zoom scale (smaller = more zoomed in)
        internal_width = int(self.config.SCREEN_WIDTH / self.config.ZOOM_SCALE)
        internal_height = int(self.config.SCREEN_HEIGHT / self.config.ZOOM_SCALE)
        self.screen = pygame.Surface((internal_width, internal_height))
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 32)
        self.timer_font = pygame.font.SysFont(None, 48)

        # Player
        self.player = MainCharacter()
        self.saved_y_momentum = 0  # Store y_momentum when menu opens

        # Camera - adjusted for 2x zoom
        self.camera_x = 0
        self.camera_y = 0
        self.look_offset_x = 0

        # Level management
        self.level_files = self.config.LEVEL_PATHS
        self.current_level_index = 0
        self.level_data = {}
        
        # Drops (flying loot on enemy death) - Must be initialized before load_level!
        self.drops = []
        
        # Audio system with metronome - Must be initialized before load_level!
        self.audio_system = AudioSystem()
        # Start with menu theme (will change when level loads)
        self.audio_system.play_song("menu_theme")
        
        # Load the starting level
        self.load_level(self.level_files[self.current_level_index])

        # Settings and menus
        self.settings = Settings(self.config.SETTINGS_PATH)
        # Ensure attack key exists in keybinds
        if "Attack" not in self.settings.keybinds:
            self.settings.keybinds["Attack"] = self.config.DEFAULT_ATTACK_KEY
            self.settings.save()
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
        
        # Go Back timer system
        self.go_back_active = False
        self.go_back_timer = 0.0
        self.go_back_fade_phase = None  # None, "fade_out", "fade_in"
        self.go_back_fade_alpha = 0
        self.go_back_start_pos = (0, 0)  # Store player position when timer starts
        
        # Bed fade system
        self.bed_fade_active = False
        self.bed_fade_phase = None  # None, "fade_out", "text", "fade_in"
        self.bed_fade_alpha = 0
        self.bed_fade_text_timer = 0
        
        # Load images if enabled
        self.images = {}
        if self.config.USE_IMAGES:
            self._load_images()

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
        except:
            print("Warning: Some images could not be loaded, falling back to rectangles")
            self.config.USE_IMAGES = False
    
    def apply_zoom(self, zoom_level):
        """Apply zoom level to screen"""
        self.config.ZOOM_SCALE = zoom_level
        internal_width = int(self.config.SCREEN_WIDTH / zoom_level)
        internal_height = int(self.config.SCREEN_HEIGHT / zoom_level)
        self.screen = pygame.Surface((internal_width, internal_height))
        # Reinitialize transition surface
        self._initialize_transition()

    def _initialize_menus(self):
        """Initialize all menu objects"""
        self.menus = {
            "start": StartMenu(self.font),
            "pause": PauseMenu(self.font, self.screen.get_width()),
            "merchant": MerchantMenu(self.font),
            "settings": SettingsMenu(self.font, self.settings, self.config),
            "status": StatusMenu(self.font, self.player)
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
        # Use internal screen size for transition (calculated dynamically)
        internal_width = int(self.config.SCREEN_WIDTH / self.config.ZOOM_SCALE)
        internal_height = int(self.config.SCREEN_HEIGHT / self.config.ZOOM_SCALE)
        self.transition_max = int((internal_width ** 2 + internal_height ** 2) ** 0.5)
        self.transition_surface = pygame.Surface((internal_width, internal_height))
        self.transition_surface.set_colorkey(self.config.COLOR_COLORKEY)

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
        
        # Change music based on level
        level_music = self.level_data.get("music", "battle_theme")
        if not self.audio_system.current_song or self.audio_system.current_song.name != level_music:
            self.audio_system.play_song(level_music)

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
        
        # Check if player is in a combo - focus camera between player and enemy
        if self.player.combo_tracker.in_combo:
            # Find the nearest enemy for exciting camera focus
            nearest_enemy = None
            nearest_distance = float('inf')
            for enemy in self.level_data.get("enemies", []):
                distance = abs(enemy.rect.centerx - self.player.rect.centerx)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_enemy = enemy
            
            # If found, focus camera between player and enemy
            if nearest_enemy:
                midpoint_x = (self.player.rect.centerx + nearest_enemy.rect.centerx) // 2
                target_x = midpoint_x - (internal_width // 2)
                target_y = self.player.rect.centery - (internal_height // 2)
            else:
                # No enemy found, fall back to player-centered
                target_x = self.player.rect.centerx - (internal_width // 2)
                target_y = self.player.rect.centery - (internal_height // 2)
        else:
            # Normal behavior: center camera on player
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
        world_height = 920  # Original world height
        
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
                # If it's a level transition, open travel menu
                if hasattr(obj, "destination_index"):
                    self.open_travel_menu()
                # Otherwise call its interact function
                elif hasattr(obj, "interact"):
                    obj.interact(self.player, self)

    def open_travel_menu(self):
        """Open the travel menu with available destinations"""
        destinations = [
            (lvl.split("/")[-1].replace(".py", "").replace("_", " "), i)
            for i, lvl in enumerate(self.level_files)
            if i != self.current_level_index
        ]
        self.travel_menu = TravelMenu(self.font, destinations)
        self.pause_player_physics()
        self.active_menu = "travel"

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
        elif result == "settings":
            self.previous_menu = self.active_menu
            self.active_menu = "settings"
        elif result == "Status":
            self.previous_menu = self.active_menu
            self.active_menu = "status"
        elif result == "go_back":
            self.resume_player_physics()
            self.start_go_back_timer()
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
        
        # Check if player has moved to cancel timer
        if not self.go_back_fade_phase:
            distance_moved = ((self.player.rect.x - self.go_back_start_pos[0]) ** 2 + 
                            (self.player.rect.y - self.go_back_start_pos[1]) ** 2) ** 0.5
            if distance_moved > self.config.GO_BACK_CANCEL_DISTANCE:
                self.go_back_active = False
                self.go_back_timer = 0
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
                self.transitioning = False
                self.transition_phase = None

    def update_bed_fade(self, dt):
        """Update bed fade animation"""
        fade_speed = 300  # Alpha change per second
        
        if self.bed_fade_phase == "fade_out":
            self.bed_fade_alpha += fade_speed * dt
            if self.bed_fade_alpha >= 255:
                self.bed_fade_alpha = 255
                self.bed_fade_phase = "text"
                self.bed_fade_text_timer = 2.0  # Show text for 2 seconds
        
        elif self.bed_fade_phase == "text":
            self.bed_fade_text_timer -= dt
            if self.bed_fade_text_timer <= 0:
                self.bed_fade_phase = "fade_in"
        
        elif self.bed_fade_phase == "fade_in":
            self.bed_fade_alpha -= fade_speed * dt
            if self.bed_fade_alpha <= 0:
                self.bed_fade_alpha = 0
                self.bed_fade_active = False
                self.bed_fade_phase = None
                self.resume_player_physics()
                # Get the Bed object and reset its interaction flag
                for obj in self.level_data.get("interactables", []):
                    if hasattr(obj, "bed_interaction_active"):
                        obj.bed_interaction_active = False

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
            # Start moving left (only if not invulnerable)
            if not self.player.invulnerable:
                self.player.moving_left = True
        
        elif event.key == kb["MoveRight"]:
            # Start moving right (only if not invulnerable)
            if not self.player.invulnerable:
                self.player.moving_right = True
        
        elif event.key == kb["Jump"] and self.player.on_ground:
            # Teleport upward (only if on ground and not invulnerable)
            if not self.player.invulnerable:
                self.player.teleport_jump(self.get_collision_rects(), self.config.PLAYER_TELEPORT_DISTANCE)
        
        elif event.key == kb["Interact"]:
            # Try to interact with nearby objects
            self.handle_interactions()
        
        elif event.key == kb.get("Attack", self.config.DEFAULT_ATTACK_KEY):
            # Attack (can't attack while stunned or invulnerable)
            if self.player.is_stunned or self.player.invulnerable:
                return
            
            # Get current beat from music
            beat_number = 1
            seconds_per_beat = 0.5  # Default
            if self.audio_system.current_song and self.audio_system.current_song.is_playing:
                beat_number = self.audio_system.current_song.current_beat
                seconds_per_beat = self.audio_system.current_song.seconds_per_beat
            
            # Start attack and check if it hits
            if self.player.start_attack(beat_number):
                hit_enemy = self.handle_combat_hits()  # Check for hits
                
                # Record this hit in combo tracker with timing info
                self.player.combo_tracker.add_hit(time.time(), beat_number, hit_enemy, seconds_per_beat)
                
                # Check if combo was invalid (wrong pattern)
                if self.player.combo_tracker.invalid_combo:
                    # Punish player: lose mana and get knocked back
                    from Assets.GameBalance import COMBO_BALANCE
                    mana_loss = COMBO_BALANCE['wrong_combo_mana_loss']
                    self.player.use_mana(mana_loss)
                    
                    knockback_direction = -1 if self.player.facing_right else 1
                    kb_config = COMBO_BALANCE['wrong_combo_knockback']
                    stun = COMBO_BALANCE['wrong_combo_stun']
                    self.player.apply_knockback(knockback_direction * kb_config['x'], kb_config['y'], stun_duration=stun)
                    
                    self.player.combo_tracker.reset()
                
                # If hit an enemy, player gets invulnerability
                elif hit_enemy:
                    self.player.set_invulnerable()

    def _handle_keyup(self, event):
        """Handle when a key is released"""
        kb = self.settings.keybinds
        
        # Stop moving when left/right keys are released (if not invulnerable)
        if event.key == kb["MoveLeft"]:
            if not self.player.invulnerable:
                self.player.moving_left = False
        elif event.key == kb["MoveRight"]:
            if not self.player.invulnerable:
                self.player.moving_right = False

    # COMBAT SYSTEM
    def handle_combat_hits(self):
        """Check if player's attack hits any enemies and apply damage"""
        # Get the player's attack hitbox (invisible rectangle where attack can hit)
        hitbox = self.player.get_attack_hitbox()
        if not hitbox:
            return False  # Player isn't attacking
        
        # Check if player completed a combo with special effects
        from Assets.GameBalance import COMBOS, COMBO_BALANCE
        combo_data = None
        if self.player.combo_tracker.matched_combo:
            combo_id = self.player.combo_tracker.matched_combo
            if combo_id in COMBOS:
                combo_data = COMBOS[combo_id]
        
        # For AOE combos (heavy combo), create larger hitbox
        if combo_data and "aoe_range" in combo_data:
            # Create AOE hitbox centered on player
            aoe_range = combo_data["aoe_range"]
            player_center_x = self.player.rect.centerx
            player_center_y = self.player.rect.centery
            hitbox = pygame.Rect(
                player_center_x - aoe_range // 2,
                player_center_y - aoe_range // 2,
                aoe_range,
                player_center_y + aoe_range // 2  # Extends down more
            )
            
            # Use mana for heavy combo
            if "mana_cost" in combo_data:
                if self.player.stats['Current_Mana'] >= combo_data["mana_cost"]:
                    self.player.use_mana(combo_data["mana_cost"])
                else:
                    return False  # Not enough mana
        
        # Find all enemies that the hitbox touches
        hit_enemies = []
        for enemy in self.level_data.get("enemies", []):
            if hasattr(enemy, 'rect') and hitbox.colliderect(enemy.rect):
                hit_enemies.append(enemy)
        
        if not hit_enemies:
            return False  # Didn't hit anything
        
        # Calculate damage (base damage * combo multiplier)
        damage_mult = self.player.combo_tracker.get_damage_multiplier()
        base_damage = self.player.stats['Attack_Damage']
        total_damage = int(base_damage * damage_mult)
        
        from Assets.GameBalance import COMBO_BALANCE
        
        # Apply damage to each enemy that was hit
        for enemy in hit_enemies:
            if hasattr(enemy, 'take_damage'):
                # Deal damage
                enemy.take_damage(total_damage, is_magical=False)
                self.player.combo_tracker.enemies_hit.add(id(enemy))
                
                # Stun enemy if player is in a combo
                if COMBO_BALANCE['combo_hit_stuns_enemies'] and self.player.combo_tracker.in_combo:
                    enemy.apply_knockback(0, 0, stun_duration=COMBO_BALANCE['combo_stun_duration'])
                
                # Apply special combo knockback if combo is complete
                if combo_data and "final_knockback" in combo_data:
                    kb = combo_data["final_knockback"]
                    knockback_dir = 1 if self.player.facing_right else -1
                    kb_x = kb.get("x", 0) * knockback_dir
                    kb_y = kb.get("y", 0)
                    is_major = kb.get("major", False)
                    enemy.apply_knockback(kb_x, kb_y, stun_duration=0.5, major=is_major)
                
                # If enemy died from this hit
                if not enemy.is_alive():
                    # Make enemy bounce away
                    knockback_dir = 1 if self.player.facing_right else -1
                    enemy.apply_knockback(knockback_dir * 15, -20, stun_duration=2.0, major=True)
                    enemy.dead = True  # Mark for removal later
                    
                    # Spawn loot drops
                    self._spawn_enemy_drops(enemy)
                    
                    # Give player experience
                    exp_gained = enemy.experience_value
                    self.player.gain_experience(exp_gained)
        
        return True  # Successfully hit at least one enemy

    # SLOPE PHYSICS
    def handle_slope_physics(self):
        """Handle special physics for sloped polygons (tents and rocks)"""
        for tent in self.level_data.get("tents", []):
            if tent.handle_tent_collision(self.player):
                self.player.moving_left = False
                self.player.moving_right = False
                return
        
        for rock in self.level_data.get("rocks", []):
            if rock.handle_rock_collision(self.player):
                self.player.moving_left = False
                self.player.moving_right = False
                return

    # ==================== GAME LOOP ====================
    def update(self):
        """Update game state - runs every frame (60 times per second)"""
        # dt = "delta time" = time since last frame in seconds
        dt = self.clock.get_time() / 1000.0
        
        if self.transitioning:
            self.update_transition()
            return
        
        if self.bed_fade_active:
            self.update_bed_fade(dt)
            return
        
        if self.go_back_active:
            self.update_go_back_timer(dt)
            if self.go_back_fade_phase:
                return
        
        if self.active_menu:
            return  # Pause game while menu is open
        
        # ========== Update Game Objects ==========
        # Update coins (collect animations, etc)
        for coin in self.level_data.get("coins", []):
            if hasattr(coin, "update"):
                coin.update(dt)
        
        # Update drops (physics, fading, removal)
        self._update_drops(dt)
        
        # Update audio system (beat tracking)
        self.audio_system.update()
        
        # Get current beat from the music
        current_beat = 1
        if self.audio_system.current_song and self.audio_system.current_song.is_playing:
            current_beat = self.audio_system.current_song.current_beat
        
        # Handle invulnerability flashing effect
        if self.player.invulnerable:
            # Flash the player by toggling a flag (used during draw)
            self.player.invuln_flash = (int(time.time() * 10) % 2) == 0
        
        # ========== Update Combo and Zoom ==========
        # Zoom in/out based on active combos
        self.player.combo_tracker.update(time.time())
        any_enemy_attacking = any(getattr(e, "combo_state", 0) > 0 for e in self.level_data.get("enemies", []))
        player_combo_active = self.player.combo_tracker.should_zoom()
        desired_zoom = (
            self.player.combo_tracker.current_zoom if player_combo_active
            else (2.0 if any_enemy_attacking else self.settings.display.get("zoom_level", 1.5))
        )
        if desired_zoom != self.config.ZOOM_SCALE:
            self.apply_zoom(desired_zoom)
        
        # ========== Update Enemies ==========
        rects = self.get_collision_rects()
        for enemy in self.level_data.get("enemies", []):
            if hasattr(enemy, "update_ai"):
                # Update enemy AI (behavior, movement, attacks)
                enemy.update_ai(self.player, rects, self.config.GRAVITY, self.config.MAX_FALL_SPEED, dt, current_beat)
        
        # Remove dead enemies (after bounce animation completes)
        if hasattr(self, 'dead_enemy_timers'):
            to_remove = []
            for enemy in self.level_data.get("enemies", []):
                if hasattr(enemy, 'dead') and enemy.dead:
                    if enemy not in self.dead_enemy_timers:
                        self.dead_enemy_timers[enemy] = 1.5  # Wait 1.5 seconds before removing
                    self.dead_enemy_timers[enemy] -= dt
                    if self.dead_enemy_timers[enemy] <= 0:
                        to_remove.append(enemy)
            for enemy in to_remove:
                self.level_data["enemies"].remove(enemy)
                if enemy in self.dead_enemy_timers:
                    del self.dead_enemy_timers[enemy]
        else:
            # First time: initialize dead enemy timer dict
            self.dead_enemy_timers = {}
            for enemy in self.level_data.get("enemies", []):
                if not enemy.is_alive():
                    enemy.dead = True
        
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
        
        # Lock movement while invulnerable
        if self.player.invulnerable:
            self.player.moving_left = False
            self.player.moving_right = False
        
        # Update player position (only if not stunned)
        if not self.player.is_stunned:
            # Apply gravity first
            self.player.apply_gravity(self.config.GRAVITY, self.config.MAX_FALL_SPEED, rects)
            
            # Handle slopes (tents, rocks with special physics)
            self.handle_slope_physics()
            
            # Move player left/right
            self.player.move(rects)
            
            # Update attack animation
            self.player.update_attack()
        else:
            # Still fall while stunned (can't prevent gravity)
            self.player.apply_gravity(self.config.GRAVITY, self.config.MAX_FALL_SPEED, rects)
        
        # ========== Update Camera ==========
        # Position camera to follow player
        self.update_camera()

    # ==================== RENDERING ====================
    def draw(self):
        """Draw everything on screen - runs every frame"""
        # Clear screen to sky color
        self.screen.fill(self.config.COLOR_SKY)
        
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
        self._draw_menus()
        self._draw_transition()
        self._draw_go_back_fade()
        self._draw_bed_fade()
        
        # Draw metronome/beat counter (only in dark forest)
        level_id = self.level_data.get("level_id", None)
        self.audio_system.draw_beat_counter(self.screen, level_id)
        
        # Draw combo UI
        self._draw_combo_ui()
        
        # Scale the internal screen to display surface with smooth scaling for better visuals
        scaled = pygame.transform.smoothscale(self.screen, (self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        self.display_surface.blit(scaled, (0, 0))
        
        pygame.display.flip()

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
        """Spawn simple loot orbs that fan out on enemy death"""
        # Create 5 drops that fly outward in random directions
        for _ in range(count):
            # Random angle (0 to 360 degrees)
            angle = random.uniform(0, math.tau)  # tau = 2*pi = full circle
            # Random speed for variety
            speed = random.uniform(160, 240)
            
            # Create a drop with position, velocity, and appearance
            self.drops.append({
                "x": enemy.rect.centerx,  # Start at enemy center
                "y": enemy.rect.centery,
                "vx": math.cos(angle) * speed,  # Horizontal velocity
                "vy": math.sin(angle) * speed - 140,  # Vertical velocity (- = up)
                "life": 2.0,  # Lives for 2 seconds
                "radius": 6,  # Size of the circle
                "color": (255, 215, 120)  # Gold color (R, G, B)
            })

    def _update_drops(self, dt):
        """Update all drops - apply physics and remove expired ones"""
        if not self.drops:
            return  # No drops to update
        
        # Physics constants
        gravity = 520  # How fast drops fall
        damping = 0.9 ** (dt * 60)  # How much velocity slows down each frame
        
        # Keep only drops that are still alive
        alive = []
        for drop in self.drops:
            # Apply physics
            drop["vy"] += gravity * dt  # Gravity pulls down
            drop["vx"] *= damping  # Slow down horizontal movement
            drop["vy"] *= damping  # Slow down vertical movement
            
            # Move the drop
            drop["x"] += drop["vx"] * dt
            drop["y"] += drop["vy"] * dt
            
            # Count down lifetime
            drop["life"] -= dt
            
            # Keep drop if it's still alive
            if drop["life"] > 0:
                alive.append(drop)
        
        # Replace drop list with only alive drops
        self.drops = alive

    def _draw_drops(self):
        """Draw all drop circles on screen"""
        for drop in self.drops:
            # Convert world position to screen position (accounting for camera)
            screen_x = int(drop["x"] - self.camera_x)
            screen_y = int(drop["y"] - self.camera_y)
            screen_pos = (screen_x, screen_y)
            
            # Draw the drop as a filled circle
            pygame.draw.circle(self.screen, drop["color"], screen_pos, drop["radius"])

    def _draw_enemies(self):
        """Draw enemies"""
        for enemy in self.level_data.get("enemies", []):
            if hasattr(enemy, "draw"):
                enemy.draw(self.screen, self.camera_x, self.camera_y, enemy.color, self.config)

    def _draw_player(self):
        """Draw player character"""
        screen_rect = self.player.rect.move(-self.camera_x, -self.camera_y)
        
        # Draw player with invulnerability flash effect
        alpha = self.config.ALPHA_PLAYER
        if self.player.invulnerable and self.player.invuln_flash:
            alpha = int(self.config.ALPHA_PLAYER * 0.5)  # Flash by reducing alpha
        
        self._draw_with_alpha(self.screen, self.config.COLOR_PLAYER, screen_rect, alpha)
        
        # Draw attack hitbox if attacking
        hitbox = self.player.get_attack_hitbox()
        if hitbox:
            hitbox_surface = pygame.Surface((hitbox.width, hitbox.height), pygame.SRCALPHA)
            config = self.player.attack_hitbox_config
            hitbox_surface.fill((*config['color'], config['alpha']))
            self.screen.blit(hitbox_surface, (hitbox.x - self.camera_x, hitbox.y - self.camera_y))

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

    def _draw_combo_ui(self):
        """Draw combo info during active combat"""
        # Only show when player is in a combo
        if not self.player.combo_tracker.in_combo:
            return
        
        base_x = 15
        y_pos = 130
        
        # Draw hit counter
        if COMBO_CONFIG["show_hit_count"]:
            hit_text = f"Hits: {self.player.combo_tracker.hit_count}"
            hit_surface = self.font.render(hit_text, True, COMBO_CONFIG["hit_text_color"])
            self.screen.blit(hit_surface, (base_x, y_pos))
            y_pos += 30
        
        # Draw combo name
        if COMBO_CONFIG["show_combo_name"] and self.player.combo_tracker.matched_combo:
            combo_name = self.player.combo_tracker.get_combo_name()
            combo_surface = self.font.render(combo_name, True, COMBO_CONFIG["combo_text_color"])
            self.screen.blit(combo_surface, (base_x, y_pos))
            y_pos += 30
            
            # Draw damage multiplier
            mult = self.player.combo_tracker.get_damage_multiplier()
            mult_text = f"{mult}x Damage"
            mult_surface = self.font.render(mult_text, True, COMBO_CONFIG["combo_text_color"])
            self.screen.blit(mult_surface, (base_x, y_pos))
    
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
        pygame.draw.rect(self.screen, (100, 0, 0), (bar_x, health_y, bar_width, bar_height))
        # Draw foreground (bright red) - size based on health
        pygame.draw.rect(self.screen, (255, 0, 0), (bar_x, health_y, int(bar_width * health_ratio), bar_height))
        # Draw white border
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, health_y, bar_width, bar_height), 2)
        
        # Draw health text
        health_text = f"HP: {int(self.player.stats['Current_Health'])}/{int(self.player.stats['Max_Health'])}"
        health_surface = self.font.render(health_text, True, (255, 255, 255))
        self.screen.blit(health_surface, (bar_x + 5, health_y + 2))
        
        # ===== MANA BAR =====
        # Calculate how full the mana bar is (0.0 to 1.0)
        mana_ratio = self.player.stats['Current_Mana'] / self.player.stats['Max_Mana']
        mana_ratio = max(0, min(1, mana_ratio))  # Keep between 0 and 1
        
        # Draw background (dark blue)
        pygame.draw.rect(self.screen, (0, 0, 100), (bar_x, mana_y, bar_width, bar_height))
        # Draw foreground (bright blue) - size based on mana
        pygame.draw.rect(self.screen, (0, 100, 255), (bar_x, mana_y, int(bar_width * mana_ratio), bar_height))
        # Draw white border
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, mana_y, bar_width, bar_height), 2)
        
        # Draw mana text
        mana_text = f"MP: {int(self.player.stats['Current_Mana'])}/{int(self.player.stats['Max_Mana'])}"
        mana_surface = self.font.render(mana_text, True, (255, 255, 255))
        self.screen.blit(mana_surface, (bar_x + 5, mana_y + 2))
        
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
        """Draw bed fade effect and text"""
        if self.bed_fade_active:
            fade_surface = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.bed_fade_alpha)
            self.screen.blit(fade_surface, (0, 0))
            
            # Draw text during text phase
            if self.bed_fade_phase == "text":
                text = self.font.render("The next day...", True, (255, 255, 255))
                text_x = self.screen.get_width() // 2 - text.get_width() // 2
                text_y = self.screen.get_height() // 2 - text.get_height() // 2
                self.screen.blit(text, (text_x, text_y))

    def _draw_menus(self):
        """Draw active menu"""
        if self.active_menu:
            menu = self.travel_menu if self.active_menu == "travel" else self.menus[self.active_menu]
            menu.draw(self.screen)

    def _draw_transition(self):
        """Draw transition effect"""
        if self.transitioning:
            self.transition_surface.fill(self.config.COLOR_COLORKEY)
            center_x = self.screen.get_width() // 2
            center_y = self.screen.get_height() // 2
            pygame.draw.circle(self.transition_surface, self.config.COLOR_TRANSITION,
                             (center_x, center_y), int(self.transition_radius))
            self.screen.blit(self.transition_surface, (0, 0))

    def run(self):
        """Main game loop"""
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(self.config.FPS)


# ENTRY POINT
Game().run()