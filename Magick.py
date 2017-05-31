import argparse


class Picture(object):
    def __init__(self, table):
        self.s = '@%#*+=-:. '
        self.translate = {}
        for i, ch in enumerate(self.s):
            self.translate[ch] = i
        self.table = table

    def T(self):
        n = len(self.table)
        m = len(self.table[0])
        self.table = [[row[m - i - 1] for row in self.table] for i in range(m)]

    def rotate(self, angle):
        angle //= 90
        angle %= 4
        for i in range(angle):
            self.T()

    def crop(self, left=0, right=0, top=0, bottom=0):
        n = len(self.table)
        m = len(self.table[0])
        self.table = [row[left:m - right] for row in self.table[top:n - bottom]]

    def change(self, ch, add):
        new_ord = self.translate[ch] + add
        if add < 0:
            return self.s[max(new_ord, 0)]
        else:
            return self.s[min(new_ord, len(self.s) - 1)]

    def expose(self, add):
        n = len(self.table)
        m = len(self.table[0])
        for i in range(n):
            for j in range(m):
                self.table[i][j] = self.change(self.table[i][j], add)

    def __str__(self):
        return '\n'.join([''.join(row) for row in self.table])


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command")

    parser_crop = subparsers.add_parser('crop', help='Crop pisture')
    parser_crop.add_argument('-l', '--left', metavar='NUM', help="crop from left",
                             type=int, default=0)
    parser_crop.add_argument('-r', '--right', metavar='NUM', help="crop from right",
                             type=int, default=0)
    parser_crop.add_argument('-t', '--top', metavar='NUM', help="crop from top",
                             type=int, default=0)
    parser_crop.add_argument('-b', '--bottom', metavar='NUM', help="crop from bottom",
                             type=int, default=0)

    parser_expose = subparsers.add_parser('expose', help='add brightness to picture')
    parser_expose.add_argument('add', metavar='NUM', default=0, type=int)

    parser_rotate = subparsers.add_parser('rotate', help='rotate picture')
    parser_rotate.add_argument('angle', help="angle to rotate anti clockwise",
                               metavar='NUM', default=0, type=int)
    table = []
    with open('input.txt') as f:
        args = parser.parse_args(f.readline().split())
        for line in f.readlines():
            table.append(list(line)[:-1])

    picture = Picture(table)
    if args.command == 'crop':
        picture.crop(args.left, args.right, args.top, args.bottom)
        print(picture)
    elif args.command == 'expose':
        picture.expose(args.add)
        print(picture)
    elif args.command == 'rotate':
        picture.rotate(args.angle)
        print(picture)


if __name__ == "__main__":
    main()
