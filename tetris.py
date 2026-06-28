import pygame
from copy import deepcopy
from random import choice, randrange , uniform

W, H = 10, 20
TILE = 25
GAME_RES = W * TILE, H * TILE
RES = 430, 540
FPS = 60

pygame.init()
sc = pygame.display.set_mode(RES)
game_sc = pygame.Surface(GAME_RES)
clock = pygame.time.Clock()

pygame.mixer.init()
pygame.mixer.music.load("assests/menu.mp3")
click_s = pygame.mixer.Sound("assests/click2.mp3")
drop_s=pygame.mixer.Sound("assests/drop.mp3")
clear_s=pygame.mixer.Sound("assests/clear.mp3")
lose_s=pygame.mixer.Sound("assests/lose.mp3")



grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]

figures_pos = [
    [(-1, 0), (-2, 0), (0, 0), (1, 0)],
    [(0, -1), (-1, -1), (-1, 0), (0, 0)],
    [(-1, 0), (-1, 1), (0, 0), (0, -1)],
    [(0, 0), (-1, 0), (0, 1), (-1, -1)],
    [(0, 0), (0, -1), (0, 1), (-1, -1)],
    [(0, 0), (0, -1), (0, 1), (1, -1)],
    [(0, 0), (0, -1), (0, 1), (-1, 0)],
]

figures = [
    [pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in fig_pos]
    for fig_pos in figures_pos
]
figure_rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)
field = [[0 for i in range(W)] for j in range(H)]

anim_count, anim_speed, anim_limit = 0, 60, 2000

bg = pygame.image.load("assests/bg.png").convert()
game_bg = pygame.image.load("assests/bg2.png").convert()

main_font = pygame.font.Font("assests/font.ttf", 35)
font = pygame.font.Font("assests/font.ttf", 25)

title_tetris = main_font.render("TETRIS", True, pygame.Color("darkorange"))
title_score = font.render("score:", True, pygame.Color("green"))
title_record = font.render("record:", True, pygame.Color("purple"))

get_color = lambda: (randrange(30, 256), randrange(30, 256), randrange(30, 256))

figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
color, next_color = get_color(), get_color()

score, lines = 0, 0
scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}


###############
class Particle:
    def __init__ (self, x , y, color):
        self.x = x
        self.y = y
        self.dx =uniform(-3,3)
        self.dy = uniform(-6 , -1)
        self.size = uniform(2,6)
        self.color = color
    
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dy += 0.3
        self.size -=0.15

    def draw(self, surface):
        if self.size> 0:
            pygame.draw.circle(surface,self.color, (int(self.x), int(self.y)), int(self.size))


particles=[] 

def check_borders(f =None):
    if f is None:
        f= figure
    
    for i in range(4):
        if (
            f[i].x < 0
            or f[i].x >= W
            or f[i].y >= H
            or field[f[i].y][f[i].x]
        ):
            return False
    return True


def get_record():
    try:
        with open("record") as f:
            return f.readline()
    except FileNotFoundError:
        with open("record", "w") as f:
            f.write("0")


def set_record(record, score):
    rec = max(int(record), score)
    with open("record", "w") as f:
        f.write(str(rec))


