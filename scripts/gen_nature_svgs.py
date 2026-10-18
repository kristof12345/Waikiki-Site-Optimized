#!/usr/bin/env python3
"""
Procedural generator for the Nature of Waikiki biome illustrations.

Generates standalone SVG files in icons/nature/ and injects localized inline
SVGs into en/nature.html and hu/nature.html. Every illustration container in
the pages is marked with data-nature-svg="KEY"; the <svg> inside it is replaced.

Scenes
  transect     Sea-to-summit cross-section through eight biomes of the nation
  reef         Split-level Caribbean mangrove coast and Jardines coral reef
  rainforest   Amazonian river, canopy strata, emergent kapok trees
  highlands    Brazilia highlands: glacier, paramo, cloud forest, cataract
  mogotes      Atlas vignette: Vinales karst towers and tobacco valley
  enriquillo   Atlas vignette: hypersaline Lago Enriquillo with flamingos
  pantanal     Atlas vignette: flooded Pantanal savanna wetland
  cerrado      Atlas vignette: Cerrado savanna with flowering ipe trees
  lencois      Atlas vignette: white dunes and rain lagoons of Lencois
  caatinga     Atlas vignette: dry Caatinga thorn forest with mandacaru

Usage
  python3 scripts/gen_nature_svgs.py

Design notes
  * All randomness is seeded, so output is deterministic and diff-friendly.
  * Every id is prefixed with "nt-<scene>-" so several inline SVGs can share a
    page without id collisions.
  * Ambient motion uses CSS classes defined in css/nature.css (drift, sway,
    swim, fly, bob, flow, shimmer) and is disabled for reduced motion.
"""

from __future__ import annotations

import html
import math
import random
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "icons" / "nature"
TAU = math.tau


# ==============================================================================
# FORMAT HELPERS
# ==============================================================================
def n(v: float) -> str:
    """Format a number compactly with one decimal place."""
    r = round(float(v), 1)
    if r == int(r):
        return str(int(r))
    return f"{r:.1f}"


def P(points, close: bool = True) -> str:
    d = "M" + " L".join(f"{n(x)},{n(y)}" for x, y in points)
    return d + ("Z" if close else "")


def smooth(points, closed: bool = False, k: float = 1 / 6) -> str:
    """Catmull-Rom spline through points as a cubic Bezier path."""
    p = list(points)
    if len(p) < 3:
        return P(p, closed)
    p = ([p[-1]] + p + [p[0], p[1]]) if closed else ([p[0]] + p + [p[-1]])
    d = [f"M{n(p[1][0])},{n(p[1][1])}"]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k)
        c2 = (p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k)
        d.append(f"C{n(c1[0])},{n(c1[1])} {n(c2[0])},{n(c2[1])} {n(p2[0])},{n(p2[1])}")
    if closed:
        d.append("Z")
    return " ".join(d)


def el(tag: str, body: str | None = None, **a) -> str:
    parts = []
    for key, val in a.items():
        name = key.rstrip("_").replace("_", "-")
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            val = n(val)
        parts.append(f'{name}="{val}"')
    attrs = (" " + " ".join(parts)) if parts else ""
    if body is None:
        return f"<{tag}{attrs}/>"
    return f"<{tag}{attrs}>{body}</{tag}>"


def g(items, **a) -> str:
    if isinstance(items, str):
        items = [items]
    return el("g", "".join(items), **a)


def hx(c: str):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(a: str, b: str, t: float) -> str:
    ra, rb = hx(a), hx(b)
    return "#%02x%02x%02x" % tuple(round(ra[i] + (rb[i] - ra[i]) * t) for i in range(3))


def quad(p0, p1, p2, t):
    u = 1 - t
    return (u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0], u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])


def quad_tan(p0, p1, p2, t):
    dx = 2 * (1 - t) * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0])
    dy = 2 * (1 - t) * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1])
    m = math.hypot(dx, dy) or 1
    return dx / m, dy / m


def interp(points):
    """Return y(x) for a polyline sorted by x."""
    xs = [p[0] for p in points]

    def f(x):
        if x <= xs[0]:
            return points[0][1]
        if x >= xs[-1]:
            return points[-1][1]
        lo, hi = 0, len(xs) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if xs[mid] <= x:
                lo = mid
            else:
                hi = mid
        t = (x - xs[lo]) / ((xs[hi] - xs[lo]) or 1)
        return points[lo][1] + (points[hi][1] - points[lo][1]) * t

    return f


# ==============================================================================
# SCENE BUILDER
# ==============================================================================
class Scene:
    def __init__(self, key: str, w: int, h: int, seed: int):
        self.key, self.w, self.h = key, w, h
        self.rng = random.Random(seed)
        self.defs: list[str] = []
        self.body: list[str] = []

    def id(self, name: str) -> str:
        return f"nt-{self.key}-{name}"

    def url(self, name: str) -> str:
        return f"url(#{self.id(name)})"

    def add(self, *items):
        for it in items:
            if isinstance(it, (list, tuple)):
                self.body.extend(it)
            elif it:
                self.body.append(it)

    @staticmethod
    def _stops(stops) -> str:
        out = []
        for st in stops:
            op = f' stop-opacity="{st[2]}"' if len(st) > 2 else ""
            out.append(f'<stop offset="{st[0]}" stop-color="{st[1]}"{op}/>')
        return "".join(out)

    def linear(self, name, stops, x1=0, y1=0, x2=0, y2=1) -> str:
        self.defs.append(
            f'<linearGradient id="{self.id(name)}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{self._stops(stops)}</linearGradient>'
        )
        return self.url(name)

    def radial(self, name, stops, cx=0.5, cy=0.5, r=0.5) -> str:
        self.defs.append(
            f'<radialGradient id="{self.id(name)}" cx="{cx}" cy="{cy}" r="{r}">{self._stops(stops)}</radialGradient>'
        )
        return self.url(name)

    def blur(self, name, sd) -> str:
        self.defs.append(
            f'<filter id="{self.id(name)}" x="-50%" y="-50%" width="200%" height="200%">'
            f'<feGaussianBlur stdDeviation="{sd}"/></filter>'
        )
        return self.url(name)

    def clip(self, name, d) -> str:
        self.defs.append(f'<clipPath id="{self.id(name)}"><path d="{d}"/></clipPath>')
        return self.url(name)

    def render(self, label: str) -> str:
        head = (
            f'<svg xmlns="http://www.w3.org/2000/svg" class="nature-ill" viewBox="0 0 {self.w} {self.h}" '
            f'role="img" aria-label="{html.escape(label, quote=True)}">'
        )
        lines = [head, "<defs>", *self.defs, "</defs>", *self.body, "</svg>"]
        return "\n".join(lines)


