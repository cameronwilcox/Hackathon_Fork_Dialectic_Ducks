# -*- coding: utf-8 -*-
from .src.asset     import Turret
from .src.enemy     import Enemy
from .src.game_data import *
from .src           import utils
from .usr           import TWR_POS

import pygame

from functools  import lru_cache
from pathlib    import Path
from sys        import argv
from typing     import List

THIS_FOLDER = Path(__file__).parent
DEMO_PNG    = THIS_FOLDER / 'demo.png'

global PLAYER_BASE


# initializing the constructor 
pygame.init() 

# screen resolution
SCREEN_RES = (1024,1024) 

# opens up a window 
screen = pygame.display.set_mode(SCREEN_RES) 
  
# white color 
color = (255,255,255) 
  
# light shade of the button 
color_light = (170,170,170) 
  
# dark shade of the button 
color_dark = (100,100,100) 

# path color
path_color = (152,118,84)

# defining a font 
smallfont = pygame.font.SysFont('Corbel',35)

@lru_cache
def gen_txt_img(txt : str) -> pygame.Surface: return smallfont.render(txt, True, color)

TXT_OFFSET = utils.Vector2(5, 5)
def draw_txt(txt : str, pos : utils.Vector2): screen.blit(gen_txt_img(txt), pos + TXT_OFFSET)

loop_count   = 0
SHELL_UPDATE = 50

def draw_enemy_path() -> List[pygame.rect.Rect]:
    for c_r in ENEMY_PATH_CORNERS: pygame.draw.rect(screen, path_color, c_r)
    return [pygame.draw.line(screen, path_color, start_pix, end_pix, ENEMY_PATH_WIDTH) for start_pix, end_pix in zip(ENEMY_PATH_PIX[:-1], ENEMY_PATH_PIX[1:])] + ENEMY_PATH_CORNERS
#End-def

bad_twr_rects = []

enemy_wave = [ [100, 'Evil Spider'] for i in range(30)] + [ [500, 'Beast Rider'] ] + [ [120, 'Beast Rider'] for i in range(16)] + [ [300, 'Onyx Golem'] for i in range(8)]
curr_enemy = enemy_wave.pop(0)

num_twr         = 0
final_score_msg = ''

if __name__ == '__main__':
    draw_demo = not DEMO_PNG.is_file()
    if draw_demo: screen.blit(BACKGROUND, (0,0) )
    path_rects = draw_enemy_path()
    if draw_demo:
        all_base_sprites.draw(screen)
        pygame.image.save(screen, DEMO_PNG)
    #End-if
    for twr in TWR_POS:
        try:
            curr_twr = Turret(twr[0], twr[1] + PLAYER_BASE.rect.centerx, twr[2] + PLAYER_BASE.rect.centery, twr[3])
            if (curr_twr.rect.collidelist(path_rects) >= 0) or bool(set(pygame.sprite.spritecollide(curr_twr, Turret.sp_grp, False) ) - {curr_twr}): # Likely that `curr_twr` collides with itself :/
                print(f'Cannot spawn {twr[0]} at position: {twr[1:3]}')
                curr_twr.kill()
            else: num_twr += 1
            #End-if
        except Exception as e:
            print(f'Error spawning {twr[0]} at position {twr[1:3]}:\n{e}')
            if hasattr(curr_twr, 'kill'): curr_twr.kill()
        # End-try
    #End-for
    game_over = num_twr == 0
    if game_over: print('Aborting: unable to spawn any towers')
    
    pygame.time.set_timer(pygame.USEREVENT, int(MSEC_PER_UPDATE) )
    while not game_over:
        
        usr_evt_flag = False
        for ev in pygame.event.get(): 
              
            if ev.type == pygame.QUIT: game_over = True
            
            match ev.type:
                case pygame.USEREVENT:
                    if usr_evt_flag or bool(utils.blocked): Turret.sp_grp.update()
                    else:
                        Turret.sp_grp.update([tgt.tgt_data for tgt in (Turret.sp_grp.sprites() + Enemy.sp_grp.sprites() )])
                        all_base_sprites.update(screen.get_rect() )
                        curr_enemy[0] -= 1
                        if ( (curr_enemy[0] == 0) or (not bool(Enemy.sp_grp.sprites() ) ) ) and bool(enemy_wave):
                            Enemy(curr_enemy[1])
                            if enemy_wave: curr_enemy = enemy_wave.pop(0)
                            else:          curr_enemy = [-1, '']
                        #End-if
                        usr_evt_flag = True
                    #End-if
                #End-case
            #End-match
        #End-for
        
        screen.blit(BACKGROUND, (0,0) )
        draw_enemy_path()
        Turret.sp_grp.draw(screen)
        all_base_sprites.draw(screen)
        
        all_twr = Turret.sp_grp.sprites()
        mouse_pos = pygame.mouse.get_pos()
        mouse_chk = None
        while all_twr:
            curr_twr = all_twr.pop()
            if curr_twr.rect.collidepoint(mouse_pos):
                mouse_chk = curr_twr.mouse_info
                all_twr   = []
            #End-if
        #End-while
        if mouse_chk: draw_txt(mouse_chk, mouse_pos)

        # updates the frames of the game 
        pygame.display.flip()
        
        if not (bool(enemy_wave) or bool(Enemy.sp_grp.sprites() ) ):
            oukd    = max([twr.overutilization for twr in Turret.sp_grp.sprites()])
            tot_pkd = float(5*Enemy.killed - PLAYER_BASE.damage - 10*num_twr)
            if tot_pkd > 0: tot_pkd *= 1 - oukd
            
            game_over       = True
            final_score_msg = f'''
            Towers Deployed:        {num_twr}
            Enemies neutralized:    {Enemy.killed}
            Enemies survided:       {PLAYER_BASE.damage}
            Max Overutilization:    {oukd}
            --------------------------------
            FINAL SCORE:            {tot_pkd}
            '''
        #End-if
    #End-while
    
    pygame.quit()
    print(final_score_msg)
#End-if