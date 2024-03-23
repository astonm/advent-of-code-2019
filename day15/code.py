from util import *
from intcode import *

import os


@click.group()
def cli():
    pass


DISPLAY = {
    0: "█",
    1: " ",
    2: "O",
}


def get_map_with_oxygen(code):
    cpu = Intcode(code)

    grid = GridN(default=" ")
    grid.set((0, 0), " ")

    seen = set([(0, 0)])
    q = [((0, 0), cpu, [])]
    while q:
        p, cpu, path = q.pop(0)

        if grid.get(p) == "O":
            fill_start = (p, len(path))

        for direction in [1, 2, 3, 4]:
            if direction == 1:
                np = p[0], p[1] - 1
            if direction == 2:
                np = p[0], p[1] + 1
            if direction == 3:
                np = p[0] - 1, p[1]
            if direction == 4:
                np = p[0] + 1, p[1]

            if np in seen:
                continue
            seen.add(np)

            npath = path + [direction]

            ncpu = cpu.copy()
            ncpu.input.append(direction)
            val = DISPLAY[ncpu.run_to_output()]
            grid.set(np, val)

            if val != "█":
                q.append((np, ncpu, npath))
    return (grid, fill_start)


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    code = process_intcode(input)
    grid, (_, answer) = get_map_with_oxygen(code)
    grid.print()
    print(answer)


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    code = process_intcode(input)
    grid, (start, _) = get_map_with_oxygen(code)

    seen = set()
    q = [(start, 0)]

    max_depth = 0

    while q:
        p, depth = q.pop(0)
        seen.add(p)

        if grid.get(p) == "█":
            continue

        grid.set(p, str(depth % 10))

        if depth > max_depth:
            click.clear()
            grid.print()
            time.sleep(0.05)

        max_depth = max(depth, max_depth)

        for direction in [1, 2, 3, 4]:
            if direction == 1:
                np = p[0], p[1] - 1
            if direction == 2:
                np = p[0], p[1] + 1
            if direction == 3:
                np = p[0] - 1, p[1]
            if direction == 4:
                np = p[0] + 1, p[1]

            if np in seen:
                continue

            q.append((np, depth + 1))

    grid.set(start, "~")
    print(max_depth)


if __name__ == "__main__":
    cli()
