from inspect import signature
from enum import Enum
from util import read_file
from getch import getche


def process_intcode(input):
    return [int(x) for x in read_file(input)[0].split(",")]


class Intcode:
    HALT = 99

    class Halted(Exception):
        pass

    class WroteOutput(Exception):
        pass

    class WaitingForInput(Exception):
        pass

    def __init__(self, mem, input=None):
        self.mem = Memory(mem, cpu=self)
        self.ip = 0
        self.input = [] if input is None else input
        self.output = []
        self.rb = 0
        self.c = 0

    def copy(self):
        out = Intcode([])
        out.mem = self.mem.copy()
        out.ip = self.ip
        out.input = self.input[:]
        out.output = self.output[:]
        out.rb = self.rb
        return out

    def next(self, n=1):
        ip = self.ip
        self.ip += n
        return self.mem[ip : ip + n]

    def run(self):
        while True:
            try:
                self.run_to_exc()
            except Intcode.WroteOutput:
                pass
            except Intcode.Halted:
                break

    def run_to_exc(self):
        while True:
            prev_ip = self.ip

            [iopcode] = self.next()
            sopcode = str(iopcode)
            opcode = int(sopcode[-2:])

            if opcode == Intcode.HALT:
                raise Intcode.Halted

            inst = self.INSTRUCTION[opcode]
            sig = signature(inst)
            nparams = len(sig.parameters) - 1

            sopcode = sopcode.zfill(2 + nparams)
            param_modes = sopcode[:-2][::-1]

            args = self.next(nparams)
            args = [(x, ParamMode(param_modes[i])) for (i, x) in enumerate(args)]
            args = [self] + args

            output_before = len(self.output)

            try:
                self.c += 1
                inst(*args)
            except Intcode.WaitingForInput:
                # reset to try input again
                self.ip = prev_ip
                self.c -= 1
                raise

    def run_to_output(self, n=None):
        use_list_output = True
        if n is None:
            use_list_output = False
            n = 1

        while len(self.output) < n:
            try:
                self.run_to_exc()
            except Intcode.WroteOutput:
                continue

        output = self.output[:]
        self.output = []

        if use_list_output:
            return output
        else:
            return output[0]

    def run_ascii(self, input=None, quiet=False):
        if input is not None:
            input_lines = [l for l in input.split("\n") if l and not l.startswith("#")]
            input = "\n".join(input_lines) + "\n"
            input = list(input)
        print_ = print if not quiet else (lambda *a, **k: None)
        last_output = None
        while True:
            try:
                c = self.run_to_output()
                if 0 < c < 128:
                    print_(chr(c), end="", flush=True)
                else:
                    print_("<" + str(c) + ">", end="", flush=True)
                last_output = c
            except Intcode.WaitingForInput:
                if input:
                    c = input.pop(0)
                    print_(c, end="", flush=True)
                else:
                    c = getche()
                self.input.append(ord(c))
            except Intcode.Halted:
                return last_output

    def add(self, a, b, dest):
        self.mem[dest] = self.mem[a] + self.mem[b]

    def mul(self, a, b, dest):
        self.mem[dest] = self.mem[a] * self.mem[b]

    def inp(self, dest):
        if not self.input:
            raise Intcode.WaitingForInput
        q = self.input.pop(0)
        self.mem[dest] = q

    def out(self, x):
        self.output.append(self.mem[x])
        raise Intcode.WroteOutput

    def jmpt(self, x, label):
        if self.mem[x]:
            self.ip = self.mem[label]

    def jmpf(self, x, label):
        if not self.mem[x]:
            self.ip = self.mem[label]

    def lt(self, a, b, dest):
        self.mem[dest] = int(self.mem[a] < self.mem[b])

    def eq(self, a, b, dest):
        self.mem[dest] = int(self.mem[a] == self.mem[b])

    def rbas(self, x):
        self.rb += self.mem[x]

    INSTRUCTION = {
        1: add,
        2: mul,
        3: inp,
        4: out,
        5: jmpt,
        6: jmpf,
        7: lt,
        8: eq,
        9: rbas,
    }


class ParamMode(Enum):
    Position = "0"
    Immediate = "1"
    Relative = "2"


class Memory:
    PADDING = 100_000

    def __init__(self, mem, cpu):
        self.mem = mem[:] + [0] * self.PADDING
        self.cpu = cpu

    def copy(self):
        out = Memory([], None)
        out.mem = self.mem[:]
        out.cpu = self.cpu
        return out

    def __getitem__(self, key):
        if isinstance(key, tuple):
            v, p = key
            if p is ParamMode.Immediate:
                return v
            elif p is ParamMode.Relative:
                return self.mem[v + self.cpu.rb]
            else:
                return self.mem[v]
        return self.mem[key]

    def __setitem__(self, key, val):
        if isinstance(key, tuple):
            v, p = key
            if p is ParamMode.Position:
                key = v
            elif p is ParamMode.Relative:
                key = v + self.cpu.rb
            else:
                raise ValueError(key)
        assert key < len(self.mem), key
        self.mem[key] = val
