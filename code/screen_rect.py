import pygame


class Screen_rect(pygame.sprite.Sprite):
    def __init__(self,settings):
        super().__init__()
        window_size = settings.window_size
        self.settings = settings
        self.float_rect = pygame.math.Vector2()
        self.rect = pygame.Rect(0,0,window_size[0] + 15 , window_size[1] + 10 )

    def set_float_rect(self, player):
        self.rect.center = player.rect.center
        self.float_rect.x = self.rect.centerx
        self.float_rect.y = self.rect.centery

    def screen_rect_scroll(self, player,dt):
        self.float_rect.x += (player.rect.centerx - self.float_rect.x)/self.settings.scroll_divider*dt
        self.float_rect.y += (player.rect.centery - self.float_rect.y)/self.settings.scroll_divider*dt
        
        self.rect.centery = self.float_rect.y
        self.rect.centerx = self.float_rect.x


        


