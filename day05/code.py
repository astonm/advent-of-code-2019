from util import *
from intcode import *


@click.group()
def cli():
    pass


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    data = process_intcode(input)

    cpu = Intcode(data)
    cpu.input = [1]
    cpu.run()
    pprint(cpu.output)


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    data = process_intcode(input)

    cpu = Intcode(data)
    cpu.input = [5]
    cpu.run()
    pprint(cpu.output)


if __name__ == "__main__":
    cli()
