# Builds the explicit state transition graph of N-Queens and exports it as text, Graphviz DOT or SVG.
#
#   python state_graph.py 4                       # print states, transitions, costs and goal states
#   python state_graph.py 4 --svg graph.svg       # draw the graph
#   python state_graph.py 4 --svg dfs.svg --order dfs   # number nodes in DFS expansion order
#   python state_graph.py 4 --dot graph.dot       # Graphviz source, render with: dot -Tpng graph.dot -o graph.png

import sys
from search import successors, isGoal, bfs, dfs


def buildGraph(n):
    """Every state reachable from (), as {state: [(child, cost), ...]}."""
    graph, todo = {}, [()]
    while todo:
        state = todo.pop()
        graph[state] = successors(n, state)
        todo.extend(child for child, _ in graph[state])
    return dict(sorted(graph.items(), key=lambda kv: (len(kv[0]), kv[0])))


def kind(n, graph, state):
    if state == ():
        return "start"
    if isGoal(n, state):
        return "goal"
    return "dead" if not graph[state] else "inner"


def label(state):
    return "()" if not state else "(" + ",".join(map(str, state)) + ")"


def describe(n, graph):
    goals = [s for s in graph if isGoal(n, s)]
    dead = [s for s in graph if kind(n, graph, s) == "dead"]
    edges = sum(len(v) for v in graph.values())
    out = [f"N={n}: {len(graph)} states, {edges} transitions, {len(goals)} goal states, {len(dead)} dead ends", ""]
    for state, children in graph.items():
        k = kind(n, graph, state)
        tag = {"goal": "  GOAL", "dead": "  dead end", "start": "  START"}.get(k, "")
        moves = ", ".join(f"col {c[-1]} -> {label(c)} [cost {w}]" for c, w in children)
        out.append(f"{label(state):<{2 * n + 2}} g={len(state)}{tag}" + (f"\n    {moves}" if moves else ""))
    out.append("")
    out.append("Goal states: " + ", ".join(label(g) for g in goals))
    return "\n".join(out)


def toDot(n, graph):
    colour = {"start": "#cfe2ff", "goal": "#c7f0d2", "dead": "#f8d0d0", "inner": "#ffffff"}
    lines = [f'digraph nqueens{n} {{', '  node [shape=box, style="rounded,filled", fontname="Helvetica"];']
    for s in graph:
        shape = ", peripheries=2" if kind(n, graph, s) == "goal" else ""
        lines.append(f'  "{label(s)}" [fillcolor="{colour[kind(n, graph, s)]}"{shape}];')
    for s, children in graph.items():
        for c, w in children:
            lines.append(f'  "{label(s)}" -> "{label(c)}" [label="col {c[-1]} / {w}"];')
    lines.append("}")
    return "\n".join(lines)


