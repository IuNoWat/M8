import sys
import random
import time
import os

import pygame
import gpiozero as gpio
import rpi_ws281x as rpi

from tools import *
import BB

#CONSTANTS
FPS=30
DIR="/home/pi/Desktop/M8/"
SCREEN_SIZE=(1080, 1920)
SCREEN = pygame.display.set_mode(SCREEN_SIZE,pygame.FULLSCREEN)
#Define DEBUG
try :
    if sys.argv[1]=="debug" :
        DEBUG=True
except IndexError :
    DEBUG=False

#GAME CONSTANTS
BALL_RADIUS = 50
TRASH_CHANGE=4*FPS
BTN_TIMEOUT=0.5*FPS

corress_btn = {
    "0":"dechet",
    "1":"jaune",
    "2":"orange",
    "3":"vert",
    "4":"gris",
    "5":"marron"
}

#STYLE CONSTANTS

#BALL
ball_mass = 10
ball_elasticity = 0.5
shape_friction = 0.9

#GPIO CONSTANTS
GPIO_btn_0="BOARD18"
GPIO_btn_1="BOARD22"
GPIO_btn_2="BOARD8"
GPIO_btn_3="BOARD32"
GPIO_btn_4="BOARD16"
GPIO_btn_5="BOARD10"

GPIO_led=18

GPIO_btn_led_0="BOARD35"
GPIO_btn_led_1="BOARD37"
GPIO_btn_led_2="BOARD31"
GPIO_btn_led_3="BOARD29"
GPIO_btn_led_4="BOARD27"
GPIO_btn_led_5="BOARD33"



#Animation CONSTANTS
color_directions = {
    "dechet":(0,1000),
    "jaune":(0,-50),
    "orange":(50,-22),
    "vert":(50,50),
    "gris":(-50,50),
    "marron":(-50,-22)
}

#STYLE
pygame.font.init()
WHITE=pygame.Color("White")
BLACK=pygame.Color("Black")
GREEN=pygame.Color("Green")
RED=pygame.Color("Red")
BLUE=pygame.Color("Blue")
COLOR_BG=pygame.Color(242,193,202,255)
COLOR_HL=pygame.Color(38,53,139,255)

debug_font=pygame.font.Font(DIR+"assets/font/debug.ttf",14)
score_font=pygame.font.Font(DIR+"assets/font/digit.TTF",120)
mult_font = pygame.font.Font(DIR+"assets/font/debug.ttf",140)

normal_font = pygame.font.Font(DIR+"assets/font/bai_jamburee.ttf",22)
title_font = pygame.font.Font(DIR+"assets/font/salford_sans_arabic.ttf",80)

#SCREEN STYLE
TRASH_POS = (540,646)

#ASSETS
#IMG
select = pygame.image.load(DIR+"assets/img/select.png").convert_alpha()
trash = pygame.image.load(DIR+"assets/img/trash.png").convert_alpha()
intro = pygame.image.load(DIR+"assets/img/intro.png").convert_alpha()
panel = pygame.image.load(DIR+"assets/img/panel.png").convert_alpha()
bg = pygame.image.load(DIR+"assets/img/bg.png").convert_alpha()

y0=pygame.image.load(DIR+"assets/img/y_0.png").convert_alpha()
y1=pygame.image.load(DIR+"assets/img/y_1.png").convert_alpha()
g0=pygame.image.load(DIR+"assets/img/g_0.png").convert_alpha()
g1=pygame.image.load(DIR+"assets/img/g_1.png").convert_alpha()
b0=pygame.image.load(DIR+"assets/img/b_1.png").convert_alpha()
b1=pygame.image.load(DIR+"assets/img/b_0.png").convert_alpha()
#IMG BALLS
ball_y0=pygame.transform.scale(y0,(BALL_RADIUS*2,BALL_RADIUS*2))
ball_y1=pygame.transform.scale(y1,(BALL_RADIUS*2,BALL_RADIUS*2))
ball_g0=pygame.transform.scale(g0,(BALL_RADIUS*2,BALL_RADIUS*2))
ball_g1=pygame.transform.scale(g1,(BALL_RADIUS*2,BALL_RADIUS*2))
ball_b0=pygame.transform.scale(b0,(BALL_RADIUS*2,BALL_RADIUS*2))
ball_b1=pygame.transform.scale(b1,(BALL_RADIUS*2,BALL_RADIUS*2))
#SOUND
pygame.mixer.init()
pop=[
    pygame.mixer.Sound(DIR+"assets/sound/pop_1.mp3"),
    pygame.mixer.Sound(DIR+"assets/sound/pop_2.mp3"),
    pygame.mixer.Sound(DIR+"assets/sound/pop_3.mp3")
]
short_good_1=pygame.mixer.Sound(DIR+"assets/sound/low_fb_pos.wav")
short_bad_1=pygame.mixer.Sound(DIR+"assets/sound/low_fb_neg.wav")
long_good_1=pygame.mixer.Sound(DIR+"assets/sound/chord_fb_pos.wav")
long_bad_1=pygame.mixer.Sound(DIR+"assets/sound/chord_fb_neg.wav")

