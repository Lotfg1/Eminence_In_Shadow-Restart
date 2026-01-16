# Assets/Menus.py
import pygame
import os

# ----------------------------
# BASE MENU
# ----------------------------
class BaseMenu:
    def __init__(self, options, font, width=400, height=250):
        self.options = options
        self.selected = 0
        self.font = font
        self.surface = pygame.Surface((width, height))
        self.rect = self.surface.get_rect()

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        if event.key == pygame.K_w:
            self.selected = (self.selected - 1) % len(self.options)
        elif event.key == pygame.K_s:
            self.selected = (self.selected + 1) % len(self.options)
        elif event.key in (pygame.K_RETURN, pygame.K_e):
            return self.options[self.selected][1]
        elif event.key == pygame.K_ESCAPE:
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
    def __init__(self, font):
        self.font = font
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
            if event.key == pygame.K_w:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_s:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_e):
                option = self.options[self.selected]
                if option == "Continue":
                    return "continue"
                elif option == "New Game":
                    return "start"
                elif option == "Options":
                    return "settings"
                elif option == "Quit":
                    return "quit"
            elif event.key == pygame.K_ESCAPE:
                return "quit"  # Escape from start menu quits game

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
    def __init__(self, font, screen_width):
        self.font = font
        self.options = ["Inventory", "Status", "Options", "Combos", "Save Game", "Go Back", "Quit"]
        self.selected = 0
        self.width = screen_width  # Full width
        self.height = 120  # Increased to fit 2 rows
        self.surface = pygame.Surface((self.width, self.height))
        self.rect = self.surface.get_rect(topleft=(0, 0))  # Top of screen, full width

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        # Use A and D for left/right navigation
        if event.key == pygame.K_a:
            self.selected = (self.selected - 1) % len(self.options)
        elif event.key == pygame.K_d:
            self.selected = (self.selected + 1) % len(self.options)
        elif event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
            choice = self.options[self.selected]
            if choice == "Quit":
                return "quit"
            elif choice == "Go Back":
                return "go_back"
            elif choice == "Options":
                return "settings"
            elif choice == "Save Game":
                return "save_game"
            else:
                return choice
        elif event.key == pygame.K_ESCAPE:
            return "resume"  # Escape from pause menu resumes game

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
    def __init__(self, font):
        super().__init__([("Buy", "buy"), ("Sell", "sell"), ("Leave", "close")], font)

# ----------------------------
# TRAVEL MENU
# ----------------------------
class TravelMenu(BaseMenu):
    def __init__(self, font, destinations):
        options = [(name, idx) for name, idx in destinations]
        super().__init__(options, font)

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

        # If remapping a key, capture it
        if self.waiting_for_key:
            self.settings.set_keybind(self.waiting_for_key, event.key)
            self.waiting_for_key = None
            return None

        if event.key == pygame.K_w:
            self.selected = (self.selected - 1) % len(self.options)
        elif event.key == pygame.K_s:
            self.selected = (self.selected + 1) % len(self.options)
        elif event.key == pygame.K_RETURN or event.key == pygame.K_e:
            choice = self.options[self.selected]
            if choice == "Back":
                return "close"
            elif choice == "Keybinds":
                return "keybinds"
            elif choice in ["Master Volume", "Music Volume", "SFX Volume"]:
                key = choice.lower().replace(" ", "_")
                self.settings.set_audio(key, min(1.0, self.settings.audio[key] + 0.1))
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
        elif event.key == pygame.K_a:
            choice = self.options[self.selected]
            if choice in ["Master Volume", "Music Volume", "SFX Volume"]:
                key = choice.lower().replace(" ", "_")
                self.settings.set_audio(key, max(0.0, self.settings.audio[key] - 0.1))
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
        elif event.key == pygame.K_d:
            choice = self.options[self.selected]
            if choice in ["Master Volume", "Music Volume", "SFX Volume"]:
                key = choice.lower().replace(" ", "_")
                self.settings.set_audio(key, min(1.0, self.settings.audio[key] + 0.1))
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
        elif event.key == pygame.K_ESCAPE:
            return "close"  # Escape from settings returns to previous menu

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
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "close"
        return None
    
    def draw(self, screen):
        width, height = 600, 500
        surf = pygame.Surface((width, height))
        surf.fill((40, 40, 40))
        
        # Title
        title = self.title_font.render("Character Stats", True, (255, 215, 0))
        surf.blit(title, (width // 2 - title.get_width() // 2, 20))
        
        # Stats
        y_offset = 80
        stats_display = [
            f"Health: {self.player.stats['Current_Health']} / {self.player.stats['Max_Health']}",
            f"Mana: {self.player.stats['Current_Mana']} / {self.player.stats['Max_Mana']}",
            "",
            f"Attack Damage: {self.player.stats['Attack_Damage']}",
            f"Magic Attack Damage: {self.player.stats['M_Attack_Damage']}",
            f"Skill Attack Damage: {self.player.stats['Skill_Attack_Damage']}",
            "",
            f"Defense: {self.player.stats['Defense']}",
            f"Magic Defense: {self.player.stats['M_Defense']}"
        ]
        
        for i, stat_text in enumerate(stats_display):
            if stat_text:  # Skip empty strings
                color = (255, 255, 255)
                # Color code health and mana
                if "Health:" in stat_text:
                    health_percent = self.player.stats['Current_Health'] / self.player.stats['Max_Health']
                    if health_percent > 0.5:
                        color = (0, 255, 0)  # Green
                    elif health_percent > 0.25:
                        color = (255, 255, 0)  # Yellow
                    else:
                        color = (255, 0, 0)  # Red
                elif "Mana:" in stat_text:
                    color = (100, 150, 255)  # Blue
                
                text = self.font.render(stat_text, True, color)
                surf.blit(text, (50, y_offset + i * 35))
        
        # Instructions
        instructions = self.font.render("Press ESC to close", True, (200, 200, 200))
        surf.blit(instructions, (width // 2 - instructions.get_width() // 2, height - 40))
        
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