from util import *


@click.group()
def cli():
    pass


def process_line(line):
    return [int(x) for x in line.split("-")]


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    start, end = [process_line(l) for l in read_file(input)][0]
    c = 0
    for num in range(start, end + 1):
        num = str(num)
        increasing = all(prev <= next for prev, next in zip(num, num[1:]))
        has_double = any(prev == next for prev, next in zip(num, num[1:]))
        if increasing and has_double:
            c += 1
    print(c)


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    start, end = [process_line(l) for l in read_file(input)][0]
    c = 0
    for num in range(start, end + 1):
        num = str(num)
        increasing = all(prev <= next for prev, next in zip(num, num[1:]))
        has_double = any(len(list(g)) == 2 for _, g in groupby(num))
        if increasing and has_double:
            c += 1
    print(c)


if __name__ == "__main__":
    cli()
