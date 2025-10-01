import sys
import random
import time
import os

import pygame
import gpiozero as gpio
import rpi_ws281x as rpi

from tools import *
import BB

#GAMEPLAY CONSTANTS
FPS=30
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

#CONSTANTS
DIR="/home/pi/Desktop/M8/"
SCREEN_SIZE=(1080, 1920)
SCREEN = pygame.display.set_mode(SCREEN_SIZE,pygame.FULLSCREEN)
#Define DEBUG
try :
    if sys.argv[1]=="debug" :
        DEBUG=True
except IndexError :
    DEBUG=False

#GPIO
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

#STYLE

#ASSETS POS
TRASH_POS = (540,850)

#BALL
ball_mass = 10
ball_elasticity = 0.5
shape_friction = 0.9

#ANIMATION
color_directions = {
    "dechet":(0,10000),
    "jaune":(100,-70),
    "orange":(100,0),
    "vert":(100,70),
    "gris":(-100,37),
    "marron":(-100,-37)
}

#STYLE

WHITE=pygame.Color("White")
BLACK=pygame.Color("Black")
GREEN=pygame.Color("Green")
RED=pygame.Color("Red")
BLUE=pygame.Color("Blue")
COLOR_BG=pygame.Color(242,193,202,255)
COLOR_HL=pygame.Color(38,53,139,255)


#FONTS
pygame.font.init()

debug_font=pygame.font.Font(DIR+"assets/font/debug.ttf",14)
score_font=pygame.font.Font(DIR+"assets/font/digit.TTF",120)
mult_font = pygame.font.Font(DIR+"assets/font/debug.ttf",140)
normal_font = pygame.font.Font(DIR+"assets/font/bai_jamburee_medium.ttf",22)
idle_font = pygame.font.Font(DIR+"assets/font/bai_jamburee_medium.ttf",25)
title_font = pygame.font.Font(DIR+"assets/font/salford_sans_arabic.ttf",80)

#ASSETS
#IMG
accueil = pygame.image.load(DIR+"assets/img_v2/accueil.png").convert_alpha()

#panel = pygame.image.load(DIR+"assets/img_v2/panneau.png").convert_alpha() #Panel is loaded in the Panel class
bandeau = pygame.image.load(DIR+"assets/img_v2/bandeau.png").convert_alpha()
tuyaux = pygame.image.load(DIR+"assets/img_v2/centre.png").convert_alpha()
bout = pygame.image.load(DIR+"assets/img_v2/tuyau.png").convert_alpha()
logo = pygame.image.load(DIR+"assets/img_v2/logo.png").convert_alpha()
title = pygame.image.load(DIR+"assets/img_v2/titre.png").convert_alpha()
poubelle = pygame.image.load(DIR+"assets/img_v2/poubelle.png").convert_alpha()

trash_emb = pygame.image.load(DIR+"assets/img_v2/emballage.png").convert_alpha()
trash_pap = pygame.image.load(DIR+"assets/img_v2/papier.png").convert_alpha()
trash_ver = pygame.image.load(DIR+"assets/img_v2/verre.png").convert_alpha()
trash_men = pygame.image.load(DIR+"assets/img_v2/menager.png").convert_alpha()
trash_bio = pygame.image.load(DIR+"assets/img_v2/biodechet.png").convert_alpha()

#GENERATED ASSETS
#idle_screen
idle_screen = pygame.Surface((1080,1920))
idle_screen.blit(accueil,(0,0))
center_blit(idle_screen,title,(SCREEN_SIZE[0]/2,210))

idle_txt = [
    "                                                                                              ",
    "Chaque pièce de la maison produit des déchets au fil du temps. Même si le mieux",
    "est encore d'en produire le moins possible, il est également possible de les trier,",
    "pour en valoriser certains.",
    "",
    "Entraines-toi à les reconnaître et à les trier en un seul coup d'oeil, et tiens le",
    "plus longtemsp possible avant d'être submergé !",
    "",
    "Les déchets font arriver dans la poubelle bleu, trouve où ils doivent être triés et",
    "appuie sur le bon bouton avant que le déchet parte dans une décharge ! Sinon, ils",
    "vont s'accumuler sur ton écran jusqu'à t'empécher de voir quoi que ce soit.",
    "",
    "",
    "Appuie sur le bouton rouge pour commencer !"
]

rendered_txt = render_multiple_lines(idle_font,idle_txt,WHITE)
center_blit(idle_screen,rendered_txt,(SCREEN_SIZE[0]/2,1500))

