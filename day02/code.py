from util import *
from intcode import *


@click.group()
def cli():
    pass


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    data = process_intcode(input)
    data[1] = 12
    data[2] = 2

    cpu = Intcode(data)
    cpu.run()
    pprint(cpu.mem[0])


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    orig_data = process_intcode(input)

    for noun in range(100):
        for verb in range(100):
            data = orig_data[:]
            data[1] = noun
            data[2] = verb

            cpu = Intcode(data)
            cpu.run()

            if cpu.mem[0] == 19690720:
                print(f"{noun}{verb:02}")


if __name__ == "__main__":
    cli()
