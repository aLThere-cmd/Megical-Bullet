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
        from config.manager import settings_manager
        self.sfx_volume = settings_manager.get_audio("sfx_volume")
        self.music_volume = settings_manager.get_audio("music_volume")
        pygame.mixer.music.set_volume(self.music_volume)

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
                    
                    # Apply master SFX volume
                    base_vol = self.sfx_volume
                    if name == "shoot":
                        sound.set_volume(base_vol * 0.4)
                    elif name == "graze":
                        sound.set_volume(base_vol * 0.6)
                    elif name == "bomb":
                        sound.set_volume(base_vol * 0.9)
                    else:
                        sound.set_volume(base_vol * 0.7)
                        
                    self.sounds[name] = sound
                except pygame.error as e:
                    print(f"Failed to load sound {name}: {e}")

    def play(self, name):
        """Play a sound by name."""
        if self.enabled and name in self.sounds:
            self.sounds[name].play()

    def play_music(self, track_name):
        """Play background music."""
        if not self.enabled:
            return
            
        music_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "music")
        if not os.path.exists(music_dir):
            os.makedirs(music_dir)
            
        path = os.path.join(music_dir, f"{track_name}.wav")
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(-1)
            except pygame.error as e:
                print(f"Failed to play music {track_name}: {e}")
        else:
            # Generate if missing (placeholder logic)
            print(f"Music track {track_name} not found. Generating...")
            try:
                from utils.sound_gen import generate_music
                generate_music(track_name, path)
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Failed to generate/play music: {e}")

    def update_volumes(self):
        """Reload volumes from settings."""
        from config.manager import settings_manager
        self.sfx_volume = settings_manager.get_audio("sfx_volume")
        self.music_volume = settings_manager.get_audio("music_volume")
        pygame.mixer.music.set_volume(self.music_volume)
        
        for name, sound in self.sounds.items():
            base_vol = self.sfx_volume
            if name == "shoot":
                sound.set_volume(base_vol * 0.4)
            elif name == "graze":
                sound.set_volume(base_vol * 0.6)
            elif name == "bomb":
                sound.set_volume(base_vol * 0.9)
            else:
                sound.set_volume(base_vol * 0.7)


# Global instance
audio = AudioSystem()
