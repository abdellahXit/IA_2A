from global_names import *
from Ghost import Ghost


class Inky(Ghost):
    def __init__(self, pos_x, pos_y, first_gr, second_gr):
        super().__init__(pos_x, pos_y, first_gr, second_gr, 'Inky')
        self.points_to_leave = 30
        self.newborn['action'] = RIGHT

    def new_target(self, target):
        act = game_obj['Pac-Man'].action
        if act in VERTICAL:
            target[0] = (-1) ** VERTICAL.index(act) * 2 + target[0]
        else:
            # this is bug in the original game
            target[0] += - 2 if act == UP else 0
            target[1] = (-1) ** HORIZONTAL.index(act) * 2 + target[1]

        target[0] = target[0] + (target[0] - (game_obj['Blinky'].rect.x
                                              + CELL_SIZE // 2) // CELL_SIZE)
        target[1] = target[1] + (target[1] - (game_obj['Blinky'].rect.y
                                              + CELL_SIZE // 2) // CELL_SIZE)
        return target
