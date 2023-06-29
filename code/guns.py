import pygame
import math
import time
import random
import item_funcs as itf
from bullets import Bullet

class Gun(pygame.sprite.Sprite):
    def __init__(self, image,bimage,pos,handle, shoot_point,rate_of_fire, inaccuracy,mag_size,reload_speed,shots,chamber_size,chamber_speed, ammo_type,bullet_mat,kwargs={}):
        super().__init__()
        self.shoot_time = 0
        self.shot = False
        self.reload_time = 0
        self.drum_time = 0
        self.kwargs = kwargs
        self.mag_size = mag_size
        self.bullet_mat = bullet_mat
        self.chamber_speed= chamber_speed
        self._reload = False
        if mag_size:
            self.mag = self.mag_size-chamber_size
        else:
            self.mag = 0
        self.chamber_size = chamber_size
        self.chamber = chamber_size
        self.breload_speed = reload_speed
        self.reload_speed = reload_speed
        self.loaded = False
        self.timer = 0
        self.dropped = True
        self.momentum = pygame.math.Vector2()
        self.type = 'item'
        self.name = 'gun'
        self.shots = shots
        self.ammo_type = ammo_type
        self.flip = False
        self.base_handle = handle
        self.base_shoot_point = shoot_point
        self.accmax = inaccuracy
        self.acc = 0
        self.rateof = rate_of_fire
        self.base_img = image.copy()
        self.flipped = image
        self.image = image
        self.end = False
        self.b_image = bimage
        self.drum = True
        self.base_rect = self.image.get_rect(midbottom = pos)
        self.rect = self.image.get_rect(midbottom = pos)
        self.pos = pygame.math.Vector2(self.rect.center)
        self.need_chamber = False
        self.chamber_timer = 0

    def rotate(self,pos, originPos,barrel, image, angle):
        image_rect = image.get_rect(topleft = (pos[0]- originPos[0],pos[1] - originPos[1]))
        ptc = pygame.math.Vector2(pos[0] - image_rect.center[0], pos[1] - image_rect.center[1])
        ptb = pygame.math.Vector2(barrel[0] -originPos[0],barrel[1]- originPos[1])

        rptc = ptc.rotate(-angle)
        rptb = ptb.rotate(-angle)

        rc = (pos[0]-rptc[0],pos[1] - rptc[1])
        muzzle = (pos[0]+rptb[0],pos[1] + rptb[1])

        new_image = pygame.transform.rotate(image, angle)
        rorect = new_image.get_rect(center = rc)

        return new_image, rorect,muzzle
    
    def reset(self,level):
        if self.flip:
            self.image = pygame.transform.flip(self.base_img,True,False)
        else:
            self.image = self.base_img
        self.rect = self.image.get_rect(center = self.rect.center)
        self.pos = pygame.math.Vector2(self.rect.midbottom)

        self.chamber_timer = 0
        if self._reload:
            self._reload = False
            self.timer = 0
            self.reload_time = 0

    def reload(self,ammo,current,level):
        reloaded = False
        if self.reload_time == 0:
            self.reload_time = time.time()
            self.need_chamber = False
            self.chamber_timer = 0
            self.reload_speed = self.breload_speed
            
            level.reload_bar.update(self.timer,self.reload_speed)
            
        self.timer = current - self.reload_time
        level.reload_bar.update(self.timer)
        if current - self.reload_time >= self.reload_speed:
            diff = self.mag_size - self.mag
            if self.mag_size == 0:
                diff = self.chamber_size - self.chamber
            shot = 'pellet' in self.kwargs
            if shot:
                #shotgun relaodinbfg
                
                if ammo[self.ammo_type][0] > 0 and (self.mag < self.mag_size or self.chamber < self.chamber_size):
                    if self.mag_size:
                        self.mag += 1
                    else:
                        self.chamber += 1
                    ammo[self.ammo_type][0] -=1
                    self.reload_time = 0
                    if (self.mag == self.mag_size if self.mag_size else self.chamber== self.chamber_size):
                        reloaded = True
                if self.end:
                    reloaded = True

            elif diff > ammo[self.ammo_type][0] and not shot :
                amount = ammo[self.ammo_type][0]
                ammo[self.ammo_type][0] -= amount
                if self.mag_size:
                    self.mag += amount
                elif self.mag_size == 0:
                    self.chamber += amount
                reloaded = True
            elif not shot:
                if self.mag_size:
                    self.mag += diff
                elif self.mag_size == 0:
                    self.chamber += diff
                ammo[self.ammo_type][0] -= diff
                reloaded = True
                
        if reloaded or ('pellet' in self.kwargs and ammo[self.ammo_type][0] <= 0):
            self.reload_time = 0
            self._reload = False
            self.end = False

        if self.chamber ==0 and self.mag and reloaded == True and not self._reload and self.chamber_size:
            self.need_chamber = True
    #ps is player speed to carry over for projectile speed    
    def update(self,projectiles, dt, pos,level,ammo = None,ps = None):
        if not self.dropped:  
            mouse = pygame.mouse.get_pos()
            mdif = (mouse[0] - (pos[0]-level.scroll.x),(pos[1]-level.scroll.y) - mouse[1])
            angle = math.degrees(math.atan2(mdif[1],mdif[0]))
            if self.flip:
                self.flipped = pygame.transform.flip(self.base_img,False,True)
                self.handle = (self.base_handle[0],self.flipped.get_height()- self.base_handle[1])
                self.shoot_point = (self.base_shoot_point[0], self.flipped.get_height() - self.base_shoot_point[1])
            else:
                self.flipped = self.base_img
                self.handle = self.base_handle
                self.shoot_point = self.base_shoot_point

            self.image,self.rect,self.barrel = self.rotate(pos, self.handle, self.shoot_point, self.flipped, angle)
            
            current = time.time()

            #cancelling shotgun reload with left click when there is at least one bullet in mag or chamber otherwise its pointles- if in mag triggers chambering
            if 'pellet' in self.kwargs:
                if self._reload:
                    if (pygame.MOUSEBUTTONDOWN,1) in level.keyed:
                        self.end = True

            droom = 'drum' in self.kwargs

            if self._reload and self.drum_time == 0 and self.drum == True and droom:
                self.drum_time = time.time()

            if (current - self.drum_time) >= self.chamber_speed and self.drum_time and droom:
                self.drum = not self.drum
                self.drum_time = 0
            
            if self._reload and (not self.drum if 'drum' in self.kwargs else True):
                self.reload(ammo, current,level)

            if not self._reload and self.drum == False and self.drum_time == 0 and droom:
                self.drum_time = time.time()
                

            #rechambering for automatic guns, isnt clipped by switching weapons
            if (current - self.shoot_time >= self.rateof) and 'man' not in self.kwargs and self.chamber == 0 and self.mag>0 and not self._reload and not self.need_chamber:
                dif = self.chamber_size - self.chamber
                if self.mag >= dif:
                    self.chamber =self.chamber_size
                    self.mag -= dif
                else:
                    self.chamber += self.mag
                    self.mag = 0
            #rechambering for manual
            if self.need_chamber and self.chamber_timer ==0 and self.drum == True and self.mag:
                self.chamber_timer = time.time()
            if (current - self.chamber_timer >= self.chamber_speed) and self.chamber == 0 and self.mag>0 and not self._reload and self.need_chamber:
                dif = self.chamber_size - self.chamber
                if self.mag >= dif:
                    self.chamber =self.chamber_size
                    self.mag -= dif
                else:
                    self.chamber += self.mag
                    self.mag = 0
                self.chamber_timer = 0
                self.need_chamber = False

            #pygame.mouse.get_pressed() == (1,0,0) and (current - self.shoot_time >= self.rateof) and 
            if 'semi' in self.kwargs:
                if self.shot:
                    if (pygame.MOUSEBUTTONUP,1) in level.keyed:
                        self.shot= False

            chambered = False
            chambert = False
            if self.chamber_size == 0 and self.mag and self.drum:
                chambered = True
            elif self.chamber_size:
                if self.chamber > 0: chambered = True

            if self.chamber_size:
                if self.chamber == 0: chambert = True
            else:
                chambert = True
        
            shotgun = 'shot' in self.kwargs
            if pygame.mouse.get_pressed() == (1,0,0) and (current - self.shoot_time >= self.rateof) and not self._reload and chambered and not level.show_wheel and not self.shot and self.drum:
                self.shoot_time = time.time()
                if not shotgun:
                    self.acc += 1
                    if self.acc > self.accmax:
                        self.acc = self.accmax
                for i in range(self.shots):
                    if shotgun:
                        offset = round(random.uniform(-self.accmax,self.accmax),2)
                    elif self.acc:
                        offset = round(random.uniform(-self.acc,self.acc),2)
                    else:
                        offset = 0
                    new_bullet = Bullet(angle+offset, self.barrel,self.b_image,self.bullet_mat,ps/5)
                    projectiles.add(new_bullet)
                if self.chamber_size:
                    self.chamber -= 1
                else:
                    self.mag -= 1
                if 'semi' in self.kwargs:
                    self.shot = True
                if 'man' in self.kwargs:
                    self.need_chamber = True
            elif (pygame.MOUSEBUTTONDOWN,1) in level.keyed and self.mag==0 and chambert and not self._reload:
                if ammo[self.ammo_type][0] > 0:
                    self._reload = True

            if not shotgun:
                if current - self.shoot_time >= self.rateof:
                    self.acc -= 0.5*dt
                    if self.acc < 0:
                        self.acc = 0
        else:
            itf.is_loaded(level,self)
            if not self.unloaded:
                itf.move(level,self,dt)

        
            
        
        
        
