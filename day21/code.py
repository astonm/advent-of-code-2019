from util import *
from intcode import *


@click.group()
def cli():
    pass


def process_line(line):
    return line


"""
# NOT a
...@.............
#####.#..########


# (NOT a) OR (NOT c AND a AND b)
..@..............
#####...#########

# (NOT a) OR (NOT c AND a AND b AND d)
....@............
#####..#.########

# (NOT a) OR (NOT c AND a AND d)
<19355790>
"""

part1_commands = """
NOT A J
NOT C T
AND A T
AND D T
OR T J
WALK
""".lstrip()

part2_commands = """
OR A T
AND B  T
NOT T J
NOT C T
AND H T
OR T J
AND D J
RUN
""".lstrip()


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    data = process_intcode(input)
    cpu = Intcode(data)
    cpu.run_ascii(part1_commands)


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    data = process_intcode(input)
    cpu = Intcode(data)
    cpu.run_ascii(part2_commands)
    print(cpu.c)


if __name__ == "__main__":
    cli()
