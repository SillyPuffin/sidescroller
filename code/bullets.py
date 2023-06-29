import pygame
import math
import time


class Bullet_mat:
    def __init__(self,**kwargs):
        self.life_time = kwargs.pop('lifetime')
        self.damage = kwargs.pop('dmg')
        self.speed = kwargs.pop('speed')
        self.props = kwargs
        #physics, explodes, bouncy, hitscan

class Bullet(pygame.sprite.Sprite):
    def __init__(self,angle,pos,img,bullet_mat,ps = None):
        super().__init__()
        self.baseimg = img
        self.props = bullet_mat.props
        self.pierce = self.props.get('pierce',None)
        self.avoid_list = []
        self.rotate = True
       
        self.type = 'particle'
        self.pos = pygame.math.Vector2(pos)
        self.rect = self.baseimg.get_rect(center = self.pos)
        self.image = pygame.transform.rotate(self.baseimg, angle)
        self.rect = self.image.get_rect(center = self.rect.center)
        self.speed = pygame.math.Vector2(bullet_mat.speed,0)
        self.speed = self.speed.rotate(-angle)
        if ps:
            self.speed += ps
        self.life = time.time()
        self.life_time = bullet_mat.life_time
        self.damage = bullet_mat.damage

    def explode(self,level):
        entites = level.enemies.sprites()
        entites.extend(level.players.sprites())
        range = self.props['explode']
        
        for p in entites:
            x_offset = p.rect.centerx - self.rect.centerx
            y_offset = p.rect.centery - self.rect.centery
            distance = pygame.math.Vector2(x_offset,y_offset).length()
            if distance > range*level.scale:
                pass
            elif distance > (range-range/3)*level.scale:
                p.health -= self.damage/2**2
            elif distance > (range/3)*level.scale:
                p.health -= self.damage/2
            elif distance != None:
                p.health -= self.damage

        self.kill()

    def get_grounded(self,level):
        self.grounded = False
        for tile in level.tiles:
            if self.rect.move(0,+2).colliderect(tile.rect):
                self.grounded = True

    def update(self,level,dt):
        current = time.time()
        if current - self.life >= self.life_time:
            if 'explode' in self.props:
                self.explode(level)
            else:
                self.kill()

        if self.pierce != None:
            col_list = []
        for i in level.enemies:
            if self.rect.colliderect(i.rect):
                if self.pierce != None:
                    if i.rect not in col_list:
                        col_list.append(i.rect)
                if 'explode' in self.props and 'physics'not in self.props:
                    self.explode(level)
                else:
                    if 'pierce' not in self.props:
                        i.health -= self.damage
                    if self.pierce and self.pierce > 0:
                        if i.rect not in self.avoid_list:
                            self.pierce-=1
                            i.health -= self.damage
                            self.avoid_list.append(i.rect)
                    elif i.rect not in self.avoid_list:
                        self.kill()
        if self.pierce != None:
            for rect in self.avoid_list:
                if rect not in col_list:
                    self.avoid_list.remove(rect)

        if 'physics' in self.props or 'grav' in self.props:
            if 'physics' in self.props:
                decceleration,bounce,gravity = self.props.get('physics')
            else:
                decceleration,gravity = self.props.get('grav')
        #decelleration
        self.get_grounded(level)
        if 'physics' in self.props or 'grav'in self.props:
            if self.speed.x < 0:   
                if self.grounded:
                    self.speed.x += decceleration * dt
                else:
                    self.speed.x += decceleration/5 * dt
                if self.speed.x > 0:
                    self.speed.x = 0
            elif self.speed.x > 0:   
                if self.grounded: 
                    self.speed.x -= decceleration * dt
                else:
                    self.speed.x -= decceleration/5 * dt    
                if self.speed.x < 0:
                    self.speed.x = 0

        if self.rotate:
            self.image = pygame.transform.rotate(self.baseimg, -self.speed.as_polar()[1])
        if abs(self.speed.length()) <0.5:
            self.rotate = False

        if 'physics' in self.props or 'grav' in self.props:
            self.speed.y+=gravity*dt

        #movement
        if 'bouncy' in self.props or 'physics' in self.props:
            #horizontal movement
            self.pos.x += self.speed.x * dt
            self.rect.centerx = self.pos.x
            
            for i in level.tiles:
                if self.rect.colliderect(i.rect):
                    if self.speed.x > 0:
                        self.speed.x = -self.speed.x
                        self.image = pygame.transform.rotate(self.baseimg, -self.speed.as_polar()[1])
                        self.rect = self.image.get_rect(center = self.rect.center)
                        self.rect.right = i.rect.left
                        self.pos.x = self.rect.centerx

                    elif self.speed.x < 0:
                        self.speed.x = - self.speed.x
                        self.image = pygame.transform.rotate(self.baseimg, -self.speed.as_polar()[1])
                        self.rect = self.image.get_rect(center = self.rect.center)
                        self.rect.left = i.rect.right
                        self.pos.x = self.rect.centerx
            
            
            self.pos.y += self.speed.y * dt
            self.rect.centery = self.pos.y
            
            for i in level.tiles:
                if self.rect.colliderect(i.rect):
                    if self.speed.y > 0:
                        if 'physics'in self.props:
                            self.speed.y = -self.speed.y
                            if self.speed.y > 0:
                                self.speed.y -= bounce*dt
                                if self.speed.y < 0:
                                    self.speed.y = 0
                            if self.speed.y<0:
                                self.speed.y += bounce*dt
                                if self.speed.y >0:
                                    self.speed.y = 0
                        else:
                            self.speed.y = -self.speed.y
                        self.image = pygame.transform.rotate(self.baseimg, -self.speed.as_polar()[1])
                        self.rect = self.image.get_rect(center= self.rect.center)
                        self.rect.bottom = i.rect.top
                        self.pos.y = self.rect.centery
                    elif self.speed.y < 0:
                        self.speed.y = -self.speed.y
                        self.image = pygame.transform.rotate(self.baseimg, -self.speed.as_polar()[1])
                        self.rect = self.image.get_rect(center = self.rect.center)
                        self.rect.top = i.rect.bottom
                        self.pos.y = self.rect.centery
        else:  
            self.pos += self.speed*dt
            self.rect.center = self.pos
            for i in level.tiles:
                if self.rect.colliderect(i.rect):
                    if 'explode' in self.props:
                        self.explode(level)
                    else:
                        self.kill()