#play_screen
play_screen = pygame.Surface((1080,1920))
play_screen.blit(accueil,(0,0))
pygame.draw.rect(play_screen,COLOR_BG,(0,310,1080,1545))
center_blit(play_screen,tuyaux,(540,660))
center_blit(play_screen,poubelle,(540,1475))
blue = pygame.Surface((1080,310-68))
blue.fill(COLOR_HL)
play_screen.blit(blue,(0,68))

rotated_emb=pygame.transform.rotate(trash_emb,35)
rotated_pap=pygame.transform.rotate(trash_pap,0)
rotated_ver=pygame.transform.rotate(trash_ver,-35)
rotated_men=pygame.transform.rotate(trash_men,20)
rotated_bio=pygame.transform.rotate(trash_bio,-20)

center_blit(play_screen,rotated_emb,(1040,503))
center_blit(play_screen,rotated_pap,(1046,853))#822
center_blit(play_screen,rotated_ver,(1040,1200))
center_blit(play_screen,rotated_men,(73,1020))
center_blit(play_screen,rotated_bio,(73,680))

#upper screen background
upper_screen_bg = pygame.Surface((1000,170))

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

trash_img = {
    "1_1_img" : pygame.image.load(DIR+"assets/trash_v2/1_1.png").convert_alpha(),
    "1_2_img" : pygame.image.load(DIR+"assets/trash_v2/1_2.png").convert_alpha(),
    "1_3_img" : pygame.image.load(DIR+"assets/trash_v2/1_3.png").convert_alpha(),
    "1_4_img" : pygame.image.load(DIR+"assets/trash_v2/1_4.png").convert_alpha(),
    "1_5_img" : pygame.image.load(DIR+"assets/trash_v2/1_5.png").convert_alpha(),
    "2_1_img" : pygame.image.load(DIR+"assets/trash_v2/2_1.png").convert_alpha(),
    "3_1_img" : pygame.image.load(DIR+"assets/trash_v2/3_1.png").convert_alpha(),
    "3_2_img" : pygame.image.load(DIR+"assets/trash_v2/3_2.png").convert_alpha(),
    "3_3_img" : pygame.image.load(DIR+"assets/trash_v2/3_3.png").convert_alpha(),
    "3_4_img" : pygame.image.load(DIR+"assets/trash_v2/3_4.png").convert_alpha(),
    "3_5_img" : pygame.image.load(DIR+"assets/trash_v2/3_5.png").convert_alpha(),
    "4_1_img" : pygame.image.load(DIR+"assets/trash_v2/4_1.png").convert_alpha(),
    "4_2_img" : pygame.image.load(DIR+"assets/trash_v2/4_2.png").convert_alpha(),
    "4_3_img" : pygame.image.load(DIR+"assets/trash_v2/4_3.png").convert_alpha(),
    "4_4_img" : pygame.image.load(DIR+"assets/trash_v2/4_4.png").convert_alpha(),
    "5_1_img" : pygame.image.load(DIR+"assets/trash_v2/5_1.png").convert_alpha(),
    "5_2_img" : pygame.image.load(DIR+"assets/trash_v2/5_2.png").convert_alpha(),
    "5_3_img" : pygame.image.load(DIR+"assets/trash_v2/5_3.png").convert_alpha(),
    "5_4_img" : pygame.image.load(DIR+"assets/trash_v2/5_4.png").convert_alpha(),
    "5_5_img" : pygame.image.load(DIR+"assets/trash_v2/5_5.png").convert_alpha()
}

#DATA

trash_data = []

for key in trash_img :
    circle = crop_as_circle(trash_img[key])
    ball = pygame.transform.scale(circle,(BALL_RADIUS*2,BALL_RADIUS*2))
    pygame.draw.circle(ball,COLOR_HL,(BALL_RADIUS,BALL_RADIUS),BALL_RADIUS+1,5)
    trash_data.append(
        {
            "img":pygame.transform.scale(circle,(350,350)),
            "ball":ball,
            "good_value":corress_btn[key[:1]],
            "txt":"C'était dans la poubelle "+corress_btn[key[:1]]
        }
    )



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
        center_blit(SCREEN,self.img,(self.pos[0]+self.direction[0]*current_frame*self.speed,self.pos[1]+self.direction[1]*current_frame*self.speed))
    def __init__(self,max_frame,img,pos,direction,speed) :
        Anim.__init__(self,max_frame)
        self.img=img
        self.pos=pos
        self.direction=direction
        self.speed=speed
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
        self.panel = pygame.image.load(DIR+"assets/img_v2/panneau.png").convert_alpha()
        alpha = 240
        self.panel.fill((255,255,255,alpha),None,pygame.BLEND_RGBA_MULT)
        self.panel_size = self.panel.get_size()
    def render(self) :
        rendered_title = title_font.render(self.title,1,COLOR_HL)
        center_blit(self.panel,rendered_title,(self.panel_size[0]/2,80))
        rendered_txt = render_multiple_lines(normal_font,self.txt,COLOR_HL)
        self.panel.blit(rendered_txt,(30,120))
        return self.panel

