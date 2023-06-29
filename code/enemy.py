import pygame
import math
import time
from debug import debug
from stats import *

class Enemy(pygame.sprite.Sprite):
    def __init__(self,speed,pos,key):
        super().__init__()
        self.health = 100
        self.scale = scale
        self.unloaded = True

        #movement
        self.selected = False
        self.speed = speed
        self.acceleration = 0.4 * self.scale
        self.decceleration = 0.3 *self.scale
        self.jump_speed = -4.1 * self.scale
        self.momentum = pygame.math.Vector2()
        self.moving = False

        #rect
        self.size = (14 * self.scale, 28 * self.scale)
        self.rect = pygame.Rect((0,0),(self.size[0],self.size[1]))
        self.float_rect = pygame.math.Vector2()
        self.rect.midbottom = pos
        self.set_float_rect(3)

        self.pos = pos
        self.type = "entity"
        self.above_block = False

        #image
        self.image = pygame.Surface((14 * abs(self.scale),28 * abs(self.scale)))
        self.image.fill((255,255,255))

    def jump(self):
        self.momentum.y = self.jump_speed

    def reset_enemy(self,level):
        self.momentum.x = 0
        self.momentum.y = 0
        self.unloaded = True
        self.health = 100

    def check_groups(self, level):
        try:
            self.colliders.empty()
        except AttributeError:
            pass
        self.colliders = level.colliders.copy()
        self.colliders.remove(self)
        
        try:
            self.tiles.empty()
        except AttributeError:
            pass
        self.tiles = level.tiles.copy()
        
    def apply_gravity(self, dt):

        self.momentum.y += 0.2 * self.scale*dt

        if self.momentum.y > 4 * self.scale:
            self.momentum.y = 4 * self.scale
            
    def split_move(self, tsize, _speed):
        tilesize = tsize
        speed = _speed
        amount = int(abs(speed) // tilesize)
        extra = abs(speed) % tilesize
        to_add = 0
        if speed < 0:
            to_add = -tilesize
            extra = -extra
        if speed > 0:
            to_add = tilesize
            extra = extra
        return extra, to_add, amount

    def set_float_rect(self, index = None,value = 0):

        if index != None:
            if index == 0:
                self.float_rect.x = self.rect.centerx
            elif index == 1:
                self.float_rect.y = self.rect.centery
            else:
                self.float_rect.y = self.rect.centery
                self.float_rect.x = self.rect.centerx

        if value != 0:
            self.float_rect.x = value[0]
            self.float_rect.y = value[1]
            self.rect.center = self.float_rect

    def move(self,level, colliders,dt):

        #horizontal
        extra, to_add, amount = self.split_move(tile_size, self.momentum.x * dt)
        count = 1
        collided = False
        for i in range(amount + 1):
            if count < amount + 1:
                self.float_rect.x += to_add
            elif count == amount + 1:
                self.float_rect.x += extra
            count += 1
            self.rect.centerx = self.float_rect.x
            for sprite in colliders:
                if sprite.rect.colliderect(self.rect):
                    if self.momentum[0] > 0:
                        #right
                        self.rect.right = sprite.rect.left
                        self.set_float_rect(0)
                        self.momentum.x = 0
                        collided = True
                    elif self.momentum[0] < 0:
                        #left
                        self.rect.left = sprite.rect.right
                        self.set_float_rect(0)
                        self.momentum.x = 0
                        collided = True
            if collided:
                break

        #vertical
        self.above_block = False

        for sprite in colliders:
            if self.momentum.y > 0:
                if self.rect.move(0,1).colliderect(sprite):
                    self.momentum.y = 0
                    self.above_block = True

        if not self.above_block:
            self.apply_gravity(dt)

        extra, to_add, amount = self.split_move(tile_size, self.momentum.y * dt)
        count = 1
        collided = False
        for i in range(amount + 1):
            if count < amount + 1:
                self.float_rect.y += to_add
            elif count == amount + 1:
                self.float_rect.y += extra
            count += 1
            self.rect.centery = self.float_rect.y
            for sprite in colliders:
                if sprite.rect.colliderect(self.rect):
                    if self.momentum.y > 0:
                        #bottom
                        self.rect.bottom = sprite.rect.top
                        self.set_float_rect(1)
                        collided = True
                        self.momentum.y = 0       
                    elif self.momentum.y < 0:
                        #top
                        self.rect.top = sprite.rect.bottom
                        self.set_float_rect(1)
                        collided = True
                        self.momentum.y = 0
            if collided:
                break

    def update(self,level, dt):
        chunk_x = int(self.rect.centerx/(level.chunk_size*tile_size))
        chunk_y = int(self.rect.centery/(level.chunk_size*tile_size))
        key = str(chunk_x) + ',' + str(chunk_y)
        if key in level.loaded_chunks:
            self.unloaded = False
        else:
            self.unloaded = True
        if not self.unloaded:
            self.moving = False
            self.moving = True
            self.momentum.x = -self.speed

            if self.health <= 0:
                self.rect.midbottom = self.pos
                self.set_float_rect(3)
                self.reset_enemy(level)
            #decceleration
            if abs(self.momentum.x) > self.speed:
                if self.momentum.x < -self.speed:
                    if self.above_block:
                        self.momentum.x += self.decceleration * dt
                    else:
                        self.momentum.x += self.decceleration/20 * dt

                    if self.momentum.x > -self.speed:
                        self.momentum.x = -self.speed

                elif self.momentum.x > self.speed:
                    if self.above_block:
                        self.momentum.x -= self.decceleration * dt
                    else:
                        self.momentum.x -= self.decceleration/20 * dt
                    if self.momentum.x < self.speed:
                        self.momentum.x = self.speed

            if self.moving == False:
                if self.momentum.x < 0:
                    if self.above_block:
                        self.momentum.x += self.decceleration * dt
                    else:
                        self.momentum.x += self.decceleration/10 * dt

                    if self.momentum.x > 0:
                        self.momentum.x = 0

                elif self.momentum.x > 0:
                    if self.above_block:
                        self.momentum.x -= self.decceleration * dt
                    else:
                        self.momentum.x -= self.decceleration/10 * dt

                    if self.momentum.x < 0:
                        self.momentum.x = 0

            self.move(level, self.colliders ,dt)

            if self.rect.y > 500 * self.scale:
                self.rect.midbottom = self.pos
                self.set_float_rect(3)
                self.reset_enemy(level)

