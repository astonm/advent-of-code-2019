from util import *


@click.group()
def cli():
    pass


def process_line(line):
    return list(line)


def generate_grids_part1(grid):
    while True:
        yield grid
        next_grid = grid.copy()
        for x, y in grid.walk_coords():
            if grid.get(x, y) == "#":
                neighbors = [grid.get(nx, ny) for (nx, ny) in grid.neighbors(x, y)]
                if neighbors.count("#") != 1:
                    next_grid.set(x, y, ".")
            if grid.get(x, y) == ".":
                neighbors = [grid.get(nx, ny) for (nx, ny) in grid.neighbors(x, y)]
                if neighbors.count("#") in (1, 2):
                    next_grid.set(x, y, "#")
        grid = next_grid


def inf_neighbors(p):
    dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # URDL
    for dir in dirs:
        np = p[0] + dir[0], p[1] + dir[1], p[2]

        # outers
        if np[0] < 0:
            yield (1, 2, p[2] - 1)
        elif np[0] > 4:
            yield (3, 2, p[2] - 1)
        elif np[1] < 0:
            yield (2, 1, p[2] - 1)
        elif np[1] > 4:
            yield (2, 3, p[2] - 1)

        # inners
        elif np[:2] == (2, 2):
            if p[:2] == (2, 1):
                yield from [(x, 0, p[2] + 1) for x in range(5)]
            elif p[:2] == (3, 2):
                yield from [(4, y, p[2] + 1) for y in range(5)]
            elif p[:2] == (2, 3):
                yield from [(x, 4, p[2] + 1) for x in range(5)]
            elif p[:2] == (1, 2):
                yield from [(0, y, p[2] + 1) for y in range(5)]
            else:
                assert 0
        else:
            yield np


def generate_grids_part2(grid):
    while True:
        yield grid
        next_grid = grid.copy()
        for p, val in grid.walk_all(pad=1):
            if p[:2] == (2, 2):
                continue

            if any(x < 0 or x > 4 for x in p[:2]):
                continue

            if val == "#":
                neighbors = [grid.get(np) for np in inf_neighbors(p)]
                if neighbors.count("#") != 1:
                    next_grid.set(p, ".")
            if val == ".":
                neighbors = [grid.get(np) for np in inf_neighbors(p)]
                if neighbors.count("#") in (1, 2):
                    next_grid.set(p, "#")
        grid = next_grid


def biodiversity_rating(grid):
    s = 0
    for i, val in enumerate(grid.walk()):
        if val == "#":
            s += 2 ** i
    return s


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    grid = Grid([process_line(l) for l in read_file(input)])
    seen = set()

    for step, grid in enumerate(generate_grids_part1(grid)):
        print("step", step)
        grid.print()

        if grid in seen:
            return print(biodiversity_rating(grid))
        seen.add(grid)


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    grid = GridN(default=".")
    input_grid = Grid([process_line(l) for l in read_file(input)])
    cutoff = 10 if "ex" in input.name else 200

    # test_inf_neighbors(); return

    for x, y in input_grid.walk_coords():
        grid.set((x, y, 0), input_grid.get(x, y))

    for step, grid in enumerate(generate_grids_part2(grid)):
        print("step", step)
        grid.print()

        if step == cutoff:
            return print(sum(1 if v == "#" else 0 for _, v in grid.walk_all()))


def test_inf_neighbors():

    answer_key = {
        (0, 0, 0): "1",
        (1, 0, 0): "2",
        (2, 0, 0): "3",
        (3, 0, 0): "4",
        (4, 0, 0): "5",
        (0, 1, 0): "6",
        (1, 1, 0): "7",
        (2, 1, 0): "8",
        (3, 1, 0): "9",
        (4, 1, 0): "10",
        (0, 2, 0): "11",
        (1, 2, 0): "12",
        (2, 2, 0): "??",
        (3, 2, 0): "14",
        (4, 2, 0): "15",
        (0, 3, 0): "16",
        (1, 3, 0): "17",
        (2, 3, 0): "18",
        (3, 3, 0): "19",
        (4, 3, 0): "20",
        (0, 4, 0): "21",
        (1, 4, 0): "22",
        (2, 4, 0): "23",
        (3, 4, 0): "24",
        (4, 4, 0): "25",
        (0, 0, 1): "A",
        (1, 0, 1): "B",
        (2, 0, 1): "C",
        (3, 0, 1): "D",
        (4, 0, 1): "E",
        (0, 1, 1): "F",
        (1, 1, 1): "G",
        (2, 1, 1): "H",
        (3, 1, 1): "I",
        (4, 1, 1): "J",
        (0, 2, 1): "K",
        (1, 2, 1): "L",
        (2, 2, 1): "?",
        (3, 2, 1): "N",
        (4, 2, 1): "O",
        (0, 3, 1): "P",
        (1, 3, 1): "Q",
        (2, 3, 1): "R",
        (3, 3, 1): "S",
        (4, 3, 1): "T",
        (0, 4, 1): "U",
        (1, 4, 1): "V",
        (2, 4, 1): "W",
        (3, 4, 1): "X",
        (4, 4, 1): "Y",
    }
    lookup = {v: k for k, v in answer_key.items()}

    for test in ["19", "G", "D", "E", "14", "N"]:
        print(f"{test} neighbors:")
        print("---")
        for n in inf_neighbors(lookup[test]):
            print(answer_key.get(n, n))
        print()


if __name__ == "__main__":
    cli()
