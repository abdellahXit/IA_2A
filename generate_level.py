from Sprites import *
from global_names import *
from PacMan import PacMan
from Blinky import Blinky
from Pinky import Pinky
from Inky import Inky
from Clyde import Clyde


def generate_level(level, new_game=True):
    if new_game:
        game_obj['Border'] = Border(borders_group, all_sprites)
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '.':
                    Food(x, y, foods_group, all_sprites)
                elif level[y][x] == '0':
                    Energizer(x, y, energizers_group, all_sprites)
        for i in range(3):
            Attempts(i, 31, attempts_group, all_sprites)

    game_obj['Pac-Man'] = PacMan(13, 23, player_group, all_sprites)
    game_obj['Blinky'] = Blinky(13, 11, enemy_group, all_sprites)
    Pinky(13, 14, enemy_group, all_sprites)
    Inky(11, 14, enemy_group, all_sprites)
    Clyde(15, 14, enemy_group, all_sprites)
