#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import random


class EmptyWindow(Exception):
    def __init__(self, position):
        self.position = position

    def __str__(self):
        return str(self.position)


class OceanObject(object):
    def __init__(self, position):
        self.position = position

    def action(self, possibilities):
        pass

    def get_position(self):
        return tuple(self.position)

    def get_table_coordinates(self, window_coordinates):
        return (self.position[0] + window_coordinates[0] - 1,
                self.position[1] + window_coordinates[1] - 1)


class Wall(OceanObject):
    def __init__(self, position):
        super(Wall, self).__init__(position)

    def __str__(self):
        return '#'


class Victim(OceanObject):
    def __init__(self, position, birth_time=30):
        super(Victim, self).__init__(position)
        self.birth_time = birth_time
        self.after_birth = 0

    def action(self, possibilities):
        assert self.after_birth <= self.birth_time, \
            'wrong birth count'
        free_cells = possibilities['free']
        if free_cells:  # теперь жертвы тоже тупые :)
            return self.birth_or_move(free_cells[random.choice(range(len(free_cells)))])
        else:
            self.after_birth += 1
            if self.after_birth >= self.birth_time:
                self.after_birth = 0
            return 'stay', self.get_position()
            # just stay if no free cells around

    def birth_or_move(self, where):
        where = self.get_table_coordinates(where)
        if self.after_birth == self.birth_time:
            self.after_birth = 0
            return 'new', where, Victim(where, self.birth_time)
        else:
            self.after_birth += 1
            return 'move', where

    def __str__(self):
        return 'v'


class Predator(OceanObject):
    def __init__(self, position, birth_time=30, starvation=7):
        super(Predator, self).__init__(position)
        self.birth_time = birth_time
        self.after_birth = 0
        self.starvation = starvation
        self.no_food = 0

    def action(self, possibilities):
        assert self.after_birth <= self.birth_time, \
            'wrong birth count'
        free_cells = possibilities['free']
        eat_cells = possibilities['eat']

        if free_cells and self.after_birth == self.birth_time:
            where = self.get_table_coordinates(free_cells[random.choice(range(len(free_cells)))])
            self.after_birth = 0
            return 'new', where, Predator(where, self.birth_time, self.starvation)

        if eat_cells:
            self.no_food = 0

            if self.after_birth >= self.birth_time:
                self.after_birth = 0

            where = eat_cells[random.choice(range(len(eat_cells)))]
            where = self.get_table_coordinates(where)
            return 'eat', where
        else:
            self.no_food += 1
            if free_cells:
                return self.birth_or_move(free_cells[random.choice(range(len(free_cells)))])
            else:
                self.after_birth += 1
                if self.after_birth >= self.birth_time:
                    self.after_birth = 0
                return 'stay', self.get_position()  # just stay if no free cells around

    def birth_or_move(self, where):
        where = self.get_table_coordinates(where)
        if self.after_birth == self.birth_time:
            self.after_birth = 0
            return 'new', where, Predator(where, self.birth_time, self.starvation)
        else:
            self.after_birth += 1
            return 'move', where

    def __str__(self):
        return 'p'


class OceanCell(object):
    """
    Добавим класс клетка, чтобы оставить логику хода, гибели, поедания и т.д. у объекта,
    а не океана. Так как класс не может сам себя удалить, а хранить ссылку на океан в объекте я
    считаю неправильным, т.к. тогда объект знает слишком много, то оставим это на клетку,
    которая будет хранить объект и убьет его, если надо.
    """
    def __init__(self):
        self.object = None
        self.child = None
        self.alive = False

    def push_object(self, object):
        self.object = object
        self.alive = True

    def has_creature(self):
        if isinstance(self.object, Predator) or isinstance(self.object, Victim):
            return True
        else:
            return False

    def is_free(self):
        return self.object is None

    def get_position(self):
        assert self.object is not None
        return self.object.get_position()

    def has_victim(self):
        if isinstance(self.object, Victim):
            return True
        else:
            return False

    def has_predator(self):
        if isinstance(self.object, Predator):
            return True
        else:
            return False

    def get_child(self):
        return self.child

    def is_alive(self):
        return self.alive

    def kill(self):
        self.object = None
        self.alive = False

    def action(self, window):
        if self.object is None:
            return  # уже съели
        decision = self.object.action(self.get_possibilities(window))
        self.apply_turn(window, decision)

    def check_predator_alive(self):
        if self.has_predator():
            if self.object.no_food >= self.object.starvation:
                self.kill()
                return False
        return True

    def apply_turn(self, window, decision):
        where_on_table = decision[1]
        pos = self.object.get_position()
        where = (where_on_table[0] - pos[0] + 1, where_on_table[1] - pos[1] + 1)  # in window
        if decision[0] == "new":
            window[where[0]][where[1]].push_object(decision[2])
            self.check_predator_alive()

        elif decision[0] == "move":
            if self.check_predator_alive():
                self.object.position = where_on_table
                window[where[0]][where[1]].push_object(self.object)
                self.object = None
                self.alive = False

        elif decision[0] == "eat":
            self.object.position = where_on_table
            window[where[0]][where[1]].kill()
            window[where[0]][where[1]].push_object(self.object)
            self.object = None
            self.alive = False

    @staticmethod
    def get_possibilities(window):
        is_predator = window[1][1].has_predator()
        possibilities = {'free': [], 'eat': []}
        for i, row in enumerate(window):
            for j, x in enumerate(row):
                if i == j == 1:
                    continue
                if x.is_free():
                    possibilities['free'] += [(i, j)]
                else:
                    if is_predator and x.has_victim():
                        possibilities['eat'] += [(i, j)]
        return possibilities

    def __str__(self):
        if self.object is None:
            return ' '
        else:
            return str(self.object)


