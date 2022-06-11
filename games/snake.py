import time
from random import randint
import keyboard

import cmd_line_screen as s     # this line is meant to be used when running in the console
# from ...CMD_Line_Graphics import cmd_line_screen    # this one to be used when running on pycharm


def main():
    width = 48
    height = 27
    fps = 10
    screen = s.Display(width, height)
    gpu = s.GPU(screen)

    # variables
    heading = 2     # direction head is facing by default
    body = [0, 1, 2, 3, 4]
    apple = (generate_apple(width, height, body), 2)

    # setup drawing
    gpu.draw_pixel(apple)
    for pix in body:
        gpu.draw_pixel(pix)

    while True:
        start = time.time()

        if keyboard.is_pressed('q'):
            break
        next_pixel, heading = key_listener(width, height, heading, body[-1])

        if next_pixel == apple[0]:
            apple = (generate_apple(width, height, body), 2)
            gpu.draw_pixel(apple)

        elif next_pixel in body:
            break   # game over
        else:
            gpu.draw_pixel((body[0], 8))
            body.pop(0)

        body.append(next_pixel)
        gpu.draw_pixel(next_pixel)

        screen.display()
        # don't mess with the line below
        time.sleep(max(1. / fps - (time.time() - start), 0))

    print('Terminating...')
    return


def key_listener(width, height, heading, head):
    if keyboard.is_pressed('w'):
        return move('w', heading, head, width, height)
    if keyboard.is_pressed('a'):
        return move('a', heading, head, width, height)
    if keyboard.is_pressed('s'):
        return move('s', heading, head, width, height)
    if keyboard.is_pressed('d'):
        return move('d', heading, head, width, height)
    return move(None, heading, head, width, height)


def move(direction, heading, head, width, height):
    directions = {
        'w': 2,
        'a': 1,
        's': 0,
        'd': 3
    }
    if direction is not None and direction in directions:
        direction = directions[direction]
        if (direction - heading) & 1 != 0:
            heading = direction

    if heading == 0:
        next_pixel = (head - width) % (width * height)

    elif heading == 1:
        x = head % width
        next_pixel = head - 1
        if x == 0:
            next_pixel += width

    elif heading == 2:
        next_pixel = (head + width) % (width * height)

    elif heading == 3:
        x = head % width
        next_pixel = head + 1
        if x == width - 1:
            next_pixel -= width

    else:
        next_pixel = -1

    return next_pixel, heading


def generate_apple(width, height, body):
    possibilities = width * height - 1
    apple = randint(0, possibilities)
    while apple in body:
        apple = randint(0, possibilities)
    return apple


if __name__ == "__main__":
    main()
