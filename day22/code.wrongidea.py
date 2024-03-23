from util import *


@click.group()
def cli():
    pass


"""
deal into new stack -> reverse (or, flip sign of any steps taken)
cut +n -> rotate left n (or, move head forward n)
cut -n -> rotate right n (or, move head back n)
deal with increment 7 -> the fancy reindex that is the hardest part of this problem


for part 1, can actually implement these and using a circular, doubly linked list will make all but the last one pretty fast

ideally, nothing would move ever
probably easiest to only move things when given a deal with increment instruction

finding 2019 will require a scan, although holding a pointer might shorten things (still linear)
----

part 2:
given we only care to track a single card, probably optimal to figure out where it will land instead of building a whole deck

cut n -> reindex via offset. card @ deck[p] -> deck[p - n]
deal into new stack -> flip ends. card @ deck[p] -> deck[len(deck) - 1 - p]
deal with increment n -> find new spot with mod. card @ deck[p] -> deck[p * n % len(deck)]
"""


def process_line(line):
    m = parse("deal with increment {:d}", line)
    if m:
        return ["permute", m[0]]

    if "deal into new stack" == line:
        return ["reverse"]

    m = parse("cut {:d}", line)
    if m:
        return ["rotate", m[0]]
    return line


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    data = [process_line(l) for l in read_file(input)]
    size = 10 if "ex" in input.name else 10007

    deck = list(range(size))
    for inst, *args in data:
        if inst == "reverse":
            deck = deck[::-1]
        elif inst == "rotate":
            n = args[0]
            deck = deck[n:] + deck[:n]
        elif inst == "permute":
            next_deck = [None] * size
            for v, m in zip(deck, range(size)):
                i = m * args[0]
                next_deck[i % len(deck)] = v
            deck = next_deck
        if "ex" not in input.name:
            print(inst, args, deck.index(2019))

    print(deck)
    try:
        print(deck.index(2019))
    except:
        print("2019 not found")


@cli.command()
@click.argument("input", type=click.File())
def part2_reduced(input):
    data = [process_line(l) for l in read_file(input)]
    start = 8 if "ex" in input.name else 2020
    size = 10 if "ex" in input.name else 119315717514047
    p = start
    for c in range(101741582076661):
        for inst, *args in data:
            if inst == "reverse":
                p = size - 1 - p
            elif inst == "rotate":
                p = (p - args[0]) % size
            elif inst == "permute":
                p = (p * args[0]) % size

        if c > 1000000:
            return
    print(p)


@cli.command()
@click.argument("input", type=click.File())
def part2a(input):
    data = [process_line(l) for l in read_file(input)]
    start = 8 if "ex" in input.name else 2019  # 2020
    size = 10 if "ex" in input.name else 10007  # 119315717514047
    p = start
    for c in range(1):
        for inst, *args in data:
            if inst == "reverse":
                p *= -1
                p -= 1
            elif inst == "rotate":
                p -= args[0]
            elif inst == "permute":
                p *= args[0]
        p %= size
    print(p)


@cli.command()
@click.argument("input", type=click.File())
def part2a_symbolic(input):
    data = [process_line(l) for l in read_file(input)]
    start = 8 if "ex" in input.name else 2020
    size = 10 if "ex" in input.name else 119315717514047
    p = "start"
    for c in [1]:
        for inst, *args in data[:10]:  # XXX doesn't need to be 10
            if inst == "reverse":
                p = f"(-1 - {p})"
            elif inst == "rotate":
                p = f"({p} - {args[0]})"
            elif inst == "permute":
                p = f"({p} * {args[0]})"
    print(p)


@cli.command()
@click.argument("input", type=click.File())
def part2a_coeffs(input):
    data = [process_line(l) for l in read_file(input)]
    start = 8 if "ex" in input.name else 2019
    size = 10 if "ex" in input.name else 10007
    coeffs = [1, 0]  # 1*start + 0
    for c in [1]:
        for inst, *args in data:
            if inst == "reverse":
                coeffs = [-coeffs[0], -coeffs[1] - 1]
            elif inst == "rotate":
                coeffs[1] -= args[0]
            elif inst == "permute":
                coeffs = [coeffs[0] * args[0], coeffs[1] * args[0]]
    print(f"({coeffs[0]}*start + {coeffs[1]}) % size")
    print((coeffs[0] * start + coeffs[1]) % size)
    print()

    coeffs = [x % size for x in coeffs]
    print(f"({coeffs[0]}*start + {coeffs[1]}) % size")
    print((coeffs[0] * start + coeffs[1]) % size)

    """
    final symbolic output:
    (9520*start + 7216) % size

    first nesting:
    (9520*((9520*start + 7216)) + 7216) = 9520**2 * start + 9520*7216 + 7216

    second nesting:
    9520**3 * start + 9520**2*7216 + 9520*7216 + 7216

    third nesting:
    9520**4 * start + 9520**3*7216 + 9520**2*7216 + 9520*7216 + 7216

    =>
    9250**n * start + 7216 * (9520**(n-1) + 9520**(n-2) + ... +  9520**1 + 1)
    """


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    start = 2020
    size = 119315717514047
    n = 101741582076661

    coeffs = (9520, 7216)
    curr = coeffs
    seen = set()
    for c in tqdm(range(n)):
        curr = (coeffs[0] * curr[0] % size, (coeffs[0] * curr[1] + coeffs[1]) % size)
        if curr in seen:
            print("repeat", curr, "@", c)
            return
        seen.add(curr)


if __name__ == "__main__":
    cli()
