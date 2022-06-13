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


# Class for every sprite (or hitbox)
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


# Class for every object. The user can create objects that extend this class, and inherit all listed methods
# each object has a concept of: space (position, hitbox)
#                               a third z dimension to allow objects to have priority when displaying
#                               visibility and orientation
# each object can also be related to others and the actions that happen to parent, will also be propagated to the child
class Object:
    def __init__(self, sprite: Sprite, position: int = -1, z=0, visible=True):
        self.position = position     # starting at -1 means not on the buffer
        self.sprite = sprite

        self.visible = visible
        self.orientation = 0
        self.z = z

        self.objects = []
        return

    def propagate_action(self, action, *args):  # apply the same function to the other objects
        for o in self.objects:
            action(o, args)
        return


# Class for living entities. The user can create objects that extend this class, and inherit all listed methods
# Each movable object has a concept of: movement on 2d plane (velocity, and acceleration)
#                                       mass
class MovableObject(Object):
    def __init__(self, sprite: Sprite, hitbox: Sprite, mass=1):
        super().__init__(sprite)
        self.hitbox = hitbox
        self.mass = mass
        self.velocity = {0, 0}
        self.acceleration = {0, 0}
        return


class Display:
    default_color = 8

    def __init__(self, width, height, fps=10):
        self.width = width
        self.height = height
        self.screen = matrix_init(width, height, self.default_color)
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
    def __init__(self, display: Display, width, height, zoom=1, tpf=1):
        self.display = display
        self.buffer = matrix_init(width, height, 8)
        self.width = width
        self.height = height
        self.x_offset = 0
        self.y_offset = 0
        self.zoom_fraction = zoom
        self.tpf = tpf  # ticks per frame
        self.objects = {0: set()}   # each z value will be mappet to a set of objects
        self.tick_count = 0
        return

    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def move_screen(self, x, y):
        self.x_offset += x
        self.y_offset += y
        return

    def set_screen_pos(self, x, y):
        self.x_offset = x
        self.y_offset = y
        return

    def set_zoom(self, zoom: float):    # float must be a power of 2. ex: 0.25, 0.5, 1, 2, 4...
        self.zoom_fraction = 1 / zoom
        return

    def zoom(self, zoom: float):   # zooming will zoom towards the center of the screen
        self.zoom_fraction /= zoom
        if zoom >= 1:
            self.x_offset += (self.display.width >> 2)
            self.y_offset += (self.display.height >> 2)
        else:
            self.x_offset -= (self.display.width >> 2)
            self.y_offset -= (self.display.height >> 2)
        return

    def draw_objects(self):
        for z in sorted(self.objects.keys()):
            objs = self.objects[z]
            for obj in objs:
                self.draw_sprite(obj.position, obj.sprite)
        return

    def print_frame(self):
        copy = self.buffer.copy()
        self.draw_objects()

        for y in range(self.display.height):
            buf_y_pos = int(y * self.zoom_fraction) + self.y_offset
            for x in range(self.display.width):
                buf_x_pos = int(x * self.zoom_fraction) + self.x_offset

                if not self.in_bounds(buf_x_pos, buf_y_pos):
                    self.display.screen[y][x] = 0   # out of range

                elif self.buffer[buf_y_pos][buf_x_pos] != 0:  # transparent should not be drawn
                    self.display.screen[y][x] = self.buffer[buf_y_pos][buf_x_pos]

        self.display.display()
        self.buffer = copy
        return

    def advance_tick(self):
        # todo
        # calculate physics collisions etc for every object

        if self.tick_count % self.tpf == 0:
            self.print_frame()
        self.tick_count += 1
        return

    # Coordinates section

    def num_to_coords(self, coords):
        return coords % self.width, coords // self.width

    def coords_to_num(self, x, y):
        return (self.width * y) + x

    # Pixel section

    def reset_pixel_at(self, x, y):
        self.draw_pixel_at(x, y, self.display.default_color)
        return

    def reset_pixel(self, pix):
        x, y = self.num_to_coords(pix)
        self.reset_pixel_at(x, y)
        return

    def draw_pixel_at(self, x, y, color=1):
        if self.in_bounds(x, y) and color != 0:
            self.buffer[y][x] = color
        return

    def draw_pixel(self, pix: int, color=1):
        x, y = self.num_to_coords(pix)
        self.draw_pixel_at(x, y, color)

    def get_pixel_at(self, x, y):
        return self.buffer[y][x]

    def get_pixel(self, pix: int):
        x, y = self.num_to_coords(pix)
        return self.get_pixel_at(x, y)

    # Line section

    def draw_h_line_at(self, xa, ya, xb, color=1):
        if self.in_bounds(xa, ya) and self.in_bounds(xb, ya):
            if xa > xb:
                tmp = xa
                xa = xb
                xb = tmp
            for i in range(xa, xb + 1):
                self.buffer[ya][i] = color
        return

    def draw_v_line_at(self, xa, ya, yb, color=1):
        if self.in_bounds(xa, ya) and self.in_bounds(xa, yb):
            if ya > yb:
                tmp = ya
                ya = yb
                yb = tmp
            for i in range(ya, yb + 1):
                self.buffer[i][xa] = color
        return

    def draw_line_at(self, xa, ya, xb, yb, color=1):
        dx = xb - xa
        dy = yb - ya
        self.draw_pixel_at(xa, ya, color)
        self.draw_pixel_at(xb, yb, color)
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
                self.draw_pixel_at(ya, xa, color)
                self.draw_pixel_at(mid_2x - ya, xb, color)

        else:
            m = (dy << 8) // dx
            y = (ya << 8) + 128
            mid_2x = ya + yb
            while xa < xb - 1:
                xa += 1
                xb -= 1
                y += m
                ya = y >> 8
                self.draw_pixel_at(xa, ya, color)
                self.draw_pixel_at(xb, mid_2x - ya, color)
        return

    def draw_line(self, pix1, pix2, color=1):
        xa, ya = self.num_to_coords(pix1)
        xb, yb = self.num_to_coords(pix2)
        self.draw_line_at(xa, ya, xb, yb, color)
        return

    # Polygons section

    def draw_circle_at(self, xa, ya, r, fill=False, color=1):
        r_sq = r * r
        mid = round(r * 0.75)  # should be using cos(pi/4) or ~0.7071
        difference = 0
        adding = 1
        x = 0
        if fill:
            while x <= mid:
                y = math.ceil(math.sqrt(r_sq - difference))
                self.draw_h_line_at(xa - x, ya + y, xa + x, color)
                self.draw_h_line_at(xa - x, ya - y, xa + x, color)
                self.draw_h_line_at(xa - y, ya + x, xa + y, color)
                self.draw_h_line_at(xa - y, ya - x, xa + y, color)
                difference += adding
                adding += 2
                x += 1
        else:
            while x <= mid:
                y = math.ceil(math.sqrt(r_sq - difference))
                self.draw_pixel_at(xa + x, ya + y, color)
                self.draw_pixel_at(xa + x, ya - y, color)
                self.draw_pixel_at(xa - x, ya + y, color)
                self.draw_pixel_at(xa - x, ya - y, color)
                self.draw_pixel_at(xa + y, ya + x, color)
                self.draw_pixel_at(xa + y, ya - x, color)
                self.draw_pixel_at(xa - y, ya + x, color)
                self.draw_pixel_at(xa - y, ya - x, color)
                difference += adding
                adding += 2
                x += 1
        return

    def draw_circle(self, pix, radius, fill=False, color=1):
        x, y = self.num_to_coords(pix)
        self.draw_circle_at(x, y, radius, fill, color)
        return

    def draw_elipse_at(self, x, y, v_radius, h_radius):

        return  # TODO

    def draw_elipse(self, pix, v_radius, h_radius):
        x, y = self.num_to_coords(pix)
        self.draw_elipse_at(x, y, v_radius, h_radius)
        return

    def draw_rectangle_at(self, xa, ya, xb, yb, fill=False, color=1):
        if fill:
            if ya > yb:
                tmp = ya
                ya = yb
                yb = tmp
            for i in range(ya, yb + 1):
                self.draw_h_line_at(xa, i, xb, color)
        else:
            self.draw_v_line_at(xa, ya, yb)
            self.draw_v_line_at(xb, ya, yb)
            self.draw_h_line_at(xa, ya, xb)
            self.draw_h_line_at(xa, yb, xb)
        return

    def draw_rectangle(self, pix1, pix2, fill=False, color=1):
        xa, ya = self.num_to_coords(pix1)
        xb, yb = self.num_to_coords(pix2)
        self.draw_rectangle_at(xa, ya, xb, yb, fill, color)
        return

    def draw_triangle_at(self, xa, ya, xb, yb, xc, yc, fill=False, color=1):  # fill not implemented yet
        if fill:

            pass    # TODO
        else:
            self.draw_line_at(xa, ya, xb, yb, color)
            self.draw_line_at(xb, yb, xc, yc, color)
            self.draw_line_at(xa, ya, xc, yc, color)
        return

    # Sprite section

    def draw_sprite_at(self, xa, ya, sprite):  # the sprite will overlap all that is below except the transparent parts
        # it will be placed with the corner closest to 0,0 at x,y
        width = sprite.width

        for pix in sprite.data:
            x = pix[0] % width
            y = pix[0] // width
            self.draw_pixel_at(xa + x, ya + y, pix[1])
        return

    def draw_sprite(self, pix, sprite):
        x, y = self.num_to_coords(pix)
        self.draw_sprite_at(x, y, sprite)
        return

    def get_screen_sprite_at(self, x, y, width, height):
        sprite = []
        for i in range(height):
            for j in range(width):
                sprite.append((j + (i * height), self.buffer[y + i][x + j]))

        return Sprite(width, height, sprite)

    # Object section

    def spawn_object(self, obj: Object, position, z=0):
        obj.position = position
        if z not in self.objects:
            self.objects[z] = set()
        self.objects[z].add(obj)
        obj.z = z
        return

    def kill_object(self, obj: Object):
        obj.position = -1
        if obj.z in self.objects:
            self.objects[obj.z].remove(obj)
            if len(self.objects[obj.z]) == 0:
                self.objects.pop(obj.z)
        return

    def set_obj_z(self, obj: Object, z: int):
        if obj.z in self.objects:
            self.objects[obj.z].remove(obj)
            if len(self.objects[obj.z]) == 0:
                self.objects.pop(obj.z)

        if z not in self.objects:
            self.objects[z] = set()
        self.objects[z].add(obj)
        obj.z = z
        return

    def set_obj_pos(self, obj: Object, pos):
        obj.position = pos
        return

    def move_obj(self, obj: Object, x, y):  # moves all the related child objects too
        current_x, current_y = self.num_to_coords(obj.position)
        x += current_x
        y += current_y
        if self.in_bounds(x, y):
            self.set_obj_pos(obj, self.coords_to_num(x, y))
        return

    def bring_obj_forward(self, obj: Object):
        top = max(self.objects.keys()) + 1
        self.set_obj_z(obj, top)
        return

    def bring_obj_backward(self, obj):
        self.set_obj_z(obj, 0)
        return


