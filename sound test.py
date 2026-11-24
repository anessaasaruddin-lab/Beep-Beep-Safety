import pygame
import time

pygame.init()
pygame.mixer.init()

print("Mixer initialized:", pygame.mixer.get_init())

sound = pygame.mixer.Sound("scene1_voice.wav")
print("Sound length:", sound.get_length())

sound.play()

time.sleep(5)
