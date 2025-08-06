import sys
import random
import time
import os

import pygame
pygame.font.init()
import gpiozero as gpio
import rpi_ws281x as rpi

import BB

pygame.mixer.init()


from tools import *

#CONSTANTS
FPS=30
DIR="/home/pi/Desktop/M8/"
SCREEN_SIZE=(1600, 900)
SCREEN = pygame.display.set_mode(SCREEN_SIZE,pygame.FULLSCREEN)
FULLSCREEN=True
BALL_RADIUS=100

#Define DEBUG
try :
    if sys.argv[1]=="debug" :
        DEBUG=True
except IndexError :
    DEBUG=False

#LED CONSTANTS
LED_y=[0,1,2,3,4,5,6,7,8]
LED_g=[14,15,16,17,18,19,20,21,22]
LED_b=[34,35,36,37,38,39,40,41,42,43]
LED_r=[53,54,55,56,57,58,59,60]
LED_p=[67,68,69,70,71,72,73,74,75,76]

#GPIO CONSTANTS
GPIO_y="BOARD18"
GPIO_g="BOARD16"
GPIO_b="BOARD22"
GPIO_r="BOARD10" 
GPIO_p="BOARD8"
GPIO_start="BOARD32"
GPIO_led=18

#Engine CONSTANTS in frame
BTN_TIMEOUT=10
TRASH_CHANGE=90

#Animation CONSTANTS

#STYLE
WHITE=pygame.Color("White")
BLACK=pygame.Color("Black")
GREEN=pygame.Color("Green")
RED=pygame.Color("Red")
BLUE=pygame.Color("Blue")
COLOR_BG=pygame.Color(242,193,202,255)
COLOR_HL=pygame.Color(255,255,255,255)

debug_font=pygame.font.Font('freesansbold.ttf',14)
score_font=pygame.font.Font('freesansbold.ttf',48)

#ASSETS
select = pygame.image.load(DIR+"assets/img/select.png").convert_alpha()
trash = pygame.image.load(DIR+"assets/img/trash.png").convert_alpha()
intro = pygame.image.load(DIR+"assets/img/intro.png").convert_alpha()
panel = pygame.image.load(DIR+"assets/img/panel.png").convert_alpha()
y0=pygame.image.load(DIR+"assets/img/y_0.png").convert_alpha()
y1=pygame.image.load(DIR+"assets/img/y_1.png").convert_alpha()
g0=pygame.image.load(DIR+"assets/img/g_0.png").convert_alpha()
g1=pygame.image.load(DIR+"assets/img/g_1.png").convert_alpha()
b0=pygame.image.load(DIR+"assets/img/b_1.png").convert_alpha()
b1=pygame.image.load(DIR+"assets/img/b_0.png").convert_alpha()

pop_1=pygame.mixer.Sound(DIR+"assets/sound/pop_1.mp3")
pop_1=pygame.mixer.Sound(DIR+"assets/sound/pop_2.mp3")
pop_1=pygame.mixer.Sound(DIR+"assets/sound/pop_3.mp3")
short_good_1=pygame.mixer.Sound(DIR+"assets/sound/low_fb_pos.wav")
shot_bad_1=pygame.mixer.Sound(DIR+"assets/sound/low_fb_neg.wav")
long_good_1=pygame.mixer.Sound(DIR+"assets/sound/chord_fb_pos.wav")
long_bad_1=pygame.mixer.Sound(DIR+"assets/sound/chord_fb_neg.wav")


ball_y0=pygame.transform.scale(y0,(BALL_RADIUS*2,BALL_RADIUS*2))
ball_y1=pygame.transform.scale(y1,(BALL_RADIUS*2,BALL_RADIUS*2))
ball_g0=pygame.transform.scale(g0,(BALL_RADIUS*2,BALL_RADIUS*2))
ball_g1=pygame.transform.scale(g1,(BALL_RADIUS*2,BALL_RADIUS*2))
ball_b0=pygame.transform.scale(b0,(BALL_RADIUS*2,BALL_RADIUS*2))
ball_b1=pygame.transform.scale(b1,(BALL_RADIUS*2,BALL_RADIUS*2))

