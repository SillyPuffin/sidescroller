import pygame
import math
import random
import time
from sys import exit

pygame.init()
window_size = (1920,1080)
screen = pygame.display.set_mode((1920,1080),pygame.FULLSCREEN)

font = pygame.font.Font(None,30)
 
def debug(info,y = 10, x = 10):
    display_surface = pygame.display.get_surface()
    debug_surf = font.render(str(info),True,(255,255,255))
    debug_rect = debug_surf.get_rect(topleft = (x,y))
    pygame.draw.rect(display_surface,(0,0,0),debug_rect)
    display_surface.blit(debug_surf,debug_rect)

image = pygame.image.load('../graphics/rifle.png').convert_alpha()
image = pygame.transform.scale(image,(image.get_width()*4,image.get_height()*4))
pos = (200,200)
bullets = []
particles = []
shoot_time = 0
do_bounce = True
num = 10
speed = 15
old_time = time.time()
spritegroup = pygame.sprite.Group()
particles_ = {
'frost':[(15, 255, 255), (0.5, 2), 0.3],
'poison':[(0,200,0), (0.5, 2), 0.3], 
'death':[(160,0,0), (0.1, 4), 0.3],
'splatter':[(160,0,0), (0.1, 2), 0.3], 
'dash':[(200,200,200), (0, 0.3), 0.01],
'gold':[(255, 215, 0), (1, 4), 0]
}

class particle(pygame.sprite.Sprite):
    def __init__(self, start_point, image, size, speed, Type):
        super().__init__()
        self.rect = pygame.Rect(start_point.center, size)
        self.rect.center = start_point.center
        self.rect_float = [self.rect.x, self.rect.y]
        self.image = image
        self.base_image = image
        self.speed = speed
        self.fade = False
        self.alpha = 255
        xs = round(random.uniform(speed[0], speed[1]),2)
        xy = round(random.uniform(speed[0], speed[1]),2)
        self.vel_list = [(xs, xy),(-xs, xy),(xs, -xy),(-xs, -xy)]
        self.velocity = self.vel_list[random.randint(0, 3)]
        self.life = random.randint(25,40)

        if self.velocity[0] != 0:
            x = self.velocity[0]/abs(self.velocity[0])
        else:
            x = 0

        if self.velocity[1] != 0:
            y = self.velocity[1]/abs(self.velocity[1])
        else:
            y = 0

        self.d = (x,y)
        self.vel_list.remove((self.velocity[0]*-1, self.velocity[1]*-1))
        self.dchange = 0
        self.count = 0
        self.type = Type

        if self.type == 'swirl':
            self.swirl_dif = (round(random.uniform(0.01, 0.05),2), round(random.uniform(0.01, 0.05),2))
            self.swirl_dif = (self.swirl_dif[0]*self.d[0], self.swirl_dif[1]*self.d[1])
        
    def update(self,dt):
        
        if self.type == 'swirl':
            self.velocity =(self.velocity[0] - self.swirl_dif[0]*dt, self.velocity[1] - self.swirl_dif[1]*dt)

        if self.type == 'spread':
            if self.dchange > 10:
                self.velocity = [self.velocity[0] / (1 + 0.15*dt), self.velocity[1] / (1+0.15*dt)]   

        if self.type == 'swirl':
            if self.count >= 25:
                self.fade = True
                
        if self.type == 'spread':
            if self.count >= self.life:
                self.fade = True

                
        if self.fade:
            self.image = self.base_image.copy()
            self.image.fill((255,255,255, self.alpha), special_flags=pygame.BLEND_RGBA_MULT)
            self.alpha -= 20 *dt
        
            if self.alpha <= 0:
                self.kill()
        
        
        self.rect_float[0] += self.velocity[0] * dt
        self.rect_float[1] += self.velocity[1] * dt
        self.rect.x = self.rect_float[0]
        self.rect.y = self.rect_float[1]
        self.count += 1 *dt
        self.dchange += 1 *dt

class particle_container():
    def __init__(self, rect, colours, size, group):
        self.start_rect = rect
        
        self.size = size
        self.base_image = pygame.Surface((self.size),pygame.SRCALPHA)
        
        self.colours = {}
        for i in colours:
            self.colours[i] = [self.base_image.copy(), 0]           #works in pygame 2.1
            pygame.draw.circle(self.colours[i][0], colours[i][0], (int(self.size[0]/2), int(self.size[1]/2)), (int(self.size[0] / 2)))
            self.colours[i].append(colours[i][1]) #speed
            self.colours[i].append(colours[i][2])   #cooldown

        
        
        self.container = group
        
    def particle_maker(self, amount, colour, Type):
        current_time = time.time()
        if amount == 1:
            number = 1
        else: 
            number = random.randint(int(amount/2), int(amount))
        
        if current_time - self.colours[colour][1] >= self.colours[colour][3]:
            for i in range(number):
                new_particle = particle(self.start_rect, self.colours[colour][0], self.size, self.colours[colour][2], Type)
                self.container.add(new_particle)
            self.colours[colour][1] = time.time()

