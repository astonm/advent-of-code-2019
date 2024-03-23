from util import *


@click.group()
def cli():
    pass


def process_line(line):
    return int(line)


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    data = [process_line(l) for l in read_file(input)]
    s = 0
    for d in data:
        s += d // 3 - 2
    pprint(s)


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    data = [process_line(l) for l in read_file(input)]
    s = 0
    for d in data:
        while True:
            d = d // 3 - 2
            if d <= 0:
                break
            s += d
    pprint(s)


if __name__ == "__main__":
    cli()
