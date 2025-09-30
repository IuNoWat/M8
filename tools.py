import pygame

def center_blit(screen,img,coord) :
    size=img.get_size()
    real_coord=(coord[0]-size[0]/2,coord[1]-size[1]/2)
    screen.blit(img,real_coord)

def render_multiple_lines(font,txt_list,color,interline=0.1) :
    max_size=font.size(txt_list[0])
    line_heigth=max_size[1]+(max_size[1]*interline)
    rendered_txt = pygame.Surface((max_size[0], len(txt_list)*line_heigth),pygame.SRCALPHA)
    rendered_txt.fill((0,0,0,0))
    for i,line in enumerate(txt_list) :
        rendered_line = font.render(line,0,color)
        rendered_txt.blit(rendered_line,(0,line_heigth*i))
    return rendered_txt

