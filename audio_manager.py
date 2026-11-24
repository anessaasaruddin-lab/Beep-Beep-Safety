import pygame

class AudioManager:
    def __init__(self):
        pygame.mixer.set_num_channels(8)
        self.ui_channel = pygame.mixer.Channel(7)

        self.next_sound = pygame.mixer.Sound("next_sound.wav")
        self.next_sound.set_volume(1.0)

        self.muted = False

    def play_next(self):
        if not self.muted:
            self.ui_channel.play(self.next_sound)

    def mute(self):
        self.muted = True
        pygame.mixer.music.set_volume(0)
        self.next_sound.set_volume(0)

    def unmute(self):
        self.muted = False
        pygame.mixer.music.set_volume(0.5)
        self.next_sound.set_volume(1.0)

    def toggle_mute(self):
        if self.muted:
            self.unmute()
        else:
            self.mute()
