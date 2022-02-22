
from __future__ import print_function, division
 
import pygame, os, sys
from pygame.locals import *
import random
import effects
from effects import *
import math
GRAD = math.pi / 180


class Brick(pygame.sprite.Sprite):
    
    def __init__(self, pos, image, top, bottom, right, left, bricks):

        pygame.sprite.Sprite.__init__(self)
        
        self.rect = image.get_rect(topleft = pos)
        self.image = image
        self.pos = pos
        self.top = top
        self.bottom = bottom
        self.right = right
        self.left = left
        self.health = 30
        bricks.add(self)
            
            
class City(object):
    def __init__(self, bricks, level):

        self.level = level
        
        self.city =  self.level.convert_alpha()  
            
        self.brick = pygame.image.load("brick.png").convert_alpha()
        self.bricks = bricks
        
        self.x = self.y = 0
        collidable = (255, 0, 0, 255)
        self.height = self.city.get_height()
        self.width = self.city.get_width()
        self.vehicle_pos = (0,0)

        while self.y < self.height:
            color = self.city.get_at((self.x, self.y))
            collidable =  (255, 0, 0, 255), (0,0,0,255)
            top = False
            bottom = False
            right = False
            left = False
            if color in collidable:
                if self.y > 0:
                    if self.city.get_at((self.x, self.y-1)) not in collidable:
                        top = True
                if self.y < self.height-1:
                    if self.city.get_at((self.x, self.y+1)) not in collidable:
                        bottom = True
                if self.x > 0:
                    if self.city.get_at((self.x-1, self.y)) not in collidable:
                        left = True
                if self.x < self.width-1:
                    if self.city.get_at((self.x+1, self.y)) not in collidable:
                        right = True
                self.bricks.add(Brick((self.x*30, self.y*30), self.brick, top, bottom, right, left, self.bricks))
                #print ("brick added!")
                #print (self.x, self.y)

                
            self.x += 1

            if self.x >= self.width:
                self.x = 0
                self.y += 1

    def get_size(self):
        return [self.city.get_size()[0]*30, self.city.get_size()[1]*30]
    

