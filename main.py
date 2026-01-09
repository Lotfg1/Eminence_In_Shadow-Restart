# main.py
import pygame
import sys
import importlib.util
from Assets.Settings import Settings
from Assets.Characters import MainCharacter
from Assets.Menus import StartMenu, PauseMenu, MerchantMenu, TravelMenu, SettingsMenu, StatusMenu

# =====================================================
# CONFIGURATION
# =====================================================
class Config:
    """Central configuration for the game"""
    # Display
    SCREEN_WIDTH = 1080
    SCREEN_HEIGHT = 920
    FPS = 60
    WINDOW_TITLE = "Eminence in Shadow"
    
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
    PLAYER_SPEED = 10
    PLAYER_JUMP_STRENGTH = -24
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
    
    # Colors
    COLOR_SKY = (30, 30, 80)
    COLOR_GROUND = (100, 100, 100)
    COLOR_PLATFORM = (160, 82, 45)
    COLOR_INTERACTABLE = (200, 100, 200)
    COLOR_PLAYER = (0, 255, 0)
    COLOR_TRANSITION = (0, 0, 0)
    COLOR_COLORKEY = (255, 0, 255)
    COLOR_TIMER_BG = (0, 0, 0)
    COLOR_TIMER_TEXT = (255, 255, 255)
    
    # Paths
    LEVEL_PATHS = [
        "Assets/Levels/Player_Room.py",
        "Assets/Levels/City.py",
        "Assets/Levels/Dark_Forest.py"
    ]
    INTERACT_ICON_PATH = "Assets/Photos/Key_Placeholder_Image.png"
    SETTINGS_PATH = "Assets/settings.json"
    
    # Attack Keybind (if not in settings file)
    DEFAULT_ATTACK_KEY = pygame.K_SPACE

