import pygame

from config import *


class SoundManager:
    config = {
        'ping': 'ping.ogg',
    }
    current = ''
    for i in config.keys():
        config[i] = os.path.abspath(os.path.join(ASSETS, 'sounds', config[i]))
    # def __init__(self):
    #     self.config = {
    #         'select': 'select.wav',
    #     }
    #     self.current = ''
    init = False

    @classmethod
    def play(cls, sound):
        if not cls.init:
            return
        for i in range(8):
            if not pygame.mixer.Channel(i).get_busy():
                cls.current = sound
                pygame.mixer.Channel(i).play(pygame.mixer.Sound(cls.config[sound]))
                pygame.mixer.Channel(i).set_volume(0)
                return
        if sound == cls.current and pygame.mixer.music.get_busy():
            return
        cls.current = sound
        # pygame.mixer.music.play()