def toSvg(n, graph, order=None, title=None):
    cell = 14 if n <= 4 else 10
    box = n * cell
    slot = max(box + 44, 92)
    rowH = box + 86
    left, top = 90, 70

    # Leaves get consecutive x slots, parents sit over the middle of their children.
    x, nxt = {}, [0]

    def place(s):
        kids = [c for c, _ in graph[s]]
        for c in kids:
            place(c)
        if kids:
            x[s] = (x[kids[0]] + x[kids[-1]]) / 2
        else:
            x[s] = nxt[0]
            nxt[0] += 1

    place(())
    width = left + nxt[0] * slot + 20
    height = top + n * rowH + box + 100
    pos = {s: (left + x[s] * slot + slot / 2, top + len(s) * rowH) for s in graph}
    step = {s: i + 1 for i, s in enumerate(order or [])}
    stroke = {"start": "#2563eb", "goal": "#16a34a", "dead": "#dc2626", "inner": "#6b7280"}
    fill = {"start": "#eff6ff", "goal": "#f0fdf4", "dead": "#fef2f2", "inner": "#ffffff"}

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
         f'viewBox="0 0 {width:.0f} {height:.0f}" font-family="Helvetica, Arial, sans-serif">',
         f'<rect width="100%" height="100%" fill="#ffffff"/>',
         f'<text x="{left}" y="30" font-size="18" font-weight="bold" fill="#111827">'
         f'{title or f"State transition graph, {n}-Queens"}</text>',
         f'<text x="{left}" y="50" font-size="12" fill="#4b5563">Each edge places one queen in the next row '
         f'(label: column, step cost). Path cost g = number of queens.</text>']

    for d in range(n + 1):
        y = top + d * rowH + box / 2
        o.append(f'<text x="12" y="{y + 4:.0f}" font-size="12" fill="#4b5563">depth {d}</text>')
        o.append(f'<text x="12" y="{y + 19:.0f}" font-size="11" fill="#9ca3af">g = {d}</text>')

    for s, children in graph.items():
        px, py = pos[s]
        for c, w in children:
            cx, cy = pos[c]
            o.append(f'<line x1="{px:.1f}" y1="{py + box + 22:.1f}" x2="{cx:.1f}" y2="{cy - 2:.1f}" '
                     f'stroke="#9ca3af" stroke-width="1.2"/>')
            mx, my = (px + cx) / 2, (py + box + 22 + cy) / 2
            o.append(f'<rect x="{mx - 22:.1f}" y="{my - 8:.1f}" width="44" height="15" rx="3" fill="#ffffff"/>')
            o.append(f'<text x="{mx:.1f}" y="{my + 3:.1f}" font-size="10" text-anchor="middle" fill="#374151">'
                     f'col {c[-1]} / {w}</text>')

    for s in graph:
        cx, y0 = pos[s]
        x0 = cx - box / 2
        k = kind(n, graph, s)
        seen = not order or s in step
        op = "1" if seen else "0.35"
        o.append(f'<g opacity="{op}">')
        o.append(f'<rect x="{x0 - 3:.1f}" y="{y0 - 3:.1f}" width="{box + 6}" height="{box + 6}" rx="3" '
                 f'fill="{fill[k]}" stroke="{stroke[k]}" stroke-width="{2.5 if k in ("goal", "start") else 1.5}"/>')
        for r in range(n):
            for c in range(n):
                shade = "#e5e7eb" if (r + c) % 2 else "#f9fafb"
                o.append(f'<rect x="{x0 + c * cell:.1f}" y="{y0 + r * cell:.1f}" width="{cell}" height="{cell}" '
                         f'fill="{shade}"/>')
        for r, c in enumerate(s):
            o.append(f'<circle cx="{x0 + c * cell + cell / 2:.1f}" cy="{y0 + r * cell + cell / 2:.1f}" '
                     f'r="{cell * 0.34:.1f}" fill="#111827"/>')
        o.append(f'<text x="{cx:.1f}" y="{y0 + box + 16:.1f}" font-size="11" text-anchor="middle" '
                 f'fill="#111827">{label(s)}</text>')
        if k == "goal":
            o.append(f'<text x="{cx:.1f}" y="{y0 + box + 30:.1f}" font-size="10" font-weight="bold" '
                     f'text-anchor="middle" fill="#16a34a">GOAL</text>')
        elif k == "dead":
            o.append(f'<text x="{cx:.1f}" y="{y0 + box + 30:.1f}" font-size="10" text-anchor="middle" '
                     f'fill="#dc2626">dead end</text>')
        o.append('</g>')
        if s in step:
            o.append(f'<circle cx="{x0 + box + 6:.1f}" cy="{y0 - 6:.1f}" r="10" fill="#7c3aed"/>')
            o.append(f'<text x="{x0 + box + 6:.1f}" y="{y0 - 2:.1f}" font-size="10" font-weight="bold" '
                     f'text-anchor="middle" fill="#ffffff">{step[s]}</text>')

    ly = height - 42
    items = [("start", "initial state"), ("inner", "intermediate state"), ("dead", "dead end (no safe column)"),
             ("goal", "goal state")]
    lx = 12
    for k, text in items:
        w = 34 + len(text) * 6.5
        if lx + w > width:
            lx, ly = 12, ly + 22
        o.append(f'<rect x="{lx}" y="{ly - 10}" width="14" height="14" rx="2" fill="{fill[k]}" '
                 f'stroke="{stroke[k]}" stroke-width="2"/>')
        o.append(f'<text x="{lx + 20}" y="{ly + 2}" font-size="12" fill="#374151">{text}</text>')
        lx += w
    if order:
        lx, ly = 12, ly + 22
        o.append(f'<circle cx="{lx + 7}" cy="{ly - 3}" r="8" fill="#7c3aed"/>')
        o.append(f'<text x="{lx + 20}" y="{ly + 2}" font-size="12" fill="#374151">expansion order '
                 f'(faded = never expanded)</text>')
    o.append('</svg>')
    return "\n".join(o)


def main():
    args = sys.argv[1:]
    try:
        n = int(args[0])
        svg = args[args.index("--svg") + 1] if "--svg" in args else None
        dot = args[args.index("--dot") + 1] if "--dot" in args else None
        algo = args[args.index("--order") + 1] if "--order" in args else None
    except (ValueError, IndexError):
        sys.exit("usage: python state_graph.py N [--svg FILE [--order dfs|bfs]] [--dot FILE]")
    if not 1 <= n <= 6 or algo not in (None, "dfs", "bfs"):
        sys.exit("N must be 1..6 (the graph grows fast) and --order must be dfs or bfs")

    graph = buildGraph(n)
    print(describe(n, graph))

    if dot:
        with open(dot, "w") as f:
            f.write(toDot(n, graph))
        print(f"\nwrote {dot}")
    if svg:
        order = (dfs if algo == "dfs" else bfs)(n)["order"] if algo else None
        title = f"{n}-Queens state graph, {algo.upper()} expansion order" if algo else None
        with open(svg, "w") as f:
            f.write(toSvg(n, graph, order, title))
        print(f"wrote {svg}")


if __name__ == "__main__":
    main()
