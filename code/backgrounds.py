import pygame
from pygame.math import Vector2 as vec2
import random

class Cloud(pygame.sprite.Sprite):
    def __init__(self,image):
        super().__init__()
        self.image = image
        self.rect = pygame.Rect((0,0),(self.image.get_size()))
        self.pos = vec2(0,0)
        self.momentum = vec2(round(random.choice([0.4]),2),0)
        self.type = 'bg'

    def update(self,dt):
        self.pos += self.momentum * dt
        self.rect.topleft = self.pos