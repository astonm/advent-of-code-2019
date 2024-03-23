from util import *
from intcode import *


@click.group()
def cli():
    pass


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    data = process_intcode(input)
    grid = Grid([list("." * 50) for _ in range(50)])

    for (x, y) in grid.walk_coords():
        cpu = Intcode(data, [x, y])
        grid.set(x, y, "#" if cpu.run_to_output() else ".")

    grid.print()
    print(len([x for x in grid.walk() if x == "#"]))


# def gen_points(pattern, start):
#     x, y = start
#     for dx in cycle(pattern):
#         yield x, y
#         x += dx
#         y += 1


@cli.command()
@click.argument("input_file", type=click.File())
def part2(input_file):
    is_example = "ex" in input_file.name
    start = (1, 1) if is_example else (5, 6)
    takes = (31, 21) if is_example else (10000, 10000)
    size = 10 if is_example else 100

    if is_example:
        grid = Grid([[0 if x == "." else 1 for x in l] for l in read_file(input_file)])
    else:
        data = process_intcode(input_file)
        grid = Grid([list("." * 500) for _ in range(500)])

    @lru_cache(maxsize=None)
    def get(x, y):
        if is_example:
            return grid.get(x, y)
        else:
            return Intcode(data, [x, y]).run_to_output()

    def follow_upper():
        x, y = start
        while True:
            yield x, y
            y += 1
            for dx in [-1, 0, 1, 2]:
                if get(x + dx, y) == 1 and get(x + dx + 1, y) == 0:
                    x += dx
                    break
            else:
                print("missed upper", x, y)
                return

    def follow_lower():
        x, y = start
        while True:
            yield x, y
            y += 1
            for dx in [0, 1]:
                if get(x + dx - 1, y) == 0 and get(x + dx, y) == 1:
                    x += dx
                    break
            else:
                print("missed lower")
                return

    lowers = follow_lower()
    uppers = follow_upper()

    def check_square(p1, p2):
        dx, dy = p2[0] - p1[0], p1[1] - p2[1]
        if dx >= size - 1 and dy >= size - 1:
            magic = p2[0] - size + 1, p1[1] - size + 1
            magic = p1[0], p2[1]
            print(dx, dy)
            print("magic", p1, p2, "=>", magic)
            print(magic[0] * 10000 + magic[1])
            return True

    for lower, upper in product(
        more_itertools.take(takes[0], lowers),
        more_itertools.take(takes[1], uppers),
    ):
        if check_square(lower, upper):
            return


if __name__ == "__main__":
    cli()