#pygame.mixer.music.load(DIR+"assets/sound/music.mp3")
#pygame.mixer.music.play()

#DATA

trash_data = [
    {
        "img":y0,
        "ball":ball_y0,
        "good_value":"jaune",
        "txt":"C'était dans la poubelle jaune !"
    },
    {"img":y1,"ball":ball_y1,"good_value":"jaune","txt":"C'était dans la poubelle jaune !"},
    {"img":g0,"ball":ball_g0,"good_value":"vert","txt":"C'était dans la poubelle verte !"},
    {"img":g1,"ball":ball_g1,"good_value":"vert","txt":"C'était dans la poubelle verte !"},
    {"img":b0,"ball":ball_b0,"good_value":"gris","txt":"C'était dans la poubelle bleue !"},
    {"img":b1,"ball":ball_b1,"good_value":"gris","txt":"C'était dans la poubelle bleue !"}
]

#ENGINE

class Anim() : #Base anim class, meant to be inherited. To define what the animation do, change the self.method variable
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

class Pop(Anim) : #Example use of the Anim class, wich create an image that fade out until max_frame
    def moove(self,current_frame) :
        self.img.set_alpha(255-current_frame*12)
        center_blit(SCREEN,self.img,(self.pos[0],self.pos[1]-current_frame*3))
    def __init__(self,max_frame,img,pos) :
        Anim.__init__(self,max_frame)
        self.img=img
        self.pos=pos
        self.method=self.moove
    def anim(self) :
        Anim.anim(self)

class Dash(Anim) : #Spawn an img and throw it in a defined direction
    def moove(self,current_frame) :
        center_blit(SCREEN,self.img,(self.pos[0]+self.direction[0]*current_frame,self.pos[1]+self.direction[1]*current_frame))
    def __init__(self,max_frame,img,pos,direction) :
        Anim.__init__(self,max_frame)
        self.img=img
        self.pos=pos
        self.direction=direction
        self.method=self.moove
    def anim(self) :
        Anim.anim(self)

