# Assets/Menus.py
import pygame
import os

# Global font helper: use Cavalhatriz if available
CAVALHATRIZ_PATH = os.path.join("Assets", "Fonts", "Cavalhatriz.ttf")

def get_font(size):
    return pygame.font.Font(CAVALHATRIZ_PATH if os.path.exists(CAVALHATRIZ_PATH) else None, size)

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
        self.options = ["Inventory", "Status", "Options", "Save Game", "Go Back", "Quit"]
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
                return "inventory"
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
    def __init__(self, font, player, settings=None):
        self.font = font
        self.player = player
        self.settings = settings
        self.title_font = get_font(48)
        self.small_font = get_font(20)
        # Only include stats that actually exist on the player to avoid KeyErrors
        candidate_stats = ["Max_Health", "M_Attack_Damage", "M_Defense", "Attack_Damage"]
        self.allocatable_stats = [s for s in candidate_stats if s in getattr(player, 'stats', {})]
        self.selected_stat = 0
        # Menu options at bottom
        self.menu_options = ["Equipment", "Close"]
        self.selected_option = -1  # -1 means we're on stats, 0+ means menu options
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "close"
            elif event.key == pygame.K_w:
                if self.selected_option == -1:
                    # Moving up in stats
                    self.selected_stat = (self.selected_stat - 1) % len(self.allocatable_stats)
                elif self.selected_option == 0:
                    # Move from first menu option back to stats
                    self.selected_option = -1
                    self.selected_stat = len(self.allocatable_stats) - 1
            elif event.key == pygame.K_s:
                if self.selected_option == -1:
                    if self.selected_stat == len(self.allocatable_stats) - 1:
                        # Move from last stat to menu options
                        self.selected_option = 0
                    else:
                        self.selected_stat = (self.selected_stat + 1) % len(self.allocatable_stats)
                else:
                    # Move between menu options
                    self.selected_option = min(self.selected_option + 1, len(self.menu_options) - 1)
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                # Allocate point to selected stat
                if self.selected_option == -1 and hasattr(self.player, 'free_stat_points') and self.player.free_stat_points > 0:
                    stat_name = self.allocatable_stats[self.selected_stat]
                    self.player.stats[stat_name] += 1
                    if stat_name == "Max_Health":
                        self.player.stats['Current_Health'] += 1
                    self.player.free_stat_points -= 1
            elif event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                # Select menu option
                if self.selected_option >= 0:
                    option = self.menu_options[self.selected_option]
                    if option == "Equipment":
                        return "equipment"
                    elif option == "Close":
                        return "close"
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
            
            stat_value = self.player.stats.get(stat_name, 0)
            display_name = stat_name.replace("_", " ")
            stat_text = f"{display_name}: {stat_value} +"
            text = self.font.render(stat_text, True, color)
            surf.blit(text, (50, y_offset + i * 35))
        
        # Menu options at bottom
        option_y = y_offset + len(self.allocatable_stats) * 35 + 20
        for i, opt in enumerate(self.menu_options):
            is_selected = (self.selected_option == i)
            color = (255, 215, 0) if is_selected else (200, 200, 200)
            opt_text = self.font.render(f"[ {opt} ]", True, color)
            surf.blit(opt_text, (50 + i * 150, option_y))
        
        # Instructions
        inst1 = self.small_font.render("W/S: Select | +: Allocate | Enter: Confirm", True, (150, 150, 150))
        inst2 = self.small_font.render("ESC: Close", True, (150, 150, 150))
        surf.blit(inst1, (width // 2 - inst1.get_width() // 2, height - 60))
        surf.blit(inst2, (width // 2 - inst2.get_width() // 2, height - 30))
        
        rect = surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(surf, rect.topleft)


# ----------------------------
# EQUIPMENT MENU
# ----------------------------
class EquipmentMenu:
    """Menu for equipping weapons, armor, and accessories"""
    
    # Equipment slot definitions
    SLOTS = ["Weapon", "Head", "Chest", "Legs", "Accessory 1", "Accessory 2"]
    
    def __init__(self, player, settings=None):
        self.player = player
        self.settings = settings
        self.font = get_font(24)
        self.title_font = get_font(36)
        self.small_font = get_font(18)
        
        # Currently selected slot
        self.selected_slot = 0
        # If True, we're picking an item to equip
        self.picking_item = False
        self.available_items = []
        self.selected_item = 0
        
        # Colors
        self.highlight_color = (255, 215, 0)
        self.normal_color = (200, 200, 200)
        self.equipped_color = (100, 255, 100)
    
    def get_equipment(self):
        """Get player's current equipment or return demo data"""
        if hasattr(self.player, 'equipment') and self.player.equipment:
            return self.player.equipment
        # Demo equipment
        return {
            "Weapon": {"name": "Iron Sword", "attack": 10},
            "Head": None,
            "Chest": {"name": "Leather Armor", "defense": 5},
            "Legs": None,
            "Accessory 1": None,
            "Accessory 2": None
        }
    
    def get_available_items_for_slot(self, slot):
        """Get items from inventory that can be equipped in this slot"""
        inv = getattr(self.player, 'inventory', None)
        if not inv:
            # Demo items
            if slot == "Weapon":
                return [("Iron Sword", {"attack": 10}), ("Steel Blade", {"attack": 15}), ("Wooden Staff", {"attack": 5, "magic": 10})]
            elif slot == "Head":
                return [("Leather Helm", {"defense": 3}), ("Iron Helm", {"defense": 6})]
            elif slot == "Chest":
                return [("Leather Armor", {"defense": 5}), ("Iron Chestplate", {"defense": 12})]
            elif slot == "Legs":
                return [("Leather Pants", {"defense": 2}), ("Iron Greaves", {"defense": 8})]
            else:
                return [("Ring of Strength", {"attack": 3}), ("Amulet of Defense", {"defense": 3})]
        # Real inventory lookup would go here
        return []
    
    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        
        if event.key == pygame.K_ESCAPE:
            if self.picking_item:
                self.picking_item = False
            else:
                return "close"
        
        if self.picking_item:
            # Navigating available items
            if event.key == pygame.K_w:
                self.selected_item = max(0, self.selected_item - 1)
            elif event.key == pygame.K_s:
                self.selected_item = min(len(self.available_items) - 1, self.selected_item + 1)
            elif event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                # Equip selected item
                if self.available_items:
                    item_name, item_stats = self.available_items[self.selected_item]
                    slot = self.SLOTS[self.selected_slot]
                    equipment = self.get_equipment()
                    equipment[slot] = {"name": item_name, **item_stats}
                    if hasattr(self.player, 'equipment'):
                        self.player.equipment = equipment
                self.picking_item = False
        else:
            # Navigating slots
            if event.key == pygame.K_w:
                self.selected_slot = (self.selected_slot - 1) % len(self.SLOTS)
            elif event.key == pygame.K_s:
                self.selected_slot = (self.selected_slot + 1) % len(self.SLOTS)
            elif event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                # Open item picker for this slot
                slot = self.SLOTS[self.selected_slot]
                self.available_items = self.get_available_items_for_slot(slot)
                self.selected_item = 0
                self.picking_item = True
            elif event.key == pygame.K_x:
                # Unequip current slot
                slot = self.SLOTS[self.selected_slot]
                equipment = self.get_equipment()
                equipment[slot] = None
                if hasattr(self.player, 'equipment'):
                    self.player.equipment = equipment
        
        return None
    
    def draw(self, screen):
        screen_w, screen_h = screen.get_size()
        width, height = 500, 450
        surf = pygame.Surface((width, height))
        surf.fill((40, 40, 50))
        pygame.draw.rect(surf, self.highlight_color, (0, 0, width, height), 3)
        
        # Title
        title = self.title_font.render("Equipment", True, self.highlight_color)
        surf.blit(title, (width // 2 - title.get_width() // 2, 15))
        
        equipment = self.get_equipment()
        
        # Draw slots
        y_start = 60
        row_height = 50
        for i, slot in enumerate(self.SLOTS):
            is_selected = (i == self.selected_slot and not self.picking_item)
            equipped = equipment.get(slot)
            
            # Slot name
            slot_color = self.highlight_color if is_selected else self.normal_color
            slot_text = self.font.render(f"{slot}:", True, slot_color)
            surf.blit(slot_text, (30, y_start + i * row_height))
            
            # Equipped item
            if equipped:
                item_name = equipped.get("name", "Unknown")
                item_text = self.font.render(item_name, True, self.equipped_color)
            else:
                item_text = self.font.render("(Empty)", True, (100, 100, 100))
            surf.blit(item_text, (180, y_start + i * row_height))
        
        # If picking item, draw item list overlay
        if self.picking_item:
            self._draw_item_picker(surf, width, height)
        
        # Instructions
        if self.picking_item:
            inst = self.small_font.render("W/S: Select | Enter: Equip | ESC: Cancel", True, (150, 150, 150))
        else:
            inst = self.small_font.render("W/S: Select | Enter: Change | X: Unequip | ESC: Close", True, (150, 150, 150))
        surf.blit(inst, (width // 2 - inst.get_width() // 2, height - 25))
        
        rect = surf.get_rect(center=(screen_w // 2, screen_h // 2))
        screen.blit(surf, rect.topleft)
    
    def _draw_item_picker(self, surf, width, height):
        """Draw the item selection overlay"""
        # Semi-transparent overlay on right side
        picker_w, picker_h = 220, 280
        picker_x = width - picker_w - 20
        picker_y = 50
        
        picker = pygame.Surface((picker_w, picker_h), pygame.SRCALPHA)
        picker.fill((30, 30, 40, 240))
        pygame.draw.rect(picker, self.highlight_color, (0, 0, picker_w, picker_h), 2)
        
        # Title
        slot = self.SLOTS[self.selected_slot]
        title = self.small_font.render(f"Select {slot}", True, self.highlight_color)
        picker.blit(title, (picker_w // 2 - title.get_width() // 2, 8))
        
        # Items
        if not self.available_items:
            empty = self.small_font.render("No items", True, (100, 100, 100))
            picker.blit(empty, (picker_w // 2 - empty.get_width() // 2, 50))
        else:
            for i, (item_name, item_stats) in enumerate(self.available_items):
                is_selected = (i == self.selected_item)
                color = self.highlight_color if is_selected else self.normal_color
                
                item_text = self.small_font.render(item_name, True, color)
                picker.blit(item_text, (15, 35 + i * 28))
                
                # Show stats
                stats_str = ", ".join(f"+{v} {k[:3]}" for k, v in item_stats.items())
                stats_text = self.small_font.render(stats_str, True, (150, 150, 150))
                picker.blit(stats_text, (15, 35 + i * 28 + 14))
        
        surf.blit(picker, (picker_x, picker_y))


# ----------------------------
# KEYBINDS MENU
# ----------------------------
class KeyBindsMenu:
    def __init__(self, font, settings):
        self.font = font
        self.settings = settings
        self.title_font = get_font(48)
        self.small_font = get_font(24)
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
        font = get_font(36)
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
# INVENTORY MENU (Categories + Items)
# ----------------------------
GRAPE_SODA_PATH = os.path.join("Assets", "Fonts", "GrapeSoda.ttf")
INVENTORY_BG_PATH = os.path.join("Assets", "Photos", "Inventory.png")
INV_CATEGORIES_PATH = os.path.join("Assets", "Photos", "Inv_categories.png")
INV_ITEMS_PATH = os.path.join("Assets", "Photos", "Inv_items.png")

def get_grape_font(size):
    """Get Grape Soda font if available, else fallback"""
    return pygame.font.Font(GRAPE_SODA_PATH if os.path.exists(GRAPE_SODA_PATH) else None, size)


class InventoryMenu:
    """
    Two-panel inventory menu:
    - Left panel: categories (using Inv_categories.png)
    - Right panel: items in selected category (using Inv_items.png)
    Text is overlaid on top of the images.
    """
    
    def __init__(self, player, settings=None):
        self.player = player
        self.settings = settings
        
        # Load panel images
        self.cat_image = None
        self.item_image = None
        if os.path.exists(INV_CATEGORIES_PATH):
            self.cat_image = pygame.image.load(INV_CATEGORIES_PATH).convert_alpha()
        if os.path.exists(INV_ITEMS_PATH):
            self.item_image = pygame.image.load(INV_ITEMS_PATH).convert_alpha()
        
        # Fonts (Grape Soda)
        self.font = get_grape_font(22)
        self.title_font = get_grape_font(26)
        self.small_font = get_grape_font(18)
        
        # Categories list
        self.categories = ["Weapons", "Armor", "Consumables", "Key Items", "Materials"]
        self.selected_category = 0
        self.category_scroll = 0
        
        # Items in current category
        self.selected_item = 0
        self.item_scroll = 0
        
        # Which panel is focused: "categories" or "items"
        self.focus = "categories"
        
        # Visible rows (based on image sizes)
        self.visible_cat_rows = 8
        self.visible_item_rows = 10
        
        # Colors
        self.highlight_color = (255, 255, 0)
        self.normal_color = (220, 220, 220)
        self.dim_color = (200, 200, 100)
    
    def get_inventory(self):
        """Get player inventory or return demo data"""
        if hasattr(self.player, 'inventory') and self.player.inventory:
            return self.player.inventory
        # Demo inventory structure: each item is (name, count, description, image_path)
        return {
            "Weapons": [
                ("Iron Sword", 1, "A sturdy sword made of iron. Good for beginners.", None),
                ("Wooden Staff", 1, "A magical staff carved from ancient oak.", None)
            ],
            "Armor": [
                ("Leather Helm", 1, "Basic head protection made from tanned leather.", None),
                ("Iron Chestplate", 1, "Heavy armor that provides excellent defense.", None),
                ("Boots", 2, "Comfortable boots for long journeys.", None)
            ],
            "Consumables": [
                ("Health Potion", 5, "Restores 50 HP when consumed.", None),
                ("Mana Potion", 3, "Restores 30 MP when consumed.", None),
                ("Antidote", 2, "Cures poison status effect.", None)
            ],
            "Key Items": [
                ("Old Key", 1, "A rusty key. Opens something somewhere...", None),
                ("Map Fragment", 3, "Part of a larger map. Collect all pieces.", None)
            ],
            "Materials": [
                ("Iron Ore", 12, "Raw iron ore. Can be smelted into ingots.", None),
                ("Wood", 25, "Basic crafting material from trees.", None),
                ("Cloth", 8, "Soft fabric for making clothes and bandages.", None),
                ("Monster Fang", 4, "Sharp fang from a defeated monster.", None)
            ]
        }
    
    def get_current_items(self):
        """Get items in currently selected category"""
        inv = self.get_inventory()
        cat = self.categories[self.selected_category]
        return inv.get(cat, [])
    
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
        
        if event.key == back:
            return "close"
        
        if self.focus == "categories":
            if event.key == up:
                self.selected_category = max(0, self.selected_category - 1)
                self._clamp_category_scroll()
                self.selected_item = 0
                self.item_scroll = 0
            elif event.key == down:
                self.selected_category = min(len(self.categories) - 1, self.selected_category + 1)
                self._clamp_category_scroll()
                self.selected_item = 0
                self.item_scroll = 0
            elif event.key == right or event.key in select_keys:
                items = self.get_current_items()
                if items:
                    self.focus = "items"
        
        elif self.focus == "items":
            items = self.get_current_items()
            if event.key == up:
                self.selected_item = max(0, self.selected_item - 1)
                self._clamp_item_scroll()
            elif event.key == down:
                self.selected_item = min(len(items) - 1, self.selected_item + 1)
                self._clamp_item_scroll()
            elif event.key == left:
                self.focus = "categories"
            elif event.key in select_keys:
                # Could trigger item use here
                pass
        
        return None
    
    def _clamp_category_scroll(self):
        """Keep category scroll in bounds"""
        if self.selected_category < self.category_scroll:
            self.category_scroll = self.selected_category
        elif self.selected_category >= self.category_scroll + self.visible_cat_rows:
            self.category_scroll = self.selected_category - self.visible_cat_rows + 1
        self.category_scroll = max(0, self.category_scroll)
    
    def _clamp_item_scroll(self):
        """Keep item scroll in bounds"""
        if self.selected_item < self.item_scroll:
            self.item_scroll = self.selected_item
        elif self.selected_item >= self.item_scroll + self.visible_item_rows:
            self.item_scroll = self.selected_item - self.visible_item_rows + 1
        self.item_scroll = max(0, self.item_scroll)
    
    def handle_scroll(self, event):
        """Handle mouse wheel scrolling"""
        if event.type == pygame.MOUSEWHEEL:
            if self.focus == "categories":
                self.category_scroll -= event.y
                self.category_scroll = max(0, min(self.category_scroll, max(0, len(self.categories) - self.visible_cat_rows)))
            else:
                items = self.get_current_items()
                self.item_scroll -= event.y
                self.item_scroll = max(0, min(self.item_scroll, max(0, len(items) - self.visible_item_rows)))
    
    def draw(self, screen):
        screen_w, screen_h = screen.get_size()
        
        # Calculate positions for panels
        gap = 20
        cat_w = self.cat_image.get_width() if self.cat_image else 200
        cat_h = self.cat_image.get_height() if self.cat_image else 350
        item_w = self.item_image.get_width() if self.item_image else 280
        item_h = self.item_image.get_height() if self.item_image else 420
        
        # Description panel dimensions
        desc_w = item_w
        desc_h = 140
        
        total_width = cat_w + gap + item_w
        start_x = (screen_w - total_width) // 2
        
        cat_x = start_x
        cat_y = (screen_h - cat_h) // 2 - 40  # Shift up to make room for description
        item_x = start_x + cat_w + gap
        item_y = cat_y
        desc_x = item_x
        desc_y = item_y + item_h + 10
        
        # Draw categories panel image
        if self.cat_image:
            screen.blit(self.cat_image, (cat_x, cat_y))
        
        # Draw items panel image
        if self.item_image:
            screen.blit(self.item_image, (item_x, item_y))
        
        # Draw description panel (rectangle with item image placeholder)
        self._draw_description_panel(screen, desc_x, desc_y, desc_w, desc_h)
        
        # Overlay category text on categories panel
        self._draw_categories_text(screen, cat_x, cat_y, cat_w, cat_h)
        
        # Overlay items text on items panel
        self._draw_items_text(screen, item_x, item_y, item_w, item_h)
        
        # Instructions
        inst = self.small_font.render("W/S: Navigate | A/D: Switch panels | ESC: Close", True, (220, 220, 220))
        screen.blit(inst, (screen_w // 2 - inst.get_width() // 2, screen_h - 20))
    
    def _draw_description_panel(self, screen, x, y, w, h):
        """Draw the description panel with item image and description"""
        # Panel background
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill((40, 30, 50, 230))
        pygame.draw.rect(panel, (180, 100, 220), (0, 0, w, h), 3, border_radius=8)
        
        items = self.get_current_items()
        
        if items and self.focus == "items":
            # Get current item data
            item_data = items[self.selected_item]
            item_name = item_data[0]
            item_count = item_data[1]
            item_desc = item_data[2] if len(item_data) > 2 else "No description available."
            item_image_path = item_data[3] if len(item_data) > 3 else None
            
            # Item image placeholder (left side)
            img_size = 80
            img_x = 15
            img_y = (h - img_size) // 2
            
            # Draw image placeholder box
            pygame.draw.rect(panel, (60, 50, 70), (img_x, img_y, img_size, img_size), border_radius=6)
            pygame.draw.rect(panel, (120, 80, 140), (img_x, img_y, img_size, img_size), 2, border_radius=6)
            
            # Try to load and draw item image
            if item_image_path and os.path.exists(item_image_path):
                try:
                    item_img = pygame.image.load(item_image_path).convert_alpha()
                    item_img = pygame.transform.smoothscale(item_img, (img_size - 8, img_size - 8))
                    panel.blit(item_img, (img_x + 4, img_y + 4))
                except:
                    # Draw placeholder icon
                    placeholder = self.small_font.render("?", True, (100, 100, 100))
                    panel.blit(placeholder, (img_x + img_size // 2 - placeholder.get_width() // 2, 
                                             img_y + img_size // 2 - placeholder.get_height() // 2))
            else:
                # Draw placeholder icon
                placeholder = self.font.render("?", True, (100, 100, 100))
                panel.blit(placeholder, (img_x + img_size // 2 - placeholder.get_width() // 2, 
                                         img_y + img_size // 2 - placeholder.get_height() // 2))
            
            # Item name and count (right of image)
            text_x = img_x + img_size + 15
            name_text = self.font.render(f"{item_name} x{item_count}", True, self.highlight_color)
            panel.blit(name_text, (text_x, 15))
            
            # Description text (word wrap)
            desc_text_x = text_x
            desc_text_y = 45
            max_text_width = w - text_x - 15
            
            # Simple word wrap
            words = item_desc.split(' ')
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                if self.small_font.size(test_line)[0] <= max_text_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())
            
            # Draw description lines
            for i, line in enumerate(lines[:3]):  # Max 3 lines
                desc_render = self.small_font.render(line, True, (200, 200, 200))
                panel.blit(desc_render, (desc_text_x, desc_text_y + i * 22))
        else:
            # No item selected
            hint = self.font.render("Select an item to see details", True, (100, 100, 100))
            panel.blit(hint, (w // 2 - hint.get_width() // 2, h // 2 - hint.get_height() // 2))
        
        screen.blit(panel, (x, y))
    
    def _draw_categories_text(self, screen, x, y, w, h):
        """Overlay category text on the categories panel image"""
        # Start text a bit inside the panel
        text_x = x + 20
        text_start_y = y + 40
        row_h = (h - 80) // self.visible_cat_rows
        
        for i in range(self.visible_cat_rows):
            idx = self.category_scroll + i
            if idx >= len(self.categories):
                break
            
            cat = self.categories[idx]
            is_selected = (idx == self.selected_category)
            
            if is_selected and self.focus == "categories":
                color = self.highlight_color
            elif is_selected:
                color = self.dim_color
            else:
                color = self.normal_color
            
            text = self.font.render(cat, True, color)
            text_y = text_start_y + i * row_h
            screen.blit(text, (text_x, text_y))
    
    def _draw_items_text(self, screen, x, y, w, h):
        """Overlay items text on the items panel image"""
        # Category title at top of panel
        cat_name = self.categories[self.selected_category]
        title = self.title_font.render(cat_name.upper(), True, self.highlight_color)
        screen.blit(title, (x + w // 2 - title.get_width() // 2, y + 10))
        
        items = self.get_current_items()
        text_x = x + 25
        text_start_y = y + 50
        row_h = (h - 100) // self.visible_item_rows
        
        if not items:
            empty = self.font.render("(Empty)", True, (150, 150, 150))
            screen.blit(empty, (x + w // 2 - empty.get_width() // 2, text_start_y + 30))
        else:
            for i in range(self.visible_item_rows):
                idx = self.item_scroll + i
                if idx >= len(items):
                    break
                
                item_data = items[idx]
                item_name = item_data[0]
                item_count = item_data[1]
                is_selected = (idx == self.selected_item)
                
                if is_selected and self.focus == "items":
                    color = self.highlight_color
                elif is_selected:
                    color = self.dim_color
                else:
                    color = self.normal_color
                
                display_text = f"{item_name} x{item_count}"
                text = self.font.render(display_text, True, color)
                text_y = text_start_y + i * row_h
                screen.blit(text, (text_x, text_y))


