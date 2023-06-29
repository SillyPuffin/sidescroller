import pygame
import math
from debug import debug
import time
from pygame.locals import *

class Bar(pygame.sprite.Sprite):
    def __init__(self,surface_data, centerw, centerh, colour,pos = None):
        super().__init__()
        if type(surface_data) == tuple:
            self.bar = pygame.Surface(surface_data[0])
            self.bar.fill((surface_data[1][0],surface_data[1][1],surface_data[1][2]))
            self.bar.set_alpha(surface_data[1][3])
            self.image = self.bar.copy()
        else:
            self.bar = surface_data
            self.image = surface_data
        self.width = self.bar.get_width()
        self.height = self.bar.get_height()
        self.colour = colour
        self.rect = self.bar.get_rect()
        self.midx = (self.width - centerw)/2
        self.midy = (self.height - centerh)/2
        self.centerw = centerw
        self.centerh = centerh
        if pos:
            self.rect.center = pos
        # self.value = 0
        # self.max = 0
        self.type = 'UI'

    def update(self,value = None,max = None):
        self.image = self.bar.copy()
        if value != None:
            self.value = value
        if max != None:
            self.max = max
        if self.value > self.max: 
            self.value = self.max

        pygame.draw.rect(self.image,self.colour,(self.midx,self.midy,self.centerw*(self.value/self.max),self.centerh))

class Text(pygame.sprite.Sprite):
    def __init__(self,character_dict,scale):
        super().__init__()
        self.chars = character_dict
        self.spacing = 1*scale
        self.type = 'UI'
        self.image = pygame.Surface((1,1))
        self.image.set_alpha(0)
        self.rect = self.image.get_rect()

    def create_image(self,words):
        width = 0
        height = 0
        for index, char in enumerate(words):
            if char =='/':
                char = 'slash'
            _width,_height = self.chars[char].get_size()
            width+= _width
            if _height > height:
                height = _height
        width += index * self.spacing
        surf = pygame.Surface((width,height)).convert()
        surf.fill((0,0,0)),surf.set_colorkey((0,0,0))
        surf.set_alpha(self.image.get_alpha())
        x_offset = 0
        for char in words:
            if char =='/':
                char = 'slash'
            surf.blit(self.chars[char],(x_offset, height - self.chars[char].get_height()))
            x_offset += self.chars[char].get_width() + self.spacing
        
        
        self.image = surf.copy()
        self.image.set_alpha(surf.get_alpha())
        self.rect = self.image.get_rect()

