from util import *


@click.group()
def cli():
    pass


def process_line(line):
    return [(v[0], int(v[1:])) for v in line.split(",")]


def path_points(path):
    x, y = 0, 0
    for step in path:
        d, dist = step
        for _ in range(dist):
            if d == "U":
                y -= 1
            if d == "D":
                y += 1
            if d == "L":
                x -= 1
            if d == "R":
                x += 1
            yield x, y


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    path1, path2 = [process_line(l) for l in read_file(input)]
    grid = GridN(default=None)

    for x, y in path_points(path1):
        grid.set((x, y), "X")

    closest = float("inf")
    for x, y in path_points(path2):
        if grid.get((x, y)) == "X":
            closest = min(closest, abs(x) + abs(y))

    pprint(closest)


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    path1, path2 = [process_line(l) for l in read_file(input)]
    grid = GridN(default=None)

    for i, (x, y) in enumerate(path_points(path1)):
        grid.set((x, y), i)

    closest = float("inf")
    for j, (x, y) in enumerate(path_points(path2)):
        i = grid.get((x, y))
        if i is not None:
            closest = min(closest, i + j + 2)

    pprint(closest)


if __name__ == "__main__":
    cli()