class Panel_wrong(Panel) :
    def __init__(self,specific_txt) :
        Panel.__init__(self,title="ERREUR !")
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
        self.pause_panel=Panel_wrong(data["txt"])
        self.frame=0
    def check_value(self,btn) :
        if corress_btn[btn]==self.good_value :
            return True
        else :
            return False
    def render(self,total) :
        if self.frame < 10 :
            step=total/10
            temp_pos = (TRASH_POS[0],TRASH_POS[1]-(total-(step*self.frame)))
            center_blit(SCREEN,self.ball,temp_pos)
        elif self.frame < 15 :
            center_blit(SCREEN,pygame.transform.scale_by(self.img,1-(0.1*(15-self.frame))),TRASH_POS)
        else :
            center_blit(SCREEN,self.img,TRASH_POS)
        self.frame += 1

class Game() :
    def __init__(self) :
        self.on = True
        self.clock = pygame.time.Clock()

        #GAME DATA
        self.trashs = []
        for entry in trash_data :
            self.trashs.append(Trash(entry))

        #GAME SETTINGS
        self.FPS=FPS
        self.base_trash_change_timer = TRASH_CHANGE

        self.leds = Leds(GPIO_led,22)
        self.leds.test()
    
    def start(self) :
        
        #GAME STATUS
        self.playing = False
        self.status = "IDLE"
        self.elapsed_frame = 0

        self.good_trash = 0
        self.bad_trash = 0
        self.score = 0
        self.mult = 1

        #GAME ENGINE
        self.current_trash = self.trashs[0]
        self.old_trash = False
        self.trash_change_timer = self.base_trash_change_timer
        self.death_timer = 10

        self.ANIMATIONS = []

        self.balls = BB.BouncyBalls(
            SCREEN,
            FPS,
            BALL_RADIUS,
            ball_mass,
            ball_elasticity,
            shape_friction
        )           

    def connect_GPIO(self) :
        btn_1=gpio.Button(GPIO_btn_1,pull_up=True,bounce_time=0.05)
        btn_2=gpio.Button(GPIO_btn_2,pull_up=True,bounce_time=0.05)
        btn_3=gpio.Button(GPIO_btn_3,pull_up=True,bounce_time=0.05)
        btn_4=gpio.Button(GPIO_btn_4,pull_up=True,bounce_time=0.05)
        btn_5=gpio.Button(GPIO_btn_5,pull_up=True,bounce_time=0.05)
        btn_0=gpio.Button(GPIO_btn_0,pull_up=True,bounce_time=0.05)
        btn_1.when_pressed = self.pressed_1
        btn_2.when_pressed = self.pressed_2
        btn_3.when_pressed = self.pressed_3
        btn_4.when_pressed = self.pressed_4
        btn_5.when_pressed = self.pressed_5
        btn_0.when_pressed = self.pressed_start
    
    def new_trash(self) :
        #Save old trash
        self.old_trash=self.current_trash
        #Select new trash, must be different from precedent
        new = random.choice(self.trashs)
        while new==self.current_trash :
            new = random.choice(self.trashs)
        self.current_trash = new
        self.current_trash.frame=0
        #Reset trash change timer
        self.trash_change_timer = self.base_trash_change_timer
    
    def good(self) :
        score_won = self.trash_change_timer * self.mult
        #Give feedback
        short_good_1.play()
        self.leds.set_mode_flash(self.current_trash.good_value)
        self.ANIMATIONS.append(Pop(20,score_font.render(f"+{score_won} !",1,BLUE,COLOR_BG),TRASH_POS))
        self.ANIMATIONS.append(Dash(FPS*5,self.current_trash.ball,TRASH_POS,color_directions[self.current_trash.good_value],0.1))
        #Update game status
        self.score += score_won
        self.good_trash += 1
        self.mult += 1
        #Update trash
        self.new_trash()
    
    def bad(self) :
        #Give feedback
        short_bad_1.play()
        self.leds.set_mode_blink()
        self.balls._create_ball(self.current_trash.ball,TRASH_POS)
        #Update game status
        self.bad_trash += 1
        self.mult = 1
        #Pause the game
        self.current_panel = self.current_trash.pause_panel
        self.status="PAUSE"
        self.playing=False
        #Update trash
        self.new_trash()
    
    def late(self) :
        #Give feedback
        short_bad_1.play()
        self.leds.set_mode_blink()
        self.balls._create_ball(self.current_trash.ball,TRASH_POS)
        #Update game status
        self.bad_trash += 1
        self.mult = 1
        #Update trash
        self.new_trash()

    def pressed_1(self,arg) :
        self.pressed("1")
    def pressed_2(self,arg) :
        self.pressed("2")
    def pressed_3(self,arg) :
        self.pressed("3")
    def pressed_4(self,arg) :
        self.pressed("4")
    def pressed_5(self,arg) :
        self.pressed("5")    
    def pressed(self,btn) :
        if self.playing :
            if self.current_trash.check_value(btn) :
                self.good()
            else :
                self.bad()
    
    def pressed_start(self,arg) :
        match self.status :
            case "IDLE" :
                self.playing = True
                self.status = "PLAY"
            case "PAUSE" :
                self.playing = True
                self.status = "PLAY"
            case "END" :
                self.start()
            case _ :
                print(f"default : {self.status}")
    
    def step_upper_screen(self) :
        #BG
        pygame.draw.rect(SCREEN,COLOR_HL,(0,90,1080,240))
        pygame.draw.rect(SCREEN,WHITE,(30,95,1020,180),2)
        #Score
        txt_score = f"SCORE : {str(self.score).zfill(7)}"
        to_blit = score_font.render(txt_score,1,WHITE,COLOR_HL)
        SCREEN.blit(to_blit,(230,120))
        #Multiplicator
        txt_mult = f"x{self.mult}"
        to_blit = mult_font.render(txt_mult,1,WHITE,COLOR_HL)
        SCREEN.blit(to_blit,(60,100))

    def step_animations(self) :
        for i,animation in enumerate(self.ANIMATIONS) :
                animation.anim()
                if animation.finished :
                    self.ANIMATIONS.pop(i)
    
    def step_balls(self) :
        lower_ball = self.balls.handle_balls(SCREEN)
        if lower_ball > 1920 :
            return True
        else :
            return False
    
    def step_trash(self) :
        if self.trash_change_timer==0 :
            self.late()
        else :
            self.trash_change_timer -= 1

    def defeat(self) :
        self.status = "END"
        self.playing = False
        self.current_panel = Panel_end(self.elapsed_frame/self.FPS,self.good_trash,self.bad_trash,self.score)  

    def launch(self) :
        while self.on :

            #SCREEN cleanup
            SCREEN.blit(play_screen,(0,0))

            #Drawing current trash
            self.current_trash.render(600)

            #Handle Animations
            self.step_animations()

            #Drawing upper screen
            self.step_upper_screen()

            #Handle leds
            self.leds.step()          

            #Handle balls physics and DEFEAT
            if self.step_balls() :
                self.defeat()

            if self.playing :
                #Handle trash change
                self.step_trash()
                self.elapsed_frame+=1
            else :
                #Panels handling
                match self.status :
                    case "IDLE" :
                        center_blit(SCREEN,idle_screen,(SCREEN_SIZE[0]/2,SCREEN_SIZE[1]/2))
                    case "PAUSE" :
                        to_blit = self.current_panel.render()
                        center_blit(SCREEN,to_blit,TRASH_POS)
                    case "END" :
                        to_blit = self.current_panel.render()
                        center_blit(SCREEN,to_blit,TRASH_POS)

            #DEBUG
            if DEBUG :
                fps = str(round(self.clock.get_fps(),1))
                txt = "DEBUG MODE | FPS : "+fps+f" | GAME_STATUS : {self.status}"
                to_blit=debug_font.render(txt,1,BLACK,COLOR_BG)
                SCREEN.blit(to_blit,(0,0))

            #Handle events
            for event in pygame.event.get():
                keys = pygame.key.get_pressed()
                if event.type == pygame.QUIT:
                    self.on = False
                if keys[pygame.K_ESCAPE] : # ECHAP : Quitter
                    self.on=False
            
            #End of loop
            pygame.display.update()
            self.clock.tick(self.FPS)  



game = Game()
game.connect_GPIO()
game.start()
game.launch()

game.leds.close()





