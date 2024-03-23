from util import *


@click.group()
def cli():
    pass


def process_line(line):
    return line


def points_between(start, end):
    dx, dy = [end[i] - start[i] for i in range(2)]
    g = gcd(dx, dy)

    dx = dx // g
    dy = dy // g
    for m in range(1, g):
        yield (start[0] + m * dx, start[1] + m * dy)


def find_best_station(asteroids):
    c = Counter()
    for a in asteroids:
        for b in asteroids:
            if a == b:
                continue

            for p in points_between(a, b):
                if p in asteroids:
                    break
            else:
                c[a] += 1

    return c.most_common(1)[0]


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    data = [process_line(l) for l in read_file(input)]
    grid = Grid(data)
    asteroids = set((x, y) for (x, y) in grid.walk_coords() if grid.get(x, y) == "#")

    best = find_best_station(asteroids)
    print(best)


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    data = [process_line(l) for l in read_file(input)]
    grid = Grid(data)
    asteroids = set((x, y) for (x, y) in grid.walk_coords() if grid.get(x, y) == "#")

    best = find_best_station(asteroids)[0]
    by_angle = defaultdict(list)
    for a in asteroids:
        if a == best:
            continue
        dx, dy = [a[i] - best[i] for i in range(2)]
        angle = atan2(dx, -dy)
        if angle < 0:
            angle += 2 * pi
        by_angle[angle].append((dx * dx + dy * dy, a))
        by_angle[angle].sort()

    angles = sorted(by_angle)
    exploded = 0
    last_exploded = None
    while exploded < 200:
        for angle in angles:
            if not (exploded < 200):
                break
            asteroids = by_angle[angle]
            if asteroids:
                _, last_exploded = asteroids.pop(0)
                exploded += 1
    print(exploded, last_exploded)


if __name__ == "__main__":
    cli()
