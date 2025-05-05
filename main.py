import pygame
from global_names import *
from tools import *
from generate_level import generate_level
from Sprites import Stop, RegulateMusic, Reset
import ai
from copy import deepcopy

def events():
    global running
    global intro_screen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_click_handler(event.pos)
        elif event.type == GAME_STARTING_EVENT_ID:
            intro_screen = False
        elif event.type == pygame.KEYUP:
            key_click_handler(event.key)
        if game_obj['Stop'] is None and intro_screen is False:
            timer_event_handler(event.type)


def mouse_click_handler(pos):
    x, y = pos
    x1, y1, h1, w1 = game_obj['RegulateMusic'].rect
    x2, y2, h2, w2 = game_obj['Reset'].rect
    if x1 + w1 > x > x1 and y1 + h1 > y > y1:
        game_obj['RegulateMusic'].change_sound_mode()
    elif x2 + w2 > x > x2 and y2 + h2 > y > y2:
        game_parameters['mod'] = GAME_OVER


def key_click_handler(key):
    if key == pygame.K_ESCAPE:
        if game_obj['Stop'] is None:
            game_obj['Stop'] = Stop(10, 11, stop_group, all_sprites)
            pause_music()
            reset_timers()
            if intro_screen is False:
                game_parameters['stopped timer'] = how_many_time_else()
        else:
            for i in stop_group:
                i.kill()
            game_obj['Stop'] = None
            pygame.mixer.music.unpause()
            game_parameters['mod changed time'] = adjust_saved_time()
            if intro_screen is False:
                timer(game_parameters['stopped timer'],
                      event_id=CHANGE_TO_EVENT_ID[game_parameters['mod']])
    elif key in [UP, DOWN, LEFT, RIGHT] and intro_screen is False:
        game_obj['Pac-Man'].key_pressed(key)


def timer_event_handler(event_id):
    if event_id == DEFAULT_EVENT_ID:
        if game_parameters['mod'] not in [FRIGHTENED, H_FRIGHTENED]:
            ans = ['Mod changed from', game_parameters['mod'], 'to']
            change_mod()
            ans.append(game_parameters['mod'])
            print(game_parameters['timer_num'])
            print(' '.join(ans))
            timer()
    elif event_id == FRIGHTENED_EVENT_ID:
        game_parameters['mod'] = H_FRIGHTENED
        time = time_in_frightened_mod()
        pygame.time.set_timer(HALF_FRIGHTENED_EVENT_ID, int(time * 0.25), True)
        game_parameters[H_FRIGHTENED] = True
    elif event_id == HALF_FRIGHTENED_EVENT_ID:
        game_parameters['mod'] = game_parameters['saved mod']
        game_parameters['ate ghosts'] = -1
        change_frightened(False)
        game_parameters['mod changed time'] = adjust_saved_time()
        timer(game_parameters['stopped timer'])


def update_fps():
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps, True, pygame.Color("coral"))
    return fps_text


def timer(time=None, event_id=None):
    if game_obj['Stop'] is not None:
        return None
    if time is not None:
        pygame.time.set_timer(
            event_id if event_id is not None else DEFAULT_EVENT_ID, time, True)
        return None
    time = level_time()
    pygame.time.set_timer(DEFAULT_EVENT_ID, time, True)
    game_parameters['mod changed time'] = pygame.time.get_ticks()
    game_parameters['timer_num'] += 1


def update_level():
    text = str(game_parameters['level']) + 'UP'
    return font.render(text, True, pygame.Color("white"))

def update_lives():
    text = 'lives' + ' : ' + str(game_parameters['lives'])
    return font.render(text, True, pygame.Color("white"))

def check_game_score():
    if len(energizers_group) == len(foods_group) == 0 and game_parameters[
        'mod'] != GAME_OVER:
        game_parameters['level'] += 1
        game_parameters['mod'] = ROUND_OVER


def check_game_status(intro=False):
    mod = game_parameters['mod']
    if mod in [ROUND_OVER, ATTEMPT, GAME_OVER]:
        game_parameters['mod'] = SCATTER
        game_parameters['score per round'] = 0
        game_parameters['timer_num'] = 0
        game_parameters['mod changed time'] = 0
        change_frightened(False)
        if mod == GAME_OVER:
            game_parameters['score'] = 0
            game_parameters['saved mod'] = None
            game_parameters['ate ghosts'] = -1
            game_parameters['stopped timer'] = LEVEL_TIME_CHANGE['1'][0] * 1000
            game_parameters['level'] = 1
        if mod != ATTEMPT:
            kill_all_sprites()
        reset_timers()
        param = True if mod in [ROUND_OVER, GAME_OVER] else False
        generate_level(game_parameters['map'], new_game=param)
        if GAME_OVER == mod:
            if game_obj['Stop'] is None:
                start_screen()
        if intro is False:
            timer()


def score_update():
    return font_score.render(str(game_parameters['score']), True,
                             pygame.Color("white"))


