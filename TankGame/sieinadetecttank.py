import math
import pygame
import random
import pyfirmata2
import time
import subprocess
import sys
from pyfirmata2 import Arduino, util

#Arduino config
board = Arduino('com22')
it = util.Iterator(board)
it.start()
board.analog[0].enable_reporting()
board.analog[1].enable_reporting()
board.analog[2].enable_reporting()
board.analog[3].enable_reporting()
board.analog[4].enable_reporting()
board.analog[5].enable_reporting()

button1 = board.digital[2]
button1.mode = pyfirmata2.INPUT
tankki1nappi = button1
button2 = board.digital[4]
button2.mode = pyfirmata2.INPUT
tankki2nappi = button2

#pygame config
pygame.init()
size = width,height = 1200,600
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
pygame.mixer.init()

#Images
tankki1 = pygame.image.load('tankki.png')
tankki1 = pygame.transform.scale(tankki1,(80,100))

tankki2 = pygame.image.load('tankki2.png')
tankki2 = pygame.transform.scale(tankki2,(80,100))

tykki1 = pygame.image.load('tykki.png')
tykki1 = pygame.transform.scale(tykki1,(30,100))

tykki2 = pygame.image.load('tykki2.png')
tykki2 = pygame.transform.scale(tykki2,(30,100))

#Creates the Tank class 
class Tank:   
    def __init__(self,tankki,tykki,ohjain1,ohjain2,ohjain3,tankkiX,tankkiY,tankBtn):
        #Picture of the bullet 
        self.panos = pygame.image.load('panos.png')
        self.panos = pygame.transform.scale(self.panos,(15,30))
        
        self.Btn = tankBtn
        self.kaantyminen = 90
        self.kaantyminen2 = 90
        self.pauseliikkuminen = 0
        self.pausekaantyminen = 0
        
        self.tankki1 = tankki
        self.tykki1 = tykki
        
        self.pin1 = ohjain1
        self.pin2 = ohjain2
        self.pin3 = ohjain3
        
        self.x = tankkiX
        self.y = tankkiY
        self.oldX = 0
        self.oldY = 0

        self.bullets = []
        self.points = 0
        self.ammuttu = 0

    #Here is the code for the game
    def play(self):

        if(self.ammuttu > 0):
            self.ammuttu += 1
        if(self.ammuttu > 90):
            self.ammuttu = 0

        #Reads pins
        self.kulma = board.analog[self.pin1].read()
        self.kulma2 = board.analog[self.pin2].read()
        self.tykki = board.analog[self.pin3].read()
        self.tankkiBtn = self.Btn.read()
        
        #Counts where to move and how much
        if((self.kulma >0.45 and self.kulma < 0.55)) and (self.kulma2 >0.45 and self.kulma2 < 0.55):
            self.x += 0
            self.y += 0
            self.kaantyminen += 0
            self.kaantyminen2 += 0
            liikkuminen = self.kaantyminen2 - self.kaantyminen
        else:
            self.kaantyminen += (int(self.kulma * 180) - 90) * 0.01
            self.kaantyminen2 += (int(self.kulma2 * 180) - 90) * 0.01
            liikkuminen = self.kaantyminen2 - self.kaantyminen
            if(self.kulma + self.kulma2 < 1):
                self.x += (math.cos(math.radians(liikkuminen+90)))*-0.5
                self.y -= math.sin(math.radians(liikkuminen+90))*-0.5
            else:
                self.x += (math.cos(math.radians(liikkuminen+90)))*0.5
                self.y -= math.sin(math.radians(liikkuminen+90))*0.5
            drive = pygame.mixer.Sound("brr.mp3")
            drive.play()
            drive.set_volume(0.1)

        if(self.kaantyminen <= 0):
            self.kaantyminen += 360
        elif(self.kaantyminen >= 360):
            self.kaantyminen -= 360
        
        #Rotates the tank
        rotated_tankki1 = pygame.transform.rotate(self.tankki1, liikkuminen)
        new_tankki1 = rotated_tankki1.get_rect(center = tankki1.get_rect(center = (self.x,self.y)).center)
        
        #Rotates the cannon 
        rotated_tykki1 = pygame.transform.rotate(self.tykki1, liikkuminen + self.tykki*100-45)
        new_tykki1 = rotated_tykki1.get_rect(center = tankki1.get_rect(center = (self.x,self.y)).center)
        
        #Prints the tank onto the canvas
        screen.blit(rotated_tankki1, new_tankki1)
        
        #Shoots the bullet
        for b in range(len(self.bullets)):
            self.bullets[b][0] += math.cos(math.radians(self.pauseliikkuminen+self.pausekaantyminen+90))*12
            self.bullets[b][1] -= math.sin(math.radians(self.pauseliikkuminen+self.pausekaantyminen+90))*12
              
        if len(self.bullets) < 1:
            print(self.tankkiBtn)
            if(self.tankkiBtn != False and self.ammuttu == 0):
                self.ammuttu += 1
                self.pauseliikkuminen = liikkuminen
                self.pausekaantyminen = self.tykki*100-45
                self.bullets.append([self.x+math.cos(math.radians(self.pauseliikkuminen+self.pausekaantyminen+90))*70,self.y-math.sin(math.radians(self.pauseliikkuminen+self.pausekaantyminen+90))*70])
                shoot = pygame.mixer.Sound("pum.mp3")
                shoot.play()
                
        for bullet in self.bullets:
            rotated_panos = pygame.transform.rotate(self.panos,self.pauseliikkuminen + self.pausekaantyminen)
            self.panos_rect = rotated_panos.get_rect(center = self.tykki1.get_rect(center = (bullet[0],bullet[1])).center)
            screen.blit(rotated_panos, self.panos_rect)
        
        #Prints the cannon
        screen.blit(rotated_tykki1, new_tykki1)
        
