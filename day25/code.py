from util import *
from intcode import *


@click.group()
def cli():
    pass


def process_line(line):
    return line


part1_commands = """
south
# take space law space brochure
south
# take mouse
south
take astrolabe
south
take mug
north
north
west
north
north
take wreath
south
south
east
north
west
take sand
west
# take monolith
west
west
""".lstrip()


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    data = process_intcode(input)
    cpu = Intcode(data)

    cpu.run_ascii(part1_commands)


if __name__ == "__main__":
    cli()