class Tank(pygame.sprite.Sprite):
    book = {} # a book of tanks to store all tanks
    number = 0 # each tank gets his own number
    
    firekey = (pygame.K_SPACE, pygame.K_RETURN)
    forwardkey = (pygame.K_w, pygame.K_i)
    backwardkey = (pygame.K_s, pygame.K_k)
    tankLeftkey = (pygame.K_a, pygame.K_j)
    tankRightkey = (pygame.K_d, pygame.K_l)
    
    color = ((200,200,0), (0,0,200))
    
    def __init__(self, pos, angle, health):
        self.pos = pos
        self.ammo = 150
        self.number = Tank.number
        Tank.number += 1
        Tank.book[self.number] = self
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.tank_pic = pygame.image.load("tank2.png").convert_alpha()
        self.image = self.tank_pic
        self.image_type = self.tank_pic
        self._image = self.image
        self.rect = self.image.get_rect()
        self.rect = self.rect.move(pos)
        self.tankAngle = angle # tank facing

        #---handles controls---#
        
        self.firekey = Tank.firekey[self.number] # main gun
        self.forwardkey = Tank.forwardkey[self.number] # move tank
        self.backwardkey = Tank.backwardkey[self.number] # reverse tank
        self.tankLeftkey = Tank.tankLeftkey[self.number] # rotate tank
        self.tankRightkey = Tank.tankRightkey[self.number] # rotat tank


        self.health = health
        self.alive = True
        self.speed = 5
        self.angle = angle
        self.timer = 3
        self.timerstart = 0
        self.x, self.y = self.rect.center
        self.bullet_s = pygame.mixer.Sound("bullet.wav")
        self.bullet_s.set_volume(.25)
        
    def rotate(self):
        center = self.rect.center
        self.image = pygame.transform.rotozoom(self._image, self.angle, 1.0)
        self.rect = self.image.get_rect(center = center)
        
    def update(self, keys, bricks, bullets, booms, bombs):
        self.bricks = bricks
        self.t = True
        self._rect = Rect(self.rect)
        self._rect.center = self.x, self.y
        self.rotate()
        turn_speed = 3


        pressedkeys = pygame.key.get_pressed()

        if pressedkeys[self.forwardkey]:
            self.x += sin(radians(self.angle))*-self.speed
            self.y += cos(radians(self.angle))*-self.speed
        if pressedkeys[self.backwardkey]:
            self.x += sin(radians(self.angle))*self.speed
            self.y += cos(radians(self.angle))*self.speed
        if pressedkeys[self.tankLeftkey]:
            self.angle += turn_speed
        if pressedkeys[self.tankRightkey]:
            self.angle -= turn_speed
        if keys[self.firekey]:
            if self.timer >= 3:
                self.timer = self.timerstart
                self.b_size = "small"
                if self.ammo >= 0:
                    if self.number == 0:
                        bullets.add(Bullet((self.rect.center[0], self.rect.center[1]) , self.angle, self.b_size, "vehicle", 0))
                        self.ammo -= 1
                    elif self.number == 1:
                        bullets.add(Bullet((self.rect.center[0], self.rect.center[1]) , self.angle, self.b_size, "vehicle", 1))
                        self.ammo -= 1
                    self.bullet_s.play()
                
        if self.timer < 3:
            self.timer += 1

        if self.angle > 360:
            self.angle = self.angle-360
        if self.angle <0:
            self.angle = self.angle+360

        self.rect.center = self.x, self.y

        x = self.rect.centerx
        y = self.rect.centery
        _x = self._rect.centerx
        _y = self._rect.centery
        for b in bricks:
            if self.rect.colliderect(b.rect):
                if _x+21 <= b.rect.left and x+21 > b.rect.left:
                    if b.left == True:
                        self.x = b.rect.left-21
                if _x-21 >= b.rect.right and x-21 < b.rect.right:
                    if b.right == True:
                        self.x = b.rect.right+21
                if _y+21 <= b.rect.top and y+21 > b.rect.top:
                    if b.top == True:
                        self.y = b.rect.top-21
                if _y-21 >= b.rect.bottom and y-21 < b.rect.bottom:
                    if b.bottom == True:
                        self.y = b.rect.bottom+21
                    
        for b in bullets:
            if self.rect.colliderect(b.rect):
                b_size = b.get_size()
                if self.number == 0 and b.tank == 1:
                    pygame.sprite.Sprite.kill(b)
                    if b_size == "small":
                        booms.add(Boom(b.rect.center, "small"))
                        self.health -= 1
                    if b_size == "big":
                        booms.add(Boom(b.rect.center, "big"))
                        self.health -=5
                elif self.number == 1 and b.tank == 0:
                    pygame.sprite.Sprite.kill(b)
                    if b_size == "small":
                        booms.add(Boom(b.rect.center, "small"))
                        self.health -= 1
                    if b_size == "big":
                        booms.add(Boom(b.rect.center, "big"))
                        self.health -=5

        for b in bombs:
            if self.rect.colliderect(b.rect) and b.timer == 20:
                self.health -=5

        if self.health <= 0:
            booms.add(Boom(self.rect.center, "huge"))
            self.alive = False
            self.health = 0
            if self.number == 1:
                pygame.sprite.Sprite.kill(Tank.book[1])
            elif self.number == 2:
                pygame.sprite.Sprite.kill(Tank.book[0])
                
               

# ---------- END OF CLASSES ---------- #


pygame.init()
version = "Tank Wars 2.0"
screen = pygame.display.set_mode((1170, 510),0,32)
health = 40
health_full = health
bricks= pygame.sprite.Group()
bullets = pygame.sprite.Group()
booms = pygame.sprite.Group()
bombers = pygame.sprite.Group()
bombs = pygame.sprite.Group()
tanks = pygame.sprite.Group()
allgroup = pygame.sprite.LayeredUpdates()
Tank.groups = tanks, allgroup
keys = pygame.key.get_pressed()
Bullet.groups = bullets, allgroup
player1 = Tank((150, 250), 360, 40)
player2 = Tank((1050, 248), 360, 40)

    
map_ = pygame.image.load("c2.png")
city = City(bricks, map_)
city_size = city.get_size()
background = pygame.Surface((city_size), 0, 32)

