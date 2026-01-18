# Assets/Animations.py
"""
Animation System
================
Handles all character and enemy animations with frame-based timing.

Features:
- Walking animations
- Idle animations
- Attack animations
- Enemy animations
- Smooth transitions between animation states
"""

import pygame


class Animation:
    """Single animation sequence"""
    def __init__(self, name, frames, duration_per_frame=0.1, loop=True):
        """
        Args:
            name: Animation name (e.g., "walk_right", "attack_neutral")
            frames: List of pygame.Surface objects or rects for each frame
            duration_per_frame: Time each frame is shown (seconds)
            loop: Whether animation loops
        """
        self.name = name
        self.frames = frames
        self.duration_per_frame = duration_per_frame
        self.loop = loop
        self.total_duration = len(frames) * duration_per_frame
        self.current_frame = 0
        self.elapsed_time = 0.0
        self.is_finished = False
    
    def update(self, dt):
        """Update animation frame based on delta time"""
        if self.is_finished and not self.loop:
            return
        
        self.elapsed_time += dt
        
        # Calculate current frame
        self.current_frame = int(self.elapsed_time / self.duration_per_frame)
        
        if self.current_frame >= len(self.frames):
            if self.loop:
                self.elapsed_time = 0.0
                self.current_frame = 0
            else:
                self.is_finished = True
                self.current_frame = len(self.frames) - 1
    
    def get_current_frame(self):
        """Get the current frame"""
        if self.current_frame < len(self.frames):
            return self.frames[self.current_frame]
        return self.frames[-1]
    
    def reset(self):
        """Reset animation to beginning"""
        self.current_frame = 0
        self.elapsed_time = 0.0
        self.is_finished = False


class AnimationController:
    """Manages animations for a character or entity"""
    def __init__(self):
        self.animations = {}  # Dict of animation_name -> Animation
        self.current_animation = None
        self.previous_animation = None
        self.transition_enabled = True
        self.transition_speed = 0.1  # Fade speed between animations
    
    def add_animation(self, animation):
        """Add an animation to the controller"""
        self.animations[animation.name] = animation
    
    def play(self, animation_name, force_restart=False):
        """Play an animation
        
        Args:
            animation_name: Name of animation to play
            force_restart: Force restart even if already playing
        """
        if animation_name not in self.animations:
            print(f"Warning: Animation '{animation_name}' not found")
            return False
        
        animation = self.animations[animation_name]
        
        # If already playing this animation and not forcing restart, skip
        if self.current_animation and self.current_animation.name == animation_name and not force_restart:
            return True
        
        # Store previous for transition
        self.previous_animation = self.current_animation
        
        # Reset and play new animation
        animation.reset()
        self.current_animation = animation
        
        return True
    
    def update(self, dt):
        """Update current animation"""
        if self.current_animation:
            self.current_animation.update(dt)
    
    def get_current_frame(self):
        """Get current animation frame"""
        if self.current_animation:
            return self.current_animation.get_current_frame()
        return None
    
    def is_animation_finished(self):
        """Check if current animation is finished"""
        if self.current_animation:
            return self.current_animation.is_finished
        return False


# =====================================================================
# ANIMATION DEFINITIONS - Add your animations here!
# =====================================================================

class PlayerAnimations:
    """All player character animations"""
    
    @staticmethod
    def create_placeholder_frames(width=64, height=64, color=(0, 255, 0)):
        """Create placeholder animation frames for testing"""
        frames = []
        for i in range(4):
            frame = pygame.Surface((width, height))
            frame.fill(color)
            # Draw frame number for testing
            font = pygame.font.Font(None, 24)
            text = font.render(str(i + 1), True, (255, 255, 255))
            frame.blit(text, (width // 2 - 6, height // 2 - 12))
            frames.append(frame)
        return frames
    
    @staticmethod
    def setup_animations(controller):
        """Setup all player animations
        
        Args:
            controller: AnimationController instance
        """
        # Placeholder animations (replace with actual sprite sheets)
        idle_frames = PlayerAnimations.create_placeholder_frames(color=(0, 255, 0))
        walk_frames = PlayerAnimations.create_placeholder_frames(color=(0, 200, 100))
        attack_frames = PlayerAnimations.create_placeholder_frames(color=(255, 0, 0))
        hit_frames = PlayerAnimations.create_placeholder_frames(color=(255, 100, 100))
        
        # Add animations
        controller.add_animation(Animation("idle", idle_frames, 0.15, loop=True))
        controller.add_animation(Animation("walk", walk_frames, 0.1, loop=True))
        controller.add_animation(Animation("walk_back", walk_frames, 0.12, loop=True))
        controller.add_animation(Animation("attack_neutral", attack_frames, 0.08, loop=False))
        controller.add_animation(Animation("attack_forward", attack_frames, 0.08, loop=False))
        controller.add_animation(Animation("attack_down", attack_frames, 0.08, loop=False))
        controller.add_animation(Animation("hit", hit_frames, 0.05, loop=False))
        controller.add_animation(Animation("block", idle_frames, 0.1, loop=True))


class EnemyAnimations:
    """All enemy animations"""
    
    @staticmethod
    def create_placeholder_frames(width=56, height=56, color=(255, 0, 0)):
        """Create placeholder enemy animation frames"""
        frames = []
        for i in range(3):
            frame = pygame.Surface((width, height))
            frame.fill(color)
            font = pygame.font.Font(None, 20)
            text = font.render(str(i + 1), True, (255, 255, 255))
            frame.blit(text, (width // 2 - 5, height // 2 - 10))
            frames.append(frame)
        return frames
    
    @staticmethod
    def setup_animations(controller, enemy_type="bandit"):
        """Setup enemy animations
        
        Args:
            controller: AnimationController instance
            enemy_type: Type of enemy (e.g., "bandit", "boss")
        """
        idle_frames = EnemyAnimations.create_placeholder_frames(color=(200, 50, 50))
        walk_frames = EnemyAnimations.create_placeholder_frames(color=(150, 0, 0))
        attack_frames = EnemyAnimations.create_placeholder_frames(color=(255, 100, 0))
        hit_frames = EnemyAnimations.create_placeholder_frames(color=(100, 0, 0))
        
        controller.add_animation(Animation("idle", idle_frames, 0.2, loop=True))
        controller.add_animation(Animation("walk", walk_frames, 0.12, loop=True))
        controller.add_animation(Animation("attack", attack_frames, 0.1, loop=False))
        controller.add_animation(Animation("hit", hit_frames, 0.06, loop=False))


# =====================================================================
# USAGE EXAMPLE
# =====================================================================
"""
In your Character class __init__:

    from Assets.Animations import AnimationController, PlayerAnimations
    
    self.animation_controller = AnimationController()
    PlayerAnimations.setup_animations(self.animation_controller)
    self.animation_controller.play("idle")

In your update loop:

    dt = clock.tick(60) / 1000.0  # Delta time in seconds
    self.animation_controller.update(dt)

In your draw loop:

    current_frame = self.animation_controller.get_current_frame()
    if current_frame:
        screen.blit(current_frame, self.rect.topleft)

"""
