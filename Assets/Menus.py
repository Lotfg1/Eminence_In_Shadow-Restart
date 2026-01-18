# Assets/Menus.py
import pygame
import os

# ----------------------------
# BASE MENU
# ----------------------------
class BaseMenu:
    def __init__(self, options, font, settings=None, width=400, height=250):
        self.options = options
        self.selected = 0
        self.font = font
        self.settings = settings
        self.surface = pygame.Surface((width, height))
        self.rect = self.surface.get_rect()

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        kb = self.settings.keybinds if self.settings else {}
        up = kb.get("Jump", pygame.K_w)
        down = kb.get("MoveDown", pygame.K_s)
        select_keys = {kb.get("Interact", pygame.K_e), pygame.K_RETURN}
        back = kb.get("Pause", pygame.K_ESCAPE)
        if event.key == up:
            self.selected = (self.selected - 1) % len(self.options)
        elif event.key == down:
            self.selected = (self.selected + 1) % len(self.options)
        elif event.key in select_keys:
            return self.options[self.selected][1]
        elif event.key == back:
            return "close"

    def draw(self, screen):
        self.surface.fill((40, 40, 40))
        for i, (text, _) in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            txt = self.font.render(text, True, color)
            self.surface.blit(txt, (40, 40 + i * 40))
        screen.blit(self.surface, self.rect.topleft)

# ----------------------------
# START MENU
# ----------------------------
class StartMenu:
    def __init__(self, font, settings=None):
        self.font = font
        self.settings = settings
        # Check if save file exists
        save_exists = os.path.exists("save_data.json")
        if save_exists:
            self.options = ["Continue", "New Game", "Options", "Quit"]
        else:
            self.options = ["New Game", "Options", "Quit"]
        self.selected = 0
        
        # Try to load background and title images
        self.background_image = None
        self.title_image = None
        
        try:
            # Try to load background image
            bg_path = "Assets/Photos/Start_Menu_Background.png"
            self.background_image = pygame.image.load(bg_path).convert()
        except:
            # Use default background color if image not found
            self.background_image = None
        
        try:
            # Try to load title image
            title_path = "Assets/Photos/Start_Menu_Title.png"
            self.title_image = pygame.image.load(title_path).convert_alpha()
        except:
            # Use text title if image not found
            self.title_image = None

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            kb = self.settings.keybinds if self.settings else {}
            up = kb.get("Jump", pygame.K_w)
            down = kb.get("MoveDown", pygame.K_s)
            select_keys = {kb.get("Interact", pygame.K_e), pygame.K_RETURN}
            back = kb.get("Pause", pygame.K_ESCAPE)
            
            if event.key == up:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == down:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in select_keys:
                option = self.options[self.selected]
                if option == "Continue":
                    return "continue"
                elif option == "New Game":
                    return "start"
                elif option == "Options":
                    return "settings"
                elif option == "Quit":
                    return "quit"
            elif event.key == back:
                return "quit"  # Escape/Back quits game

    def draw(self, screen):
        # Draw start menu
        # Draw background
        if self.background_image:
            # Scale background to fit screen
            scaled_bg = pygame.transform.scale(self.background_image, (screen.get_width(), screen.get_height()))
            screen.blit(scaled_bg, (0, 0))
        else:
            # Default dark background
            screen.fill((20, 20, 40))
        
        # Draw title
        title_y = screen.get_height() // 4
        if self.title_image:
            # Center the title image
            title_x = (screen.get_width() - self.title_image.get_width()) // 2
            screen.blit(self.title_image, (title_x, title_y))
        else:
            # Default text title
            title_text = self.font.render("Eminence in Shadow: Restart", True, (255, 255, 255))
            title_x = (screen.get_width() - title_text.get_width()) // 2
            screen.blit(title_text, (title_x, title_y))
        
        # Draw menu options (centered below title)
        menu_start_y = screen.get_height() // 2 + 100
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = self.font.render(option, True, color)
            text_x = (screen.get_width() - text.get_width()) // 2
            text_y = menu_start_y + i * 50
            screen.blit(text, (text_x, text_y))

