import math
import pygame
import time
import random
import item_funcs as itf
from bullets import Bullet_mat
from guns import Gun
from stats import *
from debug import debug
from utils import *




class Player(pygame.sprite.Sprite):
    def __init__(self,speed,pos,chunk):
        super().__init__()
        self.unloaded = True
        self.scale = scale
        self.chunk = chunk
        self.key_stats = {}

        self.health = 100
        self.max_health = 100

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

        #Gun
        self.equip_index = 0
        self.last_drop = time.time()
        self.guns = pygame.sprite.Group()
        self.ammo = {
        'medium_ammo':[60],
        'rockets':[3],
        'shells':[5],
        'light_ammo':[30],
        'sniper_ammo':[20]
        }
        self.equipped = None

        #image
        self.image = pygame.Surface((14 * abs(self.scale),28 * abs(self.scale)))
        self.image.fill((255,0,0))

    def jump(self):
        self.momentum.y = self.jump_speed

    def get_side(self,mouse):
        if mouse[0] >= self.rect.centerx:
            side = 'right'
        if mouse[0] < self.rect.centerx:
            side = 'left'

        return side

    def switch_weapon(self, level, index = None):
        change = False
        if index == None:
            for event in level.keyed:
                if event[0] == pygame.MOUSEWHEEL:
                    self.equip_index += event[1]
                    change = True

            if self.equip_index >= len(self.guns):
                self.equip_index = 0

            if self.equip_index < 0:
                if self.guns:
                    self.equip_index = len(self.guns) - 1
                else:
                    self.equip_index = 0
            
        else:
            change = True
            self.equip_index = index

        if self.guns and change:
            if self.equipped._reload:
                self.equipped._reload = False
                self.equipped.reload_time = 0
                # delattr(self.equipped,'reload_time')
                level.finish_bar = False
            self.equipped.chamber_timer = 0
            self.equipped = self.guns.sprites()[self.equip_index]
            
    def get_interact(self,level, dt, side,keys):
        if keys[pygame.K_e]:
            to_pickup = itf.can_pickup(level.items.sprites(),self)
            #pickup guns
            if to_pickup:
                guns = list(filter(lambda x: x.name == 'gun', to_pickup))
                for i in guns:
                    i.dropped = False
                    self.guns.add(i)
                    level.item_wheel.change_items(self.guns)
                    level.items.remove(i) 
                if self.guns and not self.equipped:
                    self.equipped = self.guns.sprites()[self.equip_index]

        if (pygame.KEYDOWN,pygame.K_r) in level.keyed:
            if self.equipped:
                if self.equipped.mag < self.equipped.mag_size or (self.equipped.mag_size==0 and self.equipped.chamber < self.equipped.chamber_size):
                    if self.ammo[self.equipped.ammo_type][0] > 0:
                        self.equipped._reload = True

        current = time.time()
        holding = check_holding(pygame.K_q, level, current)
        if (pygame.KEYDOWN,pygame.K_q) in level.keyed or (holding and current - self.last_drop >= 0.05):
            if self.equipped:
                self.last_drop = time.time()
                self.equipped.dropped = True
                self.guns.remove(self.equipped)
                level.item_wheel.change_items(self.guns)
                level.items.add(self.equipped)
                if side == 'left':
                    self.equipped.rect.midright = self.rect.midleft
                    self.equipped.reset(level)
                    self.equipped.momentum.x = self.momentum.x -(20*dt)
                else:
                    self.equipped.rect.midleft = self.rect.midright
                    self.equipped.reset(level)
                    self.equipped.momentum.x = self.momentum.x + (20*dt)
                self.equipped.momentum.y = self.momentum.y
                self.equipped = None
                if self.equip_index >= len(self.guns.sprites()):
                    self.equip_index = len(self.guns.sprites()) - 1
                    if self.guns:
                        self.equipped = self.guns.sprites()[self.equip_index]
                else:
                    if self.guns:
                        self.equipped = self.guns.sprites()[self.equip_index]
                    
    def get_input(self,dt,keys):
        if keys[pygame.K_d]:
            if self.momentum.x > self.speed:
                pass
            else:
                self.momentum.x += self.acceleration*dt
                if self.momentum.x > self.speed:
                    self.momentum.x = self.speed
            self.moving = True


        elif keys[pygame.K_a]:
            if self.momentum.x < -self.speed:
                pass
            else:
                self.momentum.x -= self.acceleration*dt
                if self.momentum.x < -self.speed:
                    self.momentum.x = -self.speed
            self.moving = True

        if keys[pygame.K_SPACE]:
            if self.above_block:
                self.jump()

    def check_groups(self, level):
        try:
            self.colliders.empty()
        except AttributeError:
            pass
        self.colliders = level.colliders.copy()
        self.colliders.remove(self)
        try:
            self.players.empty()
        except AttributeError:
            pass
        self.players = level.players.copy()
        self.players.remove(self)
        try:
            self.tiles.empty()
        except AttributeError:
            pass
        self.tiles = level.tiles.copy()
    
    def reset_player(self,level):
        self.momentum.x = 0
        self.momentum.y = 0
        self.unloaded = True
        self.rect.midbottom = self.pos
        self.set_float_rect(3)

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

    def apply_gravity(self, dt):

        self.momentum.y += 0.2 * self.scale*dt

        if self.momentum.y > 4 * self.scale:
            self.momentum.y = 4 * self.scale

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
            if self.rect.move(0,1).colliderect(sprite):
                self.above_block = True
                if self.momentum.y > 0:
                    self.momentum.y = 0
                    

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
        if self.health <= 0:
            for i in self.guns:
                side = random.randint(0,1)
                force = random.randint(0,25)
                self.last_drop = time.time()
                i.dropped = True
                self.guns.remove(i)
                level.items.add(i)
                if side == 0:
                    i.rect.midright = self.rect.midleft
                    i.reset(level)
                    i.momentum.x = self.momentum.x -(force*dt)
                else:
                    i.rect.midleft = self.rect.midright
                    i.reset(level)
                    i.momentum.x = self.momentum.x + (force*dt)
                i.momentum.y = self.momentum.y
            self.kill()
            level.update_players()

        chunk_x = int(self.rect.centerx/(level.chunk_size*tile_size))
        chunk_y = int(self.rect.centery/(level.chunk_size*tile_size))
        key = str(chunk_x) + ',' + str(chunk_y)
        self.chunk = key
        if key in level.loaded_chunks:
            self.unloaded = False
        else:
            self.unloaded = True
            
        if not self.unloaded:
            self.moving = False
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos += level.scroll
            if self.selected:
                side = self.get_side(mouse_pos)
                keys = pygame.key.get_pressed()
                self.get_input(dt,keys)
                self.get_interact(level,dt,side,keys)
                self.switch_weapon(level)
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
                self.reset_player(level)
                self.health -= 20
                if self.health < 0:
                    self.health = 0
            
            if self.selected:
                if self.equipped:
                    if side == 'left':
                        self.equipped.update(level.projectiles, dt, self.rect.midleft,level,self.ammo,self.momentum)
                        self.equipped.flip = True
                    else:
                        self.equipped.update(level.projectiles, dt, self.rect.midright,level,self.ammo,self.momentum)
                        self.equipped.flip = False