#Led Handler
class Leds() : # Class used to handle the ledstrip,
    def __init__(self,pin,nb_of_leds) :
        #ledstrip
        self.nb_of_leds=nb_of_leds
        self.strip=rpi.PixelStrip(nb_of_leds,pin)
        self.strip.begin()
        #btnleds
        self.btn_led = [
            gpio.LED(GPIO_btn_led_1),
            gpio.LED(GPIO_btn_led_2),
            gpio.LED(GPIO_btn_led_3),
            gpio.LED(GPIO_btn_led_4),
            gpio.LED(GPIO_btn_led_5)
        ]
        self.start_led = gpio.LED(GPIO_btn_led_0)
        #Colors
        self.RED=rpi.Color(255,0,0)
        self.BLUE=rpi.Color(0,0,255)
        self.PURPLE=rpi.Color(255,0,255)
        self.WHITE=rpi.Color(150,150,150)
        self.BLACK=rpi.Color(0,0,0)
        self.YELLOW=rpi.Color(255,255,0)
        self.ORANGE=rpi.Color(255,255,50)
        self.GREEN=rpi.Color(0,255,0)
        self.GRIS=rpi.Color(50,50,50)
        self.MARRON=rpi.Color(255,255,150)
        #Engine value
        self.current_mode=False
        self.count=0
        self.current_color=self.WHITE
    def color_to_led(self,color) :
        match color :
            case "dechet" :
                return self.WHITE
            case "jaune" :
                return self.YELLOW
            case "orange" :
                return self.ORANGE
            case "vert" :
                return self.GREEN
            case "gris" :
                return self.GRIS
            case "marron" :
                return self.MARRON
    def test(self) : # To test the leds at the start of the program
        for i in range(0,self.nb_of_leds) :
            for j in range(0,self.nb_of_leds) :
                self.strip.setPixelColor(j,self.BLACK)
            self.strip.setPixelColor(i,self.WHITE)
            self.strip.show()
            time.sleep(0.05)
        for j in range(0,self.nb_of_leds) :
            self.strip.setPixelColor(j,self.BLACK)
        self.strip.show()
    def base(self) :
        for i in range(0,self.nb_of_leds) :
            self.strip.setPixelColor(i,self.WHITE)
        for led in self.btn_led :
            led.on()
    def step(self) : # Called each frame, use self.base_colors or loop through an aniamtion defined in self.current_mode
        for i in range(0,self.nb_of_leds) :
            self.strip.setPixelColor(i,self.BLACK)
            self.base()
        if self.current_mode!=False :
            match self.current_mode :
                case "flash" :
                    self.flash()
                case "blink" :
                    self.blink()
                case _ :
                    pass
        self.strip.show()
    def set_mode_flash(self,color) : #Launch the flash mode, a flash of a specified color
        self.count=5
        self.current_color=self.color_to_led(color)
        self.current_mode="flash"
    def flash(self) :
        self.count=self.count-1
        for i in range(0,self.nb_of_leds) :
            self.strip.setPixelColor(i,self.current_color)
        if self.count<=0 :
            self.current_mode=False
    def set_mode_blink(self) : # Launch the blink mode, make all the leds blink
        self.count=15
        self.current_mode="blink"
    def blink(self) :
        self.count=self.count-1
        if self.count%3==0 :
            for i in range(0,self.nb_of_leds) :
                self.strip.setPixelColor(i,self.BLACK)
            for led in self.btn_led :
                led.off()
        else :
            for i in range(0,self.nb_of_leds) :
                self.strip.setPixelColor(i,self.RED)
            for led in self.btn_led :
                led.on()
        if self.count<=0 :
            self.current_mode=False
    def close(self) :
        for i in range(0,self.nb_of_leds) :
            self.strip.setPixelColor(i,self.BLACK)
        self.strip.show()

class Panel() :
    def __init__(self,title="Default_Title",txt=["Iorem Ipsum dolor sic amet etc etc etc etc etc etc etc etc etc etc"]) :
        self.title=title
        self.txt=txt
        self.panel = pygame.image.load(DIR+"assets/img/panel.png").convert_alpha()
        self.panel_size = panel.get_size()
    def render(self) :
        rendered_title = title_font.render(self.title,1,COLOR_HL)
        center_blit(self.panel,rendered_title,(self.panel_size[0]/2,80))
        rendered_txt = render_multiple_lines(normal_font,self.txt,COLOR_HL)
        self.panel.blit(rendered_txt,(30,120))
        return self.panel

class Panel_wrong(Panel) :
    def __init__(self,specific_txt) :
        Panel.__init__(self,title="Erreur !")
        self.txt = [
            "                                                                                         ",
            "Raté ! Tu as envoyé un déchet dans la mauvaise",
            "poubelle !",
            specific_txt,
            " ",
            " ",
            " ",
            "Appuie sur le bouton rouge pour continuer !"
        ]

class Panel_end(Panel) :
    def __init__(self,game_duration,good_nb,bad_nb,score) :
        Panel.__init__(self,title="GAME OVER !")
        self.txt = [
            "                                                                                         ",
            f"Tu as fait de ton mieux, mais les déchets ont fini",
            f"par te submerger. Tu as tenu {int(game_duration)} secondes",
            f"Au final, tu a trié {good_nb} déchets dans la bonne poubelle,",
            f" et tu t'es trompé {bad_nb} fois",
            " ",
            f"Ton score final est de {score} points",
            " ",
            " ",
            "Appuie sur le bouton rouge pour recommencer !"
        ]

#SPECIFIC ENGINE

class Trash() : #Used to store all the informations needed for each trash
    def __init__(self,data) :
        self.img=data["img"]
        self.ball=data["ball"]
        self.good_value=data["good_value"]
        self.txt=Panel_wrong(data["txt"])
    def check_value(self,btn) :
        if corress_btn[btn]==self.good_value :
            return True
        else :
            return False

def new_trash() : #Change current trash
    global CURRENT_TRASH
    global TRASH_CHANGE_COUNTER
    global DIFFICULTY
    global OLD_TRASH
    OLD_TRASH=CURRENT_TRASH
    new=random.choice(trashs)
    while new==CURRENT_TRASH :
        new=random.choice(trashs)
    CURRENT_TRASH=new
    TRASH_CHANGE_COUNTER=TRASH_CHANGE-DIFFICULTY
    if TRASH_CHANGE-DIFFICULTY>5 :
        DIFFICULTY+=1

