# Assets/Interactables.py
import pygame
import random
import time
from PIL import Image
from Assets.Characters import SmallBandit
class Interactable:
    def __init__(self, x, y, width, height, collidable=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.collidable = collidable

    def interact(self, player, game):
        pass
    
    def draw(self, screen, camera_x, camera_y, config):
        """Default draw method - can be overridden"""
        pass

# ----------------------------
# BED
# ----------------------------
class Bed(Interactable):
    def __init__(self, x, y, width=64, height=32):
        super().__init__(x, y, width, height, collidable=True)
        self.bed_interaction_active = False
        self.fade_active = False
        self.fade_phase = None
        self.fade_alpha = 0
        self.fade_text_timer = 0

    def interact(self, player, game):
        if not self.bed_interaction_active:
            self.bed_interaction_active = True
            self.fade_active = True
            self.fade_phase = "fade_out"
            self.fade_alpha = 0
            game.pause_player_physics()
    
    def update_fade(self, dt, player, game):
        """Update bed fade animation - call this from game update loop"""
        if not self.fade_active:
            return
        
        fade_speed = 300  # Alpha change per second
        
        if self.fade_phase == "fade_out":
            self.fade_alpha += fade_speed * dt
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.fade_phase = "text"
                self.fade_text_timer = 2.0  # Show text for 2 seconds
                # Heal player when resting
                player.heal(player.stats["max_health"])
        
        elif self.fade_phase == "text":
            self.fade_text_timer -= dt
            if self.fade_text_timer <= 0:
                self.fade_phase = "fade_in"
        
        elif self.fade_phase == "fade_in":
            self.fade_alpha -= fade_speed * dt
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fade_active = False
                self.fade_phase = None
                self.bed_interaction_active = False
                game.resume_player_physics()
    
    def draw_fade(self, screen):
        """Draw fade overlay and text - call this from game draw loop"""
        if not self.fade_active:
            return
        
        # Draw black fade overlay
        fade_surface = pygame.Surface(screen.get_size())
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(int(self.fade_alpha))
        screen.blit(fade_surface, (0, 0))
        
        # Draw "Resting..." text during text phase
        if self.fade_phase == "text":
            font = pygame.font.Font(None, 72)
            text = font.render("Resting...", True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(text, text_rect)

    def draw(self, screen, camera_x, camera_y, config):
        """Draw bed with config colors"""
        screen_rect = self.rect.move(-camera_x, -camera_y)
        if config.ALPHA_BED < 255:
            temp_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            temp_surface.fill((*config.COLOR_BED, config.ALPHA_BED))
            screen.blit(temp_surface, screen_rect.topleft)
        else:
            pygame.draw.rect(screen, config.COLOR_BED, screen_rect)

# ----------------------------
# MERCHANT
# ----------------------------
class Merchant(Interactable):
    def __init__(self, x, y, width=64, height=64):
        super().__init__(x, y, width, height, collidable=True)

    def interact(self, player, game):
        game.active_menu = "merchant"
    
    def draw(self, screen, camera_x, camera_y, config):
        """Draw merchant with config colors"""
        screen_rect = self.rect.move(-camera_x, -camera_y)
        if config.ALPHA_MERCHANT < 255:
            temp_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            temp_surface.fill((*config.COLOR_MERCHANT, config.ALPHA_MERCHANT))
            screen.blit(temp_surface, screen_rect.topleft)
        else:
            pygame.draw.rect(screen, config.COLOR_MERCHANT, screen_rect)

# ----------------------------
# WALL
# ----------------------------
class Wall(Interactable):
    def __init__(self, x, y, width, height, destination_index=False):
        super().__init__(x, y, width, height, collidable=True)
        self.destination_index = destination_index

    def interact(self, player, game):
        """Handle wall interaction - opens travel menu if this is a level boundary"""
        if self.destination_index:
            self.open_travel_menu(game)
    
    def open_travel_menu(self, game):
        """Open the travel menu with available destinations"""
        from Assets.Menus import TravelMenu
        destinations = [
            (lvl.split("/")[-1].replace(".py", "").replace("_", " "), i)
            for i, lvl in enumerate(game.level_files)
            if i != game.current_level_index
        ]
        game.travel_menu = TravelMenu(game.font, destinations)
        game.pause_player_physics()
        game.active_menu = "travel"
    
    def draw(self, screen, camera_x, camera_y, config):
        """Draw wall with config colors"""
        screen_rect = self.rect.move(-camera_x, -camera_y)
        if config.ALPHA_WALL < 255:
            temp_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            temp_surface.fill((*config.COLOR_WALL, config.ALPHA_WALL))
            screen.blit(temp_surface, screen_rect.topleft)
        else:
            pygame.draw.rect(screen, config.COLOR_WALL, screen_rect)

# ----------------------------
# COIN (Animated)
# ----------------------------
class Coin:
    def __init__(self, x, y, width=32, height=32):
        self.rect = pygame.Rect(x, y, width, height)
        self.collidable = False  # Coins don't block movement
        
        # Animation settings
        self.animation_timer = 0
        self.animation_interval = 5.0  # Animate every 5 seconds
        self.is_animating = False
        self.animation_frame = 0
        self.animation_duration = 0.5  # Animation lasts 0.5 seconds
        
        # Try to load coin image and animation
        self.static_image = None
        self.animation_frames = []
        try:
            self.static_image = pygame.image.load("Assets/Photos/Coin.png")
            self.static_image = pygame.transform.scale(self.static_image, (width, height))
        except:
            pass
        
        try:
            # Try to load GIF frames (requires pillow)
            
            gif = Image.open("Assets/Animations/Coin.gif")
            self.animation_frames = []
            try:
                while True:
                    frame = gif.copy()
                    frame = frame.convert("RGBA")
                    # Convert PIL image to pygame surface
                    mode = frame.mode
                    size = frame.size
                    data = frame.tobytes()
                    pygame_image = pygame.image.fromstring(data, size, mode)
                    pygame_image = pygame.transform.scale(pygame_image, (width, height))
                    self.animation_frames.append(pygame_image)
                    gif.seek(gif.tell() + 1)
            except EOFError:
                pass
        except:
            pass
        
        # Color fallback if no images
        self.color = (255, 215, 0)  # Gold color
    
    def update(self, dt):
        """Update animation state"""
        if self.is_animating:
            self.animation_frame += dt
            if self.animation_frame >= self.animation_duration:
                self.is_animating = False
                self.animation_frame = 0
                self.animation_timer = 0
        else:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_interval:
                self.is_animating = True
                self.animation_frame = 0
    
    def draw(self, screen, camera_x, camera_y):
        """Draw the coin"""
        screen_rect = self.rect.move(-camera_x, -camera_y)
        
        if self.is_animating and self.animation_frames:
            # Show animation
            frame_index = int((self.animation_frame / self.animation_duration) * len(self.animation_frames))
            frame_index = min(frame_index, len(self.animation_frames) - 1)
            screen.blit(self.animation_frames[frame_index], screen_rect.topleft)
        elif self.static_image:
            # Show static image
            screen.blit(self.static_image, screen_rect.topleft)
        else:
            # Fallback to colored rectangle
            pygame.draw.rect(screen, self.color, screen_rect)
            # Draw a simple coin symbol
            pygame.draw.circle(screen, (255, 255, 0), screen_rect.center, min(screen_rect.width, screen_rect.height) // 3)

# ----------------------------
# TENT (Large Sloped Polygon)
# ----------------------------
class Tent:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 120
        self.height = 90
        self.rect = pygame.Rect(x, y - self.height, self.width, self.height)
        self.collidable = False
        
        # Define triangle points for slope detection
        self.peak_x = x + self.width // 2
        self.peak_y = y - self.height
        self.left_x = x
        self.right_x = x + self.width
        self.base_y = y - 20
    
    def is_player_on_tent(self, player):
        player_center_x = player.rect.centerx
        player_bottom = player.rect.bottom
        
        if player_center_x < self.left_x - 5 or player_center_x > self.right_x + 5:
            return False
        
        if player_bottom < self.peak_y - 10 or player_bottom > self.base_y + 15:
            return False
        
        tent_y = self.get_tent_y_at_x(player_center_x)
        
        return abs(player_bottom - tent_y) < 25 and player.y_momentum >= -2
    
    def get_tent_y_at_x(self, player_x):
        if player_x <= self.left_x:
            return self.base_y
        if player_x >= self.right_x:
            return self.base_y
        
        if player_x <= self.peak_x:
            slope_length = self.peak_x - self.left_x
            if slope_length == 0:
                return self.base_y
            progress = (player_x - self.left_x) / slope_length
            y_on_slope = self.base_y + (self.peak_y - self.base_y) * progress
        else:
            slope_length = self.right_x - self.peak_x
            if slope_length == 0:
                return self.base_y
            progress = (player_x - self.peak_x) / slope_length
            y_on_slope = self.peak_y + (self.base_y - self.peak_y) * progress
        
        return y_on_slope
    
    def handle_tent_collision(self, player):
        """Make player slide down the tent naturally"""
        if not self.is_player_on_tent(player):
            return False
        
        tent_y = self.get_tent_y_at_x(player.rect.centerx)
        player.rect.bottom = int(tent_y)
        player.y_momentum = 0
        player.on_ground = True
        
        # Gentle push away from peak to prevent getting stuck
        distance_from_peak = abs(player.rect.centerx - self.peak_x)
        if distance_from_peak < 40:  # Only near peak
            if player.rect.centerx < self.peak_x:
                player.rect.x -= 1  # Gentle push left
            elif player.rect.centerx > self.peak_x:
                player.rect.x += 1  # Gentle push right
        
        return True
        

    def interact(self, player, game):
        """Rest at the tent - shows fade animation and heals to full, then spawns 3 bandits"""
        # Restore health/mana to full
        player.stats['Current_Health'] = player.stats.get('Max_Health', player.stats['Current_Health'])
        player.stats['Current_Mana'] = player.stats.get('Max_Mana', player.stats['Current_Mana'])

        # Start bed fade animation (same as sleeping in a bed)
        game.bed_fade_active = True
        game.bed_fade_phase = "fade_out"
        game.bed_fade_alpha = 0
        game.pause_player_physics()
        
        # Mark tent for enemy spawning after fade
        self.spawn_bandits_after_rest = True
        self.tent_spawn_timer = 4.0  # 4 seconds, or when player gets up from fade
        
        return True
    
    def get_collision_rect(self):
        """Return the base rectangle for collision"""
        return pygame.Rect(self.x, self.base_y, self.width, 20)
    
    def draw(self, screen, camera_x, camera_y, config):
        # Base
        base_rect = pygame.Rect(self.x - camera_x, self.y - camera_y - 20, self.width, 20)
        
        if config.ALPHA_TENT < 255:
            base_surface = pygame.Surface((self.width, 20), pygame.SRCALPHA)
            base_surface.fill((*config.COLOR_TENT_BASE, config.ALPHA_TENT))
            screen.blit(base_surface, base_rect.topleft)
        else:
            pygame.draw.rect(screen, config.COLOR_TENT_BASE, base_rect)
        
        # Tent triangle
        points = [
            (self.x - camera_x, self.y - camera_y - 20),
            (self.peak_x - camera_x, self.peak_y - camera_y),
            (self.right_x - camera_x, self.y - camera_y - 20)
        ]
        
        if config.ALPHA_TENT < 255:
            # Draw on temporary surface for alpha
            tent_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            local_points = [
                (0, self.height - 20),
                (self.width // 2, 0),
                (self.width, self.height - 20)
            ]
            pygame.draw.polygon(tent_surface, (*config.COLOR_TENT, config.ALPHA_TENT), local_points)
            pygame.draw.polygon(tent_surface, (*config.COLOR_TENT_OUTLINE, config.ALPHA_TENT), local_points, 3)
            screen.blit(tent_surface, (self.x - camera_x, self.peak_y - camera_y))
        else:
            pygame.draw.polygon(screen, config.COLOR_TENT, points)
            pygame.draw.polygon(screen, config.COLOR_TENT_OUTLINE, points, 3)

# ----------------------------
# ROCK (Small Sloped Polygon)
# ----------------------------
class Rock:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 160  # Increased from 100
        self.height = 128  # Increased from 80
        self.rect = pygame.Rect(x, y - self.height, self.width, self.height)
        self.collidable = False
        
        # Define triangle points for slope detection
        self.peak_x = x + self.width // 2
        self.peak_y = y - self.height
        self.left_x = x
        self.right_x = x + self.width
        self.base_y = y
    
    def is_player_on_rock(self, player):
        player_center_x = player.rect.centerx
        player_bottom = player.rect.bottom
        
        if player_center_x < self.left_x - 5 or player_center_x > self.right_x + 5:
            return False
        
        if player_bottom < self.peak_y - 10 or player_bottom > self.base_y + 15:
            return False
        
        rock_y = self.get_rock_y_at_x(player_center_x)
        
        return abs(player_bottom - rock_y) < 25 and player.y_momentum >= -2
    
    def get_collision_rect(self):
        """Return the base rectangle for collision"""
        return pygame.Rect(self.x, self.base_y - 10, self.width, 10)
    
    def get_rock_y_at_x(self, player_x):
        if player_x <= self.left_x:
            return self.base_y
        if player_x >= self.right_x:
            return self.base_y
        
        if player_x <= self.peak_x:
            slope_length = self.peak_x - self.left_x
            if slope_length == 0:
                return self.base_y
            progress = (player_x - self.left_x) / slope_length
            y_on_slope = self.base_y + (self.peak_y - self.base_y) * progress
        else:
            slope_length = self.right_x - self.peak_x
            if slope_length == 0:
                return self.base_y
            progress = (player_x - self.peak_x) / slope_length
            y_on_slope = self.peak_y + (self.base_y - self.peak_y) * progress
        
        return y_on_slope
    
    def handle_rock_collision(self, player):
        """Handle player on rock - place on surface and allow sliding"""
        if not self.is_player_on_rock(player):
            return False
        
        rock_y = self.get_rock_y_at_x(player.rect.centerx)
        player.rect.bottom = int(rock_y)
        player.y_momentum = 0
        player.on_ground = True
        
        # Gentle push away from peak to prevent getting stuck
        # Only push if we're near the peak
        distance_from_peak = abs(player.rect.centerx - self.peak_x)
        if distance_from_peak < 40:  # Only near peak
            if player.rect.centerx < self.peak_x:
                player.rect.x -= 1  # Gentle push left
            elif player.rect.centerx > self.peak_x:
                player.rect.x += 1  # Gentle push right
        
        return True
    
    def draw(self, screen, camera_x, camera_y, config):
        points = [
            (self.x - camera_x, self.base_y - camera_y),
            (self.peak_x - camera_x, self.peak_y - camera_y),
            (self.right_x - camera_x, self.base_y - camera_y)
        ]
        
        if config.ALPHA_ROCK < 255:
            # Draw on temporary surface for alpha
            rock_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            local_points = [
                (0, self.height),
                (self.width // 2, 0),
                (self.width, self.height)
            ]
            pygame.draw.polygon(rock_surface, (*config.COLOR_ROCK, config.ALPHA_ROCK), local_points)
            pygame.draw.polygon(rock_surface, (*config.COLOR_ROCK_OUTLINE, config.ALPHA_ROCK), local_points, 3)
            screen.blit(rock_surface, (self.x - camera_x, self.peak_y - camera_y))
        else:
            pygame.draw.polygon(screen, config.COLOR_ROCK, points)
            pygame.draw.polygon(screen, config.COLOR_ROCK_OUTLINE, points, 3)