taso = []

#Function that draws the stage
def draw(blockX,blockY,blockW,blockH):
    colors = pygame.Color("black")
    block = pygame.Rect(blockX,blockY,blockW,blockH)
    screen.fill(colors, block)
    taso.append(block)        

tank1_posX = 1000
tank1_posY = 200
tank2_posX = 200
tank2_posY = 200

#Assign classes
tank1 = Tank(tankki1,tykki1,0,1,2,tank1_posX,tank1_posY,tankki1nappi)
tank2 = Tank(tankki2,tykki2,3,4,5,tank2_posX,tank2_posY,tankki2nappi)
lapi  = 1 
while True:
    #Fills the canvas with light yellow RGB values
    screen.fill((244, 255, 176))
    font = pygame.font.SysFont("ubuntu", 25)
    score = font.render("Score", 1, (255,255,255))
    scorepoint = font.render("Tank 1: " + str(tank1.points) + "  ||  Tank 2: " + str(tank2.points), 1, (255,255,255))
    draw(500,0,225,75)
    screen.blit(score, (585, 15))
    screen.blit(scorepoint, (515, 40))

    #Plays the game
    tank2.play()
    tank1.play()
    tank1_rect = tank1.tankki1.get_rect(center=(tank1.x, tank1.y))
    tank2_rect = tank2.tankki1.get_rect(center=(tank2.x, tank2.y))

    #define what kind of blocks to draw
    taso.clear()
    draw(0,0,1200,20)
    draw(0,590,1200,20)
    draw(0,0,20,600)
    draw(1190,0,20,600)
    draw(400,0,20,400)
    draw(600,500,20,400)
    draw(800,0,20,400)
    draw(0,300,200,20)

    #Checks winner
    if(tank1.points == 10):
        draw(450,200,300,200)
        font = pygame.font.SysFont("ubuntu", 25)
        tan1 = font.render("Tank 1 WON!!", 1, (255,255,255))
        screen.blit(tan1, (525, 275))
        pygame.display.flip()
        #FPS limit
        clock.tick(60)
        time.sleep(5)
        subprocess.Popen(["python", "menu.py"])
        pygame.quit()
        sys.exit()
        
    elif(tank2.points == 10):
        draw(450,200,300,200)
        font = pygame.font.SysFont("ubuntu", 25)
        tan1 = font.render("Tank 2 WON!!", 1, (255,255,255))
        screen.blit(tan1, (525, 275))
        pygame.display.flip()
        #FPS limit
        clock.tick(60)
        time.sleep(5)
        subprocess.Popen(["python", "menu.py"])
        pygame.quit()
        sys.exit()
        
    #Tells which tank is which  
    if(lapi == 1):
        lapi += 1
        font = pygame.font.SysFont("ubuntu", 25)
        tan1 = font.render("Tank 1", 1, (128,128,128))
        screen.blit(tan1, (200, 100))
        font = pygame.font.SysFont("ubuntu", 25)
        tan2 = font.render("Tank 2", 1, (128,128,128))
        screen.blit(tan2, (980, 100))
        pygame.display.flip()
        #FPS limit
        clock.tick(60)
        time.sleep(2.5)

    #Checks if tank hit the wall
    for i in range(len(taso)):
        if tank1_rect.colliderect(taso[i]):
            tank1.x = tank1.oldX
            tank1.y = tank1.oldY
        if tank2_rect.colliderect(taso[i]):
            tank2.x = tank2.oldX
            tank2.y = tank2.oldY
    
    #Checks if tanks hit eachother and makes them stop
    if tank1_rect.colliderect(tank2_rect):
            tank1.x = tank1.oldX
            tank1.y = tank1.oldY

            tank2.x = tank2.oldX
            tank2.y = tank2.oldY

    #Check if bullets hit the other tank or the wall  
    for bullet in tank1.bullets:
        panos_rect = tank1.panos.get_rect(center=(bullet[0], bullet[1]))
        if tank2_rect.colliderect(panos_rect):
            tank1.points += 1
            tank1.bullets.clear()
            break
        for i in range(len(taso)):
            if panos_rect.colliderect(taso[i]):
                tank1.bullets.clear()

    for bullet in tank2.bullets:
        panos_rect = tank2.panos.get_rect(center=(bullet[0], bullet[1]))
        if tank1_rect.colliderect(panos_rect):
            tank2.points += 1
            tank2.bullets.clear()
            break
        for i in range(len(taso)):
            if panos_rect.colliderect(taso[i]):
                tank2.bullets.clear()
        
    tank1.oldX = tank1.x
    tank1.oldY = tank1.y
    tank2.oldX = tank2.x
    tank2.oldY = tank2.y

    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            subprocess.Popen(["python", "menu.py"])
            pygame.quit()
            sys.exit()
            
    pygame.display.flip()
    #FPS limit
    clock.tick(60)

    
            