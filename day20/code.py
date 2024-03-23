from util import *


@click.group()
def cli():
    pass


def process_line(line):
    return line


L = lambda l: l.isupper()  # label
D = "."

vd = [[L], [L], [D]]
vu = [[D], [L], [L]]
hr = [[L, L, D]]
hl = [[D, L, L]]


def match_shape(shape, grid):
    assert shape
    assert isinstance(shape, list)
    assert isinstance(shape[0], list)
    h = len(shape)
    w = len(shape[0])

    out = []

    for x, y in grid.walk_coords():
        matched = []
        for j, i in product(range(h), range(w)):
            pat = shape[j][i]
            try:
                val = grid.get(x + i, y + j)
                matches = pat(val) if callable(pat) else pat == val
                if matches:
                    matched.append((val, (x + i, y + j)))
                else:
                    break
            except ValueError:
                break
            if len(matched) == h * w:
                out.append(matched)
    return out


def get_portals(grid):
    start = None
    end = None
    portal_labels = defaultdict(list)
    for shape, dot_pos in [(hl, 0), (hr, 2), (vu, 0), (vd, 2)]:
        for match in match_shape(shape, grid):
            dot = match.pop(dot_pos)[1]
            label = "".join(m[0] for m in match)
            if label == "AA":
                start = dot
            elif label == "ZZ":
                end = dot
            else:
                portal_labels[label].append(dot)

    portals = {}
    for p1, p2 in portal_labels.values():
        portals[p1] = p2
        portals[p2] = p1

    return start, end, portals


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    data = [process_line(l) for l in read_file(input, strip=False)]
    grid = Grid(data)

    start, end, portals = get_portals(grid)

    seen = set()
    q = [(0, start)]
    while q:
        dist, curr = q.pop(0)
        if curr == end:
            print(dist)
            return

        if curr in seen:
            continue
        seen.add(curr)

        for p in grid.neighbors(*curr):
            if grid.get(*p) == ".":
                if p in portals:
                    q.append((dist + 2, portals[p]))
                else:
                    q.append((dist + 1, p))


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    data = [process_line(l) for l in read_file(input, strip=False)]
    grid = Grid(data)
    start, end, portals = get_portals(grid)

    min_x, min_y = float("inf"), float("inf")
    max_x, max_y = 0, 0
    for x, y in grid.walk_coords():
        if grid.get(x, y) == "#":
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)

    outer_x = (min_x, max_x)
    outer_y = (min_y, max_y)

    seen = set()
    q = [State(0, start, 0)]
    while q:
        dist, curr, level = q.pop(0)
        if curr == end and level == 0:
            print(dist)
            return

        if dist > 100_000 or level > 10_000:
            print("inf?")
            return

        if (curr, level) in seen:
            continue
        seen.add((curr, level))

        for p in grid.neighbors(*curr):
            val = grid.get(*p)
            is_portal = p in portals
            is_outer = is_portal and (p[0] in outer_x or p[1] in outer_y)
            is_exit = p in (start, end)

            is_wall = (
                (val != ".") or (level == 0 and is_outer) or (level > 0 and is_exit)
            )

            if is_wall:
                continue

            if not is_portal:
                q.append((dist + 1, p, level))
                continue

            if is_outer:
                q.append((dist + 2, portals[p], level - 1))
            else:
                q.append((dist + 2, portals[p], level + 1))


if __name__ == "__main__":
    cli()
