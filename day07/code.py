from util import *
from intcode import *


@click.group()
def cli():
    pass


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    program = process_intcode(input)

    max_value = 0
    for phase_settings in permutations(range(5)):
        value = 0
        cpus = [Intcode(program) for _ in range(5)]
        for i, phase_setting in enumerate(phase_settings):
            cpus[i].input = [phase_setting, value]
            cpus[i].run()
            value = cpus[i].output[0]

        max_value = max(value, max_value)

    print(max_value)


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    program = process_intcode(input)

    max_value = 0
    for phase_settings in permutations([5, 6, 7, 8, 9]):
        cpus = [Intcode(program) for _ in range(5)]
        for i in range(5):
            cpus[i].input = cpus[i - 1].output
            cpus[i].input.append(phase_settings[i])

        i = 0
        cpus[0].input.append(0)
        while True:
            try:
                cpus[i].run_to_exc()
            except Intcode.WroteOutput:
                pass
            except Intcode.Halted:
                break

            i = (i + 1) % 5

        max_value = max(max_value, cpus[-1].output[-1])

    print(max_value)


if __name__ == "__main__":
    cli()