def good() : # Called by the pressed() method when the good button was pressed
    global GOOD
    global SCORE
    global ANIMATIONS
    global LED_HANDLER
    global MULT
    short_good_1.play()
    LED_HANDLER.set_mode_flash(CURRENT_TRASH.good_value)

    score_won = TRASH_CHANGE_COUNTER * MULT

    ANIMATIONS.append(Pop(20,score_font.render(f"+{score_won} !",1,BLUE,COLOR_BG),TRASH_POS))
    ANIMATIONS.append(Dash(20,CURRENT_TRASH.ball,TRASH_POS,color_directions[CURRENT_TRASH.good_value]))
    
    GOOD+=1
    MULT+=1
    SCORE+=score_won
    new_trash()

def bad() : # Called by the pressed() method when the bad button was pressed
    global CURRENT_TRASH
    global BAD
    global ANIMATIONS
    global BALLS
    global LED_HANDLER
    global GAME_STATUS
    global PLAYING
    global current_pause_panel
    global MULT

    current_pause_panel = CURRENT_TRASH.txt

    short_bad_1.play()
    LED_HANDLER.set_mode_blink()
    BAD+=1
    BALLS._create_ball(CURRENT_TRASH.ball,TRASH_POS)
    GAME_STATUS="PAUSE"
    PLAYING=False
    MULT=1

    new_trash()
    
def late() : # Called if no button is pressed in time
    global BAD
    global ANIMATIONS
    global BALLS
    global LED_HANDLER
    global MULT

    short_bad_1.play()
    LED_HANDLER.set_mode_blink()
    BAD+=1
    BALLS._create_ball(CURRENT_TRASH.ball,TRASH_POS)
    MULT=1
    
    new_trash()

def pressed(btn) : # Called by all the buttons except the start button, check if the answer is good or bad 
    global CURRENT_TRASH
    global PLAYING
    if PLAYING :
        print("COUCOU")
        if CURRENT_TRASH.check_value(btn) :
            good()
        else :
            bad()

def pressed_1(arg) :
    pressed("1")
    print("btn_1 pressed")

def pressed_2(arg) :
    pressed("2")
    print("btn_2 pressed")

def pressed_3(arg) :
    pressed("3")
    print("btn_3 pressed")

def pressed_4(arg) :
    pressed("4")
    print("btn_4 pressed")

def pressed_5(arg) :
    pressed("5")
    print("btn_5 pressed")

def pressed_start(arg) :
    global GAME_STATUS
    global PLAYING
    random.choice(pop).play()
    match GAME_STATUS :
        case "IDLE" :
            PLAYING=True
            GAME_STATUS="PLAY"
        case "PAUSE" :
            PLAYING=True
            GAME_STATUS="PLAY"
        case "END" :
            reset()
        case _ :
            print(f"default : {str(GAME_STATUS)}")

# Loading all trash infromations in the trashs list
trashs=[]

for entry in trash_data :
    trashs.append(Trash(entry))


#Connections buttons to methods
btn_1=gpio.Button(GPIO_btn_1,pull_up=True,bounce_time=0.05)
btn_2=gpio.Button(GPIO_btn_2,pull_up=True,bounce_time=0.05)
btn_3=gpio.Button(GPIO_btn_3,pull_up=True,bounce_time=0.05)
btn_4=gpio.Button(GPIO_btn_4,pull_up=True,bounce_time=0.05)
btn_5=gpio.Button(GPIO_btn_5,pull_up=True,bounce_time=0.05)
btn_0=gpio.Button(GPIO_btn_0,pull_up=True,bounce_time=0.05)
btn_1.when_pressed = pressed_1
btn_2.when_pressed = pressed_2
btn_3.when_pressed = pressed_3
btn_4.when_pressed = pressed_4
btn_5.when_pressed = pressed_5
btn_0.when_pressed = pressed_start

#MAINLOOP PREPARATION
on=True
CLOCK = pygame.time.Clock()

#Initializing leds handler
LED_HANDLER=Leds(GPIO_led,22)
LED_HANDLER.test()


rad=6.28/TRASH_CHANGE

