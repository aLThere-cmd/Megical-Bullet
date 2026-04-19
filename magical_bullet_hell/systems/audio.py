"""
Audio system for managing and playing sound effects.
"""
import pygame
import os


class AudioSystem:
    """Manages game audio and sound effects."""

    def __init__(self):
        self.sounds = {}
        self.enabled = False
        self.volume = 1.0

    def init(self):
        """Initialize pygame mixer and load sounds."""
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except pygame.error:
                print("Warning: Audio could not be initialized.")
                return
        
        self.enabled = True

        # Load sounds
        sound_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sounds")
        
        # We assume utils.sound_gen has already been run or files exist
        if not os.path.exists(sound_dir):
            try:
                from utils.sound_gen import generate_all_sounds
                generate_all_sounds(sound_dir)
            except Exception as e:
                print(f"Failed to generate sounds: {e}")

        # Try to load each file
        sound_files = ["shoot", "explosion", "item", "graze", "bomb", "death"]
        for name in sound_files:
            path = os.path.join(sound_dir, f"{name}.wav")
            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(self.volume)
                    
                    # Special volumes
                    if name == "shoot":
                        sound.set_volume(self.volume * 0.5)
                    elif name == "graze":
                        sound.set_volume(self.volume * 0.8)
                    elif name == "bomb":
                        sound.set_volume(self.volume * 1.0)
                    else:
                        sound.set_volume(self.volume * 0.8)
                        
                    self.sounds[name] = sound
                except pygame.error as e:
                    print(f"Failed to load sound {name}: {e}")

    def play(self, name):
        """Play a sound by name."""
        if self.enabled and name in self.sounds:
            self.sounds[name].play()


# Global instance
audio = AudioSystem()
