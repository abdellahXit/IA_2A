from global_names import *


class Border(pygame.sprite.Sprite):
    def __init__(self, first_gr, second_gr):
        super().__init__(first_gr, second_gr)
        self.image = pygame.transform.scale(SPRITES['Border'],
                                            (CELL_SIZE * 28, CELL_SIZE * 31))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)


class Food(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, first_gr, second_gr):
        super().__init__(first_gr, second_gr)
        self.image = pygame.Surface([4, 4])
        pygame.draw.rect(self.image, FOODS_COLOR, (0, 0, 4, 4))
        self.rect = self.image.get_rect().move(
            CELL_SIZE * pos_x + CELL_SIZE // 2 - 2,
            CELL_SIZE * pos_y + CELL_SIZE // 2 - 2)


class Energizer(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, first_gr, second_gr):
        super().__init__(first_gr, second_gr)

        first = pygame.Surface([CELL_SIZE, CELL_SIZE])
        pygame.draw.circle(first, FOODS_COLOR, (CELL_SIZE // 2,
                                                CELL_SIZE // 2), CELL_SIZE // 2)
        second = pygame.Surface([CELL_SIZE, CELL_SIZE])

        self.frame = 0
        self.sprites = [first, second]
        self.image = self.sprites[self.frame]
        self.rect = self.image.get_rect().move(
            CELL_SIZE * pos_x, CELL_SIZE * pos_y)

    def update(self):
        self.frame = (self.frame + 0.1) % len(self.sprites)
        self.image = self.sprites[int(self.frame)]


class RegulateMusic(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, gr):
        super().__init__(gr)
        self.image = SPRITES['sound_on']
        self.rect = self.image.get_rect().move(
            CELL_SIZE * pos_x, CELL_SIZE * pos_y)
        self.change_sound_mode()

    def change_sound_mode(self):
        if game_parameters['sound on']:
            game_parameters['sound on'] = False
            self.image = SPRITES['sound_off']
            pygame.mixer.music.pause()
            for i in MUSIC:
                MUSIC[i].stop()
        else:
            game_parameters['sound on'] = True
            self.image = SPRITES['sound_on']
            pygame.mixer.music.unpause()


class Points(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, gr1, gr2):
        super().__init__(gr1, gr2)
        self.image = SPRITES['points'][game_parameters['ate ghosts']]
        self.rect = self.image.get_rect().move(
            CELL_SIZE * pos_x, CELL_SIZE * pos_y)


class Stop(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, gr, gr2):
        super().__init__(gr, gr2)
        self.image = pygame.transform.scale(SPRITES['stop'],
                                            (int(CELL_SIZE) * 8,
                                             int(CELL_SIZE) * 8))
        self.rect = self.image.get_rect().move(
            CELL_SIZE * pos_x, CELL_SIZE * pos_y)


class Attempts(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, fr_gr, sec_gr):
        super().__init__(fr_gr, sec_gr)
        self.image = pygame.transform.scale(SPRITES['Attempts'],
                                            (int(CELL_SIZE),
                                             int(CELL_SIZE)))
        self.rect = self.image.get_rect().move(
            CELL_SIZE // 4 + CELL_SIZE * pos_x,
            CELL_SIZE // 4 + CELL_SIZE * pos_y)


class Reset(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, gr):
        super().__init__(gr)
        self.image = SPRITES['reset']
        self.rect = self.image.get_rect().move(
            CELL_SIZE // 4 + CELL_SIZE * pos_x,
            CELL_SIZE // 4 + CELL_SIZE * pos_y)
