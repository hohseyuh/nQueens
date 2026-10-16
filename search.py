# N-Queens as a search problem: explicit states, transitions, costs and goal test, solved with BFS and DFS.
#
# State      : tuple of column indices, one per filled row, e.g. (1, 3) = queens at (0,1) and (1,3)
# Initial    : ()  (empty board)
# Action     : put a queen in the next empty row, in a column no placed queen attacks
# Step cost  : 1 per queen placed, so every goal has path cost n
# Goal test  : len(state) == n  (safe placement is guaranteed by the actions)

import sys, time
from collections import deque


def safe(state, col):
    row = len(state)
    return all(c != col and abs(c - col) != row - r for r, c in enumerate(state))


def actions(n, state):
    return [c for c in range(n) if safe(state, c)] if len(state) < n else []


def result(state, col):
    return state + (col,)


def stepCost(state, col):
    return 1


def isGoal(n, state):
    return len(state) == n


def successors(n, state):
    """Transitions out of a state as (child, cost) pairs."""
    return [(result(state, c), stepCost(state, c)) for c in actions(n, state)]


def bfs(n, findAll=False):
    """Breadth-first search with a FIFO queue. Goal test when a node is taken off the queue."""
    frontier = deque([()])
    order, goals, peak = [], [], 1
    while frontier:
        state = frontier.popleft()
        order.append(state)
        if isGoal(n, state):
            goals.append(state)
            if not findAll:
                break
            continue
        for child, _ in successors(n, state):
            frontier.append(child)
        peak = max(peak, len(frontier))
    return {"goals": goals, "order": order, "peak": peak}


def dfs(n, findAll=False):
    """Depth-first search with a LIFO stack. Children are pushed in reverse so the leftmost is explored first."""
    frontier = [()]
    order, goals, peak = [], [], 1
    while frontier:
        state = frontier.pop()
        order.append(state)
        if isGoal(n, state):
            goals.append(state)
            if not findAll:
                break
            continue
        for child, _ in reversed(successors(n, state)):
            frontier.append(child)
        peak = max(peak, len(frontier))
    return {"goals": goals, "order": order, "peak": peak}


def pathCost(state):
    """Sum of step costs from the initial state to this state."""
    return sum(stepCost(state[:i], c) for i, c in enumerate(state))


def draw(state, n):
    return "\n".join(" ".join("♛" if r < len(state) and state[r] == c else "·" for c in range(n)) for r in range(n))


def run(name, fn, n, findAll):
    t = time.perf_counter()
    res = fn(n, findAll)
    dt = time.perf_counter() - t
    goals = res["goals"]
    print(f"{name}: expanded {len(res['order'])} nodes, peak frontier {res['peak']}, {dt * 1000:.2f} ms")
    if not goals:
        print(f"  no goal state exists for n={n}\n")
    elif findAll:
        print(f"  {len(goals)} goal states found\n")
    else:
        g = goals[0]
        print(f"  first goal: {g}, path cost {pathCost(g)}")
        print("  path: " + " -> ".join(str(g[:i]) for i in range(n + 1)))
        print(draw(g, n) + "\n")
    return res


def main():
    args = sys.argv[1:]
    try:
        n = int(args[0]) if args and not args[0].startswith("-") else int(input("n = "))
        algo = args[args.index("--algo") + 1] if "--algo" in args else "both"
    except (ValueError, IndexError):
        sys.exit("usage: python search.py N [--algo bfs|dfs|both] [--all]")
    if n < 1 or algo not in ("bfs", "dfs", "both"):
        sys.exit("usage: python search.py N [--algo bfs|dfs|both] [--all]")
    findAll = "--all" in args

    if algo in ("dfs", "both"):
        run("DFS", dfs, n, findAll)
    if algo in ("bfs", "both"):
        run("BFS", bfs, n, findAll)


if __name__ == "__main__":
    main()
