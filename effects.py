import pygame
import math
import random
from pygame.locals import *
from math import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, angle, size, who, tank):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self._size = size
        self.tank = tank
        if self._size == "big":
            self.b_size = (2,7)
            self.speed = 18
        if self._size == "small":
            self.b_size = (1,3)
            self.speed = 22
        self.image = pygame.Surface((self.b_size))
        self.image.fill((255,255,0))
        self.image.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.image.get_rect(center = pos)
        self.x, self.y = self.rect.center
        self.cannon_dist = 25
        self.x -= sin(radians(angle))*self.cannon_dist
        self.y -= cos(radians(angle))*self.cannon_dist
        self.rect.center = self.x, self.y
        self.angle = angle
        self.image = pygame.transform.rotate(self.image, angle)
        self.hit_s = pygame.mixer.Sound("hit.wav")
        self.who = who
    def get_size(self):
        return self._size
    def update(self, bricks, booms):
        self.rect.center = self.x, self.y
        self.x += -sin(radians(self.angle))*self.speed
        self.y += -cos(radians(self.angle))*self.speed

        for b in bricks:
            if self.rect.colliderect(b.rect):
                pygame.sprite.Sprite.kill(self)
                booms.add(Boom(self.rect.center, self._size))
                
class Boom(pygame.sprite.Sprite):
    def __init__(self, pos, size):
        pygame.sprite.Sprite.__init__(self)
        if size == "huge":
            self.life = 70
        if size == "large":
            self.life = 20
        if size == "big":
            self.life = 15
        if size == "small":
            self.life = 7
        
        self.blasts = []
        
        if size == "big":
            self.blasts.append(Blast(pos, self.life))
        else:
            for x in range(self.life*2):
                self.blasts.append(Fireball(pos, self.life))

    def update(self, background):

        if self.life <= 0:
            pygame.sprite.Sprite.kill(self)
        else:
            for blast in self.blasts:
                blast.update(background)
        self.life-=1

class Fireball(pygame.sprite.Sprite):
    def __init__(self, pos, life):
        size = random.randint(0,2)
        self.image = pygame.Surface([size, size])
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(pos)

        self.life = life
        self.maxlife = life

        self.vec_pos = [float(self.rect.center[0]), float(self.rect.center[1])]

        self.direc = [random.randint(1.0, 50.0)*(random.randint(0, 1)*2-1),random.randint(1.0,50.0)*(random.randint(0,1)*2-1)]
        self.mag = math.sqrt(self.direc[0]**2+self.direc[1]**2)
        self.speed = random.randint(1,100)/33.333

        self.direc[0] = self.direc[0]/self.mag*self.speed
        self.direc[1] = self.direc[1]/self.mag*self.speed

    def blend(self, life):
        green1= 255
        green2 = 0

        green = (self.life * 255) / self.maxlife

        return int(green)
 
    def update(self, background):

        self.life -= 1

        self.vec_pos = [self.vec_pos[0] + self.direc[0], self.vec_pos[1] + self.direc[1]]

        self.rect = self.rect.move(int(self.vec_pos[0])-self.rect.center[0],int(self.vec_pos[1])-self.rect.center[1])

        self.green = self.blend(self.life)

        self.image.fill([240, self.green * self.life/self.maxlife, 0])

        background.blit(self.image, self.rect)

class Blast(pygame.sprite.Sprite):
    def __init__(self, pos, life):
        self.size = life
        self.image = pygame.Surface((30,30))
        self.image.set_colorkey((0,0,0))
        pygame.draw.circle(self.image, (225,225,255), (15,15), life, 0)
        #self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect(center = pos)
        self.life = life
        self.alpha = 255

    def update(self, background):
        self.image.set_alpha(self.alpha)
        background.blit(self.image, self.rect)
        self.alpha -= self.life
        
  