#ENGINE

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
        self.img.set_alpha(255-current_frame*12)
        center_blit(SCREEN,self.img,(self.pos[0],self.pos[1]-current_frame*3))
    def __init__(self,max_frame,img,pos) :
        Anim.__init__(self,max_frame)
        self.img=img
        self.pos=pos
        self.method=self.moove
    def anim(self) :
        print(self.current_frame)
        Anim.anim(self)

#Led Handler
class Leds() :
    def __init__(self,pin,nb_of_leds) :
        self.nb_of_leds=nb_of_leds
        self.strip=rpi.PixelStrip(nb_of_leds,pin)
        self.strip.begin()
        #Colors
        self.WHITE=rpi.Color(255,255,255)
        self.BLACK=rpi.Color(0,0,0)
        self.RED=rpi.Color(255,0,0)
        self.GREEN=rpi.Color(0,255,0)
        self.BLUE=rpi.Color(0,0,255)
        self.YELLOW=rpi.Color(255,255,0)
        self.PURPLE=rpi.Color(255,0,255)
        # Tests de marron self.PURPLE=rpi.Color(200,140,10)
        #Engine value
        self.current_mode=False
        self.count=0
        self.current_color=self.WHITE
    def test(self) :
        for i in range(0,self.nb_of_leds) :
            for j in range(0,self.nb_of_leds) :
                self.strip.setPixelColor(j,self.BLACK)
            self.strip.setPixelColor(i,self.WHITE)
            self.strip.show()
            print(i)
            time.sleep(0.01)
    def base_colors(self) :
        for i in LED_y :
            self.strip.setPixelColor(i,self.YELLOW)
        for i in LED_g :
            self.strip.setPixelColor(i,self.GREEN)
        for i in LED_b :
            self.strip.setPixelColor(i,self.BLUE)
        for i in LED_r :
            self.strip.setPixelColor(i,self.RED)
        for i in LED_p :
            self.strip.setPixelColor(i,self.PURPLE)
    def step(self) :
        for i in range(0,self.nb_of_leds) :
            self.strip.setPixelColor(i,self.BLACK)
            self.base_colors()
        if self.current_mode!=False :
            match self.current_mode :
                case "flash" :
                    self.flash()
                case _ :
                    pass
        self.strip.show()
    def set_mode_flash(self,color) :
        self.count=5
        self.current_color=color
        self.current_mode="flash"
    def flash(self) :
        self.count=self.count-1
        for i in range(0,self.nb_of_leds) :
            self.strip.setPixelColor(i,self.current_color)
        if self.count<=0 :
            self.current_mode=False

#SPECIFIC ENGINE

class Trash() :
    def __init__(self,img,ball,good_value,txt) :
        self.img=img
        self.ball=ball
        self.good_value=good_value
        self.txt=txt
    def check_value(self,btn) :
        if btn==self.good_value :
            return True
        else :
            return False

def new_trash() :
    global CURRENT_TRASH
    global TRASH_CHANGE_COUNTER
    global DIFFICULTY
    new=random.choice(trashs)
    while new==CURRENT_TRASH :
        new=random.choice(trashs)
    CURRENT_TRASH=new
    TRASH_CHANGE_COUNTER=TRASH_CHANGE-DIFFICULTY
    if TRASH_CHANGE>3 :
        DIFFICULTY+=1

