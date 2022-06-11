import math
import time
from sys import stdout
import keyboard


class ANSI:
    reset = '\u001b[0m'

    Bold = '\u001b[1m'
    Underline = '\u001b[4m'
    Reversed = '\u001b[7m'

    # Moving cursor

    up = '\u001b[{}A'
    down = '\u001b[{}B'
    right = '\u001b[{}C'
    left = '\u001b[{}D'
    next_line = '\u001b[{}E'
    prev_line = '\u001b[{}F'
    set_column = '\u001b[{n}G'
    set_position = '\u001b[{n};{m}H'

    clear_all = '\033[H\033[2J\033[3J'  # this one works like a charm
    clear_all2 = '\u001b[2J'            # this one not so much
    clear_beginning = '\u001b[1J'
    clear_end = '\u001b[0J'

    clear_line = '\u001b[2K'
    clear_line_start = '\u001b[1K'
    clear_line_end = '\u001b[0K'

    # Font Colors

    B_Black = '\u001b[40m'
    B_Red = '\u001b[41m'
    B_Green = '\u001b[42m'
    B_Yellow = '\u001b[43m'
    B_Blue = '\u001b[44m'
    B_Magenta = '\u001b[45m'
    B_Cyan = '\u001b[46m'
    B_White = '\u001b[47m'

    # Background colors

    B_Bright_Black = '\u001b[40;1m'
    B_Bright_Red = '\u001b[41;1m'
    B_Bright_Green = '\u001b[42;1m'
    B_Bright_Yellow = '\u001b[43;1m'
    B_Bright_Blue = '\u001b[44;1m'
    B_Bright_Magenta = '\u001b[45;1m'
    B_Bright_Cyan = '\u001b[46;1m'
    B_Bright_White = '\u001b[47;1m'

    color_map = {
        0: reset,  # transparent
        1: B_Black,
        2: B_Red,
        3: B_Green,
        4: B_Yellow,
        5: B_Blue,
        6: B_Magenta,
        7: B_Cyan,
        8: B_White,
        9: B_Bright_Black,
        10: B_Bright_Red,
        11: B_Bright_Green,
        12: B_Bright_Yellow,
        13: B_Bright_Blue,
        14: B_Bright_Magenta,
        15: B_Bright_Cyan,
        16: B_Bright_White,
    }


def color_replace(num_line, mono=False):  # replaces all the numbers on a line by the respective ANSI colors
    line = []
    for num in num_line:
        if mono:
            if num != 0:
                line.append(ANSI.B_Black)
        else:
            if num in ANSI.color_map:
                line.append(ANSI.color_map[num])
    return line


def matrix_init(width, height, num=0):
    matrix = []
    for y in range(height):
        line = []
        for x in range(width):
            line.append(num)
        matrix.append(line)
    return matrix