# =====================================================
# GAME CLASS
# =====================================================
class Game:
    def __init__(self):
        pygame.init()
        self.config = Config()
        
        # Display setup
        self.screen = pygame.display.set_mode((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        pygame.display.set_caption(self.config.WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 32)
        self.timer_font = pygame.font.SysFont(None, 48)

        # Player
        self.player = MainCharacter()
        self.saved_y_momentum = 0  # Store y_momentum when menu opens

        # Camera
        self.camera_x = 0
        self.look_offset_x = 0
        self.zoom_level = 1.0  # 1.0 = normal, 2.0 = 2x zoom, etc.
        self.zoom_target = None  # (x, y) coordinates to focus on
        self.zoom_active = False

        # Level management
        self.level_files = self.config.LEVEL_PATHS
        self.current_level_index = 0
        self.level_data = {}
        self.load_level(self.level_files[self.current_level_index])

        # Settings and menus
        self.settings = Settings(self.config.SETTINGS_PATH)
        # Ensure attack key exists in keybinds
        if "Attack" not in self.settings.keybinds:
            self.settings.keybinds["Attack"] = self.config.DEFAULT_ATTACK_KEY
            self.settings.save()
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

    def _initialize_menus(self):
        """Initialize all menu objects"""
        self.menus = {
            "start": StartMenu(self.font),
            "pause": PauseMenu(self.font, self.config.SCREEN_WIDTH),
            "merchant": MerchantMenu(self.font),
            "settings": SettingsMenu(self.font, self.settings),
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
        self.transition_max = int((self.config.SCREEN_WIDTH ** 2 + self.config.SCREEN_HEIGHT ** 2) ** 0.5)
        self.transition_surface = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        self.transition_surface.set_colorkey(self.config.COLOR_COLORKEY)

    # =================================================
    # LEVEL MANAGEMENT
    # =================================================
    def load_level(self, filepath):
        """Load a level from a Python file"""
        spec = importlib.util.spec_from_file_location("level_module", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.level_data = module.load_level()

        # Reset player
        self.player.rect.topleft = self.level_data["player_start"]
        self.player.y_momentum = 0
        self.player.on_ground = False

        # Reset camera
        self.camera_x = 0
        self.look_offset_x = 0

        # Generate initial segments for infinite levels
        if self.level_data.get("infinite", False):
            seg = self.player.rect.centerx // self.config.SEGMENT_WIDTH
            for i in range(seg - 2, seg + 3):
                self.level_data["generate_segment"](i)

    def get_collision_rects(self):
        """Get all collision rectangles in the current level"""
        rects = []
        rects.extend(self.level_data.get("ground", []))
        rects.extend(self.level_data.get("platforms", []))
        
        # Add collidable interactables
        for obj in self.level_data.get("interactables", []):
            if getattr(obj, "collidable", True):
                rects.append(obj.rect)
        
        # Add tent bases (only the base platform, not the whole tent)
        for tent in self.level_data.get("tents", []):
            rects.append(tent.get_collision_rect())
        
        # Rocks don't have collidable bases - they're pure slopes
        
        # Add infinite level segments
        if self.level_data.get("infinite", False):
            for seg in self.level_data["segments"].values():
                g = seg["ground"]
                rects.append(g) if isinstance(g, pygame.Rect) else rects.extend(g)
                rects.extend(seg["platforms"])
        
        return rects

    # =================================================
    # CAMERA SYSTEM
    # =================================================
    def set_zoom(self, zoom_level, target_pos=None):
        """Set camera zoom level and optional focus point
        Args:
            zoom_level: float, 1.0 = normal, 2.0 = 2x zoom, 0.5 = zoom out
            target_pos: tuple (x, y) world coordinates to focus on, None = focus on player
        """
        self.zoom_level = max(0.5, min(3.0, zoom_level))  # Clamp between 0.5x and 3x
        self.zoom_target = target_pos
        self.zoom_active = target_pos is not None
    
    def reset_zoom(self):
        """Reset zoom to normal"""
        self.zoom_level = 1.0
        self.zoom_target = None
        self.zoom_active = False
    
    def update_camera(self):
        """Update camera position with smoothing and look-ahead"""
        if self.zoom_active and self.zoom_target:
            # Focus on zoom target
            target_x = self.zoom_target[0] - self.config.SCREEN_WIDTH // 2
        else:
            # Normal camera following player
            target_x = self.player.rect.centerx - self.config.SCREEN_WIDTH // 2
            keys = pygame.key.get_pressed()

            # Look-ahead system for infinite levels
            if self.level_data.get("infinite", False):
                self._update_look_ahead(keys)
                target_x += self.look_offset_x
            else:
                self.look_offset_x = 0

        # Clamp camera to level bounds
        target_x = self._clamp_camera_target(target_x)

        # Smooth camera movement
        self.camera_x += (target_x - self.camera_x) * self.config.CAMERA_SMOOTHING
        self.camera_x = self._clamp_camera_position(self.camera_x)

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

    def _clamp_camera_target(self, target_x):
        """Clamp camera target to level boundaries"""
        target_x = max(0, target_x)
        
        if not self.level_data.get("infinite", False):
            world_width = self.level_data.get("world_width", self.config.SCREEN_WIDTH)
            if world_width <= self.config.SCREEN_WIDTH:
                target_x = -(self.config.SCREEN_WIDTH - world_width) // 2
            else:
                target_x = min(target_x, world_width - self.config.SCREEN_WIDTH)
        
        return target_x

    def _clamp_camera_position(self, camera_x):
        """Clamp final camera position"""
        if not self.level_data.get("infinite", False):
            world_width = self.level_data.get("world_width", self.config.SCREEN_WIDTH)
            if world_width <= self.config.SCREEN_WIDTH:
                return -(self.config.SCREEN_WIDTH - world_width) // 2
            else:
                return max(0, min(camera_x, world_width - self.config.SCREEN_WIDTH))
        else:
            return max(0, camera_x)

    # =================================================
    # INTERACTION SYSTEM
    # =================================================
    def handle_interactions(self):
        """Check for and handle player interactions"""
        box = self.player.rect.inflate(*self.config.INTERACTION_BOX_INFLATE)
        for obj in self.level_data.get("interactables", []):
            if box.colliderect(obj.rect):
                if hasattr(obj, "destination_index"):
                    self.open_travel_menu()
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

    # =================================================
    # PLAYER PHYSICS PAUSE/RESUME
    # =================================================
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

    # =================================================
    # MENU SYSTEM
    # =================================================
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
            self.previous_menu = self.active_menu  # Remember where we came from
            self.active_menu = "settings"
        elif result == "Status":
            self.previous_menu = self.active_menu  # Remember where we came from
            self.active_menu = "status"
        elif result == "go_back":
            self.resume_player_physics()
            self.start_go_back_timer()
        elif isinstance(result, int):
            self.start_transition(result)

    def start_go_back_timer(self):
        """Start the 5-second timer for going back to level start"""
        self.go_back_active = True
        self.go_back_timer = self.config.GO_BACK_TIMER_DURATION
        self.go_back_start_pos = (self.player.rect.x, self.player.rect.y)
        self.active_menu = None  # Close pause menu
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
                # Cancel timer
                self.go_back_active = False
                self.go_back_timer = 0
                return
        
        # If in fade phase, handle fade
        if self.go_back_fade_phase == "fade_out":
            self.go_back_fade_alpha += self.config.FADE_SPEED
            if self.go_back_fade_alpha >= 255:
                self.go_back_fade_alpha = 255
                # Reset player position
                self.player.rect.topleft = self.level_data["player_start"]
                self.player.y_momentum = 0
                self.player.on_ground = False
                self.camera_x = 0
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

    # =================================================
    # TRANSITION SYSTEM
    # =================================================
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

    # =================================================
    # INPUT HANDLING
    # =================================================
    def handle_input(self):
        """Process all input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Menu input
            if self.active_menu:
                self.handle_menu_input(event)
                continue
            
            # Game input (only if not in go back timer)
            if not self.go_back_active:
                if event.type == pygame.KEYDOWN:
                    self._handle_keydown(event)
                elif event.type == pygame.KEYUP:
                    self._handle_keyup(event)

    def _handle_keydown(self, event):
        """Handle key press events"""
        kb = self.settings.keybinds
        
        if event.key == kb["Pause"]:
            self.pause_player_physics()
            self.active_menu = "pause"
        elif event.key == kb["MoveLeft"]:
            self.player.moving_left = True
        elif event.key == kb["MoveRight"]:
            self.player.moving_right = True
        elif event.key == kb["Jump"] and self.player.on_ground:
            self.player.y_momentum = self.config.PLAYER_JUMP_STRENGTH
        elif event.key == kb["Interact"]:
            self.handle_interactions()
        elif event.key == kb.get("Attack", self.config.DEFAULT_ATTACK_KEY):
            self.player.start_attack()

    def _handle_keyup(self, event):
        """Handle key release events"""
        kb = self.settings.keybinds
        
        if event.key == kb["MoveLeft"]:
            self.player.moving_left = False
        elif event.key == kb["MoveRight"]:
            self.player.moving_right = False

    # =================================================
    # SLOPE PHYSICS
    # =================================================
    def handle_slope_physics(self):
        """Handle special physics for sloped polygons (tents and rocks)"""
        # Handle tents (large polygons)
        for tent in self.level_data.get("tents", []):
            if tent.handle_tent_collision(self.player):
                # Player is sliding on tent, disable movement input
                self.player.moving_left = False
                self.player.moving_right = False
                return  # Only one slope at a time
        
        # Handle rocks (small polygons)
        for rock in self.level_data.get("rocks", []):
            if rock.handle_rock_collision(self.player):
                # Player is sliding on rock, disable movement input
                self.player.moving_left = False
                self.player.moving_right = False
                return  # Only one slope at a time

    # =================================================
    # GAME LOOP
    # =================================================
    def update(self):
        """Update game state"""
        dt = self.clock.get_time() / 1000.0  # Delta time in seconds
        
        if self.transitioning:
            self.update_transition()
            return
        
        # Update go back timer
        if self.go_back_active:
            self.update_go_back_timer(dt)
            if self.go_back_fade_phase:
                return  # Don't update physics during fade
        
        # Skip physics updates if menu is active
        if self.active_menu:
            return
        
        # Generate new segments for infinite levels
        if self.level_data.get("infinite", False):
            seg = self.player.rect.centerx // self.config.SEGMENT_WIDTH
            for i in range(seg - 2, seg + 3):
                if i not in self.level_data["segments"]:
                    self.level_data["generate_segment"](i)
        
        # Update player physics
        rects = self.get_collision_rects()
        self.player.apply_gravity(self.config.GRAVITY, self.config.MAX_FALL_SPEED, rects)
        
        # Handle slope physics BEFORE regular movement
        self.handle_slope_physics()
        
        # Regular movement (will be disabled if on slope)
        self.player.move(rects)
        
        # Update attack
        self.player.update_attack()
        
        # Update camera
        self.update_camera()

    def draw(self):
        """Render the game"""
        # Clear screen
        self.screen.fill(self.config.COLOR_SKY)
        
        # Draw level elements
        self._draw_ground()
        self._draw_platforms()
        self._draw_natural_objects()
        self._draw_interactables()
        self._draw_player()
        
        # Draw UI elements
        self._draw_interaction_icons()
        self._draw_go_back_timer()
        self._draw_menus()
        self._draw_transition()
        self._draw_go_back_fade()
        
        # Update display
        pygame.display.flip()

    def _draw_ground(self):
        """Draw ground rectangles"""
        for g in self.level_data.get("ground", []):
            pygame.draw.rect(self.screen, self.config.COLOR_GROUND, g.move(-self.camera_x, 0))

    def _draw_platforms(self):
        """Draw platform rectangles"""
        for p in self.level_data.get("platforms", []):
            pygame.draw.rect(self.screen, self.config.COLOR_PLATFORM, p.move(-self.camera_x, 0))

    def _draw_natural_objects(self):
        """Draw natural objects (rocks, tents, slopes)"""
        for obj in self.level_data.get("natural_objects", []):
            if hasattr(obj, "draw"):
                obj.draw(self.screen, self.camera_x)
            else:
                # Fallback for objects without custom draw method
                pygame.draw.rect(self.screen, (150, 150, 150), obj.rect.move(-self.camera_x, 0))

    def _draw_interactables(self):
        """Draw interactable objects"""
        for obj in self.level_data.get("interactables", []):
            pygame.draw.rect(self.screen, self.config.COLOR_INTERACTABLE, obj.rect.move(-self.camera_x, 0))

    def _draw_player(self):
        """Draw player character"""
        pygame.draw.rect(self.screen, self.config.COLOR_PLAYER, self.player.rect.move(-self.camera_x, 0))
        
        # Draw attack hitbox if attacking
        hitbox = self.player.get_attack_hitbox()
        if hitbox:
            # Create transparent surface for hitbox
            hitbox_surface = pygame.Surface((hitbox.width, hitbox.height), pygame.SRCALPHA)
            config = self.player.attack_hitbox_config
            hitbox_surface.fill((*config['color'], config['alpha']))
            
            # Draw to screen
            self.screen.blit(hitbox_surface, (hitbox.x - self.camera_x, hitbox.y))

    def _draw_interaction_icons(self):
        """Draw interaction icons above nearby objects"""
        nearby = self.get_nearby_interactables()
        for obj in nearby:
            icon_x = obj.rect.centerx - self.camera_x - self.interact_icon.get_width() // 2
            icon_y = self.player.rect.top - self.config.ICON_OFFSET_Y
            self.screen.blit(self.interact_icon, (icon_x, icon_y))

    def _draw_go_back_timer(self):
        """Draw the countdown timer above player's head"""
        if self.go_back_active and not self.go_back_fade_phase:
            # Draw timer background
            timer_text = f"{int(self.go_back_timer) + 1}"
            text_surface = self.timer_font.render(timer_text, True, self.config.COLOR_TIMER_TEXT)
            
            # Position above player's head
            player_screen_x = self.player.rect.centerx - self.camera_x
            player_screen_y = self.player.rect.top - 90
            
            # Background rectangle
            bg_rect = pygame.Rect(
                player_screen_x - text_surface.get_width() // 2 - 10,
                player_screen_y - 10,
                text_surface.get_width() + 20,
                text_surface.get_height() + 20
            )
            pygame.draw.rect(self.screen, self.config.COLOR_TIMER_BG, bg_rect)
            pygame.draw.rect(self.screen, self.config.COLOR_TIMER_TEXT, bg_rect, 2)
            
            # Timer text
            self.screen.blit(text_surface, (player_screen_x - text_surface.get_width() // 2, player_screen_y))
            
            # "Move to cancel" text
            cancel_text = self.font.render("Move to cancel", True, (200, 200, 200))
            cancel_y = player_screen_y + text_surface.get_height() + 5
            self.screen.blit(cancel_text, (player_screen_x - cancel_text.get_width() // 2, cancel_y))

    def _draw_go_back_fade(self):
        """Draw fade effect for go back"""
        if self.go_back_fade_phase:
            fade_surface = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.go_back_fade_alpha)
            self.screen.blit(fade_surface, (0, 0))

    def _draw_menus(self):
        """Draw active menu"""
        if self.active_menu:
            menu = self.travel_menu if self.active_menu == "travel" else self.menus[self.active_menu]
            menu.draw(self.screen)

    def _draw_transition(self):
        """Draw transition effect"""
        if self.transitioning:
            self.transition_surface.fill(self.config.COLOR_COLORKEY)
            pygame.draw.circle(self.transition_surface, self.config.COLOR_TRANSITION,
                             (self.config.SCREEN_WIDTH // 2, self.config.SCREEN_HEIGHT // 2),
                             int(self.transition_radius))
            self.screen.blit(self.transition_surface, (0, 0))

    def run(self):
        """Main game loop"""
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(self.config.FPS)


# =====================================================
# ENTRY POINT
# =====================================================
if __name__ == "__main__":
    Game().run()