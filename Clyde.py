from global_names import *
from tools import position
from Ghost import Ghost


class Clyde(Ghost):
    def __init__(self, pos_x, pos_y, first_gr, second_gr):
        super().__init__(pos_x, pos_y, first_gr, second_gr, 'Clyde')
        self.points_to_leave = 90
        self.newborn['action'] = LEFT

    def new_target(self, target):
        pos = position(self)
        if (abs(pos[0] - target[0]) ** 2 + abs(
                pos[1] - target[1]) ** 2) ** 0.5 < 8:
            target = target_in_scatter_mod['Clyde']
        return target
