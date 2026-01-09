# Assets/Interactables.py
import pygame
import time

class Interactable:
    def __init__(self, x, y, width, height, collidable=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.collidable = collidable

    def interact(self, player, game):
        pass

# ----------------------------
# BED
# ----------------------------
class Bed(Interactable):
    def __init__(self, x, y, width=64, height=32):
        super().__init__(x, y, width, height, collidable=True)

    def interact(self, player, game):
        self.use_bed(player, game)

    def use_bed(self, player, game):
        fade = pygame.Surface((game.screen.get_width(), game.screen.get_height()))
        fade.fill((0, 0, 0))
        # Fade out
        for alpha in range(0, 255, 10):
            fade.set_alpha(alpha)
            game.draw()
            game.screen.blit(fade, (0, 0))
            pygame.display.update()
            pygame.time.delay(30)
        # Show text
        text = game.font.render("The next day...", True, (255, 255, 255))
        for alpha in range(0, 255, 10):
            fade.set_alpha(255)
            game.draw()
            fade.fill((0,0,0))
            game.screen.blit(fade, (0,0))
            game.screen.blit(text, (game.screen.get_width()//2 - text.get_width()//2,
                                    game.screen.get_height()//2 - text.get_height()//2))
            pygame.display.update()
            pygame.time.delay(30)
        # Fade back in
        for alpha in range(255, 0, -10):
            fade.set_alpha(alpha)
            game.draw()
            game.screen.blit(fade, (0, 0))
            pygame.display.update()
            pygame.time.delay(30)

# ----------------------------
# MERCHANT
# ----------------------------
class Merchant(Interactable):
    def __init__(self, x, y, width=64, height=64):
        super().__init__(x, y, width, height, collidable=True)

    def interact(self, player, game):
        game.active_menu = "merchant"

# ----------------------------
# WALL
# ----------------------------
class Wall(Interactable):
    def __init__(self, x, y, width, height, destination_index=False):
        super().__init__(x, y, width, height, collidable=True)
        self.destination_index = destination_index

    def interact(self, player, game):
        if self.destination_index:
            game.open_travel_menu()

# ----------------------------
# TENT (Large Sloped Polygon)
# ----------------------------
class Tent:
    """A large tent structure with sloped sides"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 200  # Fixed size, larger
        self.height = 150  # Fixed size, larger
        self.rect = pygame.Rect(x, y - self.height, self.width, self.height)
        self.collidable = False  # Use custom collision for sliding
        self.color = (120, 80, 60)
        
        # Define triangle points for slope detection
        self.peak_x = x + self.width // 2
        self.peak_y = y - self.height
        self.left_x = x
        self.right_x = x + self.width
        self.base_y = y - 20
    
    def is_player_on_tent(self, player):
        """Check if player is on the tent surface"""
        player_center_x = player.rect.centerx
        player_bottom = player.rect.bottom
        
        # Check if player is within horizontal bounds
        if player_center_x < self.left_x - 5 or player_center_x > self.right_x + 5:
            return False
        
        # Check if player is within vertical bounds
        if player_bottom < self.peak_y - 10 or player_bottom > self.base_y + 15:
            return False
        
        # Get the tent slope y at player's x position
        tent_y = self.get_tent_y_at_x(player_center_x)
        
        # Check if player is near the tent surface and moving downward
        return abs(player_bottom - tent_y) < 25 and player.y_momentum >= -2
    
    def get_tent_y_at_x(self, player_x):
        """Calculate the y position on the tent at given x coordinate"""
        # Clamp to tent bounds
        if player_x <= self.left_x:
            return self.base_y
        if player_x >= self.right_x:
            return self.base_y
        
        if player_x <= self.peak_x:
            # Left slope
            slope_length = self.peak_x - self.left_x
            if slope_length == 0:
                return self.base_y
            progress = (player_x - self.left_x) / slope_length
            y_on_slope = self.base_y + (self.peak_y - self.base_y) * progress
        else:
            # Right slope
            slope_length = self.right_x - self.peak_x
            if slope_length == 0:
                return self.base_y
            progress = (player_x - self.peak_x) / slope_length
            y_on_slope = self.peak_y + (self.base_y - self.peak_y) * progress
        
        return y_on_slope
    
    def handle_tent_collision(self, player):
        """Make player slide off the tent"""
        if not self.is_player_on_tent(player):
            return False
        
        # Get current tent y at player position
        tent_y = self.get_tent_y_at_x(player.rect.centerx)
        
        # Position player on the tent
        player.rect.bottom = int(tent_y)
        player.y_momentum = 0  # Reset momentum to stick to surface
        
        # Determine which side of the peak the player is on and apply slide
        if player.rect.centerx < self.peak_x:
            # Left slope - slide left
            player.rect.x -= 3
        else:
            # Right slope - slide right
            player.rect.x += 3
        
        player.on_ground = False
        return True
    
    def get_collision_rect(self):
        """Return the base rectangle for collision"""
        return pygame.Rect(self.x, self.base_y, self.width, 20)
    
    def draw(self, screen, camera_x):
        """Draw the tent as a triangle on a rectangle base"""
        # Base
        base_rect = pygame.Rect(self.x - camera_x, self.y - 20, self.width, 20)
        pygame.draw.rect(screen, (90, 60, 40), base_rect)
        
        # Tent triangle
        points = [
            (self.x - camera_x, self.y - 20),
            (self.peak_x - camera_x, self.peak_y),
            (self.right_x - camera_x, self.y - 20)
        ]
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, (80, 50, 30), points, 3)

# ----------------------------
# ROCK (Small Sloped Polygon)
# ----------------------------
class Rock:
    """A small rock obstacle with sloped sides"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 100  # Fixed size, smaller
        self.height = 80   # Fixed size, smaller
        self.rect = pygame.Rect(x, y - self.height, self.width, self.height)
        self.collidable = False  # Use custom collision for sliding
        self.color = (70, 70, 70)
        
        # Define triangle points for slope detection
        self.peak_x = x + self.width // 2
        self.peak_y = y - self.height
        self.left_x = x
        self.right_x = x + self.width
        self.base_y = y
    
    def is_player_on_rock(self, player):
        """Check if player is on the rock surface"""
        player_center_x = player.rect.centerx
        player_bottom = player.rect.bottom
        
        # Check if player is within horizontal bounds
        if player_center_x < self.left_x - 5 or player_center_x > self.right_x + 5:
            return False
        
        # Check if player is within vertical bounds
        if player_bottom < self.peak_y - 10 or player_bottom > self.base_y + 15:
            return False
        
        # Get the rock slope y at player's x position
        rock_y = self.get_rock_y_at_x(player_center_x)
        
        # Check if player is near the rock surface and moving downward
        return abs(player_bottom - rock_y) < 25 and player.y_momentum >= -2
    
    def get_rock_y_at_x(self, player_x):
        """Calculate the y position on the rock at given x coordinate"""
        # Clamp to rock bounds
        if player_x <= self.left_x:
            return self.base_y
        if player_x >= self.right_x:
            return self.base_y
        
        if player_x <= self.peak_x:
            # Left slope
            slope_length = self.peak_x - self.left_x
            if slope_length == 0:
                return self.base_y
            progress = (player_x - self.left_x) / slope_length
            y_on_slope = self.base_y + (self.peak_y - self.base_y) * progress
        else:
            # Right slope
            slope_length = self.right_x - self.peak_x
            if slope_length == 0:
                return self.base_y
            progress = (player_x - self.peak_x) / slope_length
            y_on_slope = self.peak_y + (self.base_y - self.peak_y) * progress
        
        return y_on_slope
    
    def handle_rock_collision(self, player):
        """Make player slide off the rock"""
        if not self.is_player_on_rock(player):
            return False
        
        # Get current rock y at player position
        rock_y = self.get_rock_y_at_x(player.rect.centerx)
        
        # Position player on the rock
        player.rect.bottom = int(rock_y)
        player.y_momentum = 0  # Reset momentum to stick to surface
        
        # Determine which side of the peak the player is on and apply slide
        if player.rect.centerx < self.peak_x:
            # Left slope - slide left
            player.rect.x -= 3
        else:
            # Right slope - slide right
            player.rect.x += 3
        
        player.on_ground = False
        return True
    
    def draw(self, screen, camera_x):
        """Draw the rock as a triangle"""
        points = [
            (self.x - camera_x, self.base_y),
            (self.peak_x - camera_x, self.peak_y),
            (self.right_x - camera_x, self.base_y)
        ]
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, (50, 50, 50), points, 3)