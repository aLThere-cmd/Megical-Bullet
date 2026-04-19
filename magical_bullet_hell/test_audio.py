import pygame
import time

pygame.init()
pygame.mixer.init()

sound_path = 'assets/sounds/shoot.wav'
print("Loading:", sound_path)
try:
    sound = pygame.mixer.Sound(sound_path)
    print("Length:", sound.get_length())
    
    # max volume
    sound.set_volume(1.0)
    ch = sound.play()
    print("Playing...", ch)
    time.sleep(1)
    print("Done")
except Exception as e:
    print("Error:", e)
