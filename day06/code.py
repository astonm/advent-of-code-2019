from util import *


@click.group()
def cli():
    pass


def process_line(line):
    return line.split(")")


def sum_depths(tree, node, depth=0):
    if tree[node] is None:
        return depth
    return depth + sum(sum_depths(tree, n, depth + 1) for n in tree[node])


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    data = [process_line(l) for l in read_file(input)]

    tree = defaultdict(list)
    for parent, child in data:
        tree[parent].append(child)

    print(sum_depths(tree, "COM"))


def find_path(tree, node, target, so_far=[]):
    so_far = so_far + [node]
    if node == target:
        return so_far

    if tree[node] is None:
        return None

    for child in tree[node]:
        path = find_path(tree, child, target, so_far)
        if path:
            return path


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    data = [process_line(l) for l in read_file(input)]
    tree = defaultdict(list)
    for parent, child in data:
        tree[parent].append(child)

    start_path = find_path(tree, "COM", "YOU")
    dest_path = find_path(tree, "COM", "SAN")

    lca_ind = None
    for i, (x, y) in enumerate(zip(start_path, dest_path)):
        if x == y:
            lca_ind = i

    dist1 = len(start_path) - lca_ind - 2  # -1 for zero-indexing, -1 to skip YOU/SA
    dist2 = len(dest_path) - lca_ind - 2  # -1 for zero-indexing, -1 to skip YOU/SAN
    print(dist1 + dist2)


if __name__ == "__main__":
    cli()
