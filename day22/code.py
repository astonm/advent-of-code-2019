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


def end_spot(start, size):
    # from code.wwrongidea.py
    return (9520 * start + 7216) % size


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    data = [process_line(l) for l in read_file(input)]

    if "ex" in input.name:
        end_pos = 4649
        size = 10007
        n = 1
    else:
        end_pos = 2020
        size = 119315717514047
        n = 101741582076661

    coeffs = (1, 0)
    for inst, *args in reversed(data):
        if inst == "reverse":
            coeffs = (-coeffs[0], -coeffs[1] - 1)
        elif inst == "rotate":
            coeffs = (coeffs[0], coeffs[1] + args[0])
        elif inst == "permute":
            mod_inv = pow(args[0], -1, size)
            coeffs = (mod_inv * coeffs[0], mod_inv * coeffs[1])
        coeffs = (coeffs[0] % size, coeffs[1] % size)

    """
    At this point, we have coefficients (a, b) that take a position and give the position it came from: p = a * p_0 + b (mod size)

    Hard part, applying that N times where N is large

    f1(x) = a * x + b
    f2(x) = a * (a * x + b) + b = a**2 * x + a * b + b
    f3(x) = a * (a**2 * x + a * b + b) + b = a**3 x + a**2 * b + a * b + b
    fn(x) = a**n * x + b * (1 + ... + a ** (n-1))

    The first part, a**n * x, is straightforward modular arithmetic.

    The second part is harder. But maybe there's magic?

    Assume there's an infinite sum X = a**0 + a**1 + a**2 + ...
    If so:
       1 + ... + a ** (n-1) = X - a**n * X

    Giving us

    fn(x) = a**n * x + b * (X - a**n * X)

    Only hard part remaining, what is X? Well

    X = 1 + a * X
    -1 = (a - 1) * X
    X = -1 * (a - 1) ** -1

    Can this work? Apparently it does!
    """

    a_to_the_n = pow(coeffs[0], n, size)
    inf_sum = -pow(coeffs[0] - 1, -1, size)
    pow_sum = inf_sum - a_to_the_n * inf_sum
    fnx = a_to_the_n * end_pos + coeffs[1] * pow_sum
    print(fnx % size)


if __name__ == "__main__":
    cli()
