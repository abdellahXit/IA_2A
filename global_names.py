import pygame

# sptite groups
all_sprites = pygame.sprite.Group()
borders_group = pygame.sprite.Group()
foods_group = pygame.sprite.Group()
energizers_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
attempts_group = pygame.sprite.Group()
stop_group = pygame.sprite.Group()
points_group = pygame.sprite.Group()

MUSIC = dict()

game_obj = {
    'Pac-Man': None,
    'Blinky': None,
    'Border': None,
    'Stop': None
}

# game mods
FRIGHTENED = 'frightened'
H_FRIGHTENED = 'half_frightened'
CHASE = 'chase'
SCATTER = 'scatter'
GAME_OVER = 'game over'
ROUND_OVER = 'round over'
ATTEMPT = 'attempt'
STOP = 'stop'
DEAD = 'dead'

LEVEL_TIME_CHANGE = {
    '1': [7, 20, 7, 20, 5, 20, 5],
    '2 3 4 5': [7, 20, 7, 20, 5, 1033, 1 / 60],
    'infinity': [5, 20, 5, 20, 5, 1037, 1 / 60]
}

game_parameters = {
    'mod': SCATTER,
    'level': 1,
    'lives' : 3,
    'timer_num': 0,
    'ate ghosts': -1,
    'stopped timer': LEVEL_TIME_CHANGE['1'][0] * 1000,
    'mod changed time': 0,
    'saved mod': None,
    'map': None,
    'score': 0,
    'score per round': 0,
    H_FRIGHTENED: False,
    'sound on': False
}




SPRITES = dict()

# screen options
WIDTH, HEIGHT = 990, 980
FPS = 60

SPEED = 3

DEFAULT_EVENT_ID = pygame.USEREVENT + 1
FRIGHTENED_EVENT_ID = pygame.USEREVENT + 2
HALF_FRIGHTENED_EVENT_ID = pygame.USEREVENT + 3
GAME_STARTING_EVENT_ID = pygame.USEREVENT + 4

CHANGE_TO_EVENT_ID = {
    FRIGHTENED: FRIGHTENED_EVENT_ID,
    H_FRIGHTENED: HALF_FRIGHTENED_EVENT_ID,
    CHASE: DEFAULT_EVENT_ID,
    SCATTER: DEFAULT_EVENT_ID
}

CELL_SIZE = 30

# sprite middle
MIDDLE = CELL_SIZE * 1.5 / 2

# field size, for tunnel
LEN_X = CELL_SIZE * 27

RIGHT = pygame.K_RIGHT
LEFT = pygame.K_LEFT
DOWN = pygame.K_DOWN
UP = pygame.K_UP

VERTICAL = [RIGHT, LEFT]
HORIZONTAL = [DOWN, UP]

actions = {
    RIGHT: (0, SPEED),
    LEFT: (0, -SPEED),
    DOWN: (SPEED, 0),
    UP: (-SPEED, 0),
}

opposite_keys = {
    RIGHT: LEFT,
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT
}

MODS_SPEED = {
    'frightened': SPEED * 0.6,
    'chase': SPEED,
    'scatter': SPEED,
    'tunnel': SPEED * 0.4,
    'dead': SPEED * 3
}

TUNNEL_CELLS = [[0, 14], [1, 14], [2, 14], [3, 14], [4, 14],
                [23, 14], [24, 14], [27, 14], [26, 14], [25, 14]]

BLOCK_CELLS = [[12, 11], [15, 11], [15, 23], [12, 23]]
THRESHOLD = [[13, 11], [14, 11]]

HOME_TAR = [13, 15]  # home target
h = [[i, 13] for i in range(11, 17)]
h.extend([[i, 14] for i in range(11, 17)])
h.extend([[i, 15] for i in range(11, 17)])
HOME = h.copy()  # home coordinates
h.extend([[13, 12], [14, 12]])
HOME_WITH_DOORS = h.copy()

target_in_scatter_mod = {
    'Blinky': (26, -3),
    'Pinky': (2, -3),
    'Inky': (27, 34),
    'Clyde': (0, 34)
}

# colors
BLACK = pygame.Color('black')
BLUE = pygame.Color('blue')
WHITE = pygame.Color('white')
FOODS_COLOR = (235, 146, 52)
