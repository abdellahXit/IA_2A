from global_names import *
from tools import *
from Ghost import Ghost


class Blinky(Ghost):
    def __init__(self, pos_x, pos_y, first_gr, second_gr):
        super().__init__(pos_x, pos_y, first_gr, second_gr, 'Blinky')
        self.at_home = False
        self.newborn['status'] = False
        self.newborn['move'] = CELL_SIZE * 2
        self.action = LEFT
        self.image = self.sprites[game_parameters['mod']][self.action][self.frame]
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect().move(CELL_SIZE * pos_x + CELL_SIZE // 4,
                                               CELL_SIZE * pos_y - CELL_SIZE // 4)
        self.real_rect_x = self.rect.x
        self.real_rect_y = self.rect.y
