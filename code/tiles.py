import pygame

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, size, image,name,key,type='tile'):
        super().__init__()
        self.image = image
        self.type = type
        self.key = key
        self.name = name
        self.rect = pygame.Rect(0,0, size, size)
        self.rect.topleft = pos
        self.can_collide = True

    