class Ocean(object):
    def __init__(self, m=10, n=10,
                 n_victims=10, n_predators=10, n_walls=1,
                 birth_time_victims=10, birth_time_predators=15,
                 starvation=13):
        assert m * n > n_predators + n_victims + n_walls, \
            'creatures more than place'

        self.shape = (m, n)
        self.border_size = 1
        self.table_size = (m + 2 * self.border_size, n + 2 * self.border_size)
        self.chars_for_objects = {'wall': '#', 'victim': 'v', 'predator': 'p'}
        self.starvation = starvation
        self.birth_time_victims = birth_time_victims
        self.birth_time_predators = birth_time_predators
        self.table = [[OceanCell() for j in xrange(self.table_size[1])]
                      for i in xrange(self.table_size[0])]
        self.n_victims = n_victims
        self.n_predators = n_predators
        self.creature_cells = []

        n_obj = n_victims + n_predators + n_walls
        indices = [(i + 1, j + 1) for j in xrange(n) for i in xrange(m)]
        indices = random.sample(indices, n_obj)

        for i in xrange(n_victims):
            x, y = indices[i][0], indices[i][1]
            new_victim = Victim((x, y), birth_time=self.birth_time_victims)
            self.table[x][y].push_object(new_victim)
            self.creature_cells += [self.table[x][y]]

        for i in xrange(n_predators):
            x, y = indices[i + n_victims][0], indices[i + n_victims][1]
            new_predator = Predator((x, y), birth_time=self.birth_time_predators,
                                    starvation=self.starvation)
            self.table[x][y].push_object(new_predator)
            self.creature_cells += [self.table[x][y]]

        for i in xrange(n_walls):
            x, y = indices[-i - 1]
            self.table[x][y].push_object(Wall((x, y)))
            self.fill_the_border()

    def fill_the_border(self):  # чтобы при обходе циклом не думать о выходе за границы i +,- 1
        m, n = self.table_size
        for i in xrange(n):
            self.table[0][i].push_object(Wall((0, i)))
            self.table[m - 1][i].push_object(Wall((m - 1, i)))
        for i in xrange(m):
            self.table[i][0].push_object(Wall((i, 0)))
            self.table[i][n - 1].push_object(Wall((i, n - 1)))

    def action(self):
        assert self.n_victims >= 0 and self.n_predators >= 0
        for creature_cell in self.creature_cells:
            if creature_cell.is_alive():
                window = self.get_window(creature_cell.get_position())
                creature_cell.action(window)
        self.update_creatures_list()

    def update_creatures_list(self):
        n_victims = 0
        n_predators = 0
        alive_creatures = []
        for row in self.table:
            for cell in row:
                if cell.has_creature() and cell.is_alive():
                    alive_creatures += [cell]
                    alive_creatures += [cell]
                    n_victims += cell.has_victim()
                    n_predators += cell.has_predator()

        self.n_predators = n_predators
        self.n_victims = n_victims
        self.creature_cells = alive_creatures

    def emulate(self, max_iter=10**12):
        n_victims = []
        n_predators = []
        for time in xrange(max_iter):
            self.action()
            n_victims += [self.n_victims]
            n_predators += [self.n_predators]
            if self.n_victims == 0 or self.n_predators == 0:
                break
        return n_victims, n_predators

    def get_window(self, position):  # return 3*3 window around creature
        columns = self.table[position[0] - 1: position[0] + 2]
        window = [row[position[1] - 1: position[1] + 2] for row in columns]
        return window

    def __str__(self):
        rows = [str()] * (self.shape[0] * 2 + 5)
        rows[0] = str(self.chars_for_objects)
        for i in xrange(self.shape[0] + 2):
            s = ''
            for x in self.table[i]:
                s += str(x) + '|'
            rows[2 * i + 1] = s
            rows[2 * i + 2] = '-+' * (self.shape[1] + 2)
        return '\n'.join(rows[:-1])


def main():
    ocean = Ocean()
    ocean.emulate(10**3)

if __name__ == "__main__":
    main()
