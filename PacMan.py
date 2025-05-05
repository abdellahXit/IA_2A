from global_names import *
from tools import *
import pygame
from Sprites import Points
import ai

class PacMan(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, first_gr, second_gr):
        super().__init__(first_gr, second_gr)
        self.frame = 0
        self.action = LEFT
        self.sprite = SPRITES['Pac-Man']
        self.image = self.sprite['start_image'][self.frame]
        self.temporary_action = None
        self.alive = True

        self.rect = self.image.get_rect().move(
            CELL_SIZE * pos_x + CELL_SIZE // 4,
            CELL_SIZE * pos_y - CELL_SIZE // 4)

        self.mask = pygame.mask.from_surface(self.image)

        self.real_rect_x = self.rect.x
        self.real_rect_y = self.rect.y

    def key_pressed(self, key):
        self.temporary_action = ((self.rect.x, self.rect.y), key)

    def dead(self):
        if game_parameters['sound on']:
            MUSIC["death"].play()
        self.alive = False
        for i in enemy_group:
            i.kill()

    def update(self):
        score = 0
        enemy = pygame.sprite.spritecollide(self, enemy_group, False)
        if len(enemy) != 0:
            enemy = enemy[0]
            x = abs(enemy.rect.x - self.rect.x)
            y = abs(enemy.rect.y - self.rect.y)
            if (position(self) == position(enemy) or (
                    x < 25 and y < 25)) and enemy.alive:
                if enemy.frightened:
                    game_parameters['ate ghosts'] += 1
                    sc = (2 ** game_parameters['ate ghosts']) * 200
                    x1, y1 = position(self)
                    Points(x1, y1, points_group, all_sprites)
                    if game_parameters['sound on']:
                        MUSIC['eat_ghost'].play()
                    score += sc
                    enemy.dead()
                    enemy.alive=False
                else:
                    self.dead()
                    game_parameters['lives']-=1
                    self.frame = 0

        if self.alive is False:
            frame_speed = 0.15
        else:
            frame_speed = 0.2

        if self.action in possible_keys(self) or self.alive is False:
            if self.alive is True:
                path = self.sprite['alive'][self.action]
            else:
                path = self.sprite['dead']
            self.frame = self.frame + frame_speed
            # the number of lives has reached 0 in here
            if self.frame >= len(self.sprite['dead']) and self.alive is False :
                kill_attempt_and_reset_game()
                return None

            if self.alive:
                self.frame = self.frame % len(path)

            self.image = path[int(self.frame)]
            self.mask = pygame.mask.from_surface(self.image)

            if self.alive is True:
                move_x, move_y = correct_move(self, actions)
                self.real_rect_x = (self.real_rect_x + move_x) % LEN_X
                self.real_rect_y = (self.real_rect_y + move_y)

                self.rect.x = int(self.real_rect_x)
                self.rect.y = int(self.real_rect_y)

        

        # helps to turn at corners
        if self.temporary_action is not None:
            cells_passed = abs(
                self.rect.x - self.temporary_action[0][0]) // CELL_SIZE \
                           + abs(
                self.rect.y - self.temporary_action[0][1]) // CELL_SIZE
            if cells_passed <= 1.5:
                if self.temporary_action[1] in possible_keys(self):
                    self.action = self.temporary_action[1]
                    self.temporary_action = None
            else:
                self.temporary_action = None
                
        if len(pygame.sprite.spritecollide(self, foods_group, True)) == 1:
            score += 10
            if game_parameters['sound on']:
                MUSIC['munch'].stop()
                MUSIC['munch'].play()
        if len(pygame.sprite.spritecollide(self, energizers_group, True)) == 1:
            score += 50
            change_way()
            if game_parameters['level'] < 19:
                stop_timer()
                game_parameters['ate ghosts'] = -1
            for enemy in enemy_group:
                enemy.frightened=True
        game_parameters['score per round'] += score
        game_parameters['score'] += score
