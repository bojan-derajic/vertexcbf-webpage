"""Generate the schematic SVGs used by the poster and the project page.

Run:  python tools/make_diagrams.py
Writes assets/img/{vertex-max,vertex-max-poster,tree-search}.svg
"""
import pathlib

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets/img"
OUT.mkdir(parents=True, exist_ok=True)

INK, ACC, MUT, RULE, SOFT = "#15181E", "#14467E", "#6B7383", "#D5DAE2", "#E8EEF6"
FONT = "Inter, 'Liberation Sans', system-ui, sans-serif"


# --------------------------------------------------------------------------
# 1. The Hamiltonian is linear in u  ->  its max over a polytope sits on a vertex
# --------------------------------------------------------------------------
def vertex_max(costate: str = "p") -> str:
    """`costate` names the gradient in the arrow label: the project page writes the
    Hamiltonian with a costate p, the poster writes it with the value gradient."""
    poly = [(180, 98), (352, 79), (440, 169), (412, 288), (242, 310), (164, 228)]
    best = (440, 169)                      # argmax of the linear objective over the polytope
    px, py = 0.85, -0.53                   # direction of  g(x)^T p   (screen coordinates)
    nx, ny = -py, px                       # perpendicular -> level sets of the objective

    def level(at, t=140, dash="7 8", col=RULE, w=2.2):
        x, y = at
        return (f'<line x1="{x-nx*t:.1f}" y1="{y-ny*t:.1f}" x2="{x+nx*t:.1f}" y2="{y+ny*t:.1f}" '
                f'stroke="{col}" stroke-width="{w}" stroke-dasharray="{dash}"/>')

    pts = " ".join(f"{x},{y}" for x, y in poly)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 372" '
         f'font-family="{FONT}" fill="{INK}">']
    s += ['<defs><marker id="ah" viewBox="0 0 10 10" refX="8.6" refY="5" markerWidth="7" '
          f'markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/>'
          '</marker></defs>']
    # axes
    s += ['<g stroke="#C9CFD9" stroke-width="2">',
          '<line x1="52" y1="340" x2="500" y2="340"/>',
          '<line x1="52" y1="340" x2="52" y2="34"/>', '</g>',
          f'<text x="503" y="347" font-size="17" fill="{MUT}">u<tspan dy="4" '
          f'font-size="12">1</tspan></text>',
          f'<text x="36" y="32" font-size="17" fill="{MUT}">u<tspan dy="4" '
          f'font-size="12">2</tspan></text>']
    # level sets of the linear objective, and the supporting line at the optimum
    s += [level((268, 224)), level((352, 172)), level(best, dash="none", col=ACC, w=3, t=150)]
    # the control polytope
    s += [f'<polygon points="{pts}" fill="{SOFT}" fill-opacity="0.9" '
          f'stroke="{ACC}" stroke-width="3" stroke-linejoin="round"/>',
          f'<text x="222" y="190" font-size="28" font-weight="700" font-style="italic" '
          f'fill="{ACC}">U</text>']
    # vertices
    for x, y in poly:
        if (x, y) != best:
            s += [f'<circle cx="{x}" cy="{y}" r="8.5" fill="#fff" stroke="{ACC}" stroke-width="3"/>']
    s += [f'<circle cx="{best[0]}" cy="{best[1]}" r="17" fill="{ACC}" fill-opacity="0.18"/>',
          f'<circle cx="{best[0]}" cy="{best[1]}" r="10" fill="{ACC}"/>',
          f'<text x="{best[0]+19}" y="{best[1]-11}" font-size="23" font-weight="700" '
          f'fill="{ACC}">u<tspan dy="-8" font-size="15">\u2605</tspan></text>']
    # direction of growth of the objective, kept clear of the polytope
    ax, ay = 66, 332
    s += [f'<line x1="{ax}" y1="{ay}" x2="{ax+px*92:.1f}" y2="{ay+py*92:.1f}" stroke="{INK}" '
          f'stroke-width="3.4" marker-end="url(#ah)"/>']
    label = (f'g(x)<tspan dy="-7" font-size="13">T</tspan>'
             f'<tspan dy="7">{costate}</tspan>')
    if len(costate) == 1:      # a short label runs along the arrow
        s += [f'<text x="78" y="352" font-size="19" font-weight="600" '
              f'transform="rotate(-32 78 352)">{label}</text>']
    else:                      # a longer one sits level, above the arrow head
        s += [f'<text x="62" y="262" font-size="19" font-weight="600">{label}</text>']
    s += ['</svg>']
    return "\n".join(s)