def newlevel():
    bricks.empty()
    tanks.empty()
    bullets.empty()
    booms.empty() 
    map_ = pygame.image.load("a2.png")
    city = City(bricks, map_)
    city_size = city.get_size()
    city.bricks.draw(screen)
    player1.alive = True
    player2.alive = True
    player1.ammo = 150
    player2.ammo = 150
    player1.health = health
    player2.health = health
    player1.angle = 360
    player2.angle = 360
    player1.x = 105
    player1.y = 300
    player2.x = 1100
    player2.y = 230
    player1.rect = player1.rect.move(150, 250)
    player2.rect = player2.rect.move(1100, 248)
    
 
    
    
    
def main():
    pygame.init()
    version = "Tank Wars 2.0"
    pygame.display.set_caption("Tank Wars 2.0")
    screen = pygame.display.set_mode((1170, 510),0,32)
    levelnum = 1
    size = screen.get_size()
    pygame.mouse.set_visible(False)
    health = 40
    health_full = health
    clock = pygame.time.Clock()
    timer = 0
    player1count = 0
    player2count = 0
    chance = None
    score = 0
    font4 = pygame.font.Font("7theb.ttf", 13)
    font5 = pygame.font.SysFont("Courier New", 16, bold=True)

    while True:
        screen.fill((0,0,0))
        if player1.alive == False and levelnum == 1:
            notalive = 1
            levelnum += 1
            allgroup.clear(screen, background)
            tanks.clear(screen,background)
            bullets.clear(screen, background)
            allgroup.empty()
            font = pygame.font.Font("7theb.ttf", 40)
            screen.fill((0, 0, 0))
            text = font.render("Player 2 Wins Level 1 !", 1, (255,255,255))
            player2count += 1
            textrect = text.get_rect()
            textrect.centerx, textrect.centery = size[0]/2, size[1]/2
            screen.blit(text, textrect)
            pygame.display.flip() # make everything we have drawn on the screen become visible in the window
            pygame.time.wait(1000)
            newlevel()
        if player2.alive == False and levelnum == 1:
            notalive = 2
            levelnum += 1
            allgroup.clear(screen, background)
            tanks.clear(screen,background)
            bullets.clear(screen, background)
            allgroup.empty()
            font = pygame.font.Font("7theb.ttf", 40)
            screen.fill((0, 0, 0))
            text = font.render("Player 1 Wins Level 1 !", 1, (255,255,255))
            player1count += 1
            textrect = text.get_rect()
            textrect.centerx, textrect.centery = size[0]/2, size[1]/2
            go = True
            screen.blit(text, textrect)
            pygame.display.flip() # make everything we have drawn on the screen become visible in the window
            pygame.time.wait(1000)
            newlevel()
        if player1.alive == False and levelnum == 2:
            player2count += 1
            font = pygame.font.Font("7theb.ttf", 40)
            screen.fill((0, 0, 0))
            text = font.render("Player 2 Wins Level 2 !", 1, (255,255,255))
            textrect = text.get_rect()
            textrect.centerx, textrect.centery = size[0]/2, size[1]/2
            screen.blit(text, textrect)
            pygame.display.flip() # make everything we have drawn on the screen become visible in the window
            pygame.time.wait(1000)
            if player2count > player1count:
                screen.fill((0, 0, 0))
                text2 = font.render("Player 2 Wins! Game Over!", 1, (255,255,255))
                textrect2  = text2.get_rect()
                textrect2.centerx, textrect2.centery = size[0]/2, size[1]/2
                screen.blit(text2, textrect2)
                pygame.display.flip() # make everything we have drawn on the screen become visible in the window
                pygame.time.wait(1000)
                pygame.quit()
                sys.exit()
            else:
                screen.fill((0, 0, 0))
                text2 = font.render("It's a tie! Game Over!", 1, (255,255,255))
                textrect2  = text2.get_rect()
                textrect2.centerx, textrect2.centery = size[0]/2, size[1]/2
                screen.blit(text2, textrect2)
                pygame.display.flip() # make everything we have drawn on the screen become visible in the window
                pygame.time.wait(1000)
                pygame.quit()
                sys.exit()
        if player2.alive == False and levelnum == 2:
            player1count += 1
            font = pygame.font.Font("7theb.ttf", 40)
            screen.fill((0, 0, 0))
            text = font.render("Player 1 Wins Level 2 !", 1, (255,255,255))
            textrect = text.get_rect()
            textrect.centerx, textrect.centery = size[0]/2, size[1]/2
            screen.blit(text, textrect)
            pygame.display.flip() # make everything we have drawn on the screen become visible in the window
            pygame.time.wait(1000)
            if player1count > player2count:
                screen.fill((0, 0, 0))
                text2 = font.render("Player 1 Wins! Game Over!", 1, (255,255,255))
                textrect2 = text2.get_rect()
                textrect2.centerx, textrect2.centery = size[0]/2, size[1]/2
                screen.blit(text2, textrect2)
                pygame.display.flip() # make everything we have drawn on the screen become visible in the window
                pygame.time.wait(1000)
                pygame.quit()
                sys.exit()
                
            else:
                screen.fill((0, 0, 0))
                text2 = font.render("It's a tie! Game Over!", 1, (255,255,255))
                textrect2 = text2.get_rect()
                textrect2.centerx, textrect2.centery = size[0]/2, size[1]/2
                screen.blit(text2, textrect2)
                pygame.display.flip() # make everything we have drawn on the screen become visible in the window
                pygame.time.wait(1000)
                pygame.quit()
                sys.exit()
            

           
            
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
        
        

        clock.tick(24),
        time_passed = clock.tick()
        keys = pygame.key.get_pressed()
        m_x, m_y = pygame.mouse.get_pos()

            
        city.bricks.draw(screen)

        healthshow = font4.render('Health ', False, (255,255,255))

        #---Player 1 Healthbar---#
        
        pygame.draw.ellipse(screen, (255, ((player1.health*255)/health_full),0), (90, 20, 10, 13))
        pygame.draw.ellipse(screen, (255, ((player1.health*255)/health_full),0), (92+(100*(float(player1.health)/float(health_full))), 20, 10, 13))
        screen.fill((255,((player1.health*255)/health_full),0),(96,20,(100*(float(player1.health)/float(health_full))), 13))
        screen.blit(healthshow, (5, 20))

        #---Player 2 Healthbar---#

        pygame.draw.ellipse(screen, (255, ((player2.health*255)/health_full),0), (594, 20, 10, 13))
        pygame.draw.ellipse(screen, (255, ((player2.health*255)/health_full),0), (596+(100*(float(player2.health)/float(health_full))), 20, 10, 13))
        screen.fill((255,((player2.health*255)/health_full),0),(600,20,(100*(float(player2.health)/float(health_full))), 13))
        screen.blit(healthshow, (500, 20))


        if player1.alive == True:
            player1.update(keys, bricks, bullets, booms, bombs)
            screen.blit(player1.image, player1.rect)
            
        if player2.alive == True:
            player2.update(keys, bricks, bullets, booms, bombs)
            screen.blit(player2.image, player2.rect)

        bullets.update(bricks, booms)
        bombs.update(booms, player1)
        bombs.update(booms, player2)
        booms.update(screen)
        bombs.draw(screen)
        bullets.draw(screen)
        bombers.draw(screen)

            

        pygame.display.flip()
        timer += 1
        


 


if __name__ == "__main__":
    main()

#Things to add:
#1) Several maps: when one plays dies, calls newlevel() method that creates a new map, clears old map, and draws sprites back (see newlevel() in other)
#2) Two kinds of bullets: one more powerful (laser animation/different colour, faster, bigger boom)
#3) Game Menu (implement old menu)
#4) Drones (?)
#5) Random dropping power-ups (more health (repair), speed boost, double damage bullets)