class Display:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = matrix_init(width, height, 8)
        return

    def display(self):
        log(ANSI.left.format(100))  # clear the user input
        log(ANSI.clear_all)
        print(self)
        return

    def __repr__(self, mono=False):
        output = ''
        for line in self.screen.__reversed__():
            output += '   '.join(color_replace(line, mono)) + f'   {ANSI.reset}\n'  # separator for different lines
        return output

    def inside_screen(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height


class GPU:
    def __init__(self, display: Display):
        self.display = display
        return

    def set_pixel(self, x, y, color=1):
        if self.display.inside_screen(x, y):
            self.display.screen[y][x] = color
        return

    def draw_pixel(self, pix):
        if isinstance(pix, int):
            x = pix % self.display.width
            y = pix // self.display.width
            self.set_pixel(x, y)
        elif pix is not None:
            x = pix[0] % self.display.width
            y = pix[0] // self.display.width
            self.set_pixel(x, y, pix[1])

    def draw_h_line(self, xa, ya, xb, color=1):
        if self.display.inside_screen(xa, ya) and self.display.inside_screen(xb, ya):
            if xa > xb:
                tmp = xa
                xa = xb
                xb = tmp
            for i in range(xa, xb + 1):
                self.display.screen[ya][i] = color
        return

    def draw_v_line(self, xa, ya, yb, color=1):
        if self.display.inside_screen(xa, ya) and self.display.inside_screen(xa, yb):
            if ya > yb:
                tmp = ya
                ya = yb
                yb = tmp
            for i in range(ya, yb + 1):
                self.display.screen[i][xa] = color
        return

    def draw_line(self, xa, ya, xb, yb, color=1):
        dx = xb - xa
        dy = yb - ya
        self.set_pixel(xa, ya, color)
        self.set_pixel(xb, yb, color)
        if dx < abs(dy) and abs(dx) > dy:
            dx = -dx
            dy = -dy
            tmp = xa
            xa = xb
            xb = tmp
            tmp = ya
            ya = yb
            yb = tmp

        if abs(dx) < dy:
            tmp = dx
            dx = dy
            dy = tmp
            tmp = xa
            xa = ya
            ya = tmp
            tmp = xb
            xb = yb
            yb = tmp

            m = (dy << 8) // dx
            y = (ya << 8) + 128
            mid_2x = ya + yb
            while xa < xb - 1:
                xa += 1
                xb -= 1
                y += m
                ya = y >> 8
                self.set_pixel(ya, xa, color)
                self.set_pixel(mid_2x - ya, xb, color)

        else:
            m = (dy << 8) // dx
            y = (ya << 8) + 128
            mid_2x = ya + yb
            while xa < xb - 1:
                xa += 1
                xb -= 1
                y += m
                ya = y >> 8
                self.set_pixel(xa, ya, color)
                self.set_pixel(xb, mid_2x - ya, color)
        return

    def draw_circle(self, xa, ya, r, fill=False, color=1):
        r_sq = r * r
        mid = round(r * 0.75)  # should be using cos(pi/4) or ~0.7071
        difference = 0
        adding = 1
        x = 0
        if fill:
            while x <= mid:
                y = math.ceil(math.sqrt(r_sq - difference))
                self.draw_h_line(xa - x, ya + y, xa + x, color)
                self.draw_h_line(xa - x, ya - y, xa + x, color)
                self.draw_h_line(xa - y, ya + x, xa + y, color)
                self.draw_h_line(xa - y, ya - x, xa + y, color)
                difference += adding
                adding += 2
                x += 1
        else:
            while x <= mid:
                y = math.ceil(math.sqrt(r_sq - difference))
                self.set_pixel(xa + x, ya + y, color)
                self.set_pixel(xa + x, ya - y, color)
                self.set_pixel(xa - x, ya + y, color)
                self.set_pixel(xa - x, ya - y, color)
                self.set_pixel(xa + y, ya + x, color)
                self.set_pixel(xa + y, ya - x, color)
                self.set_pixel(xa - y, ya + x, color)
                self.set_pixel(xa - y, ya - x, color)
                difference += adding
                adding += 2
                x += 1
        return

    def draw_rectangle(self, xa, ya, xb, yb, fill=False, color=1):
        if fill:
            if ya > yb:
                tmp = ya
                ya = yb
                yb = tmp
            for i in range(ya, yb + 1):
                self.draw_h_line(xa, i, xb, color)
        else:
            self.draw_v_line(xa, ya, yb)
            self.draw_v_line(xb, ya, yb)
            self.draw_h_line(xa, ya, xb)
            self.draw_h_line(xa, yb, xb)
        return

    def draw_triangle(self, xa, ya, xb, yb, xc, yc, fill=False, color=1):  # fill not implemented yet
        if fill:
            pass
        else:
            self.draw_line(xa, ya, xb, yb, color)
            self.draw_line(xb, yb, xc, yc, color)
            self.draw_line(xa, ya, xc, yc, color)
        return

    def draw_sprite(self, xa, ya, sprite):  # the sprite will overlap all that is below except the transparent parts
        # it will be placed with the corner closest to 0,0 at x,y
        width = sprite.width
        height = sprite.height

        for pix in sprite.data:
            x = pix[0] % width
            y = pix[0] // width
            self.set_pixel(xa + x, ya + y, pix[1])
        return

    def get_screen_sprite(self, x, y, width, height):
        sprite = []
        for i in range(height):
            for j in range(width):
                sprite.append((j + (i * height), self.display.screen[y + i][x + j]))

        return Sprite(width, height, sprite)


class Sprite:
    def __init__(self, width, height, args: list):  # each arg is tuple: (position, color_num)
        self.width = width
        self.height = height
        self.data = []
        for element in args:
            if len(element) == 1:  # was created with mono
                self.data.append((element[0], 1))
            elif len(element) == 2 and element[1] != 0:  # avoiding storing transparent pixels
                self.data.append(element)
        return

    def __repr__(self, mono=False):
        sprite = []
        for y in range(self.height):
            line = []
            for x in range(self.width):
                line.append(0)
            sprite.append(line)

        for pix in self.data:
            x = pix[0] % self.width
            y = pix[0] // self.width
            if self.in_bounds(x, y):
                sprite[y][x] = pix[1]

        output = ''
        for line in sprite.__reversed__():
            output += '   '.join(color_replace(line, mono)) + f'   {ANSI.reset}\n'  # separator for different lines
        return output

    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def transpose(self):
        output = []
        for pix in self.data:
            x = pix[0] % self.width
            y = pix[0] // self.width
            num = y + x * self.width
            output.append((num, pix[1]))
        return Sprite(self.height, self.width, output)

    def rotate_sq_ccw(self):   # +90 degrees, only works with square sprites
        constant = (self.width - 1) * self.height
        pixels = []
        for pix in self.data:
            x = pix[0] % self.width
            y = pix[0] // self.width
            pixels.append((constant + y - (x * self.width), pix[1]))

        return Sprite(self.width, self.height, pixels)

    def rotate_sq_cw(self):    # -90 degrees, only works with square sprites
        constant = self.width - 1
        pixels = []
        for pix in self.data:
            x = pix[0] % self.width
            y = pix[0] // self.width
            pixels.append((constant - y + (x * self.width), pix[1]))

        return Sprite(self.width, self.height, pixels)

    def rotate_ccw(self):
        return self.transpose().mirror_v()

    def rotate_cw(self):
        return self.transpose().mirror_h()

    def mirror_v(self):

        return  # TODO

    def mirror_h(self):

        return  # TODO

    def __copy__(self):
        return Sprite(self.width, self.height, self.data.copy())

    def is_empty(self):
        for pix in self.data:
            if pix[1] != 0:
                return False
        return True

    def bin_op_setup(self, other):
        set1 = set()
        for pix in self.data:
            set1.add(pix[0])

        set2 = set()
        for pix in other.data:
            set2.add(pix[0])

        return set1, set2

    def __or__(self, other):  # other will have color priority
        if self.height != other.height or self.width != other.width:  # assuming both sprites have the same size
            return
        set1, set2 = self.bin_op_setup(other)

        return Sprite(self.width, self.height, list(set1 | set2))

    def __and__(self, other):
        if self.height != other.height or self.width != other.width:  # assuming both sprites have the same size
            return
        set1, set2 = self.bin_op_setup(other)

        return Sprite(self.width, self.height, list(set1 & set2))

    def __xor__(self, other):
        if self.height != other.height or self.width != other.width:  # assuming both sprites have the same size
            return
        set1, set2 = self.bin_op_setup(other)

        return Sprite(self.width, self.height, list(set1 ^ set2))

    def __invert__(self):
        sprite = []
        for pix in self.data:
            if pix[1] == 0:
                sprite.append((pix[0], 1))
        return Sprite(self.width, self.height, sprite)

    def __sub__(self, other):
        return self & (~other)

    def __eq__(self, other):
        return set(self.data) == set(other.data)


def run(screen: Display, fps):
    running = True
    gpu = GPU(screen)
    while running:
        start = time.time()

        if keyboard.is_pressed('q'):
            break

        # code here
        gpu.draw_circle(10, 18, 7, fill=False)
        gpu.draw_circle(10, 18, 4, fill=True)

        gpu.draw_rectangle(20, 12, 45, 25)
        gpu.draw_rectangle(23, 14, 40, 20, fill=True, color=2)
        gpu.draw_triangle(1, 1, 20, 12, 27, 5)

        sprite = Sprite(3, 3, [(0, 1), (3, 2), (6, 1)])
        sprite2 = sprite.transpose()
        gpu.draw_sprite(5, 5, sprite)
        gpu.draw_sprite(3, 3, sprite2)

        log(ANSI.left.format(100))  # clear the user input
        print(screen)

        # don't mess with the line below
        time.sleep(max(1. / fps - (time.time() - start), 0))

    print('Terminating...')
    return


def main():
    screen = Display(48, 27)  # 80, 45   64, 36   48, 27   32, 18
    run(screen, 0.2)  # going faster than 5 fps will not be updated on the console

    return


def log(string):
    stdout.write(string)


if __name__ == "__main__":
    main()
