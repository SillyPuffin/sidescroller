# import pygame
from utils import *
from stats import *

class Images:
    def __init__(self,scale):

        self.items = load_folder('../graphics/items',scale,False,(255,255,255))
        self.characters = load_folder('../graphics/characters',scale,False,(0,0,0))
        self.tiles = load_folder('../graphics/tiles',scale,False,(0,0,0))
        self.tile_sets = {
            'grass': load_page('../graphics/tiles/pages/grass_page.png',(160,160,160),(20,20),scale)
        }
        self.ui = load_folder('../graphics/ui',scale)
        self.background= {'clouds':{'1':pygame.Surface((35*scale,20*scale))}}
        self.background['clouds']['1'].fill((255,255,255))
        
        #self.players
        #self.enemies