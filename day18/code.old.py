from util import *
import string


@click.group()
def cli():
    pass


def process_line(line):
    return line


path_cache = {}


def shortest_path(start, target, grid, walkables):
    cache_key = (start, target, walkables)
    if cache_key in path_cache:
        return path_cache[cache_key]

    seen = set()
    q = [(start, 0)]
    while q:
        p, dist = q.pop(0)
        val = grid.get(*p)

        if val == target:
            path_cache[cache_key] = p, dist
            return p, dist

        if val not in walkables:
            continue

        if p in seen:
            continue
        else:
            seen.add(p)

        for np in grid.neighbors(*p):
            q.append((np, dist + 1))


def prefix_match(seq, prefix):
    return prefix == seq[: len(prefix)]


def manhattan(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def gen_key_orders(loc, grid):
    closest_keys = {}
    for k in loc:
        other_keys = [o for o in loc if o != k]
        # shuffle(other_keys)
        other_keys.sort(key=lambda o: manhattan(loc[o], loc[k]))
        closest_keys[k] = other_keys

    def gen_permutations(k, used):
        # skips the starting key
        used = used.copy()
        used.add(k)

        if all(key in used for key in closest_keys[k]):
            yield tuple()

        for other in closest_keys[k]:
            if other not in used:
                for perm in gen_permutations(other, used):
                    yield (other,) + perm

    return gen_permutations("@", set())


@cli.command()
@click.argument("input", type=click.File())
def part1_permutations(input):
    data = [process_line(l) for l in read_file(input)]
    grid = Grid(data)

    loc = {}
    for x, y in grid.walk_coords():
        c = grid.get(x, y)
        if c in string.ascii_lowercase + "@":
            loc[c] = x, y

    origin = loc["@"]
    min_dist = float("inf")
    min_key_order = None
    bad_prefixes = []

    top_key = None
    c = 0
    for key_order in gen_key_orders(loc, grid):
        start = origin
        walkables = "@."
        dist = 0

        if top_key != key_order[0]:
            top_key = key_order[0]
            print("NEW START", top_key)

        # if any(prefix_match(key_order, b) for b in bad_prefixes):
        # continue

        for i, target_key in enumerate(key_order):
            # c += 1
            # if c % 1000 == 0:
            #     s = time.time()
            res = shortest_path(start, target_key, grid, walkables)
            # if c % 1000 == 0:
            #     print(time.time() - s)
            if res is None:
                # bad_prefix = key_order[: i + 1]
                # bad_prefixes.append(bad_prefix)
                # bad_prefixes.sort(key=lambda x: len(x))
                break
            else:
                target_location, target_dist = res
                start = target_location
                dist += target_dist
                walkables += target_key + target_key.upper()

                if i + 1 < len(key_order):
                    h = manhattan(target_location, loc[key_order[i + 1]])
                else:
                    h = 0

                if dist + h > min_dist:
                    # bad_prefix = key_order[: i + 1]
                    # bad_prefixes.append(bad_prefix)
                    # bad_prefixes.sort(key=lambda x: len(x))
                    break
                # else:
                # if dist > 0.95 * min_dist:
                #     print(dist)
        else:
            if dist < min_dist:
                min_dist = dist
                min_key_order = key_order
                print(dist, key_order)
    print(">", min_dist)


@cli.command()
@click.argument("input", type=click.File())
def part1_hold(input):
    data = [process_line(l) for l in read_file(input)]
    grid = Grid(data)

    loc = {}
    for x, y in grid.walk_coords():
        c = grid.get(x, y)
        if c in string.ascii_lowercase + "@":
            loc[c] = x, y
    all_keys = loc.keys()

    origin = loc["@"]
    min_dist = 0  # float("inf")
    min_key_order = None

    q = [(origin, 0, ".@")]
    seen = defaultdict(set)  # loc => set of walkables
    while q:
        p, dist, walkables = q.pop(0)

        val = grid.get(*p)
        if val in all_keys and val not in walkables:
            walkables += val + val.upper()

        if val not in walkables:
            continue

        if walkables in seen[p]:
            continue
        seen[p].add(walkables)

        if len(walkables) == len(all_keys) * 2:
            print(dist)
            return

        # if dist > min_dist and walkables.startswith(".@aAfFbBjJgG"):
        #     print(dist, len(walkables), walkables)
        #     min_dist = dist
        for np in grid.neighbors(*p):
            q.append((np, dist + 1, walkables))


@cli.command()
@click.argument("input", type=click.File())
def part1_meh(input):
    data = [process_line(l) for l in read_file(input)]
    grid = Grid(data)

    loc = {}
    for x, y in grid.walk_coords():
        c = grid.get(x, y)
        if c in string.ascii_lowercase + "@":
            loc[c] = x, y
    all_keys = set(loc.keys())

    origin = loc["@"]
    min_dist = 0  # float("inf")
    min_key_order = None

    seen = {}
    q = [(origin, 0, set(".@"))]
    c = 0
    while q:
        c += 1
        p, dist, walkables = q.pop(0)

        if p not in seen:
            seen[p] = walkables
        else:
            # keep a list instead of a union?
            next_walkables = seen[p] | walkables
            if next_walkables == seen[p]:
                continue
            seen[p] = next_walkables.copy()

        val = grid.get(*p)
        if val in all_keys:
            walkables.add(val)
            walkables.add(val.upper())

        if val not in walkables:
            continue

        if not all_keys - walkables:
            print(dist)
            return

        for np in grid.neighbors(*p):
            q.append((np, dist + 1, walkables.copy()))


def shortest_path_to_all_unseen(start, grid, walkables):
    seen = set()
    q = [(start, 0)]
    out = []
    while q:
        p, dist = q.pop(0)
        val = grid.get(*p)

        if val.islower() and val not in walkables:
            out.append((val, p, dist))

        if val not in walkables:
            continue

        if p in seen:
            continue
        else:
            seen.add(p)

        for np in grid.neighbors(*p):
            q.append((np, dist + 1))
    return out


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    data = [process_line(l) for l in read_file(input)]
    grid = Grid(data)

    loc = {}
    for x, y in grid.walk_coords():
        c = grid.get(x, y)
        if c in string.ascii_lowercase + "@":
            loc[c] = x, y
    all_keys = set(loc.keys())

    seen = {}
    origin = loc["@"]
    min_dist = float("inf")
    frontier = [("@", origin, 0, ".@")]
    c = 0
    try:
        while frontier:
            c += 1
            if c % 100 == 0 and False:
                print(frontier)
            val, p, dist, walkables = frontier.pop(0)

            seen_key = (p, walkables)
            if dist > seen.get(seen_key, float("inf")):
                continue
            seen[seen_key] = dist

            if len(walkables) == 2 * len(all_keys):
                if dist < min_dist:
                    print(dist, " ".join(set(walkables.lower())))
                    min_dist = dist
                continue
            for res in shortest_path_to_all_unseen(p, grid, walkables):
                frontier.append(
                    (
                        res[0],
                        res[1],
                        res[2] + dist,
                        walkables + res[0] + res[0].upper(),
                    )
                )
        print(min_dist)
    except KeyboardInterrupt:
        print()
        print(len(seen))
        print(frontier[:40])


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    data = [process_line(l) for l in read_file(input)]
    pprint(locals())


if __name__ == "__main__":
    # profile_it()
    cli()
