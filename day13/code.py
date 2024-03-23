from util import *
from intcode import *

import os


@click.group()
def cli():
    pass


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    data = process_intcode(input)
    cpu = Intcode(data)
    grid = GridN(default=0)

    while True:
        try:
            x, y, tile_id = cpu.run_to_output(3)
            grid.set((x, y), tile_id)
        except Intcode.Halted:
            break

    print(Counter(grid.g.values())[2])


DISPLAY = {
    0: " ",
    1: "█",
    2: "▒",
    3: "═",
    4: "©",
}

framerate = 1 / 30


@cli.command()
@click.argument("file", type=click.File())
def part2(file):
    data = process_intcode(file)
    data[0] = 2  # free play!

    cpu = Intcode(data)
    grid = GridN(default=" ")

    all_input = []
    ball = -1
    paddle = -1

    s = time.time()
    while True:
        try:
            x, y, tile_id = cpu.run_to_output(3)
            p = (x, y)

            if p == (-1, 0) and tile_id:
                score = tile_id
            else:
                if tile_id == 3:
                    paddle = x
                if tile_id == 4:
                    ball = x
                grid.set((x, y), DISPLAY[tile_id])
        except Intcode.WaitingForInput:
            t = time.time()
            elapsed = t - s
            s = t
            if elapsed < framerate:
                # print(elapsed, framerate)
                # return
                time.sleep(framerate - elapsed)
            click.clear()
            grid.print()
            if PRESTORED:
                next_input = PRESTORED.pop(0)
            else:
                try:
                    default = "-1" if ball < paddle else "1" if ball > paddle else "0"
                    k = input(f"dir? [{default}] ") or default
                    if k == "-":
                        k = "-1"
                    next_input = int(k)
                    if next_input not in (-1, 0, 1):
                        next_input = 0
                except ValueError:
                    print("<invalid>")
                    next_input = 0
                except KeyboardInterrupt:
                    print(all_input)
                    raise

            cpu.input.append(next_input)
            all_input.append(next_input)
        except Intcode.Halted:
            break

    print(cpu.input)
    print(all_input)
    print(score)


PRESTORED = json.load(
    open(os.path.join(os.path.dirname(__file__), "prestored_input.txt"))
)

if __name__ == "__main__":
    cli()