def run(scale, fps):
    running = True
    width = 16*scale
    height = 9*scale
    screen = Display(width, height)
    gpu = GPU(screen, width, height)
    while running:
        start = time.time()

        if keyboard.is_pressed('q'):
            break
        # code here
        # gpu.draw_circle_at(10, 18, 7, fill=False)
        # gpu.draw_circle_at(10, 18, 4, fill=True)
        # gpu.draw_triangle_at(1, 1, 20, 12, 27, 5)
        sprite = Sprite(3, 3, [(0, 1), (3, 2), (6, 1)])
        # sprite2 = sprite.transpose()
        # gpu.draw_sprite_at(5, 5, sprite)
        # gpu.draw_sprite_at(3, 3, sprite2)
        # gpu.draw_rectangle_at(20, 12, 45, 25)
        # gpu.draw_rectangle_at(23, 14, 40, 20, fill=True, color=2)

        obj = Object(sprite)
        gpu.spawn_object(obj, gpu.coords_to_num(5, 5))
        gpu.advance_tick()

        # don't mess with the line below
        time.sleep(max(1. / fps - (time.time() - start), 0))

    print('Terminating...')
    return


def main():
    scale = 4      # 35 is the max scale you can apply before the resolution doesn't fit in the buffer

    # display on console is limited by height of 323, anymore and doesn't appear on the buffer

    run(scale, 0.5)  # going faster than 5 fps will not be updated on the console

    return


def log(string):
    stdout.write(string)


if __name__ == "__main__":
    main()
