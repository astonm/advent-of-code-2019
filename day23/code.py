from util import *
from intcode import *


@click.group()
def cli():
    pass


Packet = namedtuple("Packet", "x y")


@cli.command()
@click.argument("input", type=click.File())
def part1(input):
    data = process_intcode(input)
    cpus = [Intcode(data) for _ in range(50)]

    for i, cpu in enumerate(cpus):
        cpu.addr = i
        cpu.input = [cpu.addr]

    while True:
        waiting = []
        packets = defaultdict(list)

        for cpu in cpus:
            try:
                cpu.run_to_exc()
            except Intcode.WaitingForInput:
                waiting.append(cpu)
            except Intcode.WroteOutput:
                addr, x, y = cpu.run_to_output(3)
                packets[addr].append(Packet(x, y))

        for cpu in waiting:
            if cpu.addr in packets:
                for packet in packets[cpu.addr]:
                    cpu.input.extend(packet)
                del packets[cpu.addr]
            else:
                cpu.input.append(-1)

        if 255 in packets:
            print(first(packets[255]))
            return


@cli.command()
@click.argument("input", type=click.File())
def part2(input):
    data = process_intcode(input)
    cpus = [Intcode(data) for _ in range(50)]

    for i, cpu in enumerate(cpus):
        cpu.addr = i
        cpu.input = [cpu.addr]

    sequence = defaultdict(list)

    NAT = None
    sent_ys = set()
    for cycles in count():
        waiting = []
        packets = defaultdict(list)

        for cpu in cpus:
            while True:  # pull all output at once, otherwise puzzle doesn't work
                try:
                    if cpu.input and cpu.input != [-1]:
                        sequence[cpu.addr].append(cpu.input[:])
                    cpu.run_to_exc()
                except Intcode.WaitingForInput:
                    waiting.append(cpu)
                    break
                except Intcode.WroteOutput:
                    addr, x, y = cpu.run_to_output(3)
                    packet = Packet(x, y)
                    if addr == 255:
                        if packet != NAT:
                            NAT = packet
                    else:
                        packets[addr].append(packet)

        if (
            all(not c.input for c in cpus)
            and len(waiting) == len(cpus)
            and not packets
            and NAT
        ):
            packets[0].append(NAT)

            if NAT.y in sent_ys:
                print(NAT.y)
                for k, v in sequence.items():
                    print(f"{k}: {','.join(str(x) for x in v)}")
                return

            sent_ys.add(NAT.y)

        for cpu in waiting:
            if cpu.addr in packets:
                for packet in packets[cpu.addr]:
                    # pull all input at once, otherwise puzzle doesn't work
                    cpu.input.extend(packet)
            elif not cpu.input:
                cpu.input.append(-1)


if __name__ == "__main__":
    cli()
