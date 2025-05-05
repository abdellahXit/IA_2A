from global_names import *
from Ghost import Ghost


class Pinky(Ghost):
    def __init__(self, pos_x, pos_y, first_gr, second_gr):
        super().__init__(pos_x, pos_y, first_gr, second_gr, 'Pinky')

    def new_target(self, target):
        act = game_obj['Pac-Man'].action
        if act in VERTICAL:
            target[0] = (-1) ** VERTICAL.index(act) * 4 + target[0]
        else:
            # this is bug in the original game
            target[0] += -4 if act == UP else 0
            target[1] = (-1) ** HORIZONTAL.index(act) * 4 + target[1]
        return target
