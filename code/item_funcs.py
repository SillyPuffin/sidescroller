import pygame
from stats import *

def is_loaded(level,sprite):
    chunk_x = int(sprite.rect.centerx/(level.chunk_size*tile_size))
    chunk_y = int(sprite.rect.centery/(level.chunk_size*tile_size))
    key = str(chunk_x) + ',' + str(chunk_y)
    sprite.chunk = key
    if key in level.loaded_chunks:
        sprite.unloaded = False
    else:
        sprite.unloaded = True

def can_pickup(item,picker):
    pick_list = []
    for i in item:
        if picker.rect.colliderect(i.rect):
            pick_list.append(i)

    return pick_list

def move(level,sprite,dt):
    colliders = level.tiles
    #deceleration
    if sprite.momentum.x:
        if sprite.momentum.x < 0:
            sprite.momentum.x += 0.1*level.scale * dt
            if sprite.momentum.x > 0:
                sprite.momentum.x = 0

        elif sprite.momentum.x > 0:
            sprite.momentum.x -= 0.1*level.scale * dt
            if sprite.momentum.x < 0:
                sprite.momentum.x = 0
    
    #horizontal movement
    sprite.pos[0] += sprite.momentum.x * dt
    sprite.rect.centerx = sprite.pos[0]
    collist = [tile for tile in colliders if tile.rect.colliderect(sprite.rect)]
    for i in collist:
        if sprite.rect.colliderect(i.rect):
            if sprite.momentum.x > 0:
                sprite.rect.right = i.rect.left
                sprite.pos[0] = sprite.rect.centerx
                sprite.momentum.x = 0
            elif sprite.momentum.x < 0 :
                sprite.rect.left = i.rect.right
                sprite.pos[0] = sprite.rect.centerx
                sprite.momentum.x = 0

    #checking grounded
    sprite.above_block = False
    for tile in colliders:
        if sprite.rect.move(0,1).colliderect(tile):
            sprite.above_block = True          
    if not sprite.above_block:
        sprite.momentum.y += 0.15* level.scale*dt
        if sprite.momentum.y > 3 * level.scale:
            sprite.momentum.y = 3 * level.scale
    #vertical
    
    sprite.pos[1] += sprite.momentum.y*dt
    sprite.rect.centery = sprite.pos[1]
    collist = [tile for tile in colliders if tile.rect.colliderect(sprite.rect)]
    for i in collist:
        if sprite.momentum.y > 0:
            sprite.rect.bottom = i.rect.top
            sprite.pos[1] = sprite.rect.centery
            sprite.momentum.y = 0
        elif sprite.momentum.y < 0 :
            sprite.rect.top = i.rect.bottom
            sprite.pos[1] = sprite.rect.centery
            sprite.momentum.y = 0     
