from .. import cmd_line_screen as s


def main():
    width = 48
    height = 27
    screen = s.Display(width, height)
    gpu = s.GPU(screen)


    return


if __name__ == "__main__":
    main()
