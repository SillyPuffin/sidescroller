import pygame

class Chunk_image(pygame.sprite.Sprite):
    def __init__(self,pos,image, size,type):
        super().__init__()
        self.type = type
        self.rect = pygame.Rect(pos,(size,size))
        self.image = image


class Chunk(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.rect = pygame.Rect(pos,(size,size))
        self.dtiles = {}
        self.tiles = pygame.sprite.Group()
        self.grass = pygame.sprite.Group()
        self.tile_image = None
        self.ctiles = pygame.sprite.Group()

    def set_chunk_image(self,image, type):
        variable = Chunk_image(self.rect.topleft, image, self.rect.width, type)
        return variable