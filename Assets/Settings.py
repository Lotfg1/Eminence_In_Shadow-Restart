# Assets/Settings.py
import json
import os

class Settings:
    def __init__(self, file_path="Assets/settings.json"):
        self.file_path = file_path
        self.audio = {
            "master_volume": 1.0,
            "music_volume": 1.0,
            "sfx_volume": 1.0
        }
        self.keybinds = {
            "MoveLeft": 97,
            "MoveRight": 100,
            "Jump": 119,
            "Interact": 101,
            "Pause": 27
        }
        self.display = {
            "zoom_level": 1.5
        }
        self.load()

    def load(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                data = json.load(f)
                self.audio.update(data.get("audio", {}))
                self.keybinds.update(data.get("keybinds", {}))
                self.display.update(data.get("display", {}))

    def save(self):
        data = {
            "audio": self.audio,
            "keybinds": self.keybinds,
            "display": self.display
        }
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

    def set_keybind(self, action, key):
        """Change a keybind in memory"""
        if action in self.keybinds:
            self.keybinds[action] = key
            self.save()

    def set_audio(self, setting, value):
        """Change an audio setting in memory"""
        if setting in self.audio:
            self.audio[setting] = max(0.0, min(1.0, value))
            self.save()
    
    def set_display(self, setting, value):
        """Change a display setting"""
        if setting in self.display:
            self.display[setting] = value
            self.save()