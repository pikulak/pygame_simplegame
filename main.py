import os.path
import pygame as pg
from pygame.locals import *
from pytmx.util_pygame import load_pygame as load_pg
import pyscroll
import pyscroll.data
from pyscroll.group import PyscrollGroup

RESOURCES_DIR = 'data'
HERO_MOVE_SPEED = 200
MAP_FILENAME = 'grasslands.tmx'

def init_screen(width,height):
    screen = pg.display.set_mode((width,height),pg.RESIZABLE)
    return screen
    
def get_map(filename):
    return os.path.join(RESOURCES_DIR,filename)
    
def load_image(filename):
    return pg.image.load(os.path.join(RESOURCES_DIR, filename))
    
class Hero(pg.sprite.Sprite):

    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.image = load_image('hero.png').convert_alpha()
        self.velocity = [0,0]
        self._position = [0,0]
        self._old_position = self.position
        self.rect = self.image.get_rect()
        self.feet = pg.Rect(0,0, self.rect.width*.5,8)
        
    @property
    def position(self):
        return list(self._position)
        
    @position.setter
    def position(self,value):
        self._position = list(value)

    def update(self,dt):
        self._old_position = self._position[:]
        self._position[0]+= self.velocity[0]*dt
        self._position[1]+= self.velocity[1]*dt
        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom
        
    def move_back(self, dt):
        self._position = self._old_position
        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom
        
        
class Game(object):
    filename = get_map(MAP_FILENAME)
    
    
    def __init__(self):
        self.running = False
        tmx_data = load_pg(self.filename)
        self.walls = list()
        for object in tmx_data.objects:
            self.walls.append(
                pg.Rect(
                object.x,
                object.y,
                object.width,
                object.height))
        map_data = pyscroll.data.TiledMapData(tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data,screen.get_size())
        self.map_layer.zioom = 2
        self.group = PyscrollGroup(map_layer=self.map_layer)
        self.hero = Hero()
        self.hero.position = self.map_layer.map_rect.center
        self.group.add(self.hero)
        
    def draw(self,surface):
        self.group.center(self.hero.rect.center)
        self.group.draw(surface)
        
    def handle_input(self):
        poll = pg.event.poll
        event = poll()
        while event:
            if event.type ==QUIT:
                self.running = False
                break
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                    break
                elif event.key == K_EQUALS:
                    self.map_layer.zoom+= .25
                elif event.key == K_MINUS:
                    value = self.map_layer.zoom - .25
                    if value > 0:
                        self.map_layer.zoom = value
            elif event.type == VIDEORESIZE:
                init_screen(event.w,event.h)
                self.map_layer.set_size((event.w,event.h))
            event = poll()
        pressed = pg.key.get_pressed()
        if pressed[K_UP]:
            self.hero.velocity[1] = - HERO_MOVE_SPEED
        elif pressed[K_DOWN]:
            self.hero.velocity[1] = HERO_MOVE_SPEED
        else:
            self.hero.velocity[1] = 0
        if pressed[K_LEFT]:
            self.hero.velocity[0] = -HERO_MOVE_SPEED
        elif pressed[K_RIGHT]:
            self.hero.velocity[0] = HERO_MOVE_SPEED
        else:
            self.hero.velocity[0] = 0
            
    def update(self,dt):
        self.group.update(dt)
        for sprite in self.group.sprites():
            if sprite.feet.collidelist(self.walls)>-1:
                sprite.move_back(dt)
                
    def run(self):
        clock = pg.time.Clock()
        self.running = True
        try:
            while self.running:
                dt = clock.tick() / 1000
                self.handle_input()
                self.update(dt)
                self.draw(screen)
                pg.display.flip()
        except KeyboardInterrupt:
            self.running = False
            
if __name__ =="__main__":
    pg.init()
    pg.font.init()
    screen = init_screen(800,600)
    pg.display.set_caption('Test gierki')
    try:
        game = Game()
        game.run()
    except:
        pg.quit()
        raise