class Croucher(Player):
    def __init__(self,speed,pos,chunk):
        Player.__init__(self, speed, pos,chunk)
        self.image.fill((0,0,255))
        self.crouch = False
        self.crouching = False

        #rect
        self.crouch_height = int(18 *self.scale)
        
        self.standing_height = int(28 * self.scale)
        self.rect.midbottom = pos
        self.rect = pygame.Rect((0,0),(14 * abs(self.scale),28 * abs(self.scale)))
        self.check_rect = pygame.Rect((0,0),(14 * abs(self.scale),28 * abs(self.scale)))
        self.rect.midbottom = pos

    def get_crouch(self,tiles):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LSHIFT] and self.selected:
            self.crouch = True
        else:
            if self.crouch:
                self.crouch = False
                self.check_rect.midbottom = self.rect.midbottom
                for sprite in tiles:
                    if self.check_rect.colliderect(sprite):
                        self.crouch = True

    def update(self,level, dt):
        top_players = []
        Player.update(self, level, dt)
        self.get_crouch(self.tiles)

        if not self.crouching:
            if self.crouch:
                quick_pos = self.rect.midbottom

                self.rect.inflate_ip(0,self.crouch_height - self.standing_height)
                self.rect.midbottom = quick_pos
                self.set_float_rect(1)
                self.image = pygame.transform.scale(self.image,(self.image.get_width(),self.crouch_height))

                self.crouching = True
        else:
            if not self.crouch:
                self.check_rect.midbottom = self.rect.midbottom
                for player in self.players:
                    if self.check_rect.colliderect(player):
                        top_players.append(player)

                quick_pos = self.rect.midbottom
                self.rect.inflate_ip(0,self.standing_height - self.crouch_height)
                self.rect.midbottom = quick_pos
                self.set_float_rect(1)
                for peep in top_players:
                    peep.rect.bottom = self.rect.top
                    peep.set_float_rect(1)

                self.image = pygame.transform.scale(self.image,(self.image.get_width(),self.standing_height))
                self.crouching = False

