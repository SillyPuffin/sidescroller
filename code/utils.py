from os import walk
import pygame
import time
pygame.init()

def load_folder(path,scale,convert_alpha = False,colour_key= None,_list=False):
    files = list(walk(path))
    names = files[0][2]
    if not _list:
        arg = {}
    else:
        arg = []
    for i in names:
        if convert_alpha:
            new_image = pygame.image.load(path +'/'+ i).convert_alpha()
        else:
            new_image = pygame.image.load(path +'/'+ i).convert()
        new_image = pygame.transform.scale(new_image,(new_image.get_width()*scale,new_image.get_height()*scale))
        if colour_key != None:
            new_image.set_colorkey(colour_key)
        name = i.split('.')[0]
        if not _list:
            arg[name] = new_image
        else:
            arg.append(new_image)

    return arg

def load_page(path,colour_key,size,scale,conver_al= False):
    page = pygame.image.load(path)
    if conver_al:
        page.convert_alpha()
    else:
        page.convert()

    half_size = (size[0]/2,size[1]/2)
    dct = {
    '1':clip_image((1,43),size,colour_key,page,scale),
    '2':clip_image((1,64),size,colour_key,page,scale),
    '4':clip_image((43,64),size,colour_key,page,scale),
    '3':clip_image((1,1),size,colour_key,page,scale),
    '13':clip_image((1,22),size,colour_key,page,scale),
    '24':clip_image((22,64),size,colour_key,page,scale),
    '0':clip_image((64,64),size,colour_key,page,scale),
    '23':clip_image((22,1),size,colour_key,page,scale),
    '34':clip_image((64,1),size,colour_key,page,scale),
    '14':clip_image((64,43),size,colour_key,page,scale),
    '12':clip_image((22,43),size,colour_key,page,scale),
    '1234':clip_image((43,22),size,colour_key,page,scale),
    '234':clip_image((43,1),size,colour_key,page,scale),
    '134':clip_image((64,22),size,colour_key,page,scale),
    '124':clip_image((43,43),size,colour_key,page,scale),
    '123':clip_image((22,22),size,colour_key,page,scale),
    '5':clip_image((1,86),size,colour_key,page,scale),
    '6':clip_image((22,86),size,colour_key,page,scale),
    '7':clip_image((43,86),size,colour_key,page,scale),
    '8':clip_image((64,86),size,colour_key,page,scale)
    }

    return dct

def clip_image(pos,size,colour_key,img,scale):
    clip = img.subsurface(((pos),(size)))
    clip.set_colorkey(colour_key)
    clip = pygame.transform.scale(clip,(clip.get_width()*scale,clip.get_height()*scale))
    return clip

def check_holding(key, level, current):
    holding = False
    if key not in level.keys_time:
        level.keys_time[key] = 0
    for event in level.keyed: 
        if event[0] == pygame.KEYDOWN and event[1] == key:
            level.keys_time[key] = time.time()
        if event[0] == pygame.KEYUP and event[1] == key:
            level.keys_time[key] = 0
    if level.keys_time[key] != 0:
        if current - level.keys_time[key]>= 0.5:
            holding = True

    return holding

# class Raycast:
#     def __init__(angle):
