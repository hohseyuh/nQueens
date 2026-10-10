# N-Queens

> ***Professor: Leyla Muradkhanli***    \
> ***Student: Huseyn Movla***         \
> ***Subject: Foundations of Artificial Intelligence***

Place N queens on an N×N board so that no two attack each other. This solver uses backtracking with bitmasks.

## Files

| File | What it does |
|---|---|
| `main.py` | Counts the solutions, optionally draws some boards, and times the run |
| `queens_viz.py` | Animates the backtracking step by step, up to the m-th solution |

Requires Python 3.8+ and no dependencies. Keep both files in the same folder.

## Usage

```bash
python main.py 8              # n=8: 92 solutions in 0.0xs
python main.py 8 --show 3     # also draw the first 3 boards
python main.py 8 --viz 5      # animate until the 5th solution
python main.py                # prompts for n
```

```bash
python queens_viz.py 8 -m 5          # animate until the 5th solution
python queens_viz.py 6 --step        # press Enter for each frame
python queens_viz.py 8 --delay 0.1   # set seconds per frame (default 0.4)
python queens_viz.py 8 --no-clear    # print frames in sequence, no redraw
```

## How it works

Queens are placed one per row. Three integer bitmasks track the attacked squares in the current row:

- `cols`: columns that are already taken
- `d1`, `d2`: the two diagonal directions. They shift by one bit each row, because diagonal attacks slide sideways.

```python
free = full & ~(cols | d1 | d2)   # safe squares in this row
bit  = free & -free               # lowest safe square
```

Attacked squares are never visited, so the pruning is built in.

## Reading the visualizer

- `♛` marks a placed queen, `×` an attacked square and `·` a safe square. `→` points to the current row.
- `free=` reads left to right, the same as the board. Raw binary reads right to left: bit 0 is the rightmost digit.
- Messages: `place queen`, `✗ no safe square, backtrack` and `↩ lift queen`.

## Notes

- Plain CPython stays fast up to about n ≈ 13. Use PyPy for larger n.
- Solution counts for n=1 to 10: 1, 0, 0, 2, 10, 4, 40, 92, 352, 724.