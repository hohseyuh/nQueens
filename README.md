# N-Queens

> ***Professor: Leyla Muradkhanli***    \
> ***Student: Huseyn Movla***         \
> ***Subject: Foundations of Artificial Intelligence***

Place N queens on an N×N board so that no two attack each other. The problem is modelled as a search problem
(states, transitions, step costs and goal states) and solved with breadth-first and depth-first search. A
bitmask backtracking solver counts all solutions quickly.

## Files

| File | What it does |
|---|---|
| `search.py` | Formulates the search problem and solves it with BFS and DFS |
| `state_graph.py` | Builds the explicit state transition graph and exports it as text, SVG or Graphviz DOT |
| `main.py` | Counts the solutions with bitmask backtracking, optionally draws some boards, and times the run |
| `queens_vis.py` | Animates the backtracking step by step, up to the m-th solution |
| `test_search.py` | Unit tests for the transitions, both searches and the state graph |
| `diagrams/` | Pre-rendered state graphs for N=4 (plain, DFS order, BFS order) and N=5 |
| `report.docx` | Report: state design, state diagram, and BFS vs DFS comparison |

Requires Python 3.8+ and no dependencies. Keep all files in the same folder.

## Problem formulation

| Component | Definition |
|---|---|
| State | Tuple of the column of each queen placed so far, one queen per row. `(1, 3)` means queens at (0,1) and (1,3) |
| Initial state | `()`, the empty board |
| Actions | Put a queen in the next empty row, in a column that no placed queen attacks |
| Transition model | `result(state, col) = state + (col,)` |
| Step cost | 1 per queen placed, so every goal has path cost N |
| Goal test | `len(state) == N`. The actions only allow safe squares, so a full board is always a solution |

Dead ends are states with fewer than N queens and no safe column left in the next row.

## Usage

### Search (BFS and DFS)

```bash
python search.py 8                 # run DFS and BFS, print the first goal, its path and cost
python search.py 8 --algo bfs      # only BFS
python search.py 8 --all           # find every goal state (92 for n=8)
```

Sample output for N=8:

```
DFS: expanded 114 nodes, peak frontier 19
BFS: expanded 1966 nodes, peak frontier 573
```

### State transition graph

```bash
python state_graph.py 4                               # list all states, transitions, costs and goal states
python state_graph.py 4 --svg graph.svg               # draw the graph
python state_graph.py 4 --svg dfs.svg --order dfs     # number the nodes in DFS expansion order
python state_graph.py 4 --dot graph.dot               # Graphviz source: dot -Tpng graph.dot -o graph.png
```

N is limited to 1–6, because the graph grows quickly (17 states for N=4, 54 for N=5, 153 for N=6).

### Counting solutions and the visualiser

```bash
python main.py 8              # n=8: 92 solutions in 0.0xs
python main.py 8 --show 3     # also draw the first 3 boards
python main.py 8 --vis 5      # animate until the 5th solution
python main.py                # prompts for n
```

```bash
python queens_vis.py 8 -m 5          # animate until the 5th solution
python queens_vis.py 6 --step        # press Enter for each frame
python queens_vis.py 8 --delay 0.1   # set seconds per frame (default 0.4)
python queens_vis.py 8 --no-clear    # print frames in sequence, no redraw
```

### Tests

```bash
python -m unittest -v
```

## BFS vs DFS

All goal states lie at the same depth N, and every step costs 1. BFS therefore gains nothing from its
shortest-path guarantee here, because every solution has the same cost. It has to expand nearly every state at
depths 0 to N−1 before it reaches a goal. DFS goes straight down one branch and backtracks only at dead ends.

| N | DFS expanded | DFS peak frontier | BFS expanded | BFS peak frontier |
|---|---|---|---|---|
| 4 | 9 | 5 | 16 | 6 |
| 8 | 114 | 19 | 1966 | 573 |
| 10 | 103 | 30 | 34816 | 9643 |

DFS uses O(N²) memory, while the BFS frontier grows with the width of the tree. For this problem DFS is the
better choice.

## How the bitmask solver works

Queens are placed one per row. Three integer bitmasks track the attacked squares in the current row:

- `cols`: columns that are already taken
- `d1`, `d2`: the two diagonal directions. They shift by one bit each row, because diagonal attacks slide sideways.

```python
free = full & ~(cols | d1 | d2)   # safe squares in this row
bit  = free & -free               # lowest safe square
```

Attacked squares are never visited, so the pruning is built in.

## Reading the visualiser

- `♛` marks a placed queen, `×` an attacked square and `·` a safe square. `→` points to the current row.
- `free=` reads left to right, the same as the board. Raw binary reads right to left: bit 0 is the rightmost digit.
- Messages: `place queen`, `✗ no safe square, backtrack` and `↩ lift queen`.

## Notes

- Plain CPython stays fast up to about n ≈ 13. Use PyPy for larger n.
- Solution counts for n=1 to 10: 1, 0, 0, 2, 10, 4, 40, 92, 352, 724.
