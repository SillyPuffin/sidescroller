import pygame
import time
from debug import debug
from sys import exit
import settings as st
from pygame.locals import *

pygame.init()

real_size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
if real_size[1] < real_size[0]:
    scale = real_size[1] // st.display_size[1]
    if real_size[1] % st.display_size[1] == 0:
        exact = True
    else:
        exact = False
else:
    st.scale = real_size[0] // st.display_size[0]
    if real_size[0] % st.display_size[0] == 0:
        exact = True
    else:
        exact = False

if scale < 1:
    scale = 1
#getting mouse postition is broken on a donwscaled windowd

window_size = (st.display_size[0] * scale, st.display_size[1] *scale)
tile_size = 20 * scale
half_height = window_size[1]/2
half_width = window_size[0]/2

#writing statsaaaa
stats = open('stats.py','w')
lines = [
    'window_size = ' +str(window_size)+'\n',
    'tile_size = '+str(tile_size)+'\n',
    'half_height = '+str(half_height)+'\n',
    'half_width = '+str(half_width)+'\n',
    'scale = '+str(scale)+'\n'

]
stats.writelines(lines)
stats.close()
from level import Level
from images import Images


#0=  -1150 - scroll(-1150)
#0+scroll(-1150) = -1150

#0+scroll(-1150/5) = -230




class Main:
    def __init__(self):
        
        self.clock = pygame.time.Clock()
        if exact:
            self.display = pygame.display.set_mode((window_size),pygame.FULLSCREEN)
        else:
            self.display = pygame.display.set_mode((window_size))
        #preloaded variables
        images = Images(scale)
        self.old_time = time.time()
        game_map = self.load_map('..\levels\level_2')
        self.level1 = Level(game_map, self.display,images)
    
    def load_map(self,path):
        f = open(path + '.txt','r')
        data = f.read()
        f.close()
        data = data.split('\n')
        game_map = []
        for row in data:
            game_map.append(list(row))
        return game_map

    def run(self):
        while True:
            enter = False
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    exit()
                if event.type == KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        enter = True

            self.new_time = time.time()
            dt = (self.new_time - self.old_time)*60
            self.old_time = self.new_time

            self.clock.tick()
            
            # if enter:
            self.display.fill((0,0,0))
            self.level1.run(events,dt)
            fps = self.clock.get_fps()
            debug(int(fps))
            pygame.display.update()

if __name__ == '__main__':
    game = Main()
    game.run()
    
 
