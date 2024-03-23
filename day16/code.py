from util import *


@click.group()
def cli():
    pass


def process_line(line):
    return Vector(int(d) for d in line)


def get_pattern(step):
    base = [0, 1, 0, -1]
    repeated = chain(*[repeat(x, step) for x in base])
    return cycle(repeated)


def calc_digit(data, step):
    pattern = get_pattern(step)
    next(pattern)  # skip the first pattern value
    pattern = Vector(more_itertools.take(len(data), pattern))

    digit = abs(sum(pattern * data)) % 10
    return digit


def get_slices(mx, n):
    i = -1
    while i + n < mx:
        yield slice(i + n, min(mx, i + 2 * n)), slice(
            min(mx, i + 3 * n), min(mx, i + 4 * n)
        )
        i += n * 4


def calc_digit_faster(data, step):
    s = 0
    for adds, subtracts in get_slices(len(data), step):
        s += sum(data[adds]) - sum(data[subtracts])
    return abs(s) % 10


def calc_digit_repeated_simple(data, repeats, step):
    l = len(data) * repeats
    data = more_itertools.ncycles(data, repeats)
    pattern = get_pattern(step)
    next(pattern)  # skip the first pattern value
    pattern = Vector(more_itertools.take(l, pattern))

    digit = abs(sum(pattern * data)) % 10
    return digit


def calc_digit_repeated(data, repeats, step):
    l = len(data)
    pattern_len = 4 * step
    cycle_len = lcm(l, pattern_len)
    total_len = l * repeats

    if total_len < cycle_len:
        return calc_digit_repeated_simple(data, repeats, step)

    data = cycle(data)
    pattern = get_pattern(step)
    next(pattern)  # skip the first pattern value

    # cycle chunk
    cycle_pattern = Vector(more_itertools.take(cycle_len, pattern))
    cycle_data = Vector(more_itertools.take(cycle_len, data))
    cycle_sum = sum(cycle_pattern * cycle_data)

    # last chunk
    num_cycles = total_len // cycle_len
    last_len = total_len - num_cycles * cycle_len
    last_pattern = Vector(more_itertools.take(last_len, pattern))
    last_data = Vector(more_itertools.take(last_len, data))
    last_sum = sum(last_pattern * last_data)

    total = last_sum + num_cycles * cycle_sum
    return abs(total) % 10


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    data = [process_line(l) for l in read_file(input)][0]
    max_steps = 4 if "ex.txt" in input.name else 100

    max_steps = 1000
    for step in range(max_steps):
        next_data = []
        for i in range(len(data)):
            next_data.append(calc_digit(data, i + 1))
        data = Vector(next_data)

    print("".join(str(s) for s in data[:8]))


@cli.command()
@click.argument("input", type=click.File())
def part2_broken(input):
    data = list([process_line(l) for l in read_file(input)][0])
    max_steps = 100
    repeats = 10000  # 10_000

    for i in tqdm(range(len(data) * repeats)):
        digit = calc_digit_repeated(data, repeats, i + 1)
        # print(digit)
    return

    data = data * repeats

    for step in range(max_steps):
        next_data = []
        for i in range(len(data)):
            digit = calc_digit_faster(data, i + 1)
            next_data.append(digit)
        data = next_data

    offset = int("".join(str(s) for s in data[:7]))
    print(offset, len(data))
    print("".join(str(s) for s in data[offset : offset + 8]))


def wrap_sum(o_start, o_end, data):
    if o_start >= o_end:
        return 0
    start = o_start % len(data)
    end = o_end % len(data)
    s = 0
    p = start
    while p != end:
        s += data[p]
        p = (p + 1) % len(data)

    n_full = (o_end - o_start) // len(data)
    s += sum(data) * n_full
    return s


@cli.command()
@click.argument("input", type=click.File())
def benchmark(input):
    input = "03036732577212944063491565474664"
    data = list(process_line(input))
    offset = int(input[:7])
    repeat = 10000
    long_data = data * repeat

    t0 = time.time()
    d0 = calc_digit(long_data, offset)
    print(d0)
    print(time.time() - t0)

    t0 = time.time()
    d1 = calc_digit_repeated(data, repeat, offset)
    print(d1)
    print(time.time() - t0)

    t0 = time.time()
    d2 = calc_digit_repeated(long_data, 1, offset)
    print(d2)
    print(time.time() - t0)

    t0 = time.time()
    s = 0
    for adds, subs in get_slices(len(long_data), offset):
        s += sum(long_data[adds]) - sum(long_data[subs])
    d3 = abs(s) % 10
    print(d3)
    print(time.time() - t0)

    t0 = time.time()
    s = 0
    for adds, subs in get_slices(len(data) * repeat, offset):
        plus = wrap_sum(adds.start, adds.stop, data)
        minus = wrap_sum(subs.start, subs.stop, data)
        s += plus - minus
    d4 = abs(s) % 10
    print(d4)
    print(time.time() - t0)


@lru_cache()
def digit(data, repeat, offset, step):
    if step == 0:
        return data[offset]

    s = 0
    for adds, subs in get_slices(len(data) * repeat, offset + 1):
        plus = wrap_sum_recursive(adds.start, adds.stop, data, repeat, step)
        minus = wrap_sum_recursive(subs.start, subs.stop, data, repeat, step)
        s += plus - minus
    return abs(s) % 10


def wrap_sum_recursive(o_start, o_end, data, repeat, step):
    if o_start >= o_end:
        return 0
    start = o_start % len(data)
    end = o_end % len(data)
    s = 0
    p = start
    while p != end:
        s += digit(data, repeat, p, step - 1)
        p = (p + 1) % len(data)

    n_full = (o_end - o_start) // len(data)
    s += sum(data) * n_full
    return s


@cli.command()
@click.argument("input", type=click.File())
def part2_meh(input):
    input = "03036732577212944063491565474664"
    data = tuple(process_line(input))
    offset = int(input[:7])
    repeat = 10000

    print(digit(data, repeat, offset, step=5))


class RangeSummer:
    def __init__(self, data):
        self.data = data
        self.prev = None

    def __call__(self, s):
        if not self.prev:
            val = sum(self.data[s])
            self.prev = (s, val)
            return val

        ps, val = self.prev
        if s == ps:
            return val

        if s.start < ps.start:
            val += sum(self.data[s.start : ps.start])
        else:
            val -= sum(self.data[ps.start : s.start])

        if s.stop < ps.stop:
            val -= sum(self.data[s.stop : ps.stop])
        else:
            val += sum(self.data[ps.stop : s.stop])

        self.prev = (s, val)
        return val


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    input = input.read().strip()
    data = [int(x) for x in input * 10000]
    lendata = len(data)
    offset = int(input[:7])

    for _ in tqdm(range(100)):
        sum_add = RangeSummer(data)
        sum_sub = RangeSummer(data)
        after = [None] * lendata
        for i in range(offset, lendata):
            for adds, subs in get_slices(lendata, i + 1):
                after[i] = (sum_add(adds) - sum_sub(subs)) % 10
        data = after
    print("".join(str(x) for x in data[offset : offset + 8]))


if __name__ == "__main__":
    cli()