#Initialize or reset the Game
def reset() : # To reset the game
    global OLD_TRASH
    global CURRENT_TRASH
    global TRASH_CHANGE_COUNTER
    global DIFFICULTY
    global ANIMATIONS
    global SCORE
    global VIES
    global GOOD
    global BAD
    global GAME_STATUS
    global PLAYING
    global BALLS
    global MULT
    global TIME_ELAPSED
    OLD_TRASH=False
    CURRENT_TRASH=trashs[0]
    TRASH_CHANGE_COUNTER=TRASH_CHANGE
    DIFFICULTY=0
    ANIMATIONS=[]
    SCORE=0
    VIES=10
    GOOD=0
    BAD=0
    TIME_ELAPSED=0
    GAME_STATUS="IDLE"
    PLAYING=False
    BALLS=BB.BouncyBalls(
        SCREEN,
        FPS,
        BALL_RADIUS,
        ball_mass,
        ball_elasticity,
        shape_friction
    )
    MULT=1

reset()



#MAINLOOP 
while on :
    
    #Cleaning of Screen
    #SCREEN.fill(COLOR_BG)
    SCREEN.blit(bg,(0,0))

    #Event handling
    for event in pygame.event.get():
        keys = pygame.key.get_pressed()
        if event.type == pygame.QUIT:
            on = False
        if keys[pygame.K_ESCAPE] : # ECHAP : Quitter
            on=False

    #Arc
    pygame.draw.arc(SCREEN,COLOR_HL,(TRASH_POS[0]-190,TRASH_POS[1]-190,380,380),1.5,1.5+TRASH_CHANGE_COUNTER*rad,20)

    #Trash
    center_blit(SCREEN,CURRENT_TRASH.img,TRASH_POS)

    #Couvercle
    #pygame.draw.circle(SCREEN,BLACK,(SCREEN_SIZE[0]/2,SCREEN_SIZE[1]/2),180,int(TRASH_CHANGE_COUNTER*1.5))

    #Score
    txt_score = f"SCORE : {str(SCORE).zfill(7)}"
    to_blit = score_font.render(txt_score,1,WHITE,COLOR_HL)
    SCREEN.blit(to_blit,(230,40))
    #Multiplicator
    txt_mult = f"x{MULT}"
    to_blit = mult_font.render(txt_mult,1,WHITE,COLOR_HL)
    SCREEN.blit(to_blit,(40,20))

    #Handle Leds
    LED_HANDLER.step()

    #Handle Animations
    for i,animation in enumerate(ANIMATIONS) :
        animation.anim()
        if animation.finished :
            ANIMATIONS.pop(i)

    #Handle BALLS physic      
    BALLS.handle_balls(SCREEN)

    #Check Defeat
    if BAD>5 :
        GAME_STATUS="END"
        PLAYING=False
        END_PANEL=Panel_end(TIME_ELAPSED/FPS,GOOD,BAD,SCORE)
    #Engine
    if PLAYING :
        #Checking trash counter
        if TRASH_CHANGE_COUNTER==0 :
            late()
        else :
            TRASH_CHANGE_COUNTER-=1
        
        TIME_ELAPSED+=1
    else :
        match GAME_STATUS :
            case "IDLE" :
                center_blit(SCREEN,intro,(SCREEN_SIZE[0]/2,SCREEN_SIZE[1]/2))
            case "PAUSE" :
                to_blit = current_pause_panel.render()
                center_blit(SCREEN,to_blit,TRASH_POS)
            case "END" :
                to_blit = END_PANEL.render()
                center_blit(SCREEN,to_blit,TRASH_POS)
    #DEBUG
    if DEBUG :
        fps = str(round(CLOCK.get_fps(),1))
        btns_status=f"1 : {str(btn_1.is_pressed)}"+f" 2 : {str(btn_2.is_pressed)}"+f" 3 : {str(btn_3.is_pressed)}"+f" 4 : {str(btn_4.is_pressed)}"+f" 5 : {str(btn_5.is_pressed)}"+f" 0 : {str(btn_0.is_pressed)}"+f"| GOOD : {str(GOOD)}"+f" | BAD : {str(BAD)}"+f" | CHANGE COUNTER : {str(TRASH_CHANGE_COUNTER)}"
        txt = "DEBUG MODE | FPS : "+fps+f" | Button values : {btns_status} | GAME_STATUS : {GAME_STATUS}"
        to_blit=debug_font.render(txt,1,BLACK,COLOR_BG)
        SCREEN.blit(to_blit,(0,0))


    #End of loop
    #pygame.display.flip()
    pygame.display.update()
    CLOCK.tick(FPS)     

LED_HANDLER.close()
