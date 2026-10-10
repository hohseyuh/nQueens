import sys, time
from queens_vis import visualise

def queens(n, keep=0):
    full = (1 << n) - 1
    count, sols, pos = 0, [], []

    def go(cols, d1, d2):
        nonlocal count
        if cols == full:
            count += 1
            if len(sols) < keep:
                sols.append(pos[:])
            return
        free = full & ~(cols | d1 | d2)
        while free:
            # print("  " * len(pos),
            #       f"row {len(pos)} free={format(free, f'0{full.bit_length()}b')[::-1]} -> col {(free & -free).bit_length() - 1}")
            bit = free & -free
            free ^= bit
            pos.append(bit.bit_length() - 1)   # bit -> column index
            go(cols | bit, ((d1 | bit) << 1) & full, (d2 | bit) >> 1)
            pos.pop()

    go(0, 0, 0)
    return count, sols

def draw(sol):
    n = len(sol)
    return "\n".join(" ".join("♛" if c == q else "·" for c in range(n)) for q in sol)

def main():
    args = sys.argv[1:]
    try:
        n = int(args[0]) if args else int(input("n = "))
        keep = int(args[args.index("--show") + 1]) if "--show" in args else 0
        vis = int(args[args.index("--vis") + 1]) if "--vis" in args else 0  # add
    except (ValueError, IndexError):
        sys.exit("usage: python main.py N [--show K] [--vis M]")  # update
    if n < 1:
        sys.exit("n must be >= 1")

    if vis:
        visualise(n, vis)
        return

    t = time.perf_counter()
    count, sols = queens(n, keep)
    dt = time.perf_counter() - t

    for i, s in enumerate(sols, 1):
        print(f"#{i}  cols: {[c + 1 for c in s]}\n{draw(s)}\n")
    print(f"n={n}: {count} solutions in {dt:.3f}s")

if __name__ == "__main__":
    main()