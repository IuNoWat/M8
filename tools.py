import pygame
import pygame.gfxdraw

def center_blit(screen,img,coord) :
    size=img.get_size()
    real_coord=(coord[0]-size[0]/2,coord[1]-size[1]/2)
    screen.blit(img,real_coord)

def render_multiple_lines(font,txt_list,color,interline=0.1) :
    max_size=[0,font.size(txt_list[0])[1]]
    for lines in txt_list :
        if font.size(lines)[0]>max_size[0] :
            max_size[0] = font.size(lines)[0]
    line_heigth=max_size[1]+(max_size[1]*interline)
    rendered_txt = pygame.Surface((max_size[0], len(txt_list)*line_heigth),pygame.SRCALPHA)
    rendered_txt.fill((0,0,0,0))
    for i,line in enumerate(txt_list) :
        rendered_line = font.render(line,0,color)
        rendered_txt.blit(rendered_line,(0,line_heigth*i))
    return rendered_txt

def crop_as_circle(img) :
    size=img.get_size()
    rect = pygame.Surface(size,pygame.SRCALPHA)
    meh = pygame.draw.rect(rect,(255,255,255),(0,0,*size), border_radius=600)
    to_return = img.copy().convert_alpha()
    to_return.blit(rect,(0,0),None,pygame.BLEND_RGBA_MIN)
    return to_return

def draw_aa_arc(size,color,width,start_angle,stop_angle) :
    rect = pygame.Surface((size,size),pygame.SRCALPHA)
    #for j in range(-1,1) :
    #    for i in range(0,width) :
    #        pygame.draw.arc(rect,color,(0+i+j/2,0+i+j/2,size-i,size-i),start_angle,stop_angle,1+i)
    for i in range(0,width) :
        pygame.draw.arc(rect,color,(0+i/2,0+i/2,size-i,size-i),start_angle,stop_angle,1+i)
    return rect

#def draw_aa_arc(size,color,width,start_angle,stope_angle) :
#    rect = pygame.Surface((size,size),pygame.SRCALPHA)
#    pygame.gfxdraw.aacircle(rect,size/2,size/2,size/2,color)
#    pygame.gfxdraw.aacircle(rect,size/2,size/2,size/2-width,(0,0,0,0))
#    for i in range(0,width) :
#        pygame.draw.arc(rect,color,(0+i/2,0+i/2,size-i,size-i),start_angle,stope_angle,1)
#    return rect