class Dasher(Player):
    def __init__(self, speed, pos,chunk):
        Player.__init__(self, speed, pos,chunk)
        self.dashing = False
        self.start_time = 0
        self.slowdown = False
        self.image.fill((100,0,200))
        self.dash_speed = 6 * self.scale

    def dash(self,dt):
        keys = pygame.key.get_pressed()
        current_time = time.time()
        if keys[pygame.K_LSHIFT]:
            if self.momentum.x:
                if current_time - self.start_time >= 4:
                    self.start_time = time.time()
                    self.dashing = True

        if current_time - self.start_time >= 0.3:
            self.dashing = False
            self.slowdown = True

        if self.dashing:
            if self.momentum.x > 0:
                self.momentum.x = self.dash_speed
            elif self.momentum.x < 0:
                self.momentum.x = -self.dash_speed
            self.moving = True

        if self.slowdown:
            if abs(self.momentum.x) > self.speed:
                if self.momentum.x < -self.speed:
                    self.momentum.x += self.decceleration * dt
                    if self.momentum.x > -self.speed:
                        self.momentum.x = -self.speed
                        self.slowdown = False

                elif self.momentum.x > self.speed:
                    self.momentum.x -= self.decceleration * dt
                    if self.momentum.x < self.speed:
                        self.momentum.x = self.speed
                        self.slowdown = False

    def get_input(self,dt,keys):
        if not self.dashing or self.momentum.x == 0:
            self.dashing = False
            if keys[pygame.K_d]:
                if self.momentum.x > self.speed:
                    pass
                else:
                    self.momentum.x += self.acceleration*dt
                    if self.momentum.x > self.speed:
                        self.momentum.x = self.speed
                self.moving = True


            elif keys[pygame.K_a]:
                if self.momentum.x < -self.speed:
                    pass
                else:
                    self.momentum.x -= self.acceleration*dt
                    if self.momentum.x < -self.speed:
                        self.momentum.x = -self.speed
                self.moving = True

        if keys[pygame.K_SPACE]:
            if self.above_block:
                self.jump()

    def apply_gravity(self, dt):
        if self.dashing:
            self.momentum.y = 0
        else:
            self.momentum.y += 0.2 * self.scale*dt

            if self.momentum.y > 4 * self.scale:
                self.momentum.y = 4 * self.scale

    def update(self,level, dt):
        self.dash(dt)
        Player.update(self, level,dt)

