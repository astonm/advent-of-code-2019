from util import *


@click.group()
def cli():
    pass


@dataclass
class Moon:
    pos: Vector
    vel: Vector

    def __str__(self):
        template = "pos=<x={:< 3d}, y={:< 3d}, z={:< 3d}>, vel=<x={:< 3d}, y={:< 3d}, z={:< 3d}>"
        return template.format(*(list(self.pos) + list(self.vel)))

    def to_state(self):
        return (tuple(self.pos), tuple(self.vel))


def process_line(line):
    return Moon(
        pos=Vector(parse("<x={:d}, y={:d}, z={:d}>", line)),
        vel=Vector([0, 0, 0]),
    )


def print_moons(steps, moons):
    print(f"After {steps+1} steps:")
    for moon in moons:
        print(moon)
    print()


def sign(x):
    return -1 if x < 0 else 0 if x == 0 else 1


def total_energy(moons):
    out = 0
    for moon in moons:
        pe = sum(map(abs, moon.pos))
        ke = sum(map(abs, moon.vel))
        out += pe * ke

    return out


@cli.command()
@click.argument("input", type=click.File())
@click.argument("steps", default=10)
def part1(input, steps):
    moons = [process_line(l) for l in read_file(input)]

    state_repeats = {}
    for moon in moons:
        state_repeats[moon.to_state()] = []

    for step in range(steps):
        gravities = []
        for i, moon in enumerate(moons):
            gravity = Vector([0, 0, 0])
            for other in moons:
                if moon is not other:
                    gravity += Vector(
                        sign(other.pos[i] - moon.pos[i]) for i in [0, 1, 2]
                    )
            gravities.append(gravity)

            # if i == 0:
            #     print("y", [m.pos[1] for m in moons])
            #     print(f"{moons[i].pos[1]=}")
            #     print(f"{gravity=}")

        for moon, gravity in zip(moons, gravities):
            moon.vel += gravity
            moon.pos += moon.vel

    print_moons(step, moons)
    print(total_energy(moons))


def gravity_for(vals):
    vals.sort()
    # if len(set(vals)) == len(vals):
    #     return {vals[0]: 3, vals[1]: 1, vals[2]: -1, vals[3]: -3}

    lt = {}
    n = 0
    p = None
    for i, v in enumerate(vals):
        if v != p:
            n = i
        p = v
        lt[v] = n

    gt = {}
    n = 0
    p = None
    for i, v in enumerate(vals[::-1]):
        if v != p:
            n = i
        p = v
        gt[v] = n

    return {k: gt[k] - lt[k] for k in lt}


def repeat_len(l):
    # requires minimum three repeats
    # [1,2,3,4,1,2,3,4,1,2,3,4,1,2] => 4
    # [1,2,3] => 0
    for n in range(1, len(l) // 3 + 1):
        if l[0:n] == l[n : 2 * n]:  # == l[2 * n : 3 * n]:
            return n
    return 0


def lcm(a, b):
    return a * b // gcd(a, b)


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    moons = [process_line(l) for l in read_file(input)]

    orig_states = [moon.to_state() for moon in moons]
    state_repeats = [[] for i in range(len(moons) * 3)]

    try:
        for step in count():
            gravity_x = gravity_for([m.pos[0] for m in moons])
            gravity_y = gravity_for([m.pos[1] for m in moons])
            gravity_z = gravity_for([m.pos[2] for m in moons])

            for i, moon in enumerate(moons):
                for j in [0, 1, 2]:
                    if moon.pos[j] == orig_states[i][0][j]:
                        state_repeats[i * 3 + j].append(step)

                gravity = Vector(
                    [
                        gravity_x[moon.pos[0]],
                        gravity_y[moon.pos[1]],
                        gravity_z[moon.pos[2]],
                    ]
                )

                moon.vel += gravity
                moon.pos += moon.vel

            repeat_deltas = [deltas(v) for v in state_repeats]
            repeat_lens = [repeat_len(d) for d in repeat_deltas]
            if all(r for r in repeat_lens):
                # for sr in state_repeats:
                #     print(deltas(sr))
                # print()
                # print(repeat_lens)
                factors = []
                for rd, rl in zip(repeat_deltas, repeat_lens):
                    factors.append(sum(rd[:rl]))

                print(f"step={step}")
                print(factors)
                print(reduce(lcm, factors))
                return

    except KeyboardInterrupt:
        for rd in repeat_deltas:
            print(rd)
        print()
        print(repeat_lens)
        print(step)
        raise


if __name__ == "__main__":
    cli()