class Bullet():
    def __init__(self, speed, angle,pos,num,bounce):
        self.img = pygame.Surface((12,4),pygame.SRCALPHA)
        if bounce:
            self.img.fill((0,100,230))
        else:
            self.img.fill((150,175,0))
        self.pos = pygame.math.Vector2(pos)
        self.rect = self.img.get_rect(center = self.pos)
        self.rimg = pygame.transform.rotate(self.img, angle)
        self.rect = self.rimg.get_rect(center = self.rect.center)
        self.speed = pygame.math.Vector2(speed,0)
        self.speed = self.speed.rotate(-angle)
        self.life = time.time()
        self.container = 0
        self.bounce = bounce
        self.life_time = num
        self.cooldown = time.time()
        
    def update(self,bullets):
        current = time.time()
        killed = False
        if current - self.life >= self.life_time:
            bullets.remove(self)
            

        self.container.start_rect = self.rect

        if self.bounce:
            if (self.rect.centerx >= window_size[0]-1 or self.rect.centerx <= 0) and current - self.cooldown >= 0.01:
                self.speed.x = -self.speed.x
                self.cooldown = time.time()
                self.rimg = pygame.transform.rotate(self.img,-self.speed.as_polar()[1])
                self.rect = self.rimg.get_rect(center = self.rect.center)
                self.container.particle_maker(5,'gold','spread')

                if self.rect.centerx > window_size[0]-1:
                    self.rect.centerx = window_size[0]-1
                elif self.rect.centerx < 0:
                    self.rect.centerx = 0

            if (self.rect.centery >= window_size[1]-1 or self.rect.centery <= 0) and current - self.cooldown >= 0.01:
                self.speed.y = -self.speed.y
                self.cooldown = time.time()
                self.rimg = pygame.transform.rotate(self.img,-self.speed.as_polar()[1])
                self.rect = self.rimg.get_rect(center = self.rect.center)
                self.container.particle_maker(5,'gold','spread')

                if self.rect.centery > window_size[1]-1:
                    self.rect.centery = window_size[1]-1
                elif self.rect.centery < 0:
                    self.rect.centery = 0

        elif not self.bounce:
            if self.rect.centery >= window_size[1]-1 or self.rect.centery <= 0:
                if self in bullets:
                    bullets.remove(self)
                self.container.particle_maker(5,'gold','spread')
            if self.rect.centerx >= window_size[0]-1 or self.rect.centerx <= 0:
                if self in bullets:
                    bullets.remove(self)
                self.container.particle_maker(5,'gold','spread')

        #self.container.particle_maker(2,'dash','swirl')
        self.pos += self.speed*dt
        self.rect.center = self.pos

def rotate(pos, originPos,barrel, image, angle):
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

clock = pygame.time.Clock()

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            exit()
               
               
    clock.tick(600)
    new_time = time.time()
    dt = (new_time - old_time) * 60
    old_time = new_time
    keys = pygame.key.get_pressed()
    barrel = 0
    mouse = pygame.mouse.get_pos()
    mdif = (mouse[0] - pos[0],pos[1] - mouse[1])
    angle = math.degrees(math.atan2(mdif[1],mdif[0]))
    modangle = angle%360
    modnegangle = angle%-360
    speeding= False

    if keys[pygame.K_r]:
        bullets.clear()

    if keys[pygame.K_e]:
        num = 10

    if keys[pygame.K_LSHIFT]:
        speeding = True
        for event in events:
            if event.type == pygame.MOUSEWHEEL:
                speed += event.y
    
    if keys[pygame.K_LCTRL]:
        speed = 15

    if not speeding:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 2:
                    if do_bounce == True:
                        do_bounce = False
                    else:
                        do_bounce = True
##
##            if event.type == pygame.MOUSEWHEEL:
##                num += event.y

    if pygame.mouse.get_pressed() == (0,0,1):
        pos = pygame.mouse.get_pos()

    if (angle > 0 and (modangle > 90 and modangle <270)) or (angle<0 and(modnegangle<-90 and modnegangle>-270)):
        dimage = pygame.transform.flip(image,False,True)
        barrel = (56,16)
    else:
        dimage = image
        barrel = (56,8)

    current = time.time()    
    rimage,rect,muzzle = rotate(pos, (20,16),barrel, dimage, angle)
    if pygame.mouse.get_pressed() == (1,0,0) and (current - shoot_time > 0.000001):
        shoot_time = time.time()
        number = 2
        offset = random.randint(-number,number)
        new_bullet = Bullet(speed, angle+offset, muzzle, num, do_bounce)
        new_container = particle_container(new_bullet.rect, particles_, (8,8), spritegroup)
        new_bullet.container = new_container
        bullets.append(new_bullet)
    

    screen.fill((0,0,0))
    for i in bullets:
        i.update(bullets)
        screen.blit(i.rimg, i.rect)
    spritegroup.update(dt)
    spritegroup.draw(screen)
    screen.blit(rimage,rect)
    debug(num,0)
    debug(do_bounce,0,50)
    debug(speed,0,120)
    #pygame.draw.circle(screen, (100,0,0),(int(muzzle[0]),int(muzzle[1])), 5)
    #pygame.draw.rect(screen,(0,100,200),rect,4)
    pygame.display.update()
