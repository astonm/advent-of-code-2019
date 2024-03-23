from util import *


@click.group()
def cli():
    pass


def process_ingredient(i):
    p = i.split()
    return int(p[0]), p[1]


def process_line(line):
    ingredients, result = line.split(" => ")
    return (
        [process_ingredient(i) for i in ingredients.split(", ")],
        process_ingredient(result),
    )


@dataclass
class Node:
    name: str
    count: int
    children: Optional[list]


def get_ore(nodes, start, qty, leftover=None):
    if leftover is None:
        leftover = defaultdict(int)

    if start == "ORE":
        return qty
    node = nodes[start]

    premade = min(qty, leftover[start])
    qty -= premade
    leftover[start] -= premade
    if not qty:
        return 0

    runs = ceil(qty / node.count)

    s = 0
    for child in node.children:
        s += get_ore(nodes, child.name, runs * child.count, leftover)

    # print(f"Consume {s} ORE to produce {qty} {start} ({premade=})")

    excess = runs * node.count - qty
    leftover[start] += excess
    return s


def get_nodes(data):
    nodes = {}
    for inputs, output in data:
        node = Node(
            name=output[1],
            count=output[0],
            children=[Node(name=c[1], count=c[0], children=None) for c in inputs],
        )
        nodes[node.name] = node
    return nodes


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    nodes = get_nodes([process_line(l) for l in read_file(input)])
    pprint(get_ore(nodes, "FUEL", 1))


def binary_search(target, f, low, high):
    while low < high:
        mid = (low + high) // 2
        val = f(mid)
        if val == target:
            return mid
        elif val > target:
            high = mid - 1
        else:
            low = mid + 1

    return mid


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    nodes = get_nodes([process_line(l) for l in read_file(input)])

    get_ore_n = lambda n: get_ore(nodes, "FUEL", n)

    ore = 0
    rough_n = 1
    while ore < 1000000000000:
        rough_n *= 2
        ore = get_ore_n(rough_n)

    low, high = rough_n // 2, rough_n
    guess = binary_search(1000000000000, get_ore_n, rough_n // 2, rough_n)

    print(guess)


if __name__ == "__main__":
    cli()