# ----------------------------
# PAUSE MENU (fills top of screen)
# ----------------------------
class PauseMenu:
    def __init__(self, font, screen_width, settings=None):
        self.font = font
        self.settings = settings
        self.options = ["Inventory", "Status", "Options", "Combos", "Save Game", "Go Back", "Quit"]
        self.selected = 0
        self.width = screen_width  # Full width
        self.height = 120  # Increased to fit 2 rows
        self.surface = pygame.Surface((self.width, self.height))
        self.rect = self.surface.get_rect(topleft=(0, 0))  # Top of screen, full width

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        kb = self.settings.keybinds if self.settings else {}
        left = kb.get("MoveLeft", pygame.K_a)
        right = kb.get("MoveRight", pygame.K_d)
        select_keys = {kb.get("Interact", pygame.K_e), pygame.K_RETURN, pygame.K_SPACE}
        back = kb.get("Pause", pygame.K_ESCAPE)
        # Left/right navigation
        if event.key == left:
            self.selected = (self.selected - 1) % len(self.options)
        elif event.key == right:
            self.selected = (self.selected + 1) % len(self.options)
        elif event.key in select_keys:
            choice = self.options[self.selected]
            if choice == "Quit":
                return "quit"
            elif choice == "Go Back":
                return "go_back"
            elif choice == "Options":
                return "settings"
            elif choice == "Save Game":
                return "save_game"
            elif choice == "Inventory":
                return "Combos"
            else:
                return choice
        elif event.key == back:
            return "resume"  # Back resumes game

    def draw(self, screen):
        self.surface.fill((50, 50, 50))
        
        # Title
        title = self.font.render("PAUSE", True, (255, 255, 255))
        self.surface.blit(title, (self.width // 2 - title.get_width() // 2, 5))
        
        # Options in 2 rows (max 4 per row)
        items_per_row = 4
        row_height = 45
        
        for i, option in enumerate(self.options):
            row = i // items_per_row
            col = i % items_per_row
            
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = self.font.render(option, True, color)
            
            # Calculate position: spread items evenly across row
            available_width = self.width - 20
            item_width = available_width / items_per_row
            x_pos = 10 + col * item_width + (item_width - text.get_width()) // 2
            y_pos = 30 + row * row_height
            
            self.surface.blit(text, (x_pos, y_pos))
        
        screen.blit(self.surface, self.rect.topleft)

# ----------------------------
# MERCHANT MENU
# ----------------------------
class MerchantMenu(BaseMenu):
    def __init__(self, font, settings=None):
        super().__init__([("Buy", "buy"), ("Sell", "sell"), ("Leave", "close")], font, settings)

# ----------------------------
# TRAVEL MENU
# ----------------------------
class TravelMenu(BaseMenu):
    def __init__(self, font, destinations, settings=None):
        options = [(name, idx) for name, idx in destinations]
        super().__init__(options, font, settings)

# ----------------------------
# SETTINGS MENU (with zoom control)
# ----------------------------
class SettingsMenu:
    def __init__(self, font, settings, config):
        self.font = font
        self.settings = settings
        self.config = config
        self.options = ["Master Volume", "Music Volume", "SFX Volume", "Zoom Level", "Keybinds", "Back"]
        self.selected = 0
        self.waiting_for_key = None  # Which action is waiting for keybind

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        kb = self.settings.keybinds if self.settings else {}
        up = kb.get("Jump", pygame.K_w)
        down = kb.get("MoveDown", pygame.K_s)
        left = kb.get("MoveLeft", pygame.K_a)
        right = kb.get("MoveRight", pygame.K_d)
        select_keys = {kb.get("Interact", pygame.K_e), pygame.K_RETURN}
        back = kb.get("Pause", pygame.K_ESCAPE)

        # If remapping a key, capture it
        if self.waiting_for_key:
            self.settings.set_keybind(self.waiting_for_key, event.key)
            self.waiting_for_key = None
            return None

        if event.key == up:
            self.selected = (self.selected - 1) % len(self.options)
        elif event.key == down:
            self.selected = (self.selected + 1) % len(self.options)
        elif event.key in select_keys:
            choice = self.options[self.selected]
            if choice == "Back":
                return "close"
            elif choice == "Keybinds":
                return "keybinds"
            elif choice in ["Master Volume", "Music Volume", "SFX Volume"]:
                key = choice.lower().replace(" ", "_")
                self.settings.set_audio(key, min(1.0, self.settings.audio[key] + 0.1))
                return "audio_changed"
            elif choice == "Zoom Level":
                # Cycle through zoom levels
                try:
                    current_zoom = self.settings.display.get("zoom_level", 1.5)
                    if current_zoom in self.config.AVAILABLE_ZOOM_LEVELS:
                        current_index = self.config.AVAILABLE_ZOOM_LEVELS.index(current_zoom)
                    else:
                        current_index = 0
                    next_index = (current_index + 1) % len(self.config.AVAILABLE_ZOOM_LEVELS)
                    self.settings.set_display("zoom_level", self.config.AVAILABLE_ZOOM_LEVELS[next_index])
                    return "zoom_changed"
                except Exception as e:
                    print(f"Zoom error: {e}")
            elif choice == "Keybinds":
                return "keybinds"
        elif event.key == left:
            choice = self.options[self.selected]
            if choice in ["Master Volume", "Music Volume", "SFX Volume"]:
                key = choice.lower().replace(" ", "_")
                self.settings.set_audio(key, max(0.0, self.settings.audio[key] - 0.1))
                return "audio_changed"
            elif choice == "Zoom Level":
                # Cycle backwards through zoom levels
                try:
                    current_zoom = self.settings.display.get("zoom_level", 1.5)
                    if current_zoom in self.config.AVAILABLE_ZOOM_LEVELS:
                        current_index = self.config.AVAILABLE_ZOOM_LEVELS.index(current_zoom)
                    else:
                        current_index = 0
                    next_index = (current_index - 1) % len(self.config.AVAILABLE_ZOOM_LEVELS)
                    self.settings.set_display("zoom_level", self.config.AVAILABLE_ZOOM_LEVELS[next_index])
                    return "zoom_changed"
                except Exception as e:
                    print(f"Zoom error: {e}")
        elif event.key == right:
            choice = self.options[self.selected]
            if choice in ["Master Volume", "Music Volume", "SFX Volume"]:
                key = choice.lower().replace(" ", "_")
                self.settings.set_audio(key, min(1.0, self.settings.audio[key] + 0.1))
                return "audio_changed"
            elif choice == "Zoom Level":
                # Cycle through zoom levels
                try:
                    current_zoom = self.settings.display.get("zoom_level", 1.5)
                    if current_zoom in self.config.AVAILABLE_ZOOM_LEVELS:
                        current_index = self.config.AVAILABLE_ZOOM_LEVELS.index(current_zoom)
                    else:
                        current_index = 0
                    next_index = (current_index + 1) % len(self.config.AVAILABLE_ZOOM_LEVELS)
                    self.settings.set_display("zoom_level", self.config.AVAILABLE_ZOOM_LEVELS[next_index])
                    return "zoom_changed"
                except Exception as e:
                    print(f"Zoom error: {e}")
        elif event.key == back:
            return "close"  # Back to previous menu

        return None

    def draw(self, screen):
        width, height = 600, 400
        surf = pygame.Surface((width, height))
        surf.fill((40, 40, 40))

        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            display_text = option
            # Show audio levels
            if option in ["Master Volume", "Music Volume", "SFX Volume"]:
                key = option.lower().replace(" ", "_")
                display_text += f": {int(self.settings.audio[key]*100)}%"
            # Show zoom level
            elif option == "Zoom Level":
                current_zoom = self.settings.display.get("zoom_level", 1.5)
                display_text += f": {current_zoom}x"

            text = self.font.render(display_text, True, color)
            surf.blit(text, (40, 40 + i * 40))
        
        # Add instructions
        instructions = self.font.render("Use A/D to change values", True, (150, 150, 150))
        surf.blit(instructions, (width // 2 - instructions.get_width() // 2, height - 40))

        rect = surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(surf, rect.topleft)

# ----------------------------
# STATUS MENU (displays character stats)
# ----------------------------
class StatusMenu:
    def __init__(self, font, player):
        self.font = font
        self.player = player
        self.title_font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 20)
        self.allocatable_stats = ["Max_Health", "Attack_Damage", "M_Attack_Damage", "Defense"]
        self.selected_stat = 0
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "close"
            elif event.key == pygame.K_w:
                self.selected_stat = (self.selected_stat - 1) % len(self.allocatable_stats)
            elif event.key == pygame.K_s:
                self.selected_stat = (self.selected_stat + 1) % len(self.allocatable_stats)
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                # Allocate point to selected stat
                if hasattr(self.player, 'free_stat_points') and self.player.free_stat_points > 0:
                    stat_name = self.allocatable_stats[self.selected_stat]
                    self.player.stats[stat_name] += 1
                    if stat_name == "Max_Health":
                        self.player.stats['Current_Health'] += 1
                    self.player.free_stat_points -= 1
        return None
    
    def draw(self, screen):
        width, height = 600, 550
        surf = pygame.Surface((width, height))
        surf.fill((40, 40, 40))
        
        # Title
        title = self.title_font.render("Character Stats", True, (255, 215, 0))
        surf.blit(title, (width // 2 - title.get_width() // 2, 20))
        
        # Free stat points
        free_points = getattr(self.player, 'free_stat_points', 0)
        points_text = self.font.render(f"Free Points: {free_points}", True, (255, 215, 0))
        surf.blit(points_text, (50, 60))
        
        # Display non-allocatable stats
        y_offset = 100
        health_text = self.font.render(f"Health: {self.player.stats['Current_Health']} / {self.player.stats['Max_Health']}", True, (100, 255, 100))
        mana_text = self.font.render(f"Mana: {self.player.stats['Current_Mana']} / {self.player.stats['Max_Mana']}", True, (100, 150, 255))
        skill_dmg_text = self.font.render(f"Skill Attack: {self.player.stats['Skill_Attack_Damage']}", True, (200, 200, 200))
        
        surf.blit(health_text, (50, y_offset))
        surf.blit(mana_text, (50, y_offset + 35))
        surf.blit(skill_dmg_text, (50, y_offset + 70))
        
        # Display allocatable stats (with selection highlight)
        y_offset += 120
        for i, stat_name in enumerate(self.allocatable_stats):
            is_selected = i == self.selected_stat
            color = (255, 215, 0) if is_selected else (200, 200, 200)
            
            stat_value = self.player.stats[stat_name]
            display_name = stat_name.replace("_", " ")
            stat_text = f"{display_name}: {stat_value} +"
            text = self.font.render(stat_text, True, color)
            surf.blit(text, (50, y_offset + i * 35))
        
        # Instructions
        inst1 = self.small_font.render("W/S: Select stat | +: Allocate point", True, (150, 150, 150))
        inst2 = self.small_font.render("ESC: Close", True, (150, 150, 150))
        surf.blit(inst1, (width // 2 - inst1.get_width() // 2, height - 60))
        surf.blit(inst2, (width // 2 - inst2.get_width() // 2, height - 30))
        
        rect = surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(surf, rect.topleft)

# ----------------------------
# KEYBINDS MENU
# ----------------------------
class KeyBindsMenu:
    def __init__(self, font, settings):
        self.font = font
        self.settings = settings
        self.title_font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 24)
        # Movement controls
        self.movement_actions = ["MoveLeft", "MoveRight", "Jump", "MoveDown", "Interact", "Attack", "Block", "Pause"]
        self.keybind_actions = self.movement_actions
        self.selected = 0
        self.waiting_for_key = None
        self.action_labels = {
            "MoveLeft": "Move Left",
            "MoveRight": "Move Right",
            "Jump": "Jump",
            "MoveDown": "Move Down (Down Attack)",
            "Interact": "Interact",
            "Attack": "Attack (Normal)",
            "Block": "Block/Counter (F)",
            "Pause": "Pause Menu",
        }

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        # If waiting for a new key, capture it
        if self.waiting_for_key:
            self.settings.set_keybind(self.waiting_for_key, event.key)
            self.waiting_for_key = None
            return None

        if event.key == pygame.K_w:
            self.selected = (self.selected - 1) % len(self.keybind_actions)
        elif event.key == pygame.K_s:
            self.selected = (self.selected + 1) % len(self.keybind_actions)
        elif event.key == pygame.K_RETURN or event.key == pygame.K_e:
            current_action = self.keybind_actions[self.selected]
            self.waiting_for_key = current_action
        elif event.key == pygame.K_ESCAPE:
            return "close"

        return None

    def _get_current_actions_count(self):
        return len(self.keybind_actions)

    def _get_current_action(self):
        return self.keybind_actions[self.selected]

    def _get_current_actions(self):
        return self.keybind_actions

    def draw(self, screen):
        width, height = 600, 550
        surf = pygame.Surface((width, height))
        surf.fill((40, 40, 40))

        # Title
        title = self.title_font.render("Keybinds", True, (255, 215, 0))
        surf.blit(title, (width // 2 - title.get_width() // 2, 20))

        # Keybinds list
        y_offset = 100
        for i, action in enumerate(self.keybind_actions):
            color = (255, 215, 0) if i == self.selected else (255, 255, 255)
            
            label = self.action_labels.get(action, action)
            current_key = pygame.key.name(self.settings.keybinds[action])
            
            if self.waiting_for_key == action:
                display_text = f"{label}: PRESS NEW KEY..."
                color = (255, 100, 100)
            else:
                display_text = f"{label}: {current_key.upper()}"

            text = self.font.render(display_text, True, color)
            surf.blit(text, (60, y_offset + i * 50))

        # Instructions
        instructions_y = height - 80
        inst1 = self.small_font.render("W/S: Navigate  |  E/Enter: Rebind", True, (200, 200, 200))
        inst2 = self.small_font.render("ESC: Back", True, (200, 200, 200))
        surf.blit(inst1, (width // 2 - inst1.get_width() // 2, instructions_y))
        surf.blit(inst2, (width // 2 - inst2.get_width() // 2, instructions_y + 30))

        rect = surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(surf, rect.topleft)


"""



Jamil 














"""
class ScrollableLayout:
    def __init__(self):
        # Default scroll state
        self.scroll_offset = 0
        self.scroll_speed = 20
        self.max_scroll = 850  # How far down you can scroll

    # Backwards-compatible init (if called elsewhere)
    def init(self):
        self.__init__()

    def handle_scroll(self, event):
        """Handle mouse wheel scrolling"""
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * self.scroll_speed
            # Clamp scroll offset
            self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

    def handle_input(self, event):
        """Allow menu handler to process scroll/escape."""
        self.handle_scroll(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "close"
        return None

    def draw(self, screen):
        
        # Define colors
        BLACK = (0, 0, 0)
        GREY = (75, 75, 85)
        DARK_GREY = (90, 92, 99)
        PURPLE = (63, 48, 75)
        WHITE = (255, 255, 255)
        SCREEN_WIDTH = screen.get_width()
        SCREEN_HEIGHT = screen.get_height()

        # Calculate center offset (shifted left)
        center_x = SCREEN_WIDTH // 2 - 180

        # Fill background with black
        screen.fill(BLACK)

        # Apply scroll offset to y positions
        y_offset = -self.scroll_offset

        # Top grey instruction box
        box_width = 586
        box_x = center_x - box_width // 2
        pygame.draw.rect(screen, DARK_GREY, (box_x, 76 + y_offset, box_width, 60))

        # Add "Instructions" text to top box
        font = pygame.font.Font(None, 36)
        text = font.render("Instructions", True, WHITE)
        text_rect = text.get_rect(center=(center_x, 106 + y_offset))
        screen.blit(text, text_rect)

        # First purple game area
        purple_width = 712
        purple_x = center_x - purple_width // 2
        pygame.draw.rect(screen, PURPLE, (purple_x, 172 + y_offset, purple_width, 205))

        # Middle grey title box (separated from first purple box)
        divider_width = 588
        divider_x = center_x - divider_width // 2
        pygame.draw.rect(screen, GREY, (divider_x, 407 + y_offset, divider_width, 60))

    # Second purple game area
        pygame.draw.rect(screen, PURPLE, (purple_x, 497 + y_offset, purple_width, 268))

    # === SECOND SET OF BOXES (below the first set) ===
        second_set_offset = 850  # Distance between sets

    # Second instruction box
        pygame.draw.rect(screen, DARK_GREY, (box_x, 76 + y_offset + second_set_offset, box_width, 60))
        text2 = font.render("Instructions", True, WHITE)
        text_rect2 = text2.get_rect(center=(center_x, 106 + y_offset + second_set_offset))
        screen.blit(text2, text_rect2)

    # Third purple area
        pygame.draw.rect(screen, PURPLE, (purple_x, 172 + y_offset + second_set_offset, purple_width, 205))

    # Second middle grey title box (separated)
        pygame.draw.rect(screen, GREY, (divider_x, 407 + y_offset + second_set_offset, divider_width, 60))

    # Fourth purple area
        pygame.draw.rect(screen, PURPLE, (purple_x, 497 + y_offset + second_set_offset, purple_width, 268))


# ----------------------------
# COMBOS MENU (uses ScrollableLayout)
# ----------------------------
class CombosMenu:
    def __init__(self, font, combo_system=None):
        self.font = font
        self.combo_system = combo_system
        self.layout = ScrollableLayout()
        # Ensure scroll state is initialized
        if hasattr(self.layout, "init"):
            self.layout.init()

    def handle_input(self, event):
        # Allow mouse wheel scrolling
        if hasattr(self.layout, "handle_scroll"):
            self.layout.handle_scroll(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "close"
        return None

    def draw(self, screen):
        # Use the existing ScrollableLayout rendering
        if hasattr(self.layout, "draw"):
            self.layout.draw(screen)
        # Simple instruction footer
        instructions = self.font.render("ESC: Back", True, (200, 200, 200))
        screen.blit(instructions, (screen.get_width() // 2 - instructions.get_width() // 2, screen.get_height() - 40))


