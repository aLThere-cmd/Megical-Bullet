import json
import os
import pygame

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "audio": {
        "music_volume": 0.5,
        "sfx_volume": 0.7
    },
    "keybinds": {
        "up": pygame.K_w,
        "down": pygame.K_s,
        "left": pygame.K_a,
        "right": pygame.K_d,
        "shoot": pygame.K_j,
        "bomb": pygame.K_k,
        "focus": pygame.K_LSHIFT,
        "pause": pygame.K_ESCAPE
    },
    "resolution": {
        "width": 1280,
        "height": 720
    }
}

class SettingsManager:
    def __init__(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.load()

    def load(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for category in DEFAULT_SETTINGS:
                        if category in loaded:
                            self.settings[category].update(loaded[category])
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save(self):
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get_audio(self, key):
        return self.settings["audio"].get(key, DEFAULT_SETTINGS["audio"][key])

    def get_key(self, key):
        return self.settings["keybinds"].get(key, DEFAULT_SETTINGS["keybinds"][key])

    def get_resolution(self):
        return (self.settings["resolution"]["width"], self.settings["resolution"]["height"])

    def set_audio(self, key, value):
        self.settings["audio"][key] = value
        self.save()

    def set_key(self, key, value):
        self.settings["keybinds"][key] = value
        self.save()

    def set_resolution(self, width, height):
        self.settings["resolution"]["width"] = width
        self.settings["resolution"]["height"] = height
        self.save()

settings_manager = SettingsManager()