class Grapple(Player):
    def __init__(self,speed,pos,chunk):
        Player.__init__(self, speed, pos, chunk)
        self.image.fill((0,150,50))
        self.grapple_point = None
        
        self.range = 240 * self.scale
        self.grappling = False

    def reset_grapple(self):
        if self.grappling:
            self.momentum += self.distance
        self.grapple_point = None
        self.grappling = None
        
    def reset_player(self,level):
        self.momentum.x = 0
        self.momentum.y = 0
        self.unloaded = True
        self.rect.midbottom = self.pos
        self.set_float_rect(3)
        self.reset_grapple()

    def get_grapple_point(self,level, mouse,dt):

        dx = mouse[0] - (self.rect.centerx - level.scroll[0])
        dy = (self.rect.centery - level.scroll[1]) - mouse[1]

        self.raycast_rect = pygame.Rect(0,0,1,1)
        self.raycast_rect.center = self.rect.center
        self.raycast_float = pygame.math.Vector2(self.raycast_rect.center)


        angle = math.atan2(dy, dx)
        self.angle_gradient = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        self.angle_gradient.scale_to_length(1*self.scale)

        collided = False
        while collided == False:
            dx = abs(self.raycast_rect.centerx - self.rect.centerx)
            dy = abs(self.rect.centery - self.raycast_rect.centery)
            self.length = math.sqrt(dx*dx + dy*dy)
            if self.length >= self.range:
                break

            self.raycast_float.x += self.angle_gradient.x
            self.raycast_float.y -= self.angle_gradient.y
            self.raycast_rect.topleft = self.raycast_float

            for tile in self.tiles:
                if self.raycast_rect.colliderect(tile):
                    self.grapple_point = self.raycast_rect.center
                    collided = True
                    self.perp_speed = 0
                    self.make_rope()

    def make_rope(self):
        self.rope_rect = pygame.Rect(0,0,1,1)
        self.rope_rect.center = self.rect.center
        self.rope_start = self.rect.center
        self.rope_float = pygame.math.Vector2(self.rope_rect.center)
        self.angle_gradient.scale_to_length(self.scale)
        self.angleV = 0

    def animate_rope(self, dt):
        self.rope_float.x += self.angle_gradient.x *dt * 13
        self.rope_float.y -= self.angle_gradient.y *dt * 13
        self.rope_rect.center = self.rope_float

        dx = self.rope_float.x - self.rope_start[0]
        dy = self.rope_start[1] - self.rope_float.y
        rope_length = math.sqrt(dx*dx + dy*dy)

        if rope_length >= self.length:
            self.grappling = True
            dx = self.rect.centerx - self.grapple_point[0]
            dy = self.grapple_point[1] - self.rect.centery
            self.length = math.sqrt(abs(dx*dx) + abs(dy*dy))
            self.grapple_angle = math.degrees(math.atan2(dy, dx))
            
    def move_to_grapple(self, level, dt):
        self.length -= (2.5*self.scale) 
        if self.length <= 0:
            self.length = 0

        force = (22*self.scale) * math.sin(math.radians(self.grapple_angle + 90))
        angleA = (-1 * force)

        if self.length > 0:
            angleA /= self.length

        self.angleV += angleA * dt
        self.grapple_angle += self.angleV

        self.angleV *= 1 - (0.01 * dt)

        x = math.cos(math.radians(self.grapple_angle)) * self.length
        y = math.sin(math.radians(self.grapple_angle)) * self.length

        move_to = (self.grapple_point[0] + x,self.grapple_point[1] - y)
        distance = (move_to[0] - self.float_rect.x, move_to[1] - self.float_rect.y)
        self.distance = pygame.math.Vector2(distance)
        self.momentum.x *= 1 - (0.1 * dt)
        self.momentum.y *= 1 - (0.1 * dt)
         
    def get_side_grap(self):
        side = ''
        if self.rect.centerx < self.grapple_point[0]:
            side = 'left'
        elif self.rect.centerx > self.grapple_point[0]:
            side = 'right'

        return side
                
    def get_input(self,dt,keys):
        if not self.grappling:
            if keys[pygame.K_d]:
                if self.momentum.x > self.speed:
                    pass
                else:
                    self.momentum.x += self.acceleration*dt
                    if self.momentum.x > self.speed:
                        self.momentum.x = self.speed
                self.moving = True


            elif keys[pygame.K_a]:
                if self.momentum.x < -self.speed:
                    pass
                else:
                    self.momentum.x -= self.acceleration*dt
                    if self.momentum.x < -self.speed:
                        self.momentum.x = -self.speed
                self.moving = True
        else:
            self.moving = True

        if keys[pygame.K_SPACE]:
            if self.above_block:
                self.jump()
            self.reset_grapple()

    def move(self,level, colliders, dt):
        if self.grappling:
            movex = self.momentum.x*dt + self.distance.x * dt
        else:
            movex = self.momentum.x * dt
        #horizontal
        extra, to_add, amount = self.split_move(tile_size, movex)
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
                    if movex > 0:
                        #right
                        self.rect.right = sprite.rect.left
                        self.set_float_rect(0)
                        self.momentum.x = 0
                        collided = True
                        if self.grappling:
                            dx = self.float_rect.x - self.grapple_point[0]
                            dy = self.grapple_point[1] - self.float_rect.y
                            self.grapple_angle = math.degrees(math.atan2(dy,dx))
                            self.angleV = 0
                    elif movex < 0:
                        #left
                        self.rect.left = sprite.rect.right
                        self.set_float_rect(0)
                        self.momentum.x = 0
                        collided = True
                        if self.grappling:
                            dx = self.float_rect.x - self.grapple_point[0]
                            dy = self.grapple_point[1] - self.float_rect.y
                            self.grapple_angle = math.degrees(math.atan2(dy,dx))
                            self.angleV = 0
            if collided:
                break
            
        #vertical
        if self.grappling:
            movey = self.momentum.y*dt + self.distance.y *dt
        else:
            movey = self.momentum.y * dt
        self.above_block = False

        for sprite in colliders:
            if self.rect.move(0,1).colliderect(sprite):
                self.above_block = True
                if movey > 0:
                    self.momentum.y = 0

                    if self.grappling:
                        dx = self.float_rect.x - self.grapple_point[0]
                        dy = self.grapple_point[1] - self.float_rect.y
                        self.grapple_angle = math.degrees(math.atan2(dy,dx))
                        side = self.get_side_grap()
                        if side == 'left':
                            self.angleV = 1
                        elif side == 'right':
                            self.angleV = -1

        if not self.above_block:
            if not self.grappling:
                self.apply_gravity(dt)
        
        extra, to_add, amount = self.split_move(tile_size, movey)
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
                    if movey > 0:
                        #bottom
                        self.rect.bottom = sprite.rect.top
                        self.set_float_rect(1)
                        collided = True
                        self.momentum.y = 0
                        
                    elif movey < 0:
                        #top
                        self.rect.top = sprite.rect.bottom
                        self.set_float_rect(1)
                        collided = True
                        self.momentum.y = 0

                        if self.grappling:
                            dx = self.float_rect.x - self.grapple_point[0]
                            dy = self.grapple_point[1] - self.float_rect.y
                            self.grapple_angle = math.degrees(math.atan2(dy,dx))
                            
            if collided:
                break
        if self.grappling:    
            dx = self.float_rect.x - self.grapple_point[0]
            dy = self.grapple_point[1] - self.float_rect.y
            self.length = math.sqrt((abs(dx)**2+abs(dy)**2))
            self.grapple_angle = math.degrees(math.atan2(dy,dx))
           
    def update(self,level, dt):
        if (pygame.KEYDOWN,pygame.K_LSHIFT) in level.keyed:
                mouse = pygame.mouse.get_pos()
                self.reset_grapple()
                self.get_grapple_point(level, mouse,dt)

        Player.update(self,level, dt)

        if self.selected:
            if self.grapple_point and not self.grappling:
                self.animate_rope(dt)
                pygame.draw.line(level.display_surface,(0,0,0),(self.rect.center - level.scroll),(self.rope_rect.center - level.scroll),int(2 * self.scale))

            if self.grapple_point and self.grappling:
                self.move_to_grapple(level, dt)
                pygame.draw.line(level.display_surface,(0,0,0),(self.rect.center - level.scroll),(self.grapple_point - level.scroll),int(2 * self.scale))
        else:
            self.grapple_point = None