def show_main_menu(first_launch=False):
    sc.blit(bg, (0, 0))
    game_sc.blit(game_bg, (0, 0))
    sc.blit(game_sc, (20, 20))

    try:
        blurred_screen = pygame.transform.box_blur(sc, 8)
    except AttributeError:
        small = pygame.transform.smoothscale(sc, (RES[0] // 8, RES[1] // 8))
        blurred_screen = pygame.transform.smoothscale(small, RES)
    
    overlay = pygame.Surface(RES, pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120)) 

    menu_title = main_font.render("Tetris", True, pygame.Color("darkorange"))
    menu_author = font.render("made by sasa", True, pygame.Color("white"))
    menu_prompt = font.render("click mouse button to play", True, pygame.Color("lightgray"))

    if first_launch:
        black_surf = pygame.Surface(RES)
        black_surf.fill((0, 0, 0))
        black_alpha = 255
        
        while black_alpha > 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
            
            sc.blit(blurred_screen, (0, 0))
            sc.blit(overlay, (0, 0))
            sc.blit(menu_title, menu_title.get_rect(center=(RES[0] // 2, RES[1] // 2 - 60)))
            sc.blit(menu_author, menu_author.get_rect(center=(RES[0] // 2, RES[1] // 2)))
            sc.blit(menu_prompt, menu_prompt.get_rect(center=(RES[0] // 2, RES[1] // 2 + 60)))
            
            black_surf.set_alpha(black_alpha)
            sc.blit(black_surf, (0, 0))
            
            black_alpha -= 5  
            pygame.display.flip()
            clock.tick(FPS)

    waiting = True
    fading = False
    alpha = 255 

    pygame.mixer.music.play(loops= -1, fade_ms=2000)

    while waiting or fading:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not fading:
                waiting = False
                click_s.play()
                pygame.mixer.music.fadeout(1000)

                fading = True
        
        sc.blit(blurred_screen, (0, 0))
        sc.blit(overlay, (0, 0))

        if fading:
            alpha -= 10  
            if alpha <= 0:
                fading = False  

        menu_title.set_alpha(alpha)
        menu_author.set_alpha(alpha)
        menu_prompt.set_alpha(alpha)

        sc.blit(menu_title, menu_title.get_rect(center=(RES[0] // 2, RES[1] // 2 - 60)))
        sc.blit(menu_author, menu_author.get_rect(center=(RES[0] // 2, RES[1] // 2)))
        sc.blit(menu_prompt, menu_prompt.get_rect(center=(RES[0] // 2, RES[1] // 2 + 60)))

        pygame.display.flip()
        clock.tick(FPS)
show_main_menu(first_launch=True)

while True:
    record = get_record()
    dx, rotate = 0, False
    sc.blit(bg, (0, 0))
    sc.blit(game_sc, (20, 20))
    game_sc.blit(game_bg, (0, 0))

    
     

    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_DOWN:
                anim_limit = 100
                drop_s.play()

            elif event.key == pygame.K_UP:
                rotate = True
    figure_old = deepcopy(figure)
    for i in range(4):
        figure[i].x += dx
        if not check_borders():
            figure = deepcopy(figure_old)
            break
    anim_count += anim_speed
    if anim_count > anim_limit:
        anim_count = 0
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].y += 1
            if not check_borders():
                for i in range(4):
                    field[figure_old[i].y][figure_old[i].x] = color
                figure, color = next_figure, next_color
                next_figure, next_color = deepcopy(choice(figures)), get_color()
                anim_limit = 2000
                break
    
    center = figure[0]
    figure_old = deepcopy(figure)
    if rotate:
        for i in range(4):
            x = figure[i].y - center.y
            y = figure[i].x - center.x
            figure[i].x = center.x - x
            figure[i].y = center.y + y
        if not check_borders():
            kicked = False
            kick_offsets = [(-1,0),(1,0), (-2,0),(2,0),(0,-1)]

            for kick_x, kick_y in kick_offsets:
                for i in range(4):
                    figure[i].x +=kick_x
                    figure[i].y +=kick_y

                if check_borders():
                    kicked =True
                    break
                else:
                    for i in range(4):
                        figure[i].x -=kick_x
                        figure[i].y -=kick_y
            if not kicked:
                figure = deepcopy(figure_old)

    line, lines = H - 1, 0
    for row in range(H - 1, -1, -1):
        count = 0
        for i in range(W):
            if field[row][i]:
                count += 1
            field[line][i] = field[row][i]
        if count < W:
            line -= 1
        else:
            anim_speed += 3
            lines += 1

            for i in range(W):
                color= field[row][i]
                if color:
                    px =i *TILE+ TILE//2
                    py =row*TILE +TILE//2
                for _ in range(8):
                    particles.append(Particle(px, py, color))

    if lines >0:
        clear_s.play()

    score += scores[lines]

    [pygame.draw.rect(game_sc, (40, 40, 40), i_rect, 1) for i_rect in grid]
    ghost_figures = deepcopy(figure)
    while True:
        for i in range(4):
            ghost_figures[i].y += 1
        if not check_borders(ghost_figures):
            for i in range(4):
                ghost_figures[i].y-=1
            break
    
    for i in range(4):

        base_x = ghost_figures[i].x*TILE
        base_y = ghost_figures[i].y*TILE

        ghost_surf= pygame.Surface((TILE,TILE), pygame.SRCALPHA)

        for layer_alpha in [40,20,10]:
            pass
    
    for i in range(4):
        base_x = ghost_figures[i].x*TILE
        base_y =ghost_figures[i].y*TILE

        ghost_surf =pygame.Surface((TILE, TILE), pygame.SRCALPHA)

        pygame.draw.rect(ghost_surf, (color[0], color[1],color[2], 120), pygame.Rect(4,4,TILE -8, TILE-8))

        pygame.draw.rect(ghost_surf, (color[0], color[1],color[2], 60), pygame.Rect(2,2,TILE -4, TILE-4))

        pygame.draw.rect(ghost_surf, (color[0], color[1],color[2], 30), pygame.Rect(0,0,TILE -2, TILE-2))

        game_sc.blit(ghost_surf, (base_x, base_y))
    
    for i in range(4):
        figure_rect.x = figure[i].x * TILE
        figure_rect.y = figure[i].y * TILE
        pygame.draw.rect(game_sc, color, figure_rect)
    for y, raw in enumerate(field):
        for x, col in enumerate(raw):
            if col:
                figure_rect.x, figure_rect.y = x * TILE, y * TILE
                pygame.draw.rect(game_sc, col, figure_rect)

    for p in particles[:]:
        p.update()
        p.draw(game_sc)
        if p.size <= 0:
            particles.remove(p)            
    for i in range(4):
        figure_rect.x = next_figure[i].x * TILE + 210
        figure_rect.y = next_figure[i].y * TILE + 90
        pygame.draw.rect(sc, next_color, figure_rect)
    sc.blit(title_tetris, (280, 20))
    sc.blit(title_score, (290, 350))
    sc.blit(font.render(str(score), True, pygame.Color("white")), (300, 400))
    sc.blit(title_record, (290, 230))
    sc.blit(font.render(record, True, pygame.Color("gold")), (300, 280))


    for i in range(W):
        if field[0][i]:
            lose_s.play()
            set_record(record, score)
            field = [[0 for i in range(W)] for j in range(H)]
            anim_count, anim_speed, anim_limit = 0, 60, 2000
            score = 0
            for i_rect in grid:
                pygame.draw.rect(game_sc, get_color(), i_rect)
                sc.blit(game_sc, (20, 20))
                pygame.display.flip()
                clock.tick(200)
            
            show_main_menu()
            break
    

    pygame.display.flip()
    clock.tick(FPS)

