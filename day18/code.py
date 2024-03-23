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
            if c in loc:
                if not isinstance(loc[c], list):
                    loc[c] = [loc[c]]
                loc[c].append((x, y))
            else:
                loc[c] = x, y
    return loc


path_cache = {}


def shortest_path(start, target, grid, avoid=""):
    cache_key = (start, target, avoid)
    if cache_key in path_cache:
        return path_cache[cache_key]

    seen = set()
    q = [(start, 0, tuple(), tuple())]
    while q:
        p, dist, doors, bonus = q.pop(0)
        val = grid.get(*p)

        if p in seen:
            continue
        seen.add(p)

        if p == target:
            path_cache[cache_key] = (dist, doors, bonus)
            return path_cache[cache_key]

        if val in "#█" + avoid:
            continue

        if val.isupper():
            doors += (val.lower(),)

        if val.islower() and p != start:
            bonus += (val,)

        for np in grid.neighbors(*p):
            q.append((np, dist + 1, doors, bonus))

    path_cache[cache_key] = None
    return None


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
def part1_finally_working(input):
    data = [process_line(l) for l in read_file(input)]
    grid = Grid(data)
    loc = find_keys(grid)

    t0 = time.time()
    all_to_all = {}
    for a in loc:
        all_to_all[a] = {}
        for b in loc:
            if a != b:
                ways = set()
                shortest = shortest_path(loc[a], loc[b], grid)
                ways.add(shortest)

                # code for more rare cases where you don't use the shortest path between two points because of doors
                # doors = shortest[1]
                # for n in range(1, len(doors)):
                #     for combo in combinations(doors, n):
                #         avoid = "".join(combo).upper()
                #         res = shortest_path(loc[a], loc[b], grid, avoid=avoid)
                #         if res:
                #             ways.add(res)
                # if len(ways) > 1 and a < b:
                #     print(a, b, ways)
                all_to_all[a][b] = sorted(ways)

    print("all_to_all", ftime(time.time() - t0))
    t0 = time.time()

    q = PriorityQueue()
    q.put((0, "@"))
    min_dist = float("inf")
    max_dist = 0

    max_keys = 1

    pruner = {}
    bail_on_bigger = False
    try:
        while not q.empty():
            dist, so_far = q.get()
            curr = so_far[-1]

            if len(so_far) > max_keys:
                max_keys = len(so_far)
                print(max_keys - 1, so_far, dist, ftime(time.time() - t0))

            if len(so_far) == len(loc):
                min_dist = dist
                print(min_dist, so_far)
                return

            prune_key = (dist, curr)
            if prune_key in pruner and pruner[prune_key] > len(so_far):
                continue
            pruner[prune_key] = len(so_far)

            keys_in_hand = set(so_far)
            for other, ways in all_to_all[curr].items():
                for (other_dist, keys_needed, bonus_keys) in ways:
                    if other in so_far:
                        continue

                    missing_keys = set(keys_needed) - keys_in_hand
                    if not missing_keys:
                        new_keys = set(bonus_keys) - keys_in_hand
                        next_so_far = so_far + "".join(new_keys) + other
                        q.put((dist + other_dist, next_so_far))

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
def part1(input):
    data = [process_line(l) for l in read_file(input)]
    grid = Grid(data)
    loc = find_keys(grid)
    t0 = time.time()

    q = PriorityQueue()
    q.put((0, "@"))
    min_dist = float("inf")

    max_keys = 1

    pruner = {}
    while not q.empty():
        dist, so_far = q.get()
        curr = so_far[-1]

        if len(so_far) > max_keys:
            max_keys = len(so_far)
            print(max_keys - 1, so_far, dist, ftime(time.time() - t0))

        if len(so_far) == len(loc):
            min_dist = dist
            print(min_dist, so_far)
            return

        prune_key = (dist, curr)
        if prune_key in pruner and pruner[prune_key] > len(so_far):
            continue
        pruner[prune_key] = len(so_far)

        keys_in_hand = set(so_far)
        for other in loc:
            if other == curr or other in so_far:
                continue

            shortest = shortest_path(loc[curr], loc[other], grid)
            if not shortest:
                continue

            other_dist, keys_needed, bonus_keys = shortest
            missing_keys = set(keys_needed) - keys_in_hand

            if not missing_keys:
                new_keys = set(bonus_keys) - keys_in_hand
                next_so_far = so_far + "".join(new_keys) + other
                q.put((dist + other_dist, next_so_far))


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    data = [process_line(l) for l in read_file(input)]
    grid = Grid(data)
    loc = find_keys(grid)

    all_keys = set(loc)
    robots = loc.pop("@")

    reachable = defaultdict(set)
    for other in loc:
        for ri, robot in enumerate(robots):
            if shortest_path(robot, loc[other], grid):
                reachable[ri].add(other)

    q = PriorityQueue()
    q.put((0, tuple((r, "@") for r in robots)))

    max_keys = 0

    t0 = time.time()

    seen = set()
    while not q.empty():
        got = q.get()
        if got in seen:
            continue
        seen.add(got)

        dist, robots = got
        keys_in_hand = set("".join(r[1] for r in robots))

        if len(keys_in_hand) > max_keys:
            print(len(keys_in_hand), got, ftime(time.time() - t0))
            max_keys = len(keys_in_hand)

        if not all_keys - keys_in_hand:
            print(dist)
            return

        for ri, (p, so_far) in enumerate(robots):
            curr = so_far[-1]

            for other in reachable[ri]:
                if other == curr or other in so_far:
                    continue

                shortest = shortest_path(p, loc[other], grid)
                if not shortest:
                    continue

                other_dist, keys_needed, bonus_keys = shortest
                missing_keys = set(keys_needed) - keys_in_hand

                if not missing_keys:
                    new_keys = set(bonus_keys) - keys_in_hand
                    next_so_far = so_far + "".join(new_keys) + other
                    next_robots = (
                        robots[:ri] + ((loc[other], next_so_far),) + robots[ri + 1 :]
                    )

                    q.put((dist + other_dist, next_robots))

    print("inf")


if __name__ == "__main__":
    # profile_it()
    cli()
