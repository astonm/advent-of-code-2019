from util import *


@click.group()
def cli():
    pass


def process_line(line):
    return list(line)


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    width, height = (3, 2) if "ex" in input.name else (25, 6)
    data = [process_line(l) for l in read_file(input)][0]

    layers = list(more_itertools.grouper(data, width * height))
    grids = [Grid(list(more_itertools.grouper(layer, width))) for layer in layers]

    by_zeros = {}
    for grid in grids:
        c = Counter(grid.walk())
        by_zeros[c["0"]] = c

    smallest = by_zeros[min(by_zeros.keys())]
    print(smallest["1"] * smallest["2"])


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    width, height = (3, 2) if "ex" in input.name else (25, 6)
    data = [process_line(l) for l in read_file(input)][0]

    layers = list(more_itertools.grouper(data, width * height))
    grids = [
        Grid([list(l) for l in more_itertools.grouper(layer, width)])
        for layer in layers
    ]

    out = grids[0].copy()

    for x, y in out.walk_coords():
        for grid in grids[::-1]:
            if grid.get(x, y) != "2":
                out.set(x, y, {"0": " ", "1": "█"}[grid.get(x, y)])
    out.print()


if __name__ == "__main__":
    cli()