# ==============================================================================
# LANDSCAPE PRIMITIVES
# ==============================================================================
def ridge(rng, keys, rough, depth=5):
    out = [keys[0]]
    for a, b in zip(keys, keys[1:]):
        seg = [a, b]
        d = rough
        for _ in range(depth):
            new = [seg[0]]
            for p, q in zip(seg, seg[1:]):
                new += [((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + rng.uniform(-d, d)), q]
            seg = new
            d *= 0.52
        out += seg[1:]
    return out


def mountain(s: Scene, name, keys, base, fill, shade="#1f3348", shade_op=0.34, snow=None,
             snow_col="#f3f7fb", rough=14, depth=5, gullies=True, tongue=0.18):
    """Ridge polygon with right-flank shading, gullies and an optional snow cap."""
    rng = s.rng
    r = ridge(rng, keys, rough, depth)
    poly = r + [(r[-1][0], base), (r[0][0], base)]
    d = P(poly)
    clip = s.clip(name, d)
    inner = []
    if snow is not None:
        xs, xe = r[0][0], r[-1][0]
        steps = max(4, int((xe - xs) / 7))
        line = []
        for i in range(steps + 1):
            x = xs + (xe - xs) * i / steps
            y = snow + rng.uniform(-5, 5)
            if rng.random() < tongue:
                y += rng.uniform(12, 42)
            line.append((x, y))
        inner.append(el("path", d=P([(xs, -20), (xe, -20)] + line[::-1]), fill=snow_col))
    peaks = [i for i in range(1, len(r) - 1) if r[i][1] <= r[i - 1][1] and r[i][1] <= r[i + 1][1]]
    sig = [i for i in peaks if r[i][1] == min(p[1] for p in r[max(0, i - 5):i + 6])]
    for idx, i in enumerate(sig):
        nxt = sig[idx + 1] if idx + 1 < len(sig) else len(r) - 1
        j = max(range(i, nxt + 1), key=lambda k: r[k][1])
        if j <= i:
            continue
        px, py = r[i]
        vx, vy = r[j]
        foot = px + (base - py) * 0.32
        shadow = r[i:j + 1] + [(vx + (base - vy) * 0.18, base), (foot, base)]
        inner.append(el("path", d=P(shadow), fill=shade, opacity=shade_op))
    if gullies:
        segs = []
        for k in range(1, len(r) - 1, 2):
            if rng.random() < 0.45:
                continue
            x, y = r[k]
            length = rng.uniform(14, 70)
            segs.append(f"M{n(x)},{n(y + 3)} q{n(rng.uniform(-4, 4))},{n(length / 2)} {n(rng.uniform(-8, 12))},{n(length)}")
        if segs:
            inner.append(el("path", d=" ".join(segs), fill="none", stroke=shade, stroke_width=1.1, opacity=0.28))
    return [el("path", d=d, fill=fill), g(inner, clip_path=clip)], r


def hill(s: Scene, keys, base, fill, rough=6, depth=4):
    r = ridge(s.rng, keys, rough, depth)
    return el("path", d=smooth(r) + f" L{n(r[-1][0])},{n(base)} L{n(r[0][0])},{n(base)}Z", fill=fill), r


def sky(s: Scene, stops, h=None):
    s.add(el("rect", width=s.w, height=h or s.h, fill=s.linear("sky", stops)))


def sun(s: Scene, x, y, r, glow="#fff1c9"):
    s.add(el("circle", cx=x, cy=y, r=r * 5, fill=s.radial("sun", [(0, "#fffbe9", 0.95), (0.18, glow, 0.6), (1, glow, 0)])))
    s.add(el("circle", cx=x, cy=y, r=r, fill="#fffaf0"))


def cloud(rng, x, y, w, col="#ffffff", shade="#dfe7ef", op=0.95, cls="drift"):
    k = max(4, int(w / 22))
    puffs = []
    for i in range(k):
        t = i / (k - 1)
        r = w * (0.09 + 0.11 * math.sin(math.pi * t)) + rng.uniform(-3, 4)
        puffs.append(el("circle", cx=x + (t - 0.5) * w * 0.9, cy=y - r * 0.35, r=max(r, 4)))
    base = el("ellipse", cx=x, cy=y + w * 0.02, rx=w * 0.5, ry=w * 0.07, fill=shade)
    return g([base, g(puffs, fill=col)], opacity=op, class_=cls, style=f"animation-delay:{n(-rng.uniform(0, 14))}s")


def mist(s: Scene, x, y, rx, ry, op=0.55, col="#ffffff", blur="mist", cls="drift"):
    return el("ellipse", cx=x, cy=y, rx=rx, ry=ry, fill=col, opacity=op, filter=s.url(blur), class_=cls,
              style=f"animation-delay:{n(-s.rng.uniform(0, 16))}s")


# ==============================================================================
# VEGETATION PRIMITIVES
# ==============================================================================
def crown(rng, cx, cy, r, cols, k=7, flat=0.82):
    """Broadleaf crown built from shaded circle clusters (dark, mid, light)."""
    dark, mid, light = cols
    layers = ([], [], [])
    for _ in range(k):
        a, d = rng.uniform(0, TAU), rng.uniform(0, r * 0.55)
        layers[0].append(el("circle", cx=cx + math.cos(a) * d * 1.15, cy=cy + math.sin(a) * d * flat + r * 0.1,
                            r=r * rng.uniform(0.42, 0.6)))
    for _ in range(max(2, k - 2)):
        a, d = rng.uniform(0, TAU), rng.uniform(0, r * 0.45)
        layers[1].append(el("circle", cx=cx + math.cos(a) * d - r * 0.1, cy=cy + math.sin(a) * d * flat - r * 0.08,
                            r=r * rng.uniform(0.32, 0.46)))
    for _ in range(max(2, k // 3)):
        layers[2].append(el("circle", cx=cx - r * 0.28 + rng.uniform(-r * 0.22, r * 0.22),
                            cy=cy - r * 0.3 + rng.uniform(-r * 0.12, r * 0.12), r=r * rng.uniform(0.16, 0.28)))
    return g([g(layers[0], fill=dark), g(layers[1], fill=mid), g(layers[2], fill=light)])


def trunk(x, yb, yt, wb, wt, col, bend=0.0, buttress=False):
    d = (f"M{n(x - wb / 2)},{n(yb)} Q{n(x - wb / 2 + bend * 0.5)},{n((yb + yt) / 2)} {n(x - wt / 2 + bend)},{n(yt)} "
         f"L{n(x + wt / 2 + bend)},{n(yt)} Q{n(x + wb / 2 + bend * 0.5)},{n((yb + yt) / 2)} {n(x + wb / 2)},{n(yb)}Z")
    out = [el("path", d=d, fill=col)]
    if buttress:
        out.append(el("path", fill=col, d=(
            f"M{n(x - wb * 2.4)},{n(yb)} Q{n(x - wb * 0.7)},{n(yb - wb * 0.4)} {n(x - wb * 0.35)},{n(yb - wb * 3)} "
            f"L{n(x + wb * 0.35)},{n(yb - wb * 3)} Q{n(x + wb * 0.7)},{n(yb - wb * 0.4)} {n(x + wb * 2.4)},{n(yb)}Z")))
    return out


def broadleaf_tree(rng, x, yb, h, r, cols, trunk_col="#5b4632", flat=0.82, k=8, emergent=False):
    top = yb - h
    out = trunk(x, yb, top + r * 0.4, max(3, r * 0.2), max(2, r * 0.1), trunk_col, bend=rng.uniform(-r * 0.2, r * 0.2),
                buttress=emergent)
    if emergent:
        subs = [(-0.75, 0.15, 0.62), (0.75, 0.12, 0.6), (-0.2, -0.18, 0.7), (0.35, -0.12, 0.6)]
        branch = []
        for dx, dy, _ in subs:
            branch.append(f"M{n(x)},{n(top + r * 0.5)} Q{n(x + dx * r * 0.3)},{n(top + r * 0.2)} {n(x + dx * r)},{n(top + dy * r + r * 0.15)}")
        out.append(el("path", d=" ".join(branch), fill="none", stroke=trunk_col, stroke_width=max(2, r * 0.07),
                      stroke_linecap="round"))
        for dx, dy, sc in subs:
            out.append(crown(rng, x + dx * r, top + dy * r, r * sc, cols, k=k, flat=0.5))
    else:
        out.append(crown(rng, x, top, r, cols, k=k, flat=flat))
    return g(out)


def palm(rng, x, y, h, lean, L, cols=("#2f6a34", "#4b8a3f"), trunk_col="#8b6b4c", nfr=10, royal=False,
         coconuts=True, sway=True, wb=None):
    """Coconut or royal palm with curved trunk and leafleted fronds."""
    dark, light = cols
    tx, ty = x + lean, y - h
    ctrl = (x + lean * 0.15, y - h * 0.55)
    wb = wb or max(3.0, h * 0.045)
    wt = wb * (0.62 if royal else 0.72)
    left, right, rings = [], [], []
    steps = 16
    for i in range(steps + 1):
        t = i / steps
        bx, by = quad((x, y), ctrl, (tx, ty), t)
        w = wb * (1 - t) + wt * t
        if royal:
            w += wb * 0.35 * math.sin(math.pi * min(1, t * 1.6)) * (1 - t)
        left.append((bx - w / 2, by))
        right.append((bx + w / 2, by))
        if 0 < i < steps and (i % 2 == 0 or not royal):
            rings.append(f"M{n(bx - w / 2)},{n(by)} L{n(bx + w / 2)},{n(by + 0.8)}")
    out = [el("path", d=P(left + right[::-1]), fill=trunk_col)]
    out.append(el("path", d=" ".join(rings), stroke=mix(trunk_col, "#000000", 0.3), stroke_width=0.7, opacity=0.5,
                  fill="none"))
    # shaded side
    out.append(el("path", d=P([((a[0] + b[0]) / 2, a[1]) for a, b in zip(left, right)] + right[::-1]),
                  fill="#000000", opacity=0.14))
    if royal:
        cs = h * 0.13
        out.append(el("path", fill="#7aa24f", d=P([(tx - wt / 2, ty), (tx + wt / 2, ty), (tx + wt * 0.4, ty - cs),
                                                    (tx - wt * 0.4, ty - cs)])))
        ty -= cs
    fronds_back, fronds_front = [], []
    for i in range(nfr):
        a = math.radians(-195 + 210 * i / (nfr - 1) + rng.uniform(-8, 8))
        dx, dy = math.cos(a), math.sin(a)
        Lf = L * rng.uniform(0.82, 1.08)
        end = (tx + dx * Lf, ty + dy * Lf * 0.5 + Lf * 0.55 * (1 - abs(dy)) + (Lf * 0.25 if dy > 0 else 0))
        c = (tx + dx * Lf * 0.55, ty + dy * Lf * 0.55 - Lf * 0.16)
        segs = [f"M{n(tx)},{n(ty)} Q{n(c[0])},{n(c[1])} {n(end[0])},{n(end[1])}"]
        leaf = []
        for j in range(13):
            t = 0.1 + 0.88 * j / 12
            px, py = quad((tx, ty), c, end, t)
            ux, uy = quad_tan((tx, ty), c, end, t)
            nx_, ny_ = -uy, ux
            ln = Lf * 0.24 * math.sin(math.pi * min(1.0, 0.25 + t * 0.9))
            for side in (1, -1):
                leaf.append(f"M{n(px)},{n(py)} l{n(nx_ * side * ln + ux * ln * 0.35)},{n(ny_ * side * ln + ln * 0.55)}")
        frond = [el("path", d=" ".join(leaf), stroke=dark if i % 2 else light, stroke_width=1.5, fill="none",
                    stroke_linecap="round"),
                 el("path", d=segs[0], stroke=mix(dark, "#000000", 0.2), stroke_width=1.6, fill="none")]
        (fronds_back if i % 2 else fronds_front).extend(frond)
    crown_g = [g(fronds_back)]
    if coconuts and not royal:
        crown_g.append(g([el("circle", cx=tx + ox, cy=ty + 4 + oy, r=wb * 0.55) for ox, oy in
                          ((-wb * 0.5, 0), (wb * 0.6, 1), (0, wb * 0.7))], fill="#6b4a22"))
    crown_g.append(g(fronds_front))
    style = f"transform-origin:{n(tx)}px {n(ty)}px;animation-delay:{n(-rng.uniform(0, 6))}s"
    out.append(g(crown_g, class_="sway" if sway else None, style=style) if sway else g(crown_g))
    return g(out)


def tufts(rng, x0, x1, ground, count, h, col, width=1.1, op=1.0):
    segs = []
    for _ in range(count):
        x = rng.uniform(x0, x1)
        y = ground(x) + 1
        for _ in range(rng.randint(3, 6)):
            dx = rng.uniform(-h * 0.5, h * 0.5)
            hh = h * rng.uniform(0.5, 1.1)
            segs.append(f"M{n(x)},{n(y)} q{n(dx * 0.2)},{n(-hh * 0.6)} {n(dx)},{n(-hh)}")
    return el("path", d=" ".join(segs), stroke=col, stroke_width=width, fill="none", stroke_linecap="round", opacity=op)


def canopy_band(s: Scene, x0, x1, ground, count, rmin, rmax, cols, lift=0.0, flat=0.8, k=6):
    rng = s.rng
    trees = []
    for _ in range(count):
        x = rng.uniform(x0, x1)
        r = rng.uniform(rmin, rmax)
        trees.append((ground(x) - lift - r * 0.4 + rng.uniform(-r * 0.2, r * 0.2), x, r))
    trees.sort()
    return [crown(rng, x, y, r, cols, k=k, flat=flat) for y, x, r in trees]


def fern(rng, x, y, L, col, n_fronds=6, droop=0.5):
    segs = []
    for i in range(n_fronds):
        a = math.radians(-160 + 140 * i / max(1, n_fronds - 1) + rng.uniform(-6, 6))
        Lf = L * rng.uniform(0.75, 1.05)
        end = (x + math.cos(a) * Lf, y + math.sin(a) * Lf * 0.6 + Lf * droop * (1 - abs(math.sin(a))))
        c = (x + math.cos(a) * Lf * 0.5, y + math.sin(a) * Lf * 0.7 - Lf * 0.1)
        segs.append(f"M{n(x)},{n(y)} Q{n(c[0])},{n(c[1])} {n(end[0])},{n(end[1])}")
        for j in range(9):
            t = 0.15 + 0.8 * j / 8
            px, py = quad((x, y), c, end, t)
            ux, uy = quad_tan((x, y), c, end, t)
            ln = Lf * 0.13 * (1 - t * 0.6)
            for side in (1, -1):
                segs.append(f"M{n(px)},{n(py)} l{n(-uy * side * ln + ux * ln * 0.3)},{n(ux * side * ln + ln * 0.3)}")
    return el("path", d=" ".join(segs), stroke=col, stroke_width=1.2, fill="none", stroke_linecap="round")


def heliconia(x, y, h, stem="#3d6b2f", bract="#d8432c", tip="#f2c230"):
    out = [el("path", d=f"M{n(x)},{n(y)} q-3,{n(-h * 0.5)} 2,{n(-h)}", stroke=stem, stroke_width=2, fill="none")]
    bracts = []
    for i in range(5):
        by = y - h * 0.45 - i * h * 0.1
        side = 1 if i % 2 else -1
        bracts.append(f"M{n(x + 1)},{n(by)} l{n(side * 9)},{n(-3)} l{n(-side * 7)},{n(-4)}Z")
    out.append(el("path", d=" ".join(bracts), fill=bract))
    out.append(el("circle", cx=x + 2, cy=y - h, r=1.6, fill=tip))
    # broad leaves
    out.append(el("path", fill="#3f7a34", d=(
        f"M{n(x)},{n(y - h * 0.2)} q{n(-h * 0.45)},{n(-h * 0.25)} {n(-h * 0.6)},{n(-h * 0.05)} "
        f"q{n(h * 0.3)},{n(h * 0.12)} {n(h * 0.6)},{n(h * 0.05)}Z M{n(x)},{n(y - h * 0.3)} "
        f"q{n(h * 0.45)},{n(-h * 0.3)} {n(h * 0.62)},{n(-h * 0.12)} q{n(-h * 0.3)},{n(h * 0.15)} {n(-h * 0.62)},{n(h * 0.12)}Z")))
    return g(out)


def bromeliad(rng, x, y, s, col="#6e9a3a", flower="#e2543a"):
    segs = []
    for i in range(9):
        a = math.radians(-170 + 160 * i / 8)
        segs.append(f"M{n(x)},{n(y)} q{n(math.cos(a) * s * 0.5)},{n(math.sin(a) * s * 0.9)} {n(math.cos(a) * s)},{n(math.sin(a) * s * 0.55)}")
    return g([el("path", d=" ".join(segs), stroke=col, stroke_width=2.2, fill="none", stroke_linecap="round"),
              el("path", d=f"M{n(x - 2)},{n(y - 2)} L{n(x)},{n(y - s * 0.9)} L{n(x + 2)},{n(y - 2)}Z", fill=flower)])


def ipe(rng, x, y, h, bloom="#f2c12e", bloom2="#e0a516", trunk_col="#4b3a2c"):
    """Twisted cerrado tree with a flowering crown."""
    out = [el("path", d=f"M{n(x)},{n(y)} q{n(rng.uniform(-8, 8))},{n(-h * 0.4)} {n(rng.uniform(-6, 6))},{n(-h * 0.7)}",
              stroke=trunk_col, stroke_width=max(2.5, h * 0.06), fill="none", stroke_linecap="round")]
    tx, ty = x, y - h * 0.7
    br = []
    for dx in (-0.35, -0.1, 0.2, 0.4):
        br.append(f"M{n(tx)},{n(ty)} q{n(dx * h * 0.4)},{n(-h * 0.05)} {n(dx * h)},{n(-h * 0.22)}")
    out.append(el("path", d=" ".join(br), stroke=trunk_col, stroke_width=max(1.2, h * 0.025), fill="none",
                  stroke_linecap="round"))
    out.append(crown(rng, tx, ty - h * 0.18, h * 0.32, (bloom2, bloom, mix(bloom, "#ffffff", 0.45)), k=8, flat=0.55))
    return g(out)


def gnarled_tree(rng, x, y, h, leaf=("#3f5f2a", "#58793a", "#7c9a52"), trunk_col="#3d3026"):
    out = []
    tx = x + rng.uniform(-h * 0.15, h * 0.15)
    out.append(el("path", d=f"M{n(x)},{n(y)} C{n(x + h * 0.15)},{n(y - h * 0.3)} {n(tx - h * 0.2)},{n(y - h * 0.45)} {n(tx)},{n(y - h * 0.65)}",
                  stroke=trunk_col, stroke_width=max(2, h * 0.07), fill="none", stroke_linecap="round"))
    for dx, dy in ((-0.4, -0.85), (0.35, -0.9), (0.05, -1.0)):
        cx, cy = tx + dx * h, y + dy * h
        out.append(el("path", d=f"M{n(tx)},{n(y - h * 0.62)} Q{n(tx + dx * h * 0.3)},{n(y - h * 0.75)} {n(cx)},{n(cy)}",
                      stroke=trunk_col, stroke_width=max(1.2, h * 0.03), fill="none", stroke_linecap="round"))
        out.append(crown(rng, cx, cy, h * 0.18, leaf, k=4, flat=0.6))
    return g(out)


def cactus(x, y, h, col="#5f8a5a", rib="#41664a"):
    w = h * 0.12
    out = [el("rect", x=x - w / 2, y=y - h, width=w, height=h, rx=w / 2, fill=col)]
    arms = [(-1, 0.45, 0.35), (1, 0.6, 0.3), (-1, 0.75, 0.22)]
    for side, at, ah in arms:
        ay = y - h * at
        ax = x + side * w * 1.6
        out.append(el("path", d=f"M{n(x)},{n(ay)} L{n(ax)},{n(ay)} L{n(ax)},{n(ay - h * ah)}", stroke=col,
                      stroke_width=w * 0.8, fill="none", stroke_linecap="round", stroke_linejoin="round"))
    out.append(el("path", d=f"M{n(x - w * 0.15)},{n(y - h + w * 0.4)} L{n(x - w * 0.15)},{n(y)} M{n(x + w * 0.18)},{n(y - h + w * 0.4)} L{n(x + w * 0.18)},{n(y)}",
                  stroke=rib, stroke_width=0.8, opacity=0.6))
    return g(out)


def thorn_bush(rng, x, y, s, col="#9a8f78", leaf="#b5ae8a"):
    segs = []
    for _ in range(9):
        a = math.radians(rng.uniform(-170, -10))
        L = s * rng.uniform(0.5, 1)
        ex, ey = x + math.cos(a) * L, y + math.sin(a) * L * 0.8
        segs.append(f"M{n(x)},{n(y)} L{n(ex)},{n(ey)}")
        for _ in range(2):
            t = rng.uniform(0.4, 0.9)
            px, py = x + (ex - x) * t, y + (ey - y) * t
            segs.append(f"M{n(px)},{n(py)} l{n(rng.uniform(-s * 0.25, s * 0.25))},{n(-rng.uniform(2, s * 0.25))}")
    dots = [el("circle", cx=x + rng.uniform(-s * 0.8, s * 0.8), cy=y - rng.uniform(s * 0.2, s * 0.8), r=rng.uniform(1, 2.2))
            for _ in range(10)]
    return g([el("path", d=" ".join(segs), stroke=col, stroke_width=1, fill="none"), g(dots, fill=leaf, opacity=0.8)])


def termite_mound(x, y, h, col="#a8653a"):
    w = h * 0.55
    return g([
        el("path", d=f"M{n(x - w)},{n(y)} Q{n(x - w * 0.6)},{n(y - h * 0.6)} {n(x - w * 0.1)},{n(y - h)} Q{n(x + w * 0.25)},{n(y - h * 0.9)} {n(x + w * 0.4)},{n(y - h * 0.55)} Q{n(x + w * 0.7)},{n(y - h * 0.2)} {n(x + w)},{n(y)}Z", fill=col),
        el("path", d=f"M{n(x)},{n(y)} Q{n(x + w * 0.3)},{n(y - h * 0.5)} {n(x - w * 0.1)},{n(y - h)} Q{n(x + w * 0.25)},{n(y - h * 0.9)} {n(x + w * 0.4)},{n(y - h * 0.55)} Q{n(x + w * 0.7)},{n(y - h * 0.2)} {n(x + w)},{n(y)}Z", fill="#000000", opacity=0.18),
    ])


def water_lily(rng, x, y, r):
    notch = rng.uniform(0, TAU)
    return g([
        el("ellipse", cx=x, cy=y, rx=r, ry=r * 0.3, fill="#3e7a3a"),
        el("ellipse", cx=x, cy=y - 0.8, rx=r * 0.92, ry=r * 0.25, fill="#5f9a45"),
        el("ellipse", cx=x, cy=y, rx=r, ry=r * 0.3, fill="none", stroke="#9b3b3b", stroke_width=1.1, opacity=0.8),
        el("path", d=f"M{n(x)},{n(y)} L{n(x + math.cos(notch) * r)},{n(y + math.sin(notch) * r * 0.3)}", stroke="#2f5f2a",
           stroke_width=0.8),
    ])


def water_lines(rng, x0, x1, y0, y1, count, col="#ffffff", op=0.35, w=1.0):
    segs = []
    for _ in range(count):
        x = rng.uniform(x0, x1)
        y = rng.uniform(y0, y1)
        L = rng.uniform(8, 40) * (0.5 + (y - y0) / max(1, (y1 - y0)))
        segs.append(f"M{n(x)},{n(y)} h{n(L)}")
    return el("path", d=" ".join(segs), stroke=col, stroke_width=w, opacity=op, stroke_linecap="round", class_="shimmer")


def waterfall(s: Scene, x, y_top, y_bot, w, col="#f4fbff"):
    rng = s.rng
    strands = []
    for i in range(int(w / 3) + 3):
        sx = x + rng.uniform(-w / 2, w / 2)
        strands.append(f"M{n(sx)},{n(y_top)} C{n(sx + rng.uniform(-2, 2))},{n(y_top + 20)} {n(sx + rng.uniform(-3, 3))},{n(y_bot - 30)} {n(sx + rng.uniform(-6, 6))},{n(y_bot)}")
    out = [el("path", d=P([(x - w / 2, y_top), (x + w / 2, y_top), (x + w * 0.75, y_bot), (x - w * 0.75, y_bot)]), fill=col,
              opacity=0.55)]
    out.append(el("path", d=" ".join(strands), stroke="#ffffff", stroke_width=1.6, opacity=0.85, fill="none",
                  class_="flow", stroke_dasharray="14 8"))
    out.append(mist(s, x, y_bot, w * 1.3, w * 0.45, op=0.85, blur="mist"))
    return out


# ==============================================================================
# FAUNA PRIMITIVES
# ==============================================================================
def fish(x, y, s, body, fin=None, stripe=None, flip=False, tall=0.42):
    fin = fin or mix(body, "#000000", 0.2)
    sx = -1 if flip else 1
    parts = [
        el("path", d=f"M{n(-s)},0 Q{n(-s * 0.1)},{n(-s * tall * 1.15)} {n(s * 0.72)},0 Q{n(-s * 0.1)},{n(s * tall * 1.15)} {n(-s)},0Z", fill=body),
        el("path", d=f"M{n(s * 0.62)},0 L{n(s * 1.18)},{n(-s * 0.38)} L{n(s * 1.05)},0 L{n(s * 1.18)},{n(s * 0.38)}Z", fill=fin),
        el("circle", cx=-s * 0.62, cy=-s * 0.08, r=max(0.6, s * 0.08), fill="#10202e"),
    ]
    if stripe:
        parts.insert(1, el("path", d=f"M{n(-s * 0.8)},{n(s * 0.04)} Q{n(0)},{n(-s * 0.06)} {n(s * 1.05)},0", stroke=stripe,
                           stroke_width=max(0.8, s * 0.14), fill="none"))
    return g(parts, transform=f"translate({n(x)} {n(y)}) scale({sx} 1)")


def school(rng, cx, cy, count, spread, s, body, stripe=None, flip=False, cls="swim"):
    fishes = [fish(cx + rng.uniform(-spread, spread), cy + rng.uniform(-spread * 0.35, spread * 0.35), s * rng.uniform(0.8, 1.1),
                   body, stripe=stripe, flip=flip) for _ in range(count)]
    return g(fishes, class_=cls, style=f"animation-delay:{n(-rng.uniform(0, 10))}s")


def turtle(x, y, s, flip=False):
    sx = -1 if flip else 1
    return g([
        el("path", d="M-6,-4 Q-20,-18 -30,-14 Q-18,-8 -8,0Z M-6,4 Q-18,16 -26,14 Q-16,8 -8,1Z M14,-3 Q20,-10 24,-9 Q20,-4 16,0Z M14,3 Q19,9 22,8 Q19,4 15,0Z", fill="#6f7f4a"),
        el("ellipse", cx=2, cy=0, rx=17, ry=11, fill="#7a6a3c"),
        el("path", d="M-8,-6 L2,-9 L12,-6 M-10,0 L14,0 M-8,6 L2,9 L12,6 M2,-9 L2,9", stroke="#4e4325", stroke_width=1, fill="none"),
        el("ellipse", cx=23, cy=0, rx=6, ry=4.5, fill="#7f8b55"),
        el("circle", cx=25.5, cy=-1.2, r=0.9, fill="#111111"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def manta(x, y, s):
    return g([
        el("path", d="M0,0 C-12,-4 -30,-22 -56,-14 C-38,-6 -20,4 -6,10 L-2,30 L2,30 L6,10 C20,4 38,-6 56,-14 C30,-22 12,-4 0,0Z", fill="#26394f"),
        el("path", d="M-6,2 C-2,0 2,0 6,2 C3,5 -3,5 -6,2Z", fill="#d9e3ea", opacity=0.6),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})")


def macaw(x, y, s, flip=False, palette=("#d22b2b", "#2f62b4", "#f2c230")):
    red, blue, yellow = palette
    sx = -1 if flip else 1
    return g([
        el("path", d="M-2,2 Q-6,16 -20,22 Q-10,10 6,3Z", fill=mix(blue, "#000000", 0.25)),
        el("path", d="M-12,1 L-46,9 L-44,12 L-11,4Z", fill=red),
        el("path", d="M-22,5 L-44,10", stroke=blue, stroke_width=1.4),
        el("ellipse", cx=0, cy=0, rx=14, ry=5, fill=red),
        el("path", d="M-2,-2 Q-8,-22 -26,-30 Q-14,-16 6,-3Z", fill=blue),
        el("path", d="M-2,-2 Q-5,-11 -12,-16 Q-6,-8 4,-2Z", fill=yellow),
        el("circle", cx=14, cy=-2, r=5, fill=red),
        el("circle", cx=15.5, cy=-3, r=2, fill="#f4efe6"),
        el("path", d="M18,-4 Q24,-2 19,3Z", fill="#e8e2d0"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})", class_="fly")


def toucan(x, y, s):
    return g([
        el("path", d="M0,0 Q-4,14 -2,26 L4,26 Q8,12 6,0Z", fill="#141414"),
        el("ellipse", cx=3, cy=4, rx=6, ry=9, fill="#141414"),
        el("ellipse", cx=5, cy=-1, rx=4, ry=4.5, fill="#f6efd8"),
        el("path", d="M7,-4 Q24,-6 27,2 Q18,2 7,2Z", fill="#f08c1c"),
        el("path", d="M7,-4 Q16,-5 20,-3 L7,-1Z", fill="#f6d33a"),
        el("circle", cx=5, cy=-3.5, r=1.3, fill="#2a6fd1"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})")


def condor(x, y, s, cls="fly"):
    return g([
        el("path", d="M0,0 Q-20,-7 -40,-5 L-53,-3 L-48,-1 L-55,1 L-48,2.5 L-53,5 L-40,5 Q-20,4 -6,6 L0,9 L6,6 Q20,4 40,5 L53,5 L48,2.5 L55,1 L48,-1 L53,-3 L40,-5 Q20,-7 0,0Z", fill="#1b1c22"),
        el("path", d="M-34,-1 Q-20,-3 -8,0 M34,-1 Q20,-3 8,0", stroke="#dadada", stroke_width=2, fill="none", opacity=0.8),
        el("circle", cx=0, cy=-1, r=2.6, fill="#f2f2f2"),
        el("circle", cx=0, cy=-3.5, r=2, fill="#a3554a"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})", class_=cls)


def bird_v(x, y, s, col="#2b3440"):
    return el("path", d=f"M{n(x - s)},{n(y - s * 0.3)} Q{n(x - s * 0.4)},{n(y - s * 0.55)} {n(x)},{n(y)} Q{n(x + s * 0.4)},{n(y - s * 0.55)} {n(x + s)},{n(y - s * 0.3)}",
              stroke=col, stroke_width=1.3, fill="none", stroke_linecap="round")


def flamingo(x, y, s, flip=False):
    sx = -1 if flip else 1
    return g([
        el("path", d="M2,0 L3,30 M-2,0 L-1,16 L4,22", stroke="#d77b80", stroke_width=1.2, fill="none"),
        el("ellipse", cx=0, cy=-4, rx=10, ry=6, fill="#f08a8f"),
        el("path", d="M-8,-6 Q-12,-8 -14,-4 Q-10,-4 -8,-2Z", fill="#d75f68"),
        el("path", d="M8,-6 Q14,-14 8,-22 Q2,-30 8,-34", stroke="#f08a8f", stroke_width=2.6, fill="none", stroke_linecap="round"),
        el("circle", cx=9, cy=-34, r=2.6, fill="#f08a8f"),
        el("path", d="M11,-34 Q15,-33 14,-29 L12,-31Z", fill="#1d1d1d"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def jabiru(x, y, s):
    return g([
        el("path", d="M-2,0 L-3,26 M3,0 L4,26", stroke="#111111", stroke_width=1.4),
        el("ellipse", cx=0, cy=-6, rx=11, ry=8, fill="#f7f7f2"),
        el("path", d="M6,-10 Q10,-22 8,-32", stroke="#121212", stroke_width=4, fill="none", stroke_linecap="round"),
        el("path", d="M5,-12 Q8,-14 10,-12", stroke="#d23a2e", stroke_width=3, fill="none"),
        el("path", d="M8,-33 L22,-26 L8,-30Z", fill="#121212"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})")


def egret(x, y, s, flip=False):
    sx = -1 if flip else 1
    return g([
        el("path", d="M0,0 L-1,20 M3,0 L4,20", stroke="#222222", stroke_width=1),
        el("ellipse", cx=0, cy=-4, rx=8, ry=4.5, fill="#ffffff"),
        el("path", d="M6,-6 Q11,-14 6,-20 Q4,-24 8,-26", stroke="#ffffff", stroke_width=2, fill="none", stroke_linecap="round"),
        el("path", d="M9,-26 L17,-24 L9,-25Z", fill="#e3b33c"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def capybara(x, y, s, flip=False):
    sx = -1 if flip else 1
    return g([
        el("path", d="M-14,0 Q-16,-12 -4,-13 Q8,-14 12,-8 Q18,-9 20,-4 Q20,0 14,0Z", fill="#8a5a36"),
        el("path", d="M-10,0 L-10,4 M10,0 L10,4", stroke="#5f3c22", stroke_width=2.4),
        el("circle", cx=15, cy=-7, r=0.9, fill="#1a1a1a"),
        el("ellipse", cx=12, cy=-11, rx=1.6, ry=1.2, fill="#6e4528"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def caiman(x, y, s, flip=False):
    sx = -1 if flip else 1
    return g([
        el("path", d="M-30,0 Q-10,-4 10,-3 Q20,-3 28,0 Q10,2 -30,0Z", fill="#3b3f2a"),
        el("path", d="M-24,-1 L-20,-3 L-16,-1 M-12,-2 L-8,-4 L-4,-2 M0,-2 L4,-4 L8,-2", stroke="#2a2d1e", stroke_width=1.2, fill="none"),
        el("circle", cx=16, cy=-3.5, r=1.6, fill="#4a4e34"),
        el("circle", cx=16, cy=-3.8, r=0.6, fill="#e6c34a"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def dolphin(x, y, s):
    return g([
        el("path", d="M-20,0 Q-6,-14 14,-4 Q20,-2 24,0 Q12,-2 6,-1 Q-6,-4 -20,0Z", fill="#e7a0a8"),
        el("path", d="M2,-8 Q4,-12 8,-12 Q6,-9 6,-6Z", fill="#d98d96"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})", class_="bob")


def maned_wolf(x, y, s, flip=False):
    sx = -1 if flip else 1
    return g([
        el("path", d="M-12,-14 L-14,6 M-8,-14 L-9,6 M8,-14 L9,6 M12,-14 L13,6", stroke="#1d1712", stroke_width=2),
        el("path", d="M-16,-14 Q-16,-22 -6,-22 L10,-22 Q16,-22 16,-15 Q14,-12 10,-12 L-12,-12 Q-16,-12 -16,-14Z", fill="#c46a2a"),
        el("path", d="M-16,-18 Q-24,-16 -26,-6 Q-20,-12 -16,-14Z", fill="#c46a2a"),
        el("path", d="M10,-22 Q16,-28 20,-30 L26,-28 Q24,-24 18,-22 Q15,-18 12,-16Z", fill="#c46a2a"),
        el("path", d="M10,-22 Q14,-26 18,-28 L16,-22Z", fill="#1d1712"),
        el("path", d="M18,-30 L18,-37 L21,-31 M21,-30 L23,-36 L23,-30", stroke="#c46a2a", stroke_width=2, fill="none"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def iguana(x, y, s):
    return g([
        el("path", d="M-30,2 Q-10,4 -4,0 Q4,-6 14,-4 Q20,-4 22,0 Q14,2 4,2 Q-6,6 -30,2Z", fill="#7d7a5a"),
        el("path", d="M-2,-2 L0,-6 L2,-3 L4,-7 L6,-4 L8,-7 L10,-4", stroke="#6a6648", stroke_width=1, fill="none"),
        el("path", d="M0,2 L-3,6 M10,1 L12,5", stroke="#6a6648", stroke_width=1.6),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})")


def morpho(x, y, s):
    return g([
        el("ellipse", cx=-3, cy=0, rx=4, ry=3, fill="#1f7fe0", transform="rotate(-25)"),
        el("ellipse", cx=3, cy=0, rx=4, ry=3, fill="#3da0ff", transform="rotate(25)"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})", class_="fly")


def hummingbird(x, y, s):
    return g([
        el("ellipse", cx=0, cy=0, rx=5, ry=2.4, fill="#1f8a6a"),
        el("path", d="M4,-1 L12,-2", stroke="#202020", stroke_width=0.8),
        el("path", d="M-1,-1 Q-6,-9 -10,-8 Q-6,-4 -2,0Z", fill="#7cc8b2", opacity=0.8),
        el("path", d="M-5,0 L-10,3 L-9,0Z", fill="#13604a"),
        el("circle", cx=3, cy=-0.8, r=1.2, fill="#d43b6a"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})", class_="fly")


# ==============================================================================
# REEF PRIMITIVES
# ==============================================================================
def branch_coral(rng, x, y, L, depth, col, width, spread=0.55, up=-math.pi / 2):
    segs = []

    def rec(px, py, ang, ln, d):
        ex, ey = px + math.cos(ang) * ln, py + math.sin(ang) * ln
        segs.append(f"M{n(px)},{n(py)} L{n(ex)},{n(ey)}")
        if d > 0:
            for k in (-1, 1):
                rec(ex, ey, ang + k * spread * rng.uniform(0.5, 1.1), ln * rng.uniform(0.62, 0.82), d - 1)

    for k in range(3):
        rec(x + (k - 1) * width, y, up + (k - 1) * 0.45 + rng.uniform(-0.1, 0.1), L * rng.uniform(0.8, 1), depth)
    d = " ".join(segs)
    return g([
        el("path", d=d, stroke=mix(col, "#000000", 0.25), stroke_width=width + 1.4, fill="none", stroke_linecap="round"),
        el("path", d=d, stroke=col, stroke_width=width, fill="none", stroke_linecap="round"),
    ])


def brain_coral(rng, x, y, r, col="#c9a24a"):
    lines = []
    for i in range(1, 5):
        rr = r * i / 5
        pts = []
        for j in range(15):
            a = math.pi + math.pi * j / 14
            wob = rr + rng.uniform(-r * 0.04, r * 0.04)
            pts.append((x + math.cos(a) * wob, y + math.sin(a) * wob * 0.75))
        lines.append(smooth(pts))
    return g([
        el("path", d=f"M{n(x - r)},{n(y)} A{n(r)},{n(r * 0.75)} 0 0 1 {n(x + r)},{n(y)}Z", fill=col),
        el("path", d=f"M{n(x - r)},{n(y)} A{n(r)},{n(r * 0.75)} 0 0 1 {n(x + r)},{n(y)}Z", fill="#000000", opacity=0.12,
           transform=f"translate({n(r * 0.25)} 0) scale(0.75 1)", style=f"transform-origin:{n(x)}px {n(y)}px"),
        el("path", d=" ".join(lines), stroke=mix(col, "#000000", 0.3), stroke_width=1, fill="none", opacity=0.7),
    ])


def sea_fan(rng, x, y, h, col="#8b4fa8"):
    segs = []
    for i in range(14):
        a = math.radians(-150 + 120 * i / 13)
        L = h * rng.uniform(0.7, 1)
        ex, ey = x + math.cos(a) * L * 0.8, y + math.sin(a) * L
        segs.append(f"M{n(x)},{n(y)} Q{n(x + math.cos(a) * L * 0.3)},{n(y + math.sin(a) * L * 0.6)} {n(ex)},{n(ey)}")
    fan = el("path", d=f"M{n(x)},{n(y)} Q{n(x - h * 0.9)},{n(y - h * 0.8)} {n(x - h * 0.2)},{n(y - h)} Q{n(x + h * 0.4)},{n(y - h * 1.05)} {n(x + h * 0.75)},{n(y - h * 0.5)}Z",
             fill=col, opacity=0.35)
    return g([fan, el("path", d=" ".join(segs), stroke=col, stroke_width=1, fill="none", opacity=0.9)],
             class_="sway", style=f"transform-origin:{n(x)}px {n(y)}px;animation-delay:{n(-rng.uniform(0, 5))}s")


def tube_sponge(x, y, h, col="#b05fb8"):
    out = []
    for dx, hh in ((-6, 1), (0, 1.25), (6, 0.85)):
        out.append(el("rect", x=x + dx - 3.5, y=y - h * hh, width=7, height=h * hh, rx=3.5, fill=col))
        out.append(el("ellipse", cx=x + dx, cy=y - h * hh + 2, rx=2.5, ry=1.2, fill=mix(col, "#000000", 0.4)))
    return g(out)


def seagrass(rng, x0, x1, y, count, h, col="#5f9a4a"):
    segs = []
    for _ in range(count):
        x = rng.uniform(x0, x1)
        hh = h * rng.uniform(0.5, 1.1)
        segs.append(f"M{n(x)},{n(y)} q{n(rng.uniform(-6, 6))},{n(-hh * 0.5)} {n(rng.uniform(-8, 8))},{n(-hh)}")
    return el("path", d=" ".join(segs), stroke=col, stroke_width=1.8, fill="none", stroke_linecap="round", class_="sway",
              style=f"transform-origin:{n((x0 + x1) / 2)}px {n(y)}px")


def light_rays(s: Scene, x0, x1, y0, y1, count, op=0.16):
    rng = s.rng
    grad = s.linear("ray", [(0, "#ffffff", op), (1, "#ffffff", 0)])
    rays = []
    for _ in range(count):
        x = rng.uniform(x0, x1)
        w = rng.uniform(14, 46)
        sk = rng.uniform(40, 110)
        rays.append(el("path", d=P([(x, y0), (x + w, y0), (x + w + sk * 1.4, y1), (x + sk, y1)])))
    return g(rays, fill=grad, class_="shimmer")


# ==============================================================================
# SCENE: SEA-TO-SUMMIT TRANSECT
# ==============================================================================
def build_transect(labels):
    s = Scene("transect", 1600, 600, 1999)
    rng = s.rng
    W, H = s.w, s.h
    s.blur("mist", 9)
    s.blur("soft", 3)
    sky(s, [(0, "#8fc1e6"), (0.55, "#d6ebf5"), (1, "#f6efe1")])
    sun(s, 1180, 92, 26)
    for cx, cy, w in ((170, 90, 160), (560, 70, 130), (900, 120, 190), (1360, 60, 150)):
        s.add(cloud(rng, cx, cy, w))
    # distant range across the right half
    far, _ = mountain(s, "far", [(700, 330), (820, 270), (930, 300), (1060, 230), (1180, 280), (1290, 190), (1420, 150), (1500, 170), (1600, 140)],
                      420, "#a9bfd3", shade="#6f86a0", shade_op=0.3, snow=215, rough=10)
    s.add(far)
    # terrain profile
    keys = [(0, 410), (200, 405), (250, 392), (330, 382), (380, 360), (430, 300), (455, 300), (470, 360), (520, 290), (548, 292), (565, 360),
            (640, 372), (860, 384), (900, 392), (1040, 392), (1100, 372), (1220, 352), (1260, 300), (1300, 300), (1330, 330), (1390, 310),
            (1600, 330)]
    terrain = interp(keys)
    # Andes massif on the right
    andes, aridge = mountain(s, "andes", [(1330, 340), (1390, 240), (1440, 150), (1475, 100), (1510, 150), (1545, 120), (1600, 170)], 470,
                             "#7f6b5a", shade="#2a2633", shade_op=0.4, snow=165, rough=9)
    s.add(andes)
    s.add(mist(s, 1450, 250, 140, 18, op=0.7))
    # sea (left)
    sea_top = 412
    s.add(el("rect", x=0, y=sea_top, width=330, height=H - sea_top, fill=s.linear("sea", [(0, "#2aa6c4"), (0.5, "#16759c"), (1, "#0c3e63")])))
    s.add(light_rays(s, 0, 280, sea_top, H, 7, op=0.18))
    # reef on sea floor
    floor = [(0, 560), (60, 548), (140, 556), (220, 540), (300, 520), (330, 470)]
    s.add(el("path", d=smooth(floor) + f" L330,{H} L0,{H}Z", fill="#d9c79a"))
    for x, c in ((30, "#e07a5f"), (90, "#c9a24a"), (150, "#e6b35a"), (210, "#d46a8a"), (270, "#e07a5f")):
        s.add(branch_coral(rng, x, 552, 16, 3, c, 2.6))
    s.add(brain_coral(rng, 120, 553, 13), brain_coral(rng, 245, 540, 11, "#b98f3e"))
    s.add(sea_fan(rng, 60, 552, 26), sea_fan(rng, 185, 548, 22, "#a8559a"))
    s.add(school(rng, 120, 480, 9, 30, 4, "#3aa6e0", stripe="#f2d23a"))
    s.add(school(rng, 230, 505, 6, 22, 5, "#f2c230", flip=True))
    s.add(turtle(70, 460, 0.7))
    s.add(water_lines(rng, 0, 320, sea_top + 2, sea_top + 18, 26, op=0.5))
    # land body
    land = [(330, 470)] + [(x, terrain(x)) for x in range(330, 1601, 10)]
    s.add(el("path", d=smooth(land) + f" L1600,{H} L330,{H}Z", fill=s.linear("land", [(0, "#8a6a46"), (1, "#5b4430")])))
    # cross-section soil strata
    strata = []
    for k, col in enumerate(("#6e5238", "#5f4632", "#51392a")):
        pts = [(x, terrain(x) + 40 + k * 45 + 6 * math.sin(x / 60 + k)) for x in range(330, 1601, 20)]
        strata.append(el("path", d=smooth(pts) + f" L1600,{H} L330,{H}Z", fill=col))
    s.add(g(strata, opacity=0.9))
    # zone 1: beach and mangroves (330-420)
    s.add(el("path", d=smooth([(318, 414), (360, 404), (400, 396), (430, 392)]) + " L430,420 L318,420Z", fill="#efe0b6"))
    for x in (338, 352, 366):
        y = terrain(x)
        roots = " ".join(f"M{n(x)},{n(y - 18)} Q{n(x + d * 0.6)},{n(y - 10)} {n(x + d)},{n(y + 8)}" for d in (-12, -6, 0, 6, 12))
        s.add(el("path", d=roots, stroke="#5b4a35", stroke_width=1.6, fill="none"))
        s.add(crown(rng, x, y - 26, 14, ("#2e5e33", "#3f7a3c", "#62994c"), k=6, flat=0.6))
    for x, h, lean in ((392, 70, 10), (408, 58, -8)):
        s.add(palm(rng, x, terrain(x) + 2, h, lean, 26, nfr=9))
    # zone 2: mogotes karst (430-560)
    for keys_m in ([(430, 384), (432, 312), (446, 296), (462, 300), (470, 384)], [(505, 384), (510, 300), (530, 286), (548, 292), (560, 384)]):
        d = smooth(keys_m)
        s.add(el("path", d=d + "Z", fill="#557e3c"))
        cid = s.clip(f"mog{keys_m[0][0]}", d + "Z")
        cliffs = " ".join(f"M{n(x)},{n(rng.uniform(300, 320))} l{n(rng.uniform(-1, 1))},{n(rng.uniform(20, 60))}"
                          for x in [rng.uniform(keys_m[0][0], keys_m[-1][0]) for _ in range(10)])
        s.add(g([el("path", d=cliffs, stroke="#a4a597", stroke_width=2.2, opacity=0.65, fill="none")], clip_path=cid))
        for _ in range(9):
            x = rng.uniform(keys_m[1][0] + 2, keys_m[-2][0] + 2)
            s.add(crown(rng, x, rng.uniform(292, 304), 6, ("#2f5a2c", "#4b7a36", "#78a24e"), k=4))
    # tobacco valley rows between mogotes
    rows = " ".join(f"M{n(472 + i * 5)},380 l2,4" for i in range(7))
    s.add(el("path", d=rows, stroke="#7fae4a", stroke_width=3, stroke_linecap="round"))
    s.add(el("path", d="M478,378 L486,368 L494,378Z", fill="#9a7a4a"))
    s.add(palm(rng, 498, 381, 48, 2, 16, royal=True, nfr=9, trunk_col="#cfc7b6"))
    # zone 3: Amazon rainforest (565-860) with river
    s.add(g(canopy_band(s, 565, 860, terrain, 26, 14, 22, ("#1e4a2a", "#2d6a35", "#4f8f45"), lift=6, k=6)))
    s.add(g(canopy_band(s, 570, 855, terrain, 18, 16, 24, ("#245530", "#3a7a3c", "#68a64e"), lift=0, k=6)))
    s.add(broadleaf_tree(rng, 640, terrain(640), 92, 30, ("#244f2b", "#3b7a3a", "#73ad52"), emergent=True))
    s.add(broadleaf_tree(rng, 790, terrain(790), 84, 26, ("#2a5a30", "#438440", "#7ab558"), emergent=True))
    s.add(el("path", d=smooth([(690, 383), (720, 381), (760, 384), (800, 386)]) + " L800,392 L690,392Z", fill="#7a6a3e"))
    s.add(macaw(700, 270, 0.55), macaw(740, 255, 0.5, flip=True))
    s.add(mist(s, 710, 330, 120, 14, op=0.55))
    # zone 4: Pantanal wetland (860-1040)
    s.add(el("path", d=smooth([(860, 386), (900, 389), (960, 390), (1040, 388)]) + " L1040,400 L860,400Z", fill="#5a8ea8"))
    s.add(water_lines(rng, 866, 1034, 389, 398, 14, op=0.5))
    s.add(tufts(rng, 860, 1040, lambda x: 389, 22, 9, "#7c9a44"))
    for x in (880, 1010):
        s.add(palm(rng, x, 390, 46, rng.uniform(-4, 4), 14, nfr=8, coconuts=False, trunk_col="#6c5a46"))
    s.add(jabiru(945, 384, 0.55), caiman(990, 393, 0.5), capybara(915, 389, 0.55))
    # zone 5: Cerrado (1040-1220)
    s.add(tufts(rng, 1040, 1220, terrain, 50, 10, "#b9a24e"))
    for x in (1065, 1120, 1190):
        s.add(gnarled_tree(rng, x, terrain(x), 40))
    s.add(ipe(rng, 1150, terrain(1150), 46))
    s.add(termite_mound(1095, terrain(1095), 16), termite_mound(1210, terrain(1210), 12))
    s.add(maned_wolf(1170, terrain(1170) - 5, 0.55))
    # zone 6: Atlantic forest cliff and cataract (1220-1330)
    cliff = [(1220, 352), (1240, 330), (1258, 300), (1300, 298), (1312, 312), (1330, 330)]
    s.add(g(canopy_band(s, 1222, 1330, interp(cliff), 14, 9, 14, ("#1f4d2c", "#2f6d37", "#5c9a4a"), k=5)))
    s.add(waterfall(s, 1280, 300, 352, 12))
    s.add(el("ellipse", cx=1280, cy=354, rx=26, ry=5, fill="#6cb3cc"))
    # cloud forest band and condor
    s.add(mist(s, 1400, 300, 110, 16, op=0.75))
    s.add(condor(1420, 120, 0.7))
    # labels
    lab = []
    zones = [(165, 0), (375, 1), (500, 2), (712, 3), (950, 4), (1130, 5), (1280, 6), (1480, 7)]
    for (x, idx) in zones:
        txt = labels["transect"][idx]
        w = len(txt) * 6.4 + 22
        lab.append(g([
            el("rect", x=x - w / 2, y=H - 46, width=w, height=24, rx=12, fill="#001830", opacity=0.82),
            el("text", txt, x=x, y=H - 30, text_anchor="middle", fill="#fbf7f0", font_family="Manrope, sans-serif",
               font_size=11, font_weight=700, letter_spacing="0.08em"),
        ]))
        lab.append(el("path", d=f"M{n(x)},{n(H - 46)} L{n(x)},{n(H - 62)}", stroke="#001830", stroke_width=1, opacity=0.5))
    s.add(g(lab))
    return s.render(labels["aria"]["transect"])


# ==============================================================================
# SCENE: CORAL REEF AND MANGROVE COAST (SPLIT LEVEL)
# ==============================================================================
def build_reef(labels):
    s = Scene("reef", 1200, 720, 2021)
    rng = s.rng
    W, H = s.w, s.h
    WL = 210  # water line
    s.blur("mist", 8)
    s.blur("soft", 2.5)
    sky(s, [(0, "#7fbbe3"), (1, "#e3f1f7")], h=WL + 2)
    sun(s, 980, 70, 22)
    s.add(cloud(rng, 260, 70, 170), cloud(rng, 700, 50, 120))
    # distant cay with palms
    s.add(el("path", d=smooth([(780, WL), (840, WL - 14), (930, WL - 20), (1010, WL - 10), (1060, WL)]) + "Z", fill="#e9dcb2"))
    for x, h, lean in ((870, 64, 8), (900, 80, -6), (940, 70, 10), (985, 56, -8)):
        s.add(palm(rng, x, WL - 14, h * 0.8, lean, 22, nfr=9))
    # mangrove island on the left
    mg_ground = WL - 4
    for x in range(-10, 420, 34):
        cx = x + rng.uniform(-6, 6)
        cy = WL - rng.uniform(70, 100)
        roots = []
        for d in (-34, -22, -10, 4, 18, 30):
            roots.append(f"M{n(cx + d * 0.25)},{n(cy + 20)} Q{n(cx + d * 0.8)},{n(WL - 30)} {n(cx + d)},{n(WL + rng.uniform(40, 120))}")
        s.add(el("path", d=" ".join(roots), stroke="#4d3d2c", stroke_width=2.2, fill="none"))
    s.add(g(canopy_band(s, -20, 440, lambda x: WL - 70, 22, 26, 40, ("#244f2c", "#356e38", "#5f9b4a"), flat=0.55, k=7)))
    s.add(egret(250, WL - 108, 0.9), egret(120, WL - 96, 0.8, flip=True))
    s.add(g([bird_v(560, 90, 9), bird_v(590, 80, 7), bird_v(620, 96, 8)], class_="drift"))
    # water body
    s.add(el("rect", x=0, y=WL, width=W, height=H - WL, fill=s.linear("water", [(0, "#38b8cf"), (0.35, "#1b8db3"), (0.75, "#0f5f8a"), (1, "#0a3f63")])))
    surf = [(x, WL + 3 * math.sin(x / 26)) for x in range(0, W + 1, 20)]
    s.add(el("path", d=smooth(surf) + f" L{W},{WL - 4} L0,{WL - 4}Z", fill="#9fe0ea", opacity=0.7))
    s.add(water_lines(rng, 0, W, WL + 4, WL + 40, 60, op=0.45))
    s.add(light_rays(s, 380, 1150, WL, H - 60, 12))
    # caustic net near surface
    caust = " ".join(f"M{n(x)},{n(WL + 20 + rng.uniform(0, 40))} q10,-6 20,0 t20,0" for x in range(420, W, 46))
    s.add(el("path", d=caust, stroke="#bdf2f7", stroke_width=1, fill="none", opacity=0.35, class_="shimmer"))
    # mangrove nursery: roots underwater with juvenile fish
    s.add(g([el("ellipse", cx=200, cy=WL + 90, rx=230, ry=60, fill="#0b4a5c", opacity=0.25, filter=s.url("mist"))]))
    s.add(school(rng, 180, WL + 70, 14, 60, 4, "#c8d6dc", stripe="#f0d24a"))
    s.add(school(rng, 300, WL + 120, 8, 40, 4.5, "#f2c230", stripe="#1d2a36", flip=True))
    # sea floor
    floor = [(0, 600), (150, 610), (330, 590), (520, 560), (700, 575), (880, 545), (1050, 560), (1200, 540)]
    fl = interp(floor)
    s.add(el("path", d=smooth(floor) + f" L{W},{H} L0,{H}Z", fill=s.linear("sand", [(0, "#e4d3a6"), (1, "#bfa877")])))
    ripples = " ".join(f"M{n(x)},{n(fl(x) + 20 + (x * 7) % 60)} q12,-4 24,0" for x in range(10, W, 34))
    s.add(el("path", d=ripples, stroke="#a99363", stroke_width=1, fill="none", opacity=0.5))
    s.add(seagrass(rng, 0, 330, 640, 120, 34, "#5d9b46"))
    s.add(seagrass(rng, 40, 300, 660, 80, 26, "#78b052"))
    # reef structure
    reef = [(400, 720), (430, 600), (480, 560), (560, 540), (640, 552), (700, 530), (780, 520), (860, 500), (940, 512), (1020, 490), (1120, 505),
            (1200, 495), (1200, 720)]
    s.add(el("path", d=smooth(reef[:-1]) + " L1200,720Z", fill="#8a7b6a"))
    rf = interp(reef[1:-1])
    # corals
    coral_cols = ["#e07a5f", "#e6b35a", "#d46a8a", "#c9a24a", "#f08a5d", "#9b6fc4", "#e2c67a"]
    for i, x in enumerate(range(440, 1200, 46)):
        y = rf(x) + 6
        kind = i % 5
        c = coral_cols[(i * 3) % len(coral_cols)]
        if kind == 0:
            s.add(branch_coral(rng, x, y, 26, 3, c, 3.4))
        elif kind == 1:
            s.add(brain_coral(rng, x, y, 24, c))
        elif kind == 2:
            s.add(sea_fan(rng, x, y, 48, "#9a55b5" if i % 2 else "#c4508a"))
        elif kind == 3:
            s.add(tube_sponge(x, y, 30, "#b05fb8" if i % 2 else "#e38a3a"))
        else:
            s.add(branch_coral(rng, x, y, 34, 3, "#d8a24a", 5, spread=0.9, up=-math.pi / 2))
    for x in range(470, 1200, 64):
        s.add(brain_coral(rng, x + 20, rf(x + 20) + 30, 16, "#b98f3e"))
        s.add(el("circle", cx=x + 6, cy=rf(x) + 36, r=7, fill="#e2543a", opacity=0.9))
    # fauna
    s.add(manta(820, 300, 1.4))
    s.add(turtle(560, 380, 1.3))
    s.add(school(rng, 960, 420, 18, 70, 6, "#3a7fd6", stripe="#1d3b7a"))
    s.add(school(rng, 700, 460, 10, 40, 6.5, "#f2d23a", stripe="#16212d", flip=True))
    for x, y, c, st in ((640, 470, "#2bb7a9", "#e86fa0"), (1040, 450, "#f28a3a", None), (900, 470, "#5ac8e6", None), (520, 500, "#e7c63a", "#3a7ad6")):
        s.add(g(fish(x, y, 11, c, stripe=st, flip=rng.random() < 0.5), class_="swim"))
    s.add(g([el("circle", cx=560 + rng.uniform(-10, 10), cy=360 - i * 18, r=rng.uniform(1.5, 3.5), fill="none",
                stroke="#e8fbff", stroke_width=0.8, opacity=0.7) for i in range(6)], class_="bob"))
    # Queen Jessica coral nursery frames (lore)
    nurs = []
    for k in range(3):
        bx = 1010 + k * 54
        by = rf(bx) - 30
        nurs.append(el("path", d=f"M{n(bx)},{n(by + 40)} L{n(bx)},{n(by)} L{n(bx + 40)},{n(by)} L{n(bx + 40)},{n(by + 40)} M{n(bx)},{n(by + 14)} L{n(bx + 40)},{n(by + 14)}",
                       stroke="#d9e4ea", stroke_width=1.6, fill="none", opacity=0.75))
        for j in range(4):
            nurs.append(el("path", d=f"M{n(bx + 6 + j * 10)},{n(by + 14)} l0,8", stroke="#f08a5d", stroke_width=3, stroke_linecap="round"))
    s.add(g(nurs))
    s.add(el("rect", x=0, y=H - 40, width=W, height=40, fill="#0a3f63", opacity=0.25))
    return s.render(labels["aria"]["reef"])


# ==============================================================================
# SCENE: AMAZONIAN RAINFOREST
# ==============================================================================
def build_rainforest(labels):
    s = Scene("rainforest", 1200, 720, 2006)
    rng = s.rng
    W, H = s.w, s.h
    s.blur("mist", 12)
    s.blur("haze", 4)
    sky(s, [(0, "#bcd9de"), (0.6, "#e6efe6"), (1, "#f3f1e6")])
    sun(s, 900, 110, 30, glow="#fff6d6")
    haze = "#c9ddd4"
    # five receding canopy layers
    layers = [(300, 10, 16, 0.75), (350, 14, 22, 0.58), (400, 18, 28, 0.4), (450, 22, 34, 0.22)]
    base_cols = ("#1d4a2a", "#2f6b38", "#5b9a4c")
    for li, (gy, rmin, rmax, hz) in enumerate(layers):
        cols = tuple(mix(c, haze, hz) for c in base_cols)
        ground = lambda x, gy=gy, li=li: gy + 14 * math.sin(x / (90 + li * 20) + li)
        s.add(el("path", d=P([(0, ground(0))] + [(x, ground(x)) for x in range(0, W + 1, 40)] + [(W, H), (0, H)]), fill=cols[0]))
        s.add(g(canopy_band(s, -30, W + 30, ground, int(W / (rmin + rmax) * 1.4), rmin, rmax, cols, k=6)))
        s.add(mist(s, rng.uniform(100, 1100), gy + 10, rng.uniform(260, 420), 18, op=0.5 - li * 0.08))
    # sun rays through canopy
    s.add(light_rays(s, 600, 1000, 120, 640, 6, op=0.22))
    # emergent kapok trees
    s.add(broadleaf_tree(rng, 250, 560, 360, 92, ("#21502c", "#3a7d3c", "#79b358"), emergent=True, k=9))
    s.add(broadleaf_tree(rng, 980, 580, 330, 84, ("#24552f", "#418543", "#80b95e"), emergent=True, k=9))
    # lianas
    lianas = []
    for x0, x1 in ((180, 210), (300, 340), (930, 960), (1030, 1080)):
        lianas.append(f"M{n(x0)},250 C{n(x0 - 10)},360 {n(x1 + 10)},420 {n(x1)},560")
    s.add(el("path", d=" ".join(lianas), stroke="#3c5a2a", stroke_width=2, fill="none", opacity=0.85))
    # near canopy layer framing the river
    near_cols = ("#163d22", "#245a30", "#4a8a42")
    s.add(g(canopy_band(s, -40, 420, lambda x: 520 - x * 0.1, 14, 34, 52, near_cols, k=7)))
    s.add(g(canopy_band(s, 800, 1240, lambda x: 470 + (x - 800) * 0.15, 14, 34, 52, near_cols, k=7)))
    # river
    river = s.linear("river", [(0, "#a9b98f"), (0.4, "#8c8a5a"), (1, "#6e6440")])
    rpts_l = [(520, 520), (470, 560), (380, 610), (230, 660), (40, 720)]
    rpts_r = [(1200, 720), (1000, 690), (820, 630), (690, 570), (600, 520)]
    s.add(el("path", d=smooth(rpts_l) + " L" + " L".join(f"{n(x)},{n(y)}" for x, y in rpts_r) + "Z", fill=river))
    s.add(el("path", d=smooth([(520, 520), (560, 512), (600, 520)]), stroke="#c9d3b5", stroke_width=2, fill="none", opacity=0.6))
    s.add(water_lines(rng, 300, 950, 560, 700, 50, col="#e7ecd8", op=0.4))
    # reflections of canopy
    s.add(el("path", d="M520,522 L600,522 L640,560 L470,560Z", fill="#2f5a2e", opacity=0.25, filter=s.url("haze")))
    # Victoria water lilies
    for x, y, r in ((300, 668, 30), (360, 640, 22), (250, 690, 26), (420, 618, 16), (850, 660, 24), (910, 690, 32), (780, 632, 18)):
        s.add(water_lily(rng, x, y, r))
    s.add(el("circle", cx=372, cy=636, r=5, fill="#f7f1f4"), el("circle", cx=372, cy=636, r=2.4, fill="#e8a3c0"))
    # river banks foreground vegetation
    for x, y, L in ((40, 640, 60), (110, 610, 50), (1120, 640, 60), (1060, 600, 46), (180, 590, 40)):
        s.add(fern(rng, x, y, L, "#3f7a34"))
    for x, y, h in ((70, 650, 60), (1150, 660, 66), (1100, 630, 50)):
        s.add(heliconia(x, y, h))
    s.add(bromeliad(rng, 236, 300, 14), bromeliad(rng, 1002, 330, 12))
    for x, y, h, lean in ((140, 600, 140, 12), (1080, 610, 150, -14), (480, 520, 110, 6), (700, 540, 100, -4)):
        s.add(palm(rng, x, y, h, lean, 40, cols=("#2a5e30", "#447f3a"), coconuts=False, trunk_col="#6a5a44", nfr=11))
    # fauna
    s.add(dolphin(610, 610, 1.6))
    s.add(macaw(560, 200, 1.1), macaw(640, 180, 0.95, flip=True), macaw(720, 220, 0.8))
    s.add(toucan(1020, 300, 1.1))
    s.add(morpho(540, 450, 1.4), morpho(760, 480, 1.1))
    s.add(mist(s, 600, 500, 300, 24, op=0.45))
    return s.render(labels["aria"]["rainforest"])


# ==============================================================================
# SCENE: BRAZILIA HIGHLANDS
# ==============================================================================
def build_highlands(labels):
    s = Scene("highlands", 1200, 700, 2890)
    rng = s.rng
    W, H = s.w, s.h
    s.blur("mist", 14)
    sky(s, [(0, "#6fa6d6"), (0.55, "#bcd8ea"), (1, "#eef3f1")])
    sun(s, 260, 100, 24)
    s.add(cloud(rng, 820, 90, 160, op=0.85), cloud(rng, 520, 60, 110, op=0.8))
    r1, _ = mountain(s, "r1", [(0, 330), (120, 250), (240, 290), (360, 190), (470, 240), (600, 150), (720, 210), (860, 130), (980, 200), (1100, 160), (1200, 220)],
                     460, "#a8bcd2", shade="#6d84a0", shade_op=0.32, snow=215, rough=9)
    s.add(r1)
    s.add(mist(s, 600, 300, 520, 26, op=0.6))
    r2, ridge2 = mountain(s, "r2", [(380, 420), (500, 300), (580, 230), (640, 160), (690, 120), (740, 170), (800, 140), (870, 210), (960, 260), (1060, 330), (1200, 380)],
                          560, "#7d7066", shade="#2b2a35", shade_op=0.42, snow=215, rough=11, tongue=0.25)
    s.add(r2)
    # glacier tongue and glacial lake
    s.add(el("path", d=smooth([(690, 200), (712, 250), (735, 300), (760, 345), (790, 360)]) + " L812,352 L780,300 L750,240 L722,198Z",
             fill="#e8f1f8", opacity=0.95))
    s.add(el("path", d="M712,250 L760,248 M724,290 L770,286 M742,322 L786,318", stroke="#a9c3d8", stroke_width=1.2, opacity=0.8))
    s.add(el("ellipse", cx=815, cy=372, rx=70, ry=13, fill=s.linear("lake", [(0, "#6fd0d6"), (1, "#2a9bb0")])))
    s.add(el("ellipse", cx=815, cy=369, rx=58, ry=6, fill="#c2f0f2", opacity=0.45))
    # mid slope: paramo grassland band
    paramo = [(0, 470), (200, 430), (420, 420), (600, 400), (820, 390), (1000, 410), (1200, 430)]
    pf = interp(paramo)
    s.add(el("path", d=smooth(paramo) + f" L{W},{H} L0,{H}Z", fill=s.linear("paramo", [(0, "#a3a061"), (1, "#7d8a49")])))
    s.add(tufts(rng, 0, W, pf, 140, 12, "#c2b46a", op=0.9))
    # puya and frailejon on the paramo
    for x in (520, 590, 900, 960):
        y = pf(x) + 6
        s.add(g([
            el("path", d=" ".join(f"M{n(x)},{n(y)} q{n(d * 0.5)},-6 {n(d)},{n(-8 + abs(d) * 0.2)}" for d in range(-14, 15, 4)), stroke="#5e7a52", stroke_width=2, fill="none"),
            el("rect", x=x - 3.5, y=y - 70, width=7, height=64, rx=3.5, fill="#c9c27a"),
            el("path", d=" ".join(f"M{n(x - 4)},{n(y - 66 + k * 6)} l8,0" for k in range(10)), stroke="#9a9455", stroke_width=1),
        ]))
    for x in (640, 680, 720, 1040, 1080):
        y = pf(x) + 8
        s.add(g([el("rect", x=x - 2, y=y - 22, width=4, height=22, fill="#5c4a3a"),
                 el("path", d=" ".join(f"M{n(x)},{n(y - 22)} l{n(math.cos(a) * 9)},{n(math.sin(a) * 6 - 3)}" for a in [i * TAU / 12 for i in range(12)]),
                    stroke="#b9c4a6", stroke_width=2.2, stroke_linecap="round")]))
    # cloud forest on the left cliff with waterfall
    cliff = [(0, 330), (60, 320), (150, 340), (230, 345), (300, 380), (330, 470), (0, 470)]
    s.add(el("path", d=smooth(cliff[:-1]) + " L0,470Z", fill="#5b5a50"))
    cf = interp(cliff[:5])
    s.add(g(canopy_band(s, -20, 310, cf, 22, 16, 26, ("#2a4f36", "#3f6e45", "#6d9a62"), k=6)))
    s.add(waterfall(s, 290, 360, 560, 22))
    lower = [(0, 560), (200, 545), (360, 560), (480, 600), (480, H), (0, H)]
    lf = interp(lower[:4])
    s.add(el("path", d=smooth(lower[:4]) + f" L480,{H} L0,{H}Z", fill="#3f5f3a"))
    s.add(el("ellipse", cx=300, cy=575, rx=90, ry=16, fill=s.linear("pool", [(0, "#7fc9d6"), (1, "#3c8ea6")])))
    s.add(water_lines(rng, 220, 380, 566, 586, 16, op=0.6))
    s.add(g(canopy_band(s, -30, 230, lf, 14, 20, 32, ("#22462e", "#356440", "#5f915a"), k=7)))
    s.add(g(canopy_band(s, 360, 500, lf, 6, 18, 28, ("#22462e", "#356440", "#5f915a"), k=7)))
    for x, y in ((60, 520), (150, 500), (420, 560)):
        s.add(fern(rng, x, y, 40, "#4d8a46"))
    s.add(mist(s, 180, 340, 240, 28, op=0.7))
    s.add(mist(s, 300, 450, 160, 20, op=0.6))
    # foreground rocks and grass
    fg = [(480, H), (480, 600), (620, 580), (800, 600), (1000, 585), (1200, 600), (1200, H)]
    s.add(el("path", d=smooth(fg[1:-1]) + f" L{W},{H} L480,{H}Z", fill="#6f7f44"))
    s.add(tufts(rng, 480, W, interp(fg[1:-1]), 90, 18, "#b8a95c", width=1.3))
    for x, y, r in ((620, 640, 28), (700, 660, 18), (1060, 650, 34), (1130, 670, 22)):
        s.add(el("path", d=f"M{n(x - r)},{n(y)} Q{n(x - r * 0.8)},{n(y - r)} {n(x)},{n(y - r * 0.9)} Q{n(x + r * 0.9)},{n(y - r * 0.7)} {n(x + r)},{n(y)}Z", fill="#8a8a86"))
        s.add(el("path", d=f"M{n(x)},{n(y - r * 0.9)} Q{n(x + r * 0.9)},{n(y - r * 0.7)} {n(x + r)},{n(y)} L{n(x + r * 0.1)},{n(y)}Z", fill="#000000", opacity=0.18))
    # fauna
    s.add(condor(640, 230, 1.5), condor(900, 260, 0.9))
    s.add(hummingbird(250, 470, 1.6))
    s.add(g([bird_v(1000, 120, 8), bird_v(1030, 110, 6)], class_="drift"))
    return s.render(labels["aria"]["highlands"])


# ==============================================================================
# ATLAS VIGNETTES
# ==============================================================================
def vignette(key, seed):
    s = Scene(key, 480, 300, seed)
    s.blur("mist", 7)
    return s


def build_mogotes(labels):
    s = vignette("mogotes", 101)
    rng = s.rng
    sky(s, [(0, "#9cc7e6"), (1, "#f2ecdc")])
    sun(s, 380, 60, 14)
    s.add(cloud(rng, 120, 55, 90))
    for x0, x1, top, col in ((-20, 140, 120, "#86a68a"), (300, 500, 110, "#86a68a"), (110, 290, 80, "#5f8a4a"), (360, 470, 130, "#4f7a3c")):
        keys = [(x0, 240), (x0 + 12, top + 40), (x0 + 30, top + 6), ((x0 + x1) / 2, top), (x1 - 30, top + 8), (x1 - 12, top + 46), (x1, 240)]
        d = smooth(keys) + "Z"
        s.add(el("path", d=d, fill=col))
        cid = s.clip(f"m{x0}", d)
        cl = " ".join(f"M{n(rng.uniform(x0, x1))},{n(rng.uniform(top + 20, top + 60))} l{n(rng.uniform(-1, 1))},{n(rng.uniform(30, 80))}" for _ in range(12))
        inner = [el("path", d=cl, stroke="#b3b2a2", stroke_width=2.4, opacity=0.6, fill="none")]
        for _ in range(16):
            x = rng.uniform(x0 + 20, x1 - 20)
            inner.append(crown(rng, x, top + rng.uniform(2, 14), 7, (mix(col, "#000000", 0.2), col, mix(col, "#ffffff", 0.25)), k=4))
        s.add(g(inner, clip_path=cid))
        s.add(mist(s, (x0 + x1) / 2, 236, (x1 - x0) * 0.6, 10, op=0.6))
    s.add(el("rect", x=0, y=232, width=480, height=68, fill="#8a5a3a"))
    rows = " ".join(f"M{n(-40 + i * 34)},300 L{n(150 + i * 14)},236" for i in range(18))
    s.add(el("path", d=rows, stroke="#6f9a3e", stroke_width=6, opacity=0.9))
    s.add(el("path", d="M300,250 L330,224 L360,250Z", fill="#a07a48"), el("rect", x=306, y=250, width=48, height=16, fill="#7a5a36"))
    for x, h in ((60, 110), (420, 120), (250, 90)):
        s.add(palm(rng, x, 262, h, rng.uniform(-3, 3), 24, royal=True, nfr=9, trunk_col="#d2cab8"))
    return s.render(labels["aria"]["mogotes"])


def build_enriquillo(labels):
    s = vignette("enriquillo", 102)
    rng = s.rng
    sky(s, [(0, "#8fbde0"), (1, "#f6e9cf")])
    sun(s, 90, 60, 15)
    m, _ = mountain(s, "m", [(0, 170), (90, 120), (180, 150), (290, 90), (380, 130), (480, 110)], 220, "#b59a76", shade="#6b5442", rough=7)
    s.add(m)
    s.add(el("rect", x=0, y=200, width=480, height=60, fill=s.linear("lake", [(0, "#58c3c7"), (1, "#2d8fa0")])))
    s.add(el("path", d="M0,200 L480,200 L480,204 L0,204Z", fill="#f2f2ea", opacity=0.8))
    s.add(water_lines(rng, 0, 480, 206, 256, 30, op=0.45))
    s.add(el("path", d=smooth([(0, 262), (120, 254), (260, 262), (480, 250)]) + " L480,300 L0,300Z", fill="#d8c79e"))
    for x in (40, 420, 450):
        s.add(cactus(x, 270, 46, "#6f8f5a"))
    for i, x in enumerate((150, 180, 205, 235, 270, 300)):
        s.add(flamingo(x, 226 + (i % 2) * 6, 0.9, flip=i % 3 == 0))
    s.add(iguana(360, 278, 1.1))
    s.add(caiman(110, 238, 0.8))
    return s.render(labels["aria"]["enriquillo"])


def build_pantanal(labels):
    s = vignette("pantanal", 103)
    rng = s.rng
    sky(s, [(0, "#e8a86a"), (0.5, "#f5d29a"), (1, "#f8ecd2")])
    sun(s, 330, 150, 20, glow="#ffd38a")
    s.add(el("rect", x=0, y=170, width=480, height=130, fill=s.linear("water", [(0, "#d9b07a"), (1, "#6f8f8f")])))
    s.add(water_lines(rng, 0, 480, 176, 296, 40, col="#fff2d6", op=0.5))
    for x0, x1, y in ((0, 180, 172), (260, 480, 168), (120, 380, 210)):
        s.add(el("ellipse", cx=(x0 + x1) / 2, cy=y, rx=(x1 - x0) / 2, ry=8, fill="#6f8a3e"))
        s.add(tufts(rng, x0 + 10, x1 - 10, lambda x, y=y: y - 2, 30, 9, "#8aa04a"))
    s.add(g(canopy_band(s, 280, 470, lambda x: 160, 8, 12, 20, ("#3e5a2a", "#56763a", "#7f9a52"), k=5)))
    for x, h in ((60, 70), (100, 86), (210, 60)):
        s.add(palm(rng, x, 174, h, rng.uniform(-4, 4), 20, cols=("#4a6a32", "#6a8a40"), coconuts=False, trunk_col="#5a4a3a", nfr=9))
    s.add(jabiru(330, 202, 1.2), jabiru(370, 206, 1.0))
    s.add(capybara(150, 214, 1.2), capybara(120, 216, 0.9, flip=True))
    s.add(caiman(240, 250, 1.3))
    s.add(g([el("ellipse", cx=x, cy=268 + (x % 13), rx=10, ry=3, fill="#4e7a3a") for x in range(20, 480, 37)]))
    s.add(g([bird_v(180, 80, 7), bird_v(200, 74, 6), bird_v(215, 86, 6)], class_="drift"))
    return s.render(labels["aria"]["pantanal"])


def build_cerrado(labels):
    s = vignette("cerrado", 104)
    rng = s.rng
    sky(s, [(0, "#79b2e0"), (1, "#f4ead0")])
    s.add(cloud(rng, 360, 60, 110), cloud(rng, 110, 80, 70))
    h1, _ = hill(s, [(0, 190), (140, 160), (300, 175), (480, 150)], 240, "#b6a46a")
    s.add(h1)
    ground = interp([(0, 230), (240, 220), (480, 228)])
    s.add(el("path", d=smooth([(0, 230), (240, 220), (480, 228)]) + " L480,300 L0,300Z", fill="#c7a95c"))
    s.add(tufts(rng, 0, 480, ground, 120, 12, "#d8bf6e"))
    s.add(tufts(rng, 0, 480, lambda x: 270 + (x % 17), 80, 16, "#a98a42"))
    for x in (60, 180, 400):
        s.add(gnarled_tree(rng, x, ground(x), 60))
    s.add(ipe(rng, 290, ground(290), 80), ipe(rng, 440, ground(440) + 10, 64, bloom="#e46fa8", bloom2="#c9558c"))
    s.add(termite_mound(120, 262, 34), termite_mound(350, 250, 24))
    s.add(maned_wolf(230, 268, 1.2))
    s.add(macaw(150, 110, 0.7, palette=("#2f62b4", "#2a4fa0", "#f2c230")))
    return s.render(labels["aria"]["cerrado"])


def build_lencois(labels):
    s = vignette("lencois", 105)
    rng = s.rng
    sky(s, [(0, "#4f9ad8"), (1, "#d8ecf6")])
    s.add(cloud(rng, 300, 60, 120))
    lagoon = s.linear("lag", [(0, "#4fd0d0"), (1, "#1d8fb0")])
    rows = [(150, 0.55), (190, 0.75), (240, 1.0)]
    for yi, (y, sc) in enumerate(rows):
        for k in range(-1, 6):
            x = k * 110 * sc + (yi % 2) * 50
            w = 140 * sc
            s.add(el("ellipse", cx=x + w * 0.5, cy=y + 22 * sc, rx=w * 0.42, ry=8 * sc, fill=lagoon))
            s.add(el("path", d=f"M{n(x)},{n(y + 20 * sc)} Q{n(x + w * 0.35)},{n(y - 30 * sc)} {n(x + w * 0.6)},{n(y - 22 * sc)} Q{n(x + w * 0.85)},{n(y - 10 * sc)} {n(x + w * 1.05)},{n(y + 18 * sc)}Z",
                     fill="#fbf8f0"))
            s.add(el("path", d=f"M{n(x + w * 0.6)},{n(y - 22 * sc)} Q{n(x + w * 0.85)},{n(y - 10 * sc)} {n(x + w * 1.05)},{n(y + 18 * sc)} L{n(x + w * 0.62)},{n(y + 18 * sc)}Z",
                     fill="#d8d2c2", opacity=0.8))
    s.add(el("rect", x=0, y=262, width=480, height=38, fill="#fbf8f0"))
    s.add(el("ellipse", cx=240, cy=284, rx=170, ry=12, fill=lagoon))
    s.add(water_lines(rng, 90, 390, 278, 292, 14, op=0.6))
    return s.render(labels["aria"]["lencois"])


def build_caatinga(labels):
    s = vignette("caatinga", 106)
    rng = s.rng
    sky(s, [(0, "#a9c8e2"), (1, "#f4e2c6")])
    sun(s, 400, 70, 18, glow="#ffe1a8")
    h1, _ = hill(s, [(0, 170), (120, 150), (260, 175), (360, 140), (480, 165)], 230, "#c39a72")
    s.add(h1)
    ground = interp([(0, 232), (240, 222), (480, 230)])
    s.add(el("path", d=smooth([(0, 232), (240, 222), (480, 230)]) + " L480,300 L0,300Z", fill="#b9875a"))
    for _ in range(14):
        x = rng.uniform(0, 480)
        s.add(thorn_bush(rng, x, ground(x) + rng.uniform(0, 40), rng.uniform(14, 26)))
    for x, h in ((90, 110), (300, 130), (420, 80)):
        s.add(cactus(x, ground(x) + 30, h, "#6e9070"))
    s.add(g([el("ellipse", cx=rng.uniform(0, 480), cy=rng.uniform(250, 296), rx=rng.uniform(4, 10), ry=2.4, fill="#8f6a46") for _ in range(30)]))
    s.add(macaw(200, 100, 0.75, palette=("#2f62b4", "#26499a", "#2f62b4")))
    return s.render(labels["aria"]["caatinga"])


# ==============================================================================
# LOCALIZATION
# ==============================================================================
LABELS = {
    "en": {
        "transect": ["CORAL REEF", "MANGROVES", "KARST", "RAINFOREST", "PANTANAL", "CERRADO", "CATARACTS", "ANDES"],
        "aria": {
            "transect": "Sea-to-summit cross-section of Waikiki: coral reef, mangrove coast, karst towers, Amazon rainforest, Pantanal wetland, Cerrado savanna, cataract forest and the snow-capped highlands",
            "reef": "Split-level view of a Waikiki mangrove coast and the coral reef beneath it, with sea turtle, manta ray, reef fish and coral nursery frames",
            "rainforest": "Amazonian river scene with layered canopy, emergent kapok trees, giant water lilies, pink river dolphin, macaws and a toucan",
            "highlands": "Brazilia highlands with glacier, turquoise glacial lake, paramo grassland, cloud forest waterfall and soaring Andean condors",
            "mogotes": "Karst mogote towers rising over a tobacco valley with royal palms",
            "enriquillo": "Hypersaline Lago Enriquillo with flamingos, cacti, a rhinoceros iguana and an American crocodile",
            "pantanal": "Flooded Pantanal savanna at sunset with jabiru storks, capybaras and a caiman",
            "cerrado": "Cerrado savanna with flowering ipe trees, termite mounds and a maned wolf",
            "lencois": "White sand dunes with turquoise rain lagoons",
            "caatinga": "Dry Caatinga thorn forest with mandacaru cacti and a hyacinth macaw",
        },
    },
    "hu": {
        "transect": ["KORALLZÁTONY", "MANGROVE", "KARSZT", "ESŐERDŐ", "PANTANAL", "CERRADO", "ZUHATAGOK", "ANDOK"],
        "aria": {
            "transect": "Waikiki keresztmetszete a tengertől a csúcsokig: korallzátony, mangrovepart, karszttornyok, amazóniai esőerdő, Pantanal vizes élőhely, Cerrado szavanna, zuhatagerdő és a havas hegyvidék",
            "reef": "Waikiki mangrovepartja és az alatta húzódó korallzátony osztott nézetben, tengeri teknőssel, ördögrájával, zátonyhalakkal és korallkertekkel",
            "rainforest": "Amazóniai folyó rétegzett lombkoronával, kiemelkedő kapokfákkal, óriás tündérrózsákkal, rózsaszín folyami delfinnel, arákkal és tukánnal",
            "highlands": "Brazilia hegyvidéke gleccserrel, türkiz gleccsertóval, páramo füves pusztával, köderdei vízeséssel és köröző andoki kondorokkal",
            "mogotes": "Dohányvölgy fölé magasodó karsztos mogote-tornyok királypálmákkal",
            "enriquillo": "A sós Enriquillo-tó flamingókkal, kaktuszokkal, orrszarvúleguánnal és hegyesorrú krokodillal",
            "pantanal": "Elárasztott Pantanal szavanna naplementében jabiru gólyákkal, vízidisznókkal és kajmánnal",
            "cerrado": "Cerrado szavanna virágzó ipéfákkal, termeszvárakkal és sörényes farkassal",
            "lencois": "Fehér homokdűnék türkiz esővíz-lagúnákkal",
            "caatinga": "Száraz Caatinga tüskeerdő mandacaru kaktuszokkal és jácintarával",
        },
    },
}

BUILDERS = {
    "transect": build_transect,
    "reef": build_reef,
    "rainforest": build_rainforest,
    "highlands": build_highlands,
    "mogotes": build_mogotes,
    "enriquillo": build_enriquillo,
    "pantanal": build_pantanal,
    "cerrado": build_cerrado,
    "lencois": build_lencois,
    "caatinga": build_caatinga,
}

CONTAINER_RE = r'(<div[^>]*\bdata-nature-svg="{key}"[^>]*>\s*)<svg\b.*?</svg>(\s*</div>)'


def validate(svg: str, key: str) -> None:
    try:
        ET.fromstring(svg)
    except ET.ParseError as exc:
        sys.exit(f"Error: generated SVG '{key}' is invalid XML: {exc}")


def inline(svg: str) -> str:
    return re.sub(r'\s+xmlns="http://www\.w3\.org/2000/svg"', "", svg, count=1)


def update_pages(rendered: dict[str, dict[str, str]]) -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from build_pages import format_and_remove_empty_lines

    for lang in ("en", "hu"):
        path = ROOT / lang / "nature.html"
        text = path.read_text(encoding="utf-8")
        for key, svg in rendered[lang].items():
            pattern = re.compile(CONTAINER_RE.format(key=key), re.S)
            match = pattern.search(text)
            if not match:
                print(f"  ! no data-nature-svg=\"{key}\" container in {path.relative_to(ROOT)}")
                continue
            text = text[: match.start()] + match.group(1) + inline(svg) + match.group(2) + text[match.end():]
        path.write_text(format_and_remove_empty_lines(text), encoding="utf-8")
        print(f"Updated {path.relative_to(ROOT)}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rendered: dict[str, dict[str, str]] = {"en": {}, "hu": {}}
    for key, builder in BUILDERS.items():
        for lang in ("en", "hu"):
            svg = builder(LABELS[lang])
            validate(svg, key)
            rendered[lang][key] = svg
        out = OUT_DIR / f"{key}.svg"
        out.write_text(rendered["en"][key] + "\n", encoding="utf-8")
        print(f"Generated {out.relative_to(ROOT)} ({len(rendered['en'][key]) / 1024:.1f} KB)")
    if "--no-inject" not in sys.argv:
        update_pages(rendered)


if __name__ == "__main__":
    main()
