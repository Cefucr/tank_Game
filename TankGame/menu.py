import pygame
import pygame_menu
import sys
import subprocess

size = width,height = 600,400
screen = pygame.display.set_mode(size)
github_kuva = pygame.image.load('github.png')
github_kuva = pygame.transform.scale(github_kuva,(100,100))
pygame.init()
pygame.display.set_caption('Tankkipeli')
 
menu = pygame_menu.Menu("Tankkipeli", 600, 400, theme=pygame_menu.themes.THEME_GREEN)
 
def tankkipeli():
    subprocess.Popen(["python", "sieinadetecttank.py"])
    pygame.quit()
    sys.exit()

def lopeta():
    pygame.quit()
    sys.exit()
 
menu.add.button("Pelaa", tankkipeli)
menu.add.button("Lopeta", lopeta)
 
myfont = pygame.font.SysFont("ubuntu", 25)
label = myfont.render("Made by: @Unn0o & @Cefucr ©", 1, (0,0,0))
 
 
while True:
    events = pygame.event.get()
    menu.update(events)
    menu.draw(screen)
    screen.blit(label, (10, 360))
    screen.blit(github_kuva, (20, 230))
 
    pygame.display.update()
 