import pygame

def center_blit(screen,img,coord) :
    size=img.get_size()
    real_coord=(coord[0]-size[0]/2,coord[1]-size[1]/2)
    screen.blit(img,real_coord)
