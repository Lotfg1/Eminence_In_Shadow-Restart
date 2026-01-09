# Assets/Menus.py
import pygame

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
        self.options = ["Start", "Options", "Quit"]
        self.selected = 0
        self.rect = pygame.Rect(0, 0, 400, 200)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_s:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key in (pygame.K_RETURN, pygame.K_e):
                return {"Start": "start", "Quit": "quit", "Options": "settings"}[self.options[self.selected]]
            elif event.key == pygame.K_ESCAPE:
                return "quit"  # Escape from start menu quits game

    def draw(self, screen):
        self.rect.center = (screen.get_width() // 2, screen.get_height() // 2)
        pygame.draw.rect(screen, (40, 40, 40), self.rect)
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = self.font.render(option, True, color)
            screen.blit(text, (self.rect.x + 50, self.rect.y + 40 + i * 40))

# ----------------------------
# PAUSE MENU (single rectangle at top)
# ----------------------------
class PauseMenu:
    def __init__(self, font, screen_width):
        self.font = font
        self.options = ["Inventory", "Status", "Options", "Combos", "Go Back", "Quit"]
        self.selected = 0
        self.width = screen_width - 40
        self.height = 40 + len(self.options) * 40
        self.surface = pygame.Surface((self.width, self.height))
        self.rect = self.surface.get_rect(topleft=(20, 20))  # Top of screen

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        if event.key == pygame.K_w:
            self.selected = (self.selected - 1) % len(self.options)
        elif event.key == pygame.K_s:
            self.selected = (self.selected + 1) % len(self.options)
        elif event.key in (pygame.K_RETURN, pygame.K_e):
            choice = self.options[self.selected]
            if choice == "Quit":
                return "quit"
            elif choice == "Go Back":
                return "go_back"  # Changed to trigger timer
            elif choice == "Options":
                return "settings"
            else:
                return choice
        elif event.key == pygame.K_ESCAPE:
            return "resume"  # Escape from pause menu resumes game

    def draw(self, screen):
        self.surface.fill((50, 50, 50))
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = self.font.render(option, True, color)
            self.surface.blit(text, (20, 20 + i * 40))
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
# SETTINGS MENU (integrates Settings class)
# ----------------------------
class SettingsMenu:
    def __init__(self, font, settings):
        self.font = font
        self.settings = settings
        self.options = ["Master Volume", "Music Volume", "SFX Volume",
                        "Move Left", "Move Right", "Jump", "Interact", "Attack", "Back"]
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
            elif choice in ["Master Volume", "Music Volume", "SFX Volume"]:
                key = choice.lower().replace(" ", "_")
                self.settings.set_audio(key, min(1.0, self.settings.audio[key] + 0.1))
            elif choice in ["Move Left", "Move Right", "Jump", "Interact", "Attack"]:
                # Start remapping
                self.waiting_for_key = choice.replace(" ", "")
        elif event.key == pygame.K_a:
            choice = self.options[self.selected]
            if choice in ["Master Volume", "Music Volume", "SFX Volume"]:
                key = choice.lower().replace(" ", "_")
                self.settings.set_audio(key, max(0.0, self.settings.audio[key] - 0.1))
        elif event.key == pygame.K_d:
            choice = self.options[self.selected]
            if choice in ["Master Volume", "Music Volume", "SFX Volume"]:
                key = choice.lower().replace(" ", "_")
                self.settings.set_audio(key, min(1.0, self.settings.audio[key] + 0.1))
        elif event.key == pygame.K_ESCAPE:
            return "close"  # Escape from settings returns to previous menu

        return None

    def draw(self, screen):
        width, height = 500, 500
        surf = pygame.Surface((width, height))
        surf.fill((40, 40, 40))

        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            display_text = option
            # Show audio levels
            if option in ["Master Volume", "Music Volume", "SFX Volume"]:
                key = option.lower().replace(" ", "_")
                display_text += f": {int(self.settings.audio[key]*100)}%"
            # Show keybinds
            elif option in ["Move Left", "Move Right", "Jump", "Interact", "Attack"]:
                display_text += f": {pygame.key.name(self.settings.keybinds[option.replace(' ', '')])}"
                if self.waiting_for_key == option.replace(" ", ""):
                    display_text = f"{option}: PRESS NEW KEY"

            text = self.font.render(display_text, True, color)
            surf.blit(text, (40, 40 + i * 40))

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