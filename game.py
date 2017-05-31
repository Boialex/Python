#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Реализован интерфейс и боты для игры "Реверси"
https://ru.wikipedia.org/wiki/Реверси
Интерфейс может работать как в консольном режиме,
так и с графической UI (реализовано на PyQT5)

Умный бот для каждого возможного хода запускает times
игр между рандомными ботами и выбирает самый частый по выигрышам
Этого хватает чтобы обыгрывать рандомного в >90% игр

По правилам черные ходят первыми и по статистике получается, что
они чаще проигрывают (например если запускать два рандомных бота).
Поэтому выиграть черными сложнее.
"""

import sys
import argparse
import random
from enum import Enum
from collections import namedtuple
import copy
import operator

from PyQt5.QtWidgets import QDesktopWidget, QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, QEventLoop


class State(Enum):
    NO = 0
    WHITE = 1
    BLACK = 2


Point = namedtuple('Point', ['x', 'y'])
Line = namedtuple('Line', ['begin', 'end'])

Direction = namedtuple('Direction', ['dx', 'dy'])
DIRECTIONS = (Direction(1, 0), Direction(1, 1), Direction(0, 1), Direction(-1, 1),
              Direction(-1, 0), Direction(-1, -1), Direction(0, -1), Direction(1, -1))


class Bot(object):
    def __init__(self, colour):
        self.colour = colour

    def turn(self, table):
        pass

    @staticmethod
    def get_possibilities(table, colour):  # find available moves
        anticolour = State.WHITE if colour == State.BLACK else State.BLACK
        possibilities = []
        for i in range(1, 9):
            for j in range(1, 9):
                if table[i][j] == State.NO:
                    for direction in DIRECTIONS:
                        k = 1
                        x, y = i + k * direction.dx, j + k * direction.dy
                        while table[x][y] == anticolour:
                            k += 1
                            x, y = i + k * direction.dx, j + k * direction.dy
                        if k != 1 and table[x][y] == colour:
                            possibilities.append(Point(i, j))
        return possibilities


class RandomBot(Bot):
    def __init__(self, colour):
        super(RandomBot, self).__init__(colour)

    def turn(self, table):
        possibilities = Bot.get_possibilities(table, self.colour)
        if len(possibilities) == 0:
            return 'stay'
        else:
            return 'move', random.choice(possibilities)


class CleverBot(Bot):
    def __init__(self, colour, times=10):
        super(CleverBot, self).__init__(colour)
        self.times = times

    def turn(self, table):
        possibilities = Bot.get_possibilities(table, self.colour)
        anticolour = State.WHITE if self.colour == State.BLACK else State.BLACK
        if len(possibilities) == 0:
            return 'stay'
        else:  # for each possible move let's run times games with two random bots and choose best
            wins = []
            for move in possibilities:
                count_wins = 0
                for t in range(self.times):
                    new_interface = Interface()
                    new_interface.table = copy.deepcopy(table)
                    new_interface.repaint(move, self.colour)  # start new game as if move was done
                    if new_interface.play(RandomBot(anticolour),
                                          RandomBot(self.colour)) == self.colour:
                        count_wins += 1
                wins.append(count_wins)
            best = max(enumerate(wins), key=operator.itemgetter(1))[0]
            return 'move', possibilities[best]


class UserBot(Bot):
    def __init__(self, colour, window=None):
        super(UserBot, self).__init__(colour)
        self.window = window

    def turn(self, table):
        possibilities = Bot.get_possibilities(table, self.colour)
        if len(possibilities) == 0:
            return 'stay'
        move = ('move', '0', '0')
        while Point(int(move[1]), int(move[2])) not in possibilities:  # check correctness
            if self.window:
                move = self.window.get_user_move()  # get from UI where mouse clicked
            else:  # input from console
                print('move x y')
                move = input(sys.stdin).split()
        return move[0], Point(int(move[1]), int(move[2]))

    def set_window(self, window):
        self.window = window


class Interface(object):
    def __init__(self, window=None):
        self.size = 8
        self.borders = 2  # not to check iterator out of range
        self.table = [[State.NO
                       for i in range(self.size + self.borders)]
                      for j in range(self.size + self.borders)]

        self.table[4][4] = State.WHITE
        self.table[5][5] = State.WHITE
        self.table[4][5] = State.BLACK
        self.table[5][4] = State.BLACK

        self.window = window

    def play(self, first_bot, second_bot, user=False):
        place_left = self.count_left()
        stay = False
        previous_stay = False  # if 2 stays then game stops because no possibilities to move
        self.bots = (first_bot, second_bot)

        while place_left > 0 and not (previous_stay and stay):
            for bot in self.bots:
                correct_move = False
                while not correct_move:
                    move = bot.turn(self.table)
                    if move == 'stay':
                        if not Bot.get_possibilities(self.table, bot.colour):
                            correct_move = True
                            stay = True
                    elif move[0] == 'move':
                        if self.check(move[1], bot.colour):
                            stay = False
                            correct_move = True
                            self.repaint(move[1], bot.colour)
                    if not correct_move and user:
                        print('wrong turn')
                if user:
                    print(move, bot.colour, self, sep='\n', end='\n' * 2)
                if stay and previous_stay:
                    break
                else:
                    previous_stay = stay
        winer = self.win()
        if self.window:
            self.window.end_game(winer)
        self.clean()
        return winer

    def count_left(self):
        count = 0
        for row in self.table[1:-1]:
            for x in row[1:-1]:
                if x == State.NO:
                    count += 1
        return count

    def clean(self):
        self.table = [[State.NO
                       for i in range(self.size + self.borders)]
                      for j in range(self.size + self.borders)]

        self.table[4][4] = State.WHITE
        self.table[5][5] = State.WHITE
        self.table[4][5] = State.BLACK
        self.table[5][4] = State.BLACK

        if self.window:
            self.window.update()

    def check(self, where, colour):
        if self.table[where.x][where.y] != State.NO:
            return False

        anticolour = State.WHITE if colour == State.BLACK else State.BLACK
        for direction in DIRECTIONS:
            k = 1
            x, y = where.x + k * direction.dx, where.y + k * direction.dy
            while self.table[x][y] == anticolour:
                k += 1
                x, y = where.x + k * direction.dx, where.y + k * direction.dy
            if k != 1 and self.table[x][y] == colour:
                return True
        return False

    def repaint(self, where, colour):
        anticolour = State.WHITE if colour == State.BLACK else State.BLACK
        for direction in DIRECTIONS:
            k = 1
            x, y = where.x + k * direction.dx, where.y + k * direction.dy
            while self.table[x][y] == anticolour:
                k += 1
                x, y = where.x + k * direction.dx, where.y + k * direction.dy
            if k != 1 and self.table[x][y] == colour:
                for i in range(k):
                    x, y = where.x + i * direction.dx, where.y + i * direction.dy
                    self.table[x][y] = colour

        if self.window:
            self.window.update()

    def win(self):
        count_white = 0
        count_black = 0
        for row in self.table:
            for x in row:
                if x == State.WHITE:
                    count_white += 1
                if x == State.BLACK:
                    count_black += 1
        if count_white > count_black:
            return State.WHITE
        elif count_black > count_white:
            return State.BLACK
        else:
            return State.NO

    def __str__(self):
        return '\n'.join(' '.join(map(lambda x: str(x.value), row[1:-1]))
                         for row in self.table[1:-1])

    def set_window(self, window):
        self.window = window


class Field(QMainWindow):
    def __init__(self, *args):
        super().__init__()
        self.width, self.height = args[0], args[1]
        self.cell_width, self.cell_height = self.width // 8, self.height // 8

        self.grid = [Line(QPoint(self.cell_width * k, 0),
                          QPoint(self.cell_width * k, self.height)) for k in range(1, 8)]
        self.grid += [Line(QPoint(0, self.cell_height * k),
                           QPoint(self.width, self.cell_height * k)) for k in range(1, 8)]
        self.interface = args[-1]
        self.user_turn = False
        self.user_move = None
        self.loop = QEventLoop()
        self.initUI()

    def initUI(self):
        self.resize(self.width, self.height)
        self.center()

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.green)
        self.setPalette(p)

        self.statusBar()

        self.setWindowTitle('Reversi')
        self.show()

    def paintEvent(self, e):
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        qp = QPainter()
        qp.begin(self)
        qp.setPen(pen)
        for line in self.grid:
            qp.drawLine(line.begin, line.end)
        diam = min(self.cell_width, self.cell_height) / 2
        for i in range(1, 9):
            for j in range(1, 9):
                if self.interface.table[i][j] != State.NO:
                    if self.interface.table[i][j] == State.BLACK:
                        qp.setBrush(Qt.black)
                    else:
                        qp.setBrush(Qt.white)
                    center = QPoint(i * self.cell_width, j * self.cell_height) - QPoint(diam, diam)
                    qp.drawEllipse(center, diam / 1.5, diam / 1.5)
        qp.end()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, QMouseEvent):
        if self.user_turn:
            pos = QMouseEvent.pos()
            i, j = (pos.x() // self.cell_width) + 1, (pos.y() // self.cell_height) + 1
            self.user_move = ('move', str(i), str(j))
            self.loop.quit()
            self.user_turn = False

    def get_user_move(self):
        self.user_turn = True
        self.statusBar().showMessage('Your turn')
        self.loop.exec_()
        self.statusBar().showMessage('')
        return self.user_move

    def end_game(self, winer):
        if winer == State.WHITE:
            winer = 'white wins'
        elif winer == State.BLACK:
            winer = 'black wins'
        else:
            winer = 'draw'
        QMessageBox.information(self, 'end of game', winer)
        exit(0)

    def closeEvent(self, QCloseEvent):
        exit(0)


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command")

    parser_test = subparsers.add_parser('test',
                                        help='Test bots playing,\n'
                                             'first is random, second:\n'
                                             '--mode=clever for clever bot,\n'
                                             '--mode=random for random bot,\n'
                                             'default=clever')
    parser_test.add_argument('-m', '--mode', dest='mode', choices=['clever', 'random'],
                             default='clever', type=str)
    parser_test.add_argument('-n', dest='test_games', default=50, help='games to run', type=int)

    parser_play = subparsers.add_parser('play', help='Play with bot')
    parser_play.add_argument('-m', '--mode', dest='mode', choices=['clever', 'random'],
                             default='clever', type=str,
                             help='your opponent: random/clever, default=clever')
    parser_play.add_argument('-c', '--colour', choices=['black', 'white'],
                             default='black', type=str,
                             help='your colour: black/white, default=black')
    parser_play.add_argument('-w', '--width', dest='width', default=500,
                             type=int, help='window width')
    parser_play.add_argument('-ht', '--height', dest='height', default=500,
                             type=int, help='window height')

    args = parser.parse_args()
    if args.command == 'test':
        interface = Interface()
        test_games = args.test_games
        black_wins = 0
        white_wins = 0
        bot = RandomBot
        if args.mode == 'clever':
            bot = CleverBot
        for i in range(test_games):
            if interface.play(bot(State.BLACK), RandomBot(State.WHITE)) == State.BLACK:
                black_wins += 1

        for i in range(test_games):
            if interface.play(RandomBot(State.BLACK), bot(State.WHITE)) == State.WHITE:
                white_wins += 1
        print('win rate black', black_wins / test_games)
        print('win rate white', white_wins / test_games)

    elif args.command == 'play':
        interface = Interface()
        app = QApplication(sys.argv)
        field = Field(args.width, args.height, interface)
        interface.set_window(field)
        if args.mode == 'clever':
            opponent = CleverBot
        else:
            opponent = RandomBot
        if args.colour == 'black':
            print(interface.play(UserBot(State.BLACK, field), opponent(State.WHITE), True))
        else:
            print(interface.play(opponent(State.BLACK), UserBot(State.WHITE, field), True))
        sys.exit(app.exec_())


if __name__ == "__main__":
    main()
