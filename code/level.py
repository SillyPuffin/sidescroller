import pygame
from pygame.math import Vector2 as vec2
import random
from UI import *
from player import *
from enemy import Enemy
from tiles import Tile
from chunks import Chunk
from objects_ import *
from stats import *
from settings import *
from backgrounds import Cloud
from utils import load_folder


class Level:
    def __init__(self, level_data, surface,images):
        self.display_surface = surface
        self.images = images
        self.keys_time = {}
        self.scroll = pygame.math.Vector2()
        self.screen_rect = pygame.Rect(-5,-5,window_size[0]+10,window_size[1]+10)
        self.scale  = scale
        self.show_wheel = False
        self.ammo_readout = '0'
        self.last_indexed = 0
        self.level_data = level_data
        self.chunk_size = chunk_size
        self.parallax = parallax_dif
        self.tile_size = tile_size
        self.finish_bar = False
        self.p_index = 0
        self.last_update = 0
        self.layers = {
            '7':pygame.sprite.Group(),#parallax backgrounds and clouds
            '6':pygame.sprite.Group(),#things you can walk in front of like trees or back walls
            '5':pygame.sprite.Group(),#tiles
            '4':pygame.sprite.Group(),#players/entities
            '3':pygame.sprite.Group(),#items e.g guns
            '2':pygame.sprite.Group(),#particles e.g bullets
            '1':pygame.sprite.Group(),#front wall or platforms
            '0':pygame.sprite.Group()
        }

        self.ui_elements = pygame.sprite.Group()

        self.text = Text(self.images.characters,self.scale)
        self.ui_elements.add(self.text)

        self.equip = Text(self.images.characters,self.scale)
        # self.equip.image.set_alpha(255)
        self.ui_elements.add(self.equip)

        self.reload_bar = Bar(((80*self.scale,2*self.scale),(128,128,128,0)),80*self.scale,2*self.scale,(255,255,255))
        self.reload_bar.rect.bottomleft = (0,window_size[1]-9*self.scale)
        self.ui_elements.add(self.reload_bar)

        health_bar = self.images.ui['health_bar']
        self.health_bar = Bar(health_bar, 78*self.scale, 6*self.scale,(4,234,77))
        self.health_bar.rect.bottomleft = (0,window_size[1])
        self.ui_elements.add(self.health_bar)

        self.divider = pygame.Surface((80*self.scale,1*self.scale),pygame.SRCALPHA)
        self.divider.fill((128,128,128,170))

        self.item_wheel = Item_wheel((window_size[0]/2,window_size[1]/2),35,self.scale)

        #chamber icon
        self.chamber_status = pygame.Surface((1*scale,7*scale))
        self.chamber_status.fill((255,255,255))
        self.chamber_status.set_alpha(0)

        #drum icon
        self.drum = pygame.Surface((4*scale,4*scale))
        self.drum.fill((0,0,0))
        self.drum.set_colorkey((0,0,0))
        pygame.draw.circle(self.drum,(255,255,255),(4*scale/2,4*scale/2),4*scale/2)
        self.drum.set_alpha(0)


        self.setup_level(level_data)
                
    def setup_level(self,level_data):
        #sprite group
        self.tile_images = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.to_draw = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.tiles = pygame.sprite.Group()
        self.players = pygame.sprite.Group()
        self.scenery = pygame.sprite.Group()
        self.colliders = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()

        #images
        tiles = self.images.tiles
        items = self.images.items

        grass = tiles['grass']
        grass_frond = tiles['grass_frond']
        
        biggest_length = 0
        for i in level_data:
            length = len(i)
            if length > biggest_length:
                biggest_length = length

        map_width = biggest_length
        map_height = len(level_data)
        
        self.chunks = {}
        self.loaded_chunks = []
        empty = True
        ##chunk making code
        for cx in range(math.ceil(map_width/self.chunk_size)):
            for cy in range(math.ceil(map_height/self.chunk_size)):
                key = str(cx) + ',' + str(cy)
                chunk = Chunk((cx*tile_size*self.chunk_size,cy*tile_size*self.chunk_size),self.chunk_size*tile_size)
                for icx in range(self.chunk_size):
                    for icy in range(self.chunk_size):
                        mapx = cx * self.chunk_size + icx
                        mapy = cy * self.chunk_size + icy
                        char = ''
                        try:
                            char = level_data[mapy][mapx]
                        except IndexError:
                            pass

                        x = mapx * tile_size
                        y = mapy * tile_size
                        pos = (x+tile_size/2, y + tile_size)     

                        if char:
                            if char == "g":
                                new_tile = Tile((x, y), tile_size, grass,'grass',f'{mapx}:{mapy}')
                                chunk.tiles.add(new_tile)
                                chunk.dtiles[f'{mapx}:{mapy}'] = new_tile
                                empty = False

                            elif char == '4':
                                player_sprite = Grapple(2 * scale, pos,key)
                                self.players.add(player_sprite)
                                self.colliders.add(player_sprite)
                                empty = False
                            elif char == '3':
                                player_sprite = Dasher(2 * scale, pos,key)
                                self.players.add(player_sprite)
                                self.colliders.add(player_sprite)
                                empty = False
                            elif char == "2":
                                player_sprite = Croucher(2*scale,pos,key)
                                self.players.add(player_sprite)
                                self.colliders.add(player_sprite)
                                empty = False
                            elif char == '1':
                                player_sprite = Player(2.5 *scale,pos,key)
                                self.players.add(player_sprite)
                                self.colliders.add(player_sprite)
                                empty = False
                            elif char == 'e':
                                new_enemy = Enemy(2.5*self.scale, pos,key)
                                self.enemies.add(new_enemy)
                                self.colliders.add(new_enemy)
                                empty = False
                            elif char != '-':
                                tag = tags[char]
                                new_gun = guns[tag][0](items[tag],items['B_'+tag],pos,*guns[tag][1],guns[tag][2],guns[tag][3])
                                self.items.add(new_gun)
                                empty = False
                               
                if not empty:
                    self.chunks[key] = chunk

        self.finalise_level()
        for i in self.chunks:
            self.update_chunk_image(i)
        #pre-loop definitions
        self.selected_player = self.players.sprites()[self.p_index]
        self.selected_player.selected = True
        self.health_bar.max = self.selected_player.max_health
        
        self.truescroll = pygame.math.Vector2()
        self.truescroll.x +=  (self.selected_player.rect.centerx - self.truescroll.x- half_width)
        self.truescroll.y +=  (self.selected_player.rect.centery - self.truescroll.y- half_height)
        self.scrolling(1)

        #clouds
        for i in range(10):
            self.spawn_cloud()

    def spawn_cloud(self,side='mid'):
        new_cloud  = Cloud(self.images.background['clouds']['1'])
        end = False
        if side == 'left':
            pos = vec2(0+self.scroll.x/parallax_dif,random.randint(int(0+new_cloud.rect.height/2),int(half_height/2)))
            new_cloud.rect.topright = pos
            new_cloud.pos = new_cloud.rect.topleft
        elif side == 'right':
            pos = vec2(window_size[0]-1+self.scroll.x/parallax_dif,random.randint(int(0+new_cloud.rect.height/2),int(half_height/2)))
            new_cloud.rect.topleft = pos
            new_cloud.pos = new_cloud.rect.topleft
        else:
            while not end:
                pos = vec2 (random.randint(int(0+new_cloud.rect.width/2+self.scroll.x/parallax_dif),int(window_size[0]-new_cloud.rect.width/2+self.scroll.x/parallax_dif)),random.randint(int(0+new_cloud.rect.height/2),int(half_height/2)))
                new_cloud.rect.center = pos
                new_cloud.pos = new_cloud.rect.topleft

                collided = False
                for i in self.clouds:
                    if new_cloud.rect.colliderect(i.rect):
                        collided = True
                if not collided:
                    end = True
        
        self.clouds.add(new_cloud)

    def finalise_level(self):
        tiles ={}
        for i in self.chunks:
            tiles.update(self.chunks[i].dtiles)

        get_list = lambda x: [int(n) for n in x.split(':')]
        get_str = lambda x: f'{x[0]}:{x[1]}'

        for i in tiles:
            tile = tiles[i]
            num = get_list(tile.key)
            north = get_str([num[0],num[1]-1])
            northwest = get_str([num[0]-1,num[1]-1])
            northeast = get_str([num[0]+1,num[1]-1])
            south = get_str([num[0],num[1]+1])
            southwest = get_str([num[0]-1,num[1]+1])
            southeast = get_str([num[0]+1,num[1]+1])
            west= get_str([num[0]-1,num[1]])
            east=  get_str([num[0]+1,num[1]])

            no = tiles.get(north,False)
            ne = tiles.get(northeast,False)
            nw = tiles.get(northwest,False)
            so = tiles.get(south,False)
            sw = tiles.get(southwest,False)
            se = tiles.get(southeast,False)
            we = tiles.get(west,False)
            ea = tiles.get(east,False)
            
            if no and so and we and ea:
                tile.can_collide = False

            #tiling images
            lst = []
            if no:
                lst.append(1)
            if so:
                lst.append(3)
            if we:
                lst.append(4)
            if ea:
                lst.append(2)
            lst.sort()
            s = ''
            for letter in lst:
                s += str(letter)
            if s =='':
                s = '0'
            tile.image = self.images.tile_sets[tile.name][s].copy()
            if (not nw) and (no and we):
                tile.image.blit(self.images.tile_sets[tile.name]['5'],(0,0))
            if (not ne) and (no and ea):
                tile.image.blit(self.images.tile_sets[tile.name]['6'],(0,0))
            if (not se) and (so and ea):
                tile.image.blit(self.images.tile_sets[tile.name]['7'],(0,0))
            if (not sw) and (so and we):
                tile.image.blit(self.images.tile_sets[tile.name]['8'],(0,0))

            #decor

            #grass fronds
            if not no and tile.name == 'grass' and (s=='24' or s=='234'):
                chance = random.randint(1,100)
                chunk_x = int(tile.rect.move(0,-self.tile_size).centerx/(self.chunk_size*self.tile_size))
                chunk_y = int(tile.rect.move(0,-self.tile_size).centery/(self.chunk_size*self.tile_size))
                key = str(chunk_x) + ',' + str(chunk_y)
                cx = chunk_x*chunk_size
                cy = chunk_y*chunk_size
                x = tile.rect.x/tile_size%chunk_size
                y = tile.rect.y-self.tile_size/tile_size%chunk_size
                world_key = f'{int(cx+x)}:{int(cy+y)}'
                if chance <= 25:
                    new_grass = Tile((tile.rect.x,tile.rect.y - self.tile_size),self.tile_size,self.images.tiles['grass_frond'],'grass_frond',world_key,'front_wall')
                    self.chunks[key].grass.add(new_grass)
                    
        for i in self.chunks:
            for t in self.chunks[i].tiles:
                if t.can_collide == True:
                    self.chunks[i].ctiles.add(t)

    def update_chunk_image(self, key):
        chunk_x = int(key.split(',')[0])
        chunk_y = int(key.split(',')[1])
        tempsurf = pygame.Surface((self.chunk_size*self.tile_size,self.chunk_size*self.tile_size))
        tempsurf.set_colorkey((0,0,0))
        for i in self.chunks[key].tiles:
            tempsurf.blit(i.image,(i.rect.x-self.chunk_size*self.tile_size*chunk_x,i.rect.y-self.chunk_size*self.tile_size*chunk_y))
        self.chunks[key].tile_image = self.chunks[key].set_chunk_image(tempsurf,'tile')
    
    def clear_groups(self):
        self.tiles.empty()
        self.tile_images.empty()
        self.colliders.empty()
        self.scenery.empty()
        self.loaded_chunks = []
        self.update_groups()

    def update_groups(self):
        for player in self.players:
            player.check_groups(self)
        for e in self.enemies:
            e.check_groups(self)

    def fill_layers(self):
        self.to_draw.empty()
        
        self.to_draw.add(self.items)
        if self.selected_player.equipped:
            self.to_draw.add(self.selected_player.equipped)
        
        self.to_draw.add(self.projectiles)

        self.to_draw.add(self.clouds)
        
        self.to_draw.add(self.players)
        
        self.to_draw.add(self.ui_elements)

        self.to_draw.add(self.scenery)

        self.to_draw.add(self.tile_images)

        self.to_draw.add(self.projectiles)
        
        self.to_draw.add(self.enemies)

        for i in self.layers:
            self.layers[i].empty()

        for i in self.to_draw:
            if i.type == 'UI':
                self.layers['0'].add(i)

            if i.type == 'particle':
                self.layers['2'].add(i)

            if i.type == 'front_wall':
                self.layers['1'].add(i)
                
            if i.type == 'item':
                self.layers['3'].add(i)

            if i.type == 'entity':
                self.layers['4'].add(i)

            if i.type == 'tile':
                self.layers['5'].add(i)  

            if i.type == 'bg':
                self.layers['7'].add(i)  

    def scrolling(self,dt):
        player = self.players.sprites()[self.p_index]
        self.truescroll[0] += (player.rect.centerx - self.truescroll[0] - half_width)/scroll_divider*dt
        self.truescroll[1] += (player.rect.centery - self.truescroll[1] - half_height)/scroll_divider*dt
        self.scroll[0] = int(self.truescroll.x)
        self.scroll[1] = int(self.truescroll.y)
        
    def get_switch(self):
        if (pygame.KEYDOWN,pygame.K_RIGHT) in self.keyed:
            self.p_index -= 1
        if (pygame.KEYDOWN,pygame.K_LEFT) in self.keyed:
            self.p_index += 1

        if self.p_index >= len(self.players.sprites()):
            self.p_index = 0

        if self.p_index < 0:
            self.p_index = len(self.players.sprites()) - 1

        self.selected_player.selected = False
        self.selected_player = self.players.sprites()[self.p_index]
        self.item_wheel.change_items(self.selected_player.guns)
        self.selected_player.selected = True
        self.health_bar.max = self.selected_player.max_health

    def update_players(self):
        if self.players:
            if self.p_index >= len(self.players.sprites()):
                self.p_index = len(self.players.sprites()) - 1
                self.selected_player = self.players.sprites()[self.p_index]
                self.selected_player.selected = True
                self.health_bar.max = self.selected_player.max_health
                self.item_wheel.change_items(self.selected_player.guns)
            else:
                self.selected_player = self.players.sprites()[self.p_index]
                self.selected_player.selected = True
                self.health_bar.max = self.selected_player.max_health
                self.item_wheel.change_items(self.selected_player.guns)
        else:
            self.setup_level(self.level_data)

    def run(self,events,dt):
        self.display_surface.fill((60,220,255))
        self.events = events
        self.keyed = []
        for event in self.events:
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                self.keyed.append((event.type,event.key))
            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
                self.keyed.append((event.type,event.button))
            if event.type == pygame.MOUSEWHEEL:
                self.keyed.append((event.type,event.y))
        self.scrolling(dt)
        current = time.time()
        #chunks
        if current - self.last_update >= 0.016:
            self.last_update = time.time()
            load = False
            chunks = []
            chunkxrange = math.ceil(window_size[0]/(tile_size * self.chunk_size))
            chunkyrange = math.ceil(window_size[1]/(tile_size * self.chunk_size))
            for y in range(chunkyrange + 1):
                for x in range(chunkxrange + 1):
                    target_x = x + int((self.scroll.x)/(self.chunk_size*tile_size))
                    target_y = y + int((self.scroll.y)/(self.chunk_size*tile_size))
                    key = str(target_x) + ',' + str(target_y)
                    chunks.append(key)
                    if key not in self.loaded_chunks:
                        load = True

            if load:
                self.clear_groups()
                self.loaded_chunks = chunks[:]
                for i in self.loaded_chunks:
                    if i in self.chunks:
                        self.tiles.add(self.chunks[i].tiles)
                        self.tile_images.add(self.chunks[i].tile_image)
                        self.colliders.add(self.chunks[i].ctiles)
                        self.scenery.add(self.chunks[i].grass)   
                
                self.colliders.add(self.players)
                self.colliders.add(self.enemies)

            self.update_groups()

        #clouds
        self.clouds.update(dt)
        for cloud in self.clouds:
            if not cloud.rect.move(- vec2(self.scroll.x/parallax_dif,self.scroll.y/(parallax_dif*2))).colliderect(self.screen_rect):
                if cloud.rect.centerx > self.screen_rect.centerx:
                    cloud.kill()
                    self.spawn_cloud('left')
                if cloud.rect.centerx < self.screen_rect.centerx:
                    cloud.kill()
                    self.spawn_cloud('right')
                

        #projectiles
        self.projectiles.update(self, dt)

        #items
        self.items.update(self.projectiles, dt, None, self)

        #player
        self.players.update(self, dt)
        self.get_switch()

        #enemy
        self.enemies.update(self,dt)

        #ui
        #healthbar
        self.health_bar.update(self.selected_player.health)
        #reload bar
        p = self.selected_player.equipped
        if p and self.selected_player.equipped._reload == True:
            self.reload_bar.bar.set_alpha(self.reload_bar.bar.get_alpha() + math.ceil(15*dt))
        elif (p and self.selected_player.equipped._reload == False and self.reload_bar.bar.get_alpha()) or (not p and self.reload_bar.bar.get_alpha()):
            self.reload_bar.bar.set_alpha(self.reload_bar.bar.get_alpha() - math.ceil(15*dt))
            self.reload_bar.update()
            if self.reload_bar.value and self.reload_bar.bar.get_alpha() <= 0:
                self.reload_bar.update(0)

        #ammo readout
        if self.selected_player.equipped:
            new_ammo_readout = str(self.selected_player.equipped.mag + self.selected_player.equipped.chamber) + '/' + str(self.selected_player.ammo[self.selected_player.equipped.ammo_type][0])
            if self.ammo_readout != new_ammo_readout:
                self.ammo_readout = new_ammo_readout
                self.text.create_image(self.ammo_readout)
                self.text.rect.topleft = (1*self.scale,window_size[1]-22*self.scale)

        #equipped
        if self.last_indexed != self.selected_player.equip_index + 1:
            self.equip.create_image(str(self.selected_player.equip_index + 1))
            self.equip.rect.right = self.reload_bar.rect.right
            self.equip.rect.top = window_size[1]-22*self.scale
            
            self.last_indexed = self.selected_player.equip_index + 1

        if self.selected_player.equipped:
            self.text.image.set_alpha(self.text.image.get_alpha()+math.ceil(15*dt))
            self.equip.image.set_alpha(self.equip.image.get_alpha()+math.ceil(15*dt))      
        else:       
            self.text.image.set_alpha(self.text.image.get_alpha()-math.ceil(15*dt)) 
            self.equip.image.set_alpha(self.equip.image.get_alpha()-math.ceil(15*dt))   



        #visibles
        self.fill_layers()

        for s in self.layers['7']:
                self.display_surface.blit(s.image, (s.rect.topleft - vec2(self.scroll.x/parallax_dif,self.scroll.y/(parallax_dif*2))))
        pygame.draw.rect(self.display_surface,(100,200,100),(-230-self.scroll[0]/5,0-self.scroll[1]/5+half_height,100,100),0)

        for s in self.layers['6']:
            self.display_surface.blit(s.image, (s.rect.topleft - self.scroll))

        for s in self.layers['5']:
            self.display_surface.blit(s.image, (s.rect.topleft - self.scroll))
        
        for s in self.layers['4']:
            self.display_surface.blit(s.image, (s.rect.topleft - self.scroll))
        pygame.draw.rect(self.display_surface, (240,190,0),(self.selected_player.rect.topleft - self.scroll,(self.selected_player.rect.width,self.selected_player.rect.height)),1*self.scale)

        for s in self.layers['3']:
            self.display_surface.blit(s.image, (s.rect.topleft - self.scroll))

        for s in self.layers['2']:
            self.display_surface.blit(s.image, (s.rect.topleft - self.scroll))

        for s in self.layers['1']:
            self.display_surface.blit(s.image, (s.rect.topleft - self.scroll))

        buffer = (self.divider.get_height()-1)/2
        if buffer < 1:
            buffer = 1
        self.display_surface.blit(self.divider,(0,self.reload_bar.rect.midleft[1]-buffer))

        #chambered
        if self.selected_player.equipped and self.selected_player.equipped.chamber > 0:
            self.chamber_status.set_alpha(self.chamber_status.get_alpha()+math.ceil(15*dt))
            self.display_surface.blit(self.chamber_status,(self.text.rect.topright[0]+1*scale,self.text.rect.topright[1]+1*scale))
        else:
            self.chamber_status.set_alpha(self.chamber_status.get_alpha()-math.ceil(15*dt))
            self.display_surface.blit(self.chamber_status,(self.text.rect.topright[0]+1*scale,self.text.rect.topright[1]+1*scale))


        #drumed
        if self.selected_player.equipped and self.selected_player.equipped.drum == True and 'drum' in self.selected_player.equipped.kwargs:
            self.drum.set_alpha(self.drum.get_alpha()+math.ceil(15*dt))
            self.display_surface.blit(self.drum,(self.text.rect.topright[0]+3*scale,self.text.rect.topright[1] + 3*scale))
        else:
            self.drum.set_alpha(self.drum.get_alpha()-math.ceil(15*dt))
            self.display_surface.blit(self.drum,(self.text.rect.topright[0]+3*scale,self.text.rect.topright[1] + 3*scale))

        for s in self.layers['0']:
            self.display_surface.blit(s.image, (s.rect.topleft))

        #item wheel
        mouse_pos = pygame.mouse.get_pos()
        if (pygame.KEYDOWN,pygame.K_LCTRL) in self.keyed:
            self.show_wheel = not self.show_wheel
        
        if self.show_wheel:
            self.item_wheel.update(self.selected_player.equip_index,self.display_surface,mouse_pos,self,dt)
        # for i in self.loaded_chunks:
        #     if i in self.chunks:
        #         pygame.draw.rect(self.display_surface,(0,200,0),(self.chunks[i].rect.topleft - self.scroll,(self.chunk_size*tile_size,self.chunk_size*tile_size)),2*self.scale)
        debug(self.selected_player.rect.centerx-half_width,30,10)   
        debug(self.scroll,45,10)
       
        

                
