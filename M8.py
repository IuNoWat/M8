import sys
import random
import time

import pygame
pygame.font.init()

import gpiozero as gpio
import rpi_ws281x as rpi
strip = rpi.PixelStrip(40,18)
strip.begin()

for i in range(0,40) :
    for j in range(0,40) :
        strip.setPixelColor(j,rpi.Color(0,0,0))
    strip.setPixelColor(i,rpi.Color(255,255,255))
    strip.show()
    time.sleep(0.5)

class Leds() :
    def __init__(self,strip) :
        self.strip=strip
        self.count=0
    def step(self) :
        for i in range(0,40) :
            self.strip.setPixelColor(i,rpi.Color(0,0,0))
        if self.count>0 :
            self.count=self.count-1
            for i in range(0,40) :
                self.strip.setPixelColor(i,rpi.Color(255,255,255))
        self.strip.show()

from tools import *

#CONSTANTS
FPS=30
SCREEN_SIZE=(1600, 900)
FULLSCREEN=True
BTN_TIMEOUT=10
DIR="/home/pi/Desktop/M8/"

try :
    if sys.argv[1]=="debug" :
        DEBUG=True
except IndexError :
    DEBUG=False

GPIO_y="BOARD8"
GPIO_g="BOARD10"
GPIO_b="BOARD12"


#STYLE
WHITE=pygame.Color("White")
BLACK=pygame.Color("Black")
GREEN=pygame.Color("Green")
RED=pygame.Color("Red")
COLOR_BG=pygame.Color(242,193,202,255)
COLOR_HL=pygame.Color(255,255,255,255)

debug_font=pygame.font.Font('freesansbold.ttf',16)


#ASSETS
select = pygame.image.load(DIR+"assets/select.png")
trash = pygame.image.load(DIR+"assets/trash.png")
y0=pygame.image.load(DIR+"assets/y_0.png")
y1=pygame.image.load(DIR+"assets/y_1.png")
g0=pygame.image.load(DIR+"assets/g_0.png")
g1=pygame.image.load(DIR+"assets/g_1.png")
b0=pygame.image.load(DIR+"assets/b_1.png")
b1=pygame.image.load(DIR+"assets/b_0.png")

#ENGINE

class Trash() :
    def __init__(self,img,good_value,txt) :
        self.img=img
        self.good_value=good_value
        self.txt=txt
    def check_value(self,btn) :
        if btn==self.good_value :
            return True
        else :
            return False

class Anim() :
    def __init__(self,max_frame) :
        self.max_frame=max_frame
        self.current_frame=0
        self.method=print
        self.finished=False
    def anim(self) :
        self.method(self.current_frame)
        self.current_frame=self.current_frame+1
        if self.current_frame==self.max_frame :
            self.finished=True

class Pop(Anim) :
    def moove(self,current_frame) :
        self.img.set_alpha(255-current_frame*16)
        center_blit(SCREEN,self.img,(self.pos[0],self.pos[1]-current_frame*3))
    def __init__(self,max_frame,img,pos) :
        Anim.__init__(self,max_frame)
        self.img=img
        self.pos=pos
        self.method=self.moove
    def anim(self) :
        print(self.current_frame)
        Anim.anim(self)

trashs=[
    Trash(y0,"y","Ceci est le déchet y0"),
    Trash(y1,"y","Ceci est le déchet y1"),
    Trash(g0,"g","Ceci est le déchet g0"),
    Trash(g1,"g","Ceci est le déchet g1"),
    Trash(b0,"b","Ceci est le déchet b0"),
    Trash(b1,"b","Ceci est le déchet b1"),
]

CURRENT_TRASH=trashs[0]
TIMEOUT=0
ANIMATIONS=[]
LED_HANDLER=Leds(strip)

def new_trash() :
    global CURRENT_TRASH
    new=random.choice(trashs)
    while new==CURRENT_TRASH :
        new=random.choice(trashs)
    CURRENT_TRASH=new

def pressed(btn) :
    global CURRENT_TRASH
    global TIMEOUT
    global ANIMATIONS
    global LED_HANDLER
    if TIMEOUT==0 :
        TIMEOUT=BTN_TIMEOUT
        LED_HANDLER.count=20
        if CURRENT_TRASH.check_value(btn) :
            ANIMATIONS.append(Pop(15,debug_font.render("Gagné !",1,BLACK,COLOR_BG),(800,450-200)))
        else :
            ANIMATIONS.append(Pop(15,debug_font.render("Perdu !",1,BLACK,COLOR_BG),(800,450-200)))
        new_trash()

def pressed_y(arg) :
    pressed("y")

def pressed_g(arg) :
    pressed("g")

def pressed_b(arg) :
    pressed("b")
    
    

btn_y=gpio.Button(GPIO_y)
btn_g=gpio.Button(GPIO_g)
btn_b=gpio.Button(GPIO_b)

btn_y.when_pressed = pressed_y
btn_g.when_pressed = pressed_g
btn_b.when_pressed = pressed_b


#MAINLOOP PREPARATION
on=True
SCREEN = pygame.display.set_mode(SCREEN_SIZE,pygame.FULLSCREEN)
CLOCK = pygame.time.Clock()

#MAINLOOP

while on :
    #Cleaning of Screen
    SCREEN.fill(COLOR_BG)

    #Event handling
    for event in pygame.event.get():
        keys = pygame.key.get_pressed()
        if event.type == pygame.QUIT:
            on = False
        if keys[pygame.K_ESCAPE] : # ECHAP : Quitter
            on=False

    #Show current trash
    center_blit(SCREEN,CURRENT_TRASH.img,(SCREEN_SIZE[0]/2,SCREEN_SIZE[1]/2))

    if TIMEOUT>0 :
        TIMEOUT-=1
    
    for i,animation in enumerate(ANIMATIONS) :
        animation.anim()
        if animation.finished :
            ANIMATIONS.pop(i)

    LED_HANDLER.step()

    #Show DEBUG
    if DEBUG :
        fps = str(round(CLOCK.get_fps(),1))
        btns_status=f"y : {str(btn_y.is_pressed)}"+f" g : {str(btn_g.is_pressed)}"+f" b : {str(btn_b.is_pressed)}"+f" TIMEOUT : {str(TIMEOUT)}"+f" LED COUNT : {str(LED_HANDLER.count)}"
        txt = "DEBUG MODE | FPS : "+fps+f" | Button values : {btns_status}"
        to_blit=debug_font.render(txt,1,WHITE,COLOR_BG)
        SCREEN.blit(to_blit,(0,0))

    #End of loop
    pygame.display.flip()
    CLOCK.tick(FPS) 
