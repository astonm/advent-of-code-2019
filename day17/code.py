from util import *
from intcode import *


@click.group()
def cli():
    pass


def process_line(line):
    return line


WALL_CHARS = "<^>v#"


def get_grid(cpu):
    lines = []
    line = []
    while True:
        try:
            c = chr(cpu.run_to_output())
            if c == "\n":
                if line:
                    lines.append(line)
                    line = []
            else:
                line.append(c)
        except Intcode.Halted:
            break

    return Grid(lines)


def get_intersections(grid):
    intersections = []
    for x, y in grid.walk_coords():
        if grid.get(x, y) in WALL_CHARS:
            if all(grid.get(i, j) in WALL_CHARS for (i, j) in grid.neighbors(x, y)):
                intersections.append((x, y))
    return intersections


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    cpu = Intcode(process_intcode(input))
    grid = get_grid(cpu)
    intersections = get_intersections(grid)

    grid.print()
    print(sum(a * b for (a, b) in intersections))


def sublist_indices(l, sl):
    # does not return overlapping indices...
    out = []
    ll = len(l)
    sll = len(sl)

    ind = 0
    while ind < ll:
        end = ind + sll
        if l[ind:end] == sl:
            out.append((ind, end))
            ind = end
        else:
            ind += 1

    return out


def split_list(l, sl):
    # there may be more than one way to split the list...
    out = []
    start = 0
    for end, next_start in sublist_indices(l, sl):
        out.append(l[start:end])
        start = next_start
    if len(l) >= start:
        out.append(l[start:])
    return out


def replace_list(l, sl, r):
    out = l[:]
    for start, end in reversed(sublist_indices(l, sl)):
        out[start:end] = [r]
    return out


def assign_routines(unassigned, to_label, assignments={}):
    if bool(unassigned) != bool(to_label):
        return None

    if not unassigned:
        return assignments

    label, next_to_label = to_label[0], to_label[1:]
    for length in count(1):
        guess = unassigned[0][:length]
        if len(guess) < length:
            if label == "A":
                print("DONE BECAUSE", guess, "SHORTER THAN", length)
            break

        next_assignments = assignments.copy()
        next_assignments[label] = guess

        next_unassigned = []
        for l in unassigned:
            next_unassigned.extend(x for x in split_list(l, guess) if x)

        res = assign_routines(next_unassigned, next_to_label, next_assignments)
        if res:
            return res

    return None


def count_runs(grid, start, dirs):
    out = []
    dx, dy = 0, -1
    x, y = start

    for direction in dirs:
        out.append(direction)
        if direction == "R":
            dx, dy = -dy, dx
        else:
            dx, dy = dy, -dx

        c = 0
        while grid.get(x + dx, y + dy, ".") == "#":
            x += dx
            y += dy
            c += 1
        assert c, out
        out.append(str(c))

    assert len(out) == 2 * len(dirs)
    return out


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    program = process_intcode(input)

    cpu = Intcode(program)
    grid = get_grid(cpu)
    intersections = set(get_intersections(grid))

    all_points = set()
    for x, y in grid.walk_coords():
        if grid.get(x, y) == "^":
            start = (x, y)
        if grid.get(x, y) in WALL_CHARS:
            all_points.add((x, y))

    path = count_runs(grid, start, "RLRRLRLLRLLLRLLRLLLRLLRRLRLLLRRLR")

    assignments = assign_routines([path], ["A", "B", "C"])
    for letter, val in assignments.items():
        path = replace_list(path, val, letter)

    print()
    print(path)
    print(assignments)

    input_data = [
        path,
        assignments["A"],
        assignments["B"],
        assignments["C"],
        ["n"],  # no feed
    ]
    input_str = "\n".join(",".join(x) for x in input_data) + "\n"

    print()
    print(input_str)

    program[0] = 2
    cpu = Intcode(program)
    cpu.input = [ord(c) for c in input_str]
    cpu.run()

    display, number = cpu.output[:-1], cpu.output[-1]
    print("".join(chr(x) for x in display))
    print(number)


if __name__ == "__main__":
    cli()