# --------------------------------------------------------------------------
# 2. Vertex-restricted beam search over the control tree
# --------------------------------------------------------------------------
def tree_search() -> str:
    """Beam search with M = 3 vertices and beam width B = 3.  Depth runs left to right;
    the beam is vertical: in every column the B kept nodes (filled) form one block,
    outlined and marked with a bracket, the other candidates are pruned (hollow)."""
    xs = [40, 168, 300, 432]
    l1 = [68, 155, 242]
    l2 = {y: [y - 28, y, y + 28] for y in l1}
    kept2 = [96, 127, 155]                     # adjacent candidates, so the beam is one block
    slots = [48, 75, 102, 129, 156, 183, 210, 237, 264]
    l3 = {y: slots[3 * i: 3 * i + 3] for i, y in enumerate(kept2)}
    kept3 = [75, 102, 129]                     # the third branch dies out here

    e, n, t = [], [], []
    def edge(x1, y1, x2, y2, on):
        e.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                 f'stroke="{ACC if on else RULE}" stroke-width="{2.8 if on else 2}"/>')
    def node(x, y, r, on, solid=True):
        if on:
            n.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{ACC}"/>' if solid else
                     f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" stroke="{ACC}" stroke-width="2.6"/>')
        else:
            n.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" stroke="{RULE}" stroke-width="2.4"/>')

    node(xs[0], 155, 9, True, solid=False)
    for y in l1:
        edge(xs[0] + 9, 155, xs[1] - 8, y, True)
        node(xs[1], y, 8, True)
        for cy in l2[y]:
            on = cy in kept2
            edge(xs[1] + 8, y, xs[2] - 7, cy, on)
            node(xs[2], cy, 7, on)
    for y in kept2:
        for cy in l3[y]:
            on = cy in kept3
            edge(xs[2] + 7, y, xs[3] - 6, cy, on)
            node(xs[3], cy, 6, on)

    # the beam at each step: one outlined block around the B kept nodes
    beam = []
    for x, ys, r in [(xs[1], l1, 8), (xs[2], kept2, 7), (xs[3], kept3, 6)]:
        pad = r + 8
        beam.append(f'<rect x="{x - pad}" y="{ys[0] - pad}" width="{2 * pad}" '
                    f'height="{ys[-1] - ys[0] + 2 * pad}" rx="{pad}" fill="{SOFT}" '
                    f'stroke="{ACC}" stroke-width="1.6" stroke-opacity="0.45"/>')

    # depth along the top
    for i, x in enumerate(xs):
        t.append(f'<text x="{x}" y="22" font-size="19" fill="{MUT}" text-anchor="middle">'
                 + (f'k = {i}' if i == 0 else f'{i}') + '</text>')
    t.append(f'<text x="{xs[3] + 50}" y="22" font-size="19" fill="{MUT}" '
             f'text-anchor="middle">…</text>')
    t.append(f'<text x="{xs[0]}" y="190" font-size="20" font-style="italic" '
             f'text-anchor="middle">x</text>')

    # beam width: a vertical bracket beside the last beam
    bx, y0, y1 = xs[3] + 22, kept3[0] - 14, kept3[-1] + 14
    t.append(f'<path d="M{bx},{y0} h7 V{y1} h-7" fill="none" stroke="{INK}" stroke-width="2.2"/>')
    t.append(f'<text x="{bx + 16}" y="{(y0 + y1) / 2 - 3}" font-size="24">'
             f'<tspan font-style="italic" font-weight="700">B</tspan> = 3</text>')
    t.append(f'<text x="{bx + 16}" y="{(y0 + y1) / 2 + 20}" font-size="18" fill="{MUT}">'
             f'beam width</text>')

    # legend: kept vs pruned
    t.append(f'<circle cx="16" cy="252" r="6" fill="{ACC}"/>'
             f'<text x="28" y="258" font-size="18" fill="{MUT}">kept</text>')
    t.append(f'<circle cx="16" cy="276" r="6" fill="#fff" stroke="{RULE}" stroke-width="2.4"/>'
             f'<text x="28" y="282" font-size="18" fill="{MUT}">pruned</text>')

    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 572 292" '
        f'font-family="{FONT}" fill="{INK}">',
        *beam, *e, *n, *t, '</svg>'])


FILES = {
    "vertex-max.svg":        vertex_max(),
    "vertex-max-poster.svg": vertex_max("\u2207V(x)"),
    "tree-search.svg":       tree_search(),
}
for name, svg in FILES.items():
    (OUT / name).write_text(svg)
    print("wrote", OUT / name)
