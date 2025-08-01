import pygame

import gpiozero as gpio

#CONSTANTS

GPIO_y="BOARD9"
GPIO_g="BOARD10"
GPIO_b="BOARD12"

#GPIO SETUP
btn_y=gppio.Button(GPIO_y)
btn_g=gppio.Button(GPIO_g)
btn_b=gppio.Button(GPIO_b)


#MAINLOOP