def pressed(btn) :
    global CURRENT_TRASH
    global BTN_TIMEOUT_COUNTER
    global ANIMATIONS
    global LED_HANDLER
    global TRASH_CHANGE_COUNTER
    global SCORE
    global GOOD
    global BAD
    if BTN_TIMEOUT_COUNTER==0 :
        BTN_TIMEOUT_COUNTER=BTN_TIMEOUT
        if btn=="y" :
            LED_HANDLER.set_mode_flash(LED_HANDLER.YELLOW)
        if btn=="g" :
            LED_HANDLER.set_mode_flash(LED_HANDLER.GREEN)
        if btn=="b" :
            LED_HANDLER.set_mode_flash(LED_HANDLER.BLUE)
        if btn=="r" :
            LED_HANDLER.set_mode_flash(LED_HANDLER.RED)
        if btn=="p" :
            LED_HANDLER.set_mode_flash(LED_HANDLER.PURPLE)
        if CURRENT_TRASH.check_value(btn) :
            ANIMATIONS.append(Pop(20,score_font.render("+1 !",1,BLUE,COLOR_BG),(800,450-225)))
            GOOD+=1
        else :
            ANIMATIONS.append(Pop(20,score_font.render("-1 !",1,RED,COLOR_BG),(800,450-225)))
            BAD+=1
        new_trash()

def pressed_y(arg) :
    pressed("y")
    print("y")

def pressed_g(arg) :
    pressed("g")
    print("g")

def pressed_b(arg) :
    pressed("b")
    print("b")

def pressed_r(arg) :
    pressed("r")
    print("r")

def pressed_p(arg) :
    pressed("p")
    print("p")

def pressed_start(arg) :
    global IDLE
    if IDLE :
        IDLE=False
    if END :
        reset()
    print("start")

trashs=[
    Trash(y0,ball_y0,"y","Ceci est le déchet y0"),
    Trash(y1,ball_y1,"y","Ceci est le déchet y1"),
    Trash(g0,ball_g0,"g","Ceci est le déchet g0"),
    Trash(g1,ball_g1,"g","Ceci est le déchet g1"),
    Trash(b0,ball_b0,"b","Ceci est le déchet b0"),
    Trash(b1,ball_b1,"b","Ceci est le déchet b1"),
]

#MAINLOOP PREPARATION
on=True

CLOCK = pygame.time.Clock()

#Initializing leds handler
LED_HANDLER=Leds(GPIO_led,120)
LED_HANDLER.test()

#Initializing Engine constants
CURRENT_TRASH=trashs[0]
BTN_TIMEOUT_COUNTER=0
TRASH_CHANGE_COUNTER=TRASH_CHANGE
DIFFICULTY=0
ANIMATIONS=[]
SCORE=0
GOOD=0
BAD=0
IDLE=True
END=False
BALLS=BB.BouncyBalls(SCREEN,FPS,radius=BALL_RADIUS)

def reset() :
    global CURRENT_TRASH
    global BTN_TIMEOUT_COUNTER
    global TRASH_CHANGE_COUNTER
    global DIFFICULTY
    global ANIMATIONS
    global SCORE
    global GOOD
    global BAD
    global IDLE
    global END
    global BALLS
    CURRENT_TRASH=trashs[0]
    BTN_TIMEOUT_COUNTER=0
    TRASH_CHANGE_COUNTER=TRASH_CHANGE
    DIFFICULTY=0
    ANIMATIONS=[]
    SCORE=0
    GOOD=0
    BAD=0
    IDLE=True
    END=False
    BALLS=BB.BouncyBalls(SCREEN,FPS,radius=BALL_RADIUS)

#Connections buttons to methods
btn_y=gpio.Button(GPIO_y)
btn_g=gpio.Button(GPIO_g)
btn_b=gpio.Button(GPIO_b)
btn_r=gpio.Button(GPIO_r)
btn_p=gpio.Button(GPIO_p)
btn_start=gpio.Button(GPIO_start)
btn_y.when_pressed = pressed_y
btn_g.when_pressed = pressed_g
btn_b.when_pressed = pressed_b
btn_r.when_pressed = pressed_r
btn_p.when_pressed = pressed_p
btn_start.when_pressed = pressed_start