class Item_wheel:
    def __init__(self,pos,radius,scale):
        self.pos = pos
        self.radius = radius*scale
        self.spacing =  2*math.pi
        self.last_index = 0
        self.animate = False
        self.offset = 0
        self.scale = scale
        circle_d = (radius+15)*2*self.scale
        self.wheel_r = circle_d/2
        self.circle = pygame.Surface((circle_d,circle_d),pygame.SRCALPHA)
        pygame.draw.circle(self.circle,(60,60,60,128),(circle_d/2,circle_d/2),(circle_d/2))
        pygame.draw.circle(self.circle,(0,0,0),(circle_d/2,circle_d/2),(circle_d/2),2)

    def check_collision(self,mask):
        collide = False
        for index,item in enumerate(self.mask_list):
            angle = self.spacing*index
            width,height = item.get_size()
            imgy = self.radius*math.sin(angle) - height/2
            imgx = self.radius*math.cos(angle) - width /2
            y_offset = imgy + self.wheel_r
            x_offset = imgx + self.wheel_r
            if mask.overlap(item,(x_offset,y_offset)):
                collide = True
            
        return collide

    def change_items(self,item_list):
        self.new_circle = self.circle.copy()
        mask_surf = pygame.Surface(self.new_circle.get_size());mask_surf.fill((255,255,255)),mask_surf.set_colorkey((255,255,255))
        self.mask_list = [pygame.mask.from_surface(item.base_img) for item in item_list]
        self.img_list = [item.base_img for item in item_list]
        if self.mask_list:
            self.spacing = 2*math.pi/len(self.mask_list)

        collide = True
        if len(self.mask_list) > 1:
            for index,item in enumerate(self.mask_list):
                angle = self.spacing*index - (self.spacing)/2
                imgy = math.sin(angle)*self.wheel_r
                imgx = math.cos(angle)*self.wheel_r 
                center = (self.wheel_r,self.wheel_r)
                pygame.draw.line(self.new_circle,(0,0,0),center,(imgx+center[0],imgy+center[0]),2)
                pygame.draw.line(mask_surf,(0,0,0),center,(imgx+center[0],imgy+center[0]),2)

            mask = pygame.mask.from_surface(mask_surf)
            while collide == True:
                collide = self.check_collision(mask)
                if collide:
                    self.img_list = [pygame.transform.scale(img,(img.get_width()/2,img.get_height()/2)) for img in self.img_list]
                    self.mask_list = [pygame.mask.from_surface(img) for img in self.img_list]
            
        pygame.draw.circle(self.new_circle,(255,255,255,0),(self.wheel_r,self.wheel_r),(self.wheel_r/4))
        pygame.draw.circle(self.new_circle,(0,0,0),(self.wheel_r,self.wheel_r),(self.wheel_r/4),2)

    def update(self,equipped,surface,mouse,level,dt):
        surface.blit(self.new_circle,self.circle.get_rect(center = self.pos))
        vec_mouse = pygame.math.Vector2(mouse)
        vec_mouse += level.scroll
        drop = 'empty'
        x = mouse[0] - self.pos[0]
        y = self.pos[1] - mouse[1]
        polar_angle = math.atan2(y,x)
        sh = False
        if polar_angle <0:
            polar_angle = 2*math.pi + polar_angle
            sh = True
        for index,item in enumerate(self.mask_list):
            angle = self.spacing*index
            width,height = item.get_size()
            imgy = self.pos[1] - self.radius*math.sin(angle) - height/2
            imgx = self.pos[0] + self.radius*math.cos(angle) - width /2
            if index == equipped:
                surface.blit(self.img_list[index],(imgx,imgy))
            else:
                surface.blit(item.to_surface(unsetcolor=(100,100,100,0),setcolor=(90,90,90,200)),(imgx,imgy))
            #get in sector
            in_sec = False
            startangle = angle - self.spacing/2
            if startangle <0:
                startangle = 2*math.pi + startangle
            endangle = angle + self.spacing/2

            if endangle < startangle:
                if sh and polar_angle > endangle and polar_angle >= startangle:
                    in_sec = True
                elif not sh and polar_angle <= endangle and polar_angle < startangle:
                    in_sec = True

            if (endangle >= polar_angle and polar_angle >= startangle) or in_sec or len(self.mask_list) == 1:
                outlist = [(coord[0]+imgx,coord[1]+imgy) for coord in item.outline()]
                pygame.draw.lines(surface,(255,255,255),False,outlist,2)
                if (pygame.MOUSEBUTTONDOWN,1) in level.keyed:
                    level.selected_player.switch_weapon(level,index)

                if (pygame.MOUSEBUTTONDOWN,3) in level.keyed:
                    drop = index
                
        if drop != 'empty':
            player = level.selected_player
            gun = player.guns.sprites()[drop]
            if player.guns:
                gun.dropped = True
                level.items.add(gun)
                side = player.get_side(vec_mouse)
                if side == 'left':
                    gun.rect.midright = player.rect.midleft
                    gun.reset(level)
                    gun.momentum.x = player.momentum.x -(20*dt)
                else:
                    gun.rect.midleft = player.rect.midright
                    gun.reset(level)
                    gun.momentum.x = player.momentum.x + (20*dt)
                gun.momentum.y = player.momentum.y
                player.guns.remove(gun)
                level.item_wheel.change_items(player.guns)
                if gun == player.equipped:
                    if drop > len(player.guns.sprites())-1:
                        player.equip_index = len(player.guns.sprites())-1
                    if player.guns:
                        player.equipped = player.guns.sprites()[player.equip_index]
                else:
                    player.equip_index = player.guns.sprites().index(player.equipped)

        
    
