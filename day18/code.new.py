from util import *
import string


@click.group()
def cli():
    pass


def process_line(line):
    return line


def find_keys(grid):
    loc = {}
    for x, y in grid.walk_coords():
        c = grid.get(x, y)
        if c in string.ascii_lowercase + "@":
            loc[c] = x, y
    return loc


def shortest_path(start, target, grid):
    seen = set()
    q = [(start, 0, [])]
    while q:
        p, dist, path = q.pop(0)
        val = grid.get(*p)

        if val in "#█":
            continue

        if p == target:
            return dist, path

        if p in seen:
            continue
        else:
            seen.add(p)

        for np in grid.neighbors(*p):
            q.append((np, dist + 1, path + [p]))


def shortest_path_to_all(start, grid):
    seen = set()
    q = [(start, 0, set())]
    out = {}
    while q:
        p, dist, doors = q.pop(0)
        val = grid.get(*p)

        if p in seen:
            continue
        seen.add(p)

        if val in "#█":
            continue

        if dist and val.islower() and val not in out:
            out[val] = (dist, doors)
            # continue  # stop once we hit a key?

        if val.isupper():
            doors.add(val.lower())

        for np in grid.neighbors(*p):
            q.append((np, dist + 1, doors.copy()))

    return out


def ftime(t):
    if t < 1:
        return f"{t:0.3f}s"

    t = int(t)
    m, s = divmod(t, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:d}h {m:d}m"
    if m:
        return f"{m:d}m {s:d}s"
    return f"{s:d}s"


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    data = [process_line(l) for l in read_file(input)]
    grid = Grid(data)
    loc = find_keys(grid)

    all_to_all = {}
    for key, p in loc.items():
        all_to_all[key] = sorted(
            shortest_path_to_all(p, grid).items(),
            key=lambda x: x[1][0],
        )
    pprint(all_to_all)

    q = PriorityQueue()
    q.put((0, "@"))
    min_dist = float("inf")
    max_dist = 0
    t0 = time.time()

    max_keys = 1

    pruner = {}
    bail_on_bigger = False
    try:
        while not q.empty():
            dist, so_far = q.get()
            curr = so_far[-1]

            if dist > min_dist:
                if bail_on_bigger:
                    return
                else:
                    continue

            if len(so_far) > max_keys:
                max_keys = len(so_far)
                print(max_keys - 1, so_far, dist)

            # if dist > max_dist:
            #     print(">", dist, so_far, ftime(time.time() - t0))
            #     max_dist = dist

            if len(so_far) == len(loc):
                # if dist < min_dist:
                min_dist = dist
                print(min_dist, so_far)
                # bail_on_bigger = True
                continue

            prune_key = (dist, curr)
            if prune_key in pruner and pruner[prune_key] > len(so_far):
                continue
            pruner[prune_key] = len(so_far)

            keys_in_hand = set(so_far)

            for other, (other_dist, keys_needed) in all_to_all[curr]:
                if other in so_far:
                    continue

                missing_keys = keys_needed - keys_in_hand
                if not missing_keys:
                    q.put((dist + other_dist, so_far + other))

        print(min_dist)
    except KeyboardInterrupt:
        out = [q.get()]
        while True:
            o = q.get()
            if o[0] != out[-1][0]:
                break
            out.append(o)
        print()
        print(len(out), out[:10])


@cli.command()
@click.argument("input", type=click.File())
@click.argument("path")
def check(input, path):
    data = [
        process_line(list(l.replace(".", " ").replace("#", "█")))
        for l in read_file(input)
    ]
    grid = Grid(data)
    loc = find_keys(grid)

    _, path = shortest_path(loc["@"], loc["w"], grid)
    for p in path:
        if grid.get(*p) in " .":
            grid.set(p[0], p[1], "*")
    grid.print()
    return

    all_to_all = {}
    for key, p in loc.items():
        all_to_all[key] = {c: x[0] for (c, x) in shortest_path_to_all(p, grid).items()}

    prev, path = path[0], path[1:]
    total = 0
    for c in path:
        total += all_to_all[prev][c]
        prev = c
    print(total, path)


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    data = [process_line(l) for l in read_file(input)]
    pprint(locals())


if __name__ == "__main__":
    # profile_it()
    cli()