def start_screen():
    global intro_screen
    pygame.mixer.music.load(os.path.join('data/game/music', 'intro.wav'))
    pygame.mixer.music.play()
    if game_parameters['sound on'] is False:
        pygame.mixer.music.pause()
    im = SPRITES['ready!']
    all_sprites.update()
    pygame.time.set_timer(GAME_STARTING_EVENT_ID, 4200, True)
    intro_screen = True
    while intro_screen:
        events()
        check_game_status(intro=True)
        screen.fill(BLACK)
        screen.blit(im, (11 * CELL_SIZE, 17 * CELL_SIZE))
        draw_screen_items()
        game_obj['RegulateMusic'].update()
        all_sprites.draw(screen)
        if game_obj['Stop'] is not None:
            stop_group.draw(screen)
        pygame.display.flip()


def check_background_music():
    if pygame.mixer.music.get_busy() == 0 and game_parameters['sound on'] \
            is True and game_obj['Stop'] is None:
        pygame.mixer.music.load(os.path.join('data/game/music', 'fon.mp3'))
        pygame.mixer.music.play()
    if game_parameters['sound on'] is False or game_obj['Stop'] is not None:
        pygame.mixer.music.pause()


def draw_screen_items():
    screen.blit(update_fps(), (CELL_SIZE * 29, 0))
    screen.blit(score_update(), (int(CELL_SIZE * 28.5), CELL_SIZE * 3))
    screen.blit(update_level(), (CELL_SIZE * 28.5, CELL_SIZE * 5))
    screen.blit(update_lives(), (CELL_SIZE * 28.5, CELL_SIZE * 7))
    pygame.draw.rect(screen, BLUE, (0, 0, CELL_SIZE * 28, CELL_SIZE * 31),
                     width=1)


def check_screen_items():
    check_game_score()
    check_game_status()
    check_background_music()


def load_data():
    load_sprites()
    load_musics()
    game_parameters['map'] = load_level('map.txt')
    game_obj['RegulateMusic'] = RegulateMusic(29, 26, all_sprites)
    game_obj['Reset'] = Reset(28.75, 29, all_sprites)


def all_sprites_draw():
    if game_obj['Stop'] is None:
        all_sprites.update()
    all_sprites.draw(screen)
    if game_obj['Stop'] is not None:
        stop_group.draw(screen)

def draw_sprite_rects(screen, sprite_groups):
    for group in sprite_groups:
        for sprite in group:
            pygame.draw.rect(screen, (255, 0, 0), sprite.rect, 1)  # Rouge = contours

def draw_debug_rect_from_pos(screen, pos, sprite_type, color=(255, 0, 0)):
    x, y = pos

    if sprite_type == 'pacman':
        rect = pygame.Rect(
            CELL_SIZE * x -CELL_SIZE//4,
            CELL_SIZE * y -CELL_SIZE//4,
            CELL_SIZE *1.5,
            CELL_SIZE *1.5
        )
    elif sprite_type == 'ghost':
        rect = pygame.Rect(
            CELL_SIZE * x ,
            CELL_SIZE * y ,
            CELL_SIZE *1.5,
            CELL_SIZE *1.5
        )
    elif sprite_type == 'food':
        rect = pygame.Rect(
            CELL_SIZE * (x-1) + CELL_SIZE // 2 - 2,
            CELL_SIZE * (y-1) + CELL_SIZE // 2 - 2,
            4, 4
        )
    elif sprite_type == 'energizer':
        rect = pygame.Rect(
            CELL_SIZE * x,
            CELL_SIZE * y,
            CELL_SIZE, CELL_SIZE
        )
    else:
        raise ValueError(f"Type de sprite inconnu : {sprite_type}")

    pygame.draw.rect(screen, color, rect, 1)
    
if __name__ == '__main__':
    pygame.init()
    size = WIDTH, HEIGHT
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Pac-Man')
    pygame.display.set_icon(load_image('pacman.ico', key_path='game'))

    font = pygame.font.SysFont("Comic Sans MS", 32)
    font_score = pygame.font.SysFont("PerfectDOSVGA437", 62)

    clock = pygame.time.Clock()
    running = True
    load_data()
    generate_level(game_parameters['map'])
    start_screen()
    #foods_group_ia=deepcopy(foods_group)
    #energizers_group_ia=deepcopy(energizers_group)
    timer()
    while running:
        events()
        game_obj['Pac-Man'].key_pressed(ai.next_move(game_obj,game_parameters, enemy_group, foods_group, energizers_group))
        check_screen_items()
        screen.fill(BLACK)
        draw_screen_items()
        all_sprites_draw()
        #draw_debug_rect_from_pos(screen, position(game_obj['Pac-Man'])[:2], 'pacman', (0, 255, 0))
        
        for ghost in enemy_group:
            draw_debug_rect_from_pos(screen, position(ghost)[:2], 'ghost', (255, 0, 0))
        
        for food in foods_group:
            draw_debug_rect_from_pos(screen, position(food)[:2], 'food', (255, 255, 0))
        
        for energizer in energizers_group:
            draw_debug_rect_from_pos(screen, position(energizer)[:2], 'energizer', (0, 0, 255))
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()
