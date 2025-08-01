import pygame

import gpiozero as gpio

#CONSTANTS
FPS=30
SCREEN_SIZE=(1920, 1080)
FULLSCREEN=True

try :
    if sys.argv[1]=="debug" :
        DEBUG=True
except IndexError :
    DEBUG=False

GPIO_y="BOARD9"
GPIO_g="BOARD10"
GPIO_b="BOARD12"

#GPIO SETUP
btn_y=gppio.Button(GPIO_y)
btn_g=gppio.Button(GPIO_g)
btn_b=gppio.Button(GPIO_b)

#STYLE
WHITE=pygame.Color("White")
BLACK=pygame.Color("Black")
GREEN=pygame.Color("Green")
RED=pygame.Color("Red")
COLOR_BG=pygame.Color(242,193,202,255)
COLOR_HL=pygame.Color(255,255,255,255)

debug_font=pygame.font.Font(16)

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
                if keys[pygame.K_x] : # X : Cacher Debug
                    self.show_debug = False
        if keys[pygame.K_ESCAPE] : # ECHAP : Quitter
            self.on=False
            
    #Show DEBUG
    if DEBUG :
        fps = str(round(CLOCK.get_fps(),1))
        btns_status=f"y:{str(btn_y.is_pressed)}+f" g:{str(btn_g.is_pressed)}+f" b:{str(btn_b.is_pressed)}"
        txt = "DEBUG MODE | FPS : "+fps+f" | Button values : {btns_status}"
        to_blit=debug_font.render(txt,1,WHITE,COLOR_BG)
        SCREEN.blit(to_blit,(0,0))

    #End of loop
    pygame.display.flip()
    CLOCK.tick(FPS) 