rad=6.28/TRASH_CHANGE



#MAINLOOP
SCREEN.fill(COLOR_BG)
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
    if IDLE :
        center_blit(SCREEN,intro,(SCREEN_SIZE[0]/2,SCREEN_SIZE[1]/2))
        LED_HANDLER.step()
    elif END :
        center_blit(SCREEN,panel,(SCREEN_SIZE[0]/2,SCREEN_SIZE[1]/2))
        center_blit(SCREEN,score_font.render("BRAVO !",1,BLACK,COLOR_BG),(SCREEN_SIZE[0]/2,250))
        center_blit(SCREEN,score_font.render("Tu as tenu "+str(round(SCORE/30))+" secondes !",1,BLACK,COLOR_BG),(SCREEN_SIZE[0]/2,400))
        center_blit(SCREEN,score_font.render("Tu as trié "+str(GOOD)+" déchets !",1,BLACK,COLOR_BG),(SCREEN_SIZE[0]/2,500))
        center_blit(SCREEN,score_font.render("Pour recommencer, appuie sur le bouton jaune !",1,BLACK,COLOR_BG),(SCREEN_SIZE[0]/2,600))
        LED_HANDLER.step()
    else :
        #Add background
        center_blit(SCREEN,trash,(SCREEN_SIZE[0]/2,SCREEN_SIZE[1]/2))



        #Show change countdown
        pygame.draw.arc(SCREEN,BLACK,(SCREEN_SIZE[0]/2-190,SCREEN_SIZE[1]/2-190,380,380),1.5,1.5+TRASH_CHANGE_COUNTER*rad,20)

        #Show current trash
        center_blit(SCREEN,CURRENT_TRASH.img,(SCREEN_SIZE[0]/2,SCREEN_SIZE[1]/2))

        #Show couvercle
        #pygame.draw.circle(SCREEN,BLACK,(SCREEN_SIZE[0]/2,SCREEN_SIZE[1]/2),180,int(TRASH_CHANGE_COUNTER*1.5))

        #Show Score
        center_blit(SCREEN,score_font.render("SCORE : "+str(SCORE),1,BLACK,COLOR_BG),(SCREEN_SIZE[0]/2,100))

        #Handle trash counter
        if TRASH_CHANGE_COUNTER==0 :
            ANIMATIONS.append(Pop(20,score_font.render("-1 !",1,RED,COLOR_BG),(800,450-225)))
            BAD+=1
            BALLS._create_ball(CURRENT_TRASH.ball)
            new_trash()
        else :
            TRASH_CHANGE_COUNTER-=1

        #Handle button timeout counter
        if BTN_TIMEOUT_COUNTER>0 :
            BTN_TIMEOUT_COUNTER-=1

        #Handle Animations
        for i,animation in enumerate(ANIMATIONS) :
            animation.anim()
            if animation.finished :
                ANIMATIONS.pop(i)

        #Handle Leds
        LED_HANDLER.step()

        BALLS.handle_balls(SCREEN)

        if BAD>30 :
            END=True
        
        SCORE+=1

    #Show DEBUG
    if DEBUG :
        fps = str(round(CLOCK.get_fps(),1))
        btns_status=f"y : {str(btn_y.is_pressed)}"+f" g : {str(btn_g.is_pressed)}"+f" b : {str(btn_b.is_pressed)}"+f"| GOOD : {str(GOOD)}"+f" | BAD : {str(BAD)}"+f" | CHANGE COUNTER : {str(TRASH_CHANGE_COUNTER)}"
        txt = "DEBUG MODE | FPS : "+fps+f" | Button values : {btns_status}"
        to_blit=debug_font.render(txt,1,BLACK,COLOR_BG)
        SCREEN.blit(to_blit,(0,0))

    #End of loop
    #pygame.display.flip()
    pygame.display.update()
    CLOCK.tick(FPS) 
