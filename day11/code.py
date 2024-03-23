from util import *
from intcode import *


@click.group()
def cli():
    pass


def process_line(line):
    return line


class Colors:
    Black = " "
    White = "█"


def run_painter(cpu, grid):
    seen = set()
    p = (0, 0)
    d = (0, -1)
    v = grid.get(p)

    running = True
    outputs = []
    while running:
        # pgrid = grid.copy()
        # pgrid.set(p, {(1, 0): ">", (0, 1): "v", (-1, 0): "<", (0, -1): "^"}[d])
        # pgrid.print()
        # print()

        try:
            cpu.run_to_exc()
        except Intcode.Halted:
            running = False
        except Intcode.WaitingForInput:
            cpu.input.append(0 if v == Colors.Black else 1)
        except Intcode.WroteOutput:
            outputs.append(cpu.output.pop())

            if len(outputs) == 2:
                color, turn = outputs
                outputs = []

                grid.set(p, Colors.White if color else Colors.Black)

                if turn == 0:
                    d = d[1], -d[0]
                else:
                    d = -d[1], d[0]

                p = (p[0] + d[0], p[1] + d[1])
                v = grid.get(p)
    return grid


def run_painter2(cpu, grid):
    seen = set()
    p = (0, 0)
    d = (0, -1)
    v = grid.get(p)

    while True:
        try:
            color, turn = cpu.run_to_output(2)
        except Intcode.Halted:
            break
        except Intcode.WaitingForInput:
            cpu.input.append(0 if v == Colors.Black else 1)
        else:
            grid.set(p, Colors.White if color else Colors.Black)

            if turn == 0:
                d = d[1], -d[0]
            else:
                d = -d[1], d[0]

            p = (p[0] + d[0], p[1] + d[1])
            v = grid.get(p)
    return grid


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    data = process_intcode(input)
    cpu = Intcode(data)
    grid = GridN(default=Colors.Black)

    grid = run_painter(cpu, grid)
    grid.print()
    print(len(grid))


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    data = process_intcode(input)
    cpu = Intcode(data)
    grid = GridN(default=Colors.Black)
    grid.set((0, 0), Colors.White)

    grid = run_painter2(cpu, grid)
    grid.print()
    print(len(grid))


if __name__ == "__main__":
    cli()
