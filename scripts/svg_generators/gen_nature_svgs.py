#!/usr/bin/env python3
"""
Procedural generator for the Nature of Waikiki biome illustrations.

Generates standalone SVG files in icons/nature/ and injects localized inline
SVGs into en/nature.html and hu/nature.html. Every illustration container in
the pages is marked with data-nature-svg="KEY"; the <svg> inside it is replaced.

Scenes
  reef         Split-level Caribbean mangrove coast and Jardines coral reef
  rainforest   Amazonian river, canopy strata, emergent kapok trees
  highlands    Brazilia highlands: glacier, paramo, cloud forest, cataract
  mogotes      Atlas vignette: Vinales karst towers and tobacco valley
  enriquillo   Atlas vignette: hypersaline Lago Enriquillo with flamingos
  pantanal     Atlas vignette: flooded Pantanal savanna wetland
  cerrado      Atlas vignette: Cerrado savanna with flowering ipe trees
  lencois      Atlas vignette: white dunes and rain lagoons of Lencois
  caatinga     Atlas vignette: dry Caatinga thorn forest with mandacaru
  bluehole     Atlas vignette: Columbus Deep submarine karst sinkhole
  tepui        Atlas vignette: Monte Roraima sandstone tabletop tepui
  cataracts    Atlas vignette: Rio Esmeralda multi-tiered basalt cataracts

Usage
  python3 scripts/gen_nature_svgs.py
"""

from __future__ import annotations

import html
import math
import random
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
from functools import lru_cache

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
    return "0" if f"{r:.1f}" == "-0.0" else f"{r:.1f}"


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
        if val is None:
            continue
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
    flat = []
    for it in items:
        if isinstance(it, (list, tuple)):
            flat.extend(it)
        elif it:
            flat.append(it)
    return el("g", "".join(flat), **a)


def hx(c: str):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(a: str, b: str, t: float) -> str:
    t = max(0.0, min(1.0, t))
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
    pts = sorted(points, key=lambda p: p[0])
    xs = [p[0] for p in pts]

    def f(x):
        if x <= xs[0]:
            return pts[0][1]
        if x >= xs[-1]:
            return pts[-1][1]
        lo, hi = 0, len(xs) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if xs[mid] <= x:
                lo = mid
            else:
                hi = mid
        t = (x - xs[lo]) / ((xs[hi] - xs[lo]) or 1)
        return pts[lo][1] + (pts[hi][1] - pts[lo][1]) * t

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
                self.add(*it)
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

    def relief_pattern(self) -> str:
        if not hasattr(self, "_has_relief") or not self._has_relief:
            self._has_relief = True
            self.defs.append(
                f'<pattern id="{self.id("relief")}" width="32" height="32" patternUnits="userSpaceOnUse">'
                f'<path d="M0,6 L12,2 M16,14 L30,8 M2,22 L18,17 M14,30 L32,24 M6,12 L10,10 M22,28 L28,26" stroke="#1b3022" stroke-width="0.75" opacity="0.45" stroke-linecap="round"/>'
                f'<circle cx="8" cy="18" r="0.6" fill="#1b3022" opacity="0.4"/>'
                f'<circle cx="24" cy="6" r="0.7" fill="#1b3022" opacity="0.4"/>'
                f'<circle cx="20" cy="22" r="0.6" fill="#1b3022" opacity="0.4"/>'
                f'<circle cx="4" cy="28" r="0.5" fill="#1b3022" opacity="0.4"/>'
                f'</pattern>'
            )
        return self.url("relief")

    def ripple_pattern(self) -> str:
        if not hasattr(self, "_has_ripple") or not self._has_ripple:
            self._has_ripple = True
            self.defs.append(
                f'<pattern id="{self.id("ripple")}" width="64" height="32" patternUnits="userSpaceOnUse">'
                f'<path d="M0,8 Q16,4 32,8 T64,8 M-16,24 Q0,20 16,24 T48,24" fill="none" stroke="#ffffff" stroke-width="0.8" opacity="0.35"/>'
                f'</pattern>'
            )
        return self.url("ripple")

    def grain_pattern(self) -> str:
        if not hasattr(self, "_has_grain") or not self._has_grain:
            self._has_grain = True
            self.defs.append(
                f'<pattern id="{self.id("grain")}" width="24" height="24" patternUnits="userSpaceOnUse">'
                f'<circle cx="4" cy="4" r="0.6" fill="#000000" opacity="0.3"/>'
                f'<circle cx="16" cy="10" r="0.5" fill="#000000" opacity="0.25"/>'
                f'<circle cx="8" cy="18" r="0.7" fill="#000000" opacity="0.3"/>'
                f'<circle cx="20" cy="20" r="0.5" fill="#000000" opacity="0.25"/>'
                f'</pattern>'
            )
        return self.url("grain")

    def render(self) -> str:
        vp_id = self.id("vp")
        vp_clip = f'<clipPath id="{vp_id}"><rect width="{self.w}" height="{self.h}"/></clipPath>'
        head = f'<svg xmlns="http://www.w3.org/2000/svg" class="nature-ill" viewBox="0 0 {self.w} {self.h}">'
        lines = [
            head,
            "<defs>",
            vp_clip,
            *self.defs,
            "</defs>",
            f'<g clip-path="url(#{vp_id})">',
            *self.body,
            "</g>",
            "</svg>",
        ]
        return "\n".join(lines)


# ==============================================================================
# ATMOSPHERE & LANDSCAPE PRIMITIVES
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


def mountain(s: Scene, name, keys, base, fill, shade="#1f3348", shade_op=0.38, snow=None,
             snow_col="#f4f8fc", rough=14, depth=5, gullies=True, tongue=0.22):
    """Realistic multi-faceted mountain massif with arête ridges, rock strata, elevation-aware snow fields, and couloirs."""
    rng = s.rng
    r = ridge(rng, keys, rough, depth)
    poly = r + [(r[-1][0], base), (r[0][0], base)]
    d = P(poly)
    clip = s.clip(name, d)
    lit_col = mix(fill, "#fff8eb", 0.22)
    mid_shade = mix(fill, shade, 0.45)
    base_grad = s.linear(f"{name}-grad", [
        (0, mix(fill, "#ffffff", 0.10)),
        (0.55, fill),
        (1, mix(fill, shade, 0.28)),
    ])
    inner = [
        # Sunlit base rock tone
        el("path", d=d, fill=lit_col, opacity=0.28),
        # Embossed micro-relief rock texture
        el("path", d=d, fill=s.relief_pattern(), opacity=0.18, style="mix-blend-mode:multiply"),
    ]

    # Identify peaks and valleys for 3D ridge facets
    peaks = [i for i in range(1, len(r) - 1) if r[i][1] <= r[i - 1][1] and r[i][1] <= r[i + 1][1]]
    sig = [i for i in peaks if r[i][1] == min(p[1] for p in r[max(0, i - 5):i + 6])]

    # Stepped geological rock strata bands across the massif
    for band in range(5):
        sy_off = 18 + band * 28
        pts = [(px, py + sy_off + 4 * math.sin(px * 0.025 + band * 1.3)) for px, py in r[::2]]
        if len(pts) > 2:
            band_poly = pts + [(pts[-1][0], pts[-1][1] + 8), (pts[0][0], pts[0][1] + 8)]
            inner.append(el("path", d=P(band_poly), fill=mid_shade, opacity=0.14))

    # Right-flank 3D shadow facets from every prominent peak with irregular arête spines and secondary spurs
    for idx, i in enumerate(sig):
        nxt = sig[idx + 1] if idx + 1 < len(sig) else len(r) - 1
        j = max(range(i, nxt + 1), key=lambda k: r[k][1])
        if j <= i:
            continue
        px, py = r[i]
        vx, vy = r[j]
        foot = px + (base - py) * rng.uniform(0.16, 0.32)
        spine = [(px, py)]
        for st in range(1, 8):
            t = st / 7
            sx = px + (foot - px) * t + rng.uniform(-7, 7) * (1 - abs(2 * t - 1))
            sy = py + (base - py) * t
            spine.append((sx, sy))
        v_foot = vx + (base - vy) * 0.20
        shadow_poly = r[i:j + 1] + [(v_foot, base)] + spine[::-1]
        inner.append(el("path", d=P(shadow_poly), fill=shade, opacity=shade_op))
        # Secondary mid-tone rock facet inside the shadow face for 3D relief
        mid_spine = [(px + (vx - px) * 0.35, py + (vy - py) * 0.35)]
        for st in range(1, 5):
            t = st / 4
            mid_spine.append((px + (v_foot - px) * (0.35 + 0.45 * t) + rng.uniform(-5, 5), py + (base - py) * (0.25 + 0.75 * t)))
        inner.append(el("path", d=P(mid_spine + [(v_foot, base), spine[-1]]), fill=shade, opacity=shade_op * 0.42))
        # Sunlit arête highlight along the left of the main spine
        lit_spine = [(px, py)] + [(sx - rng.uniform(7, 16), sy) for sx, sy in spine[1:-1]] + [(foot - 14, base)]
        inner.append(el("path", d=P(spine + lit_spine[::-1]), fill=mix(fill, "#ffffff", 0.28), opacity=0.30))

        # Sculpted triangular talus / scree cones and diagonal rock ribs inside facets (no vertical barcode lines)
        if gullies and (base - py) > 28:
            for c_idx in range(2):
                f_t = 0.28 + c_idx * 0.34
                rx0 = px + (vx - px) * f_t
                ry0 = py + (vy - py) * f_t + rng.uniform(6, 16)
                ch_len = min(65, (base - ry0) * rng.uniform(0.35, 0.62))
                if ch_len > 12:
                    bx_c = rx0 + (foot - px) * 0.38 + rng.uniform(-6, 8)
                    by_c = ry0 + ch_len
                    w_cone = max(3.5, ch_len * 0.16)
                    inner.append(el("path", d=P([(rx0, ry0), (bx_c - w_cone, by_c), (bx_c + w_cone, by_c)]),
                                    fill=shade, opacity=0.18))
                    inner.append(el("path", d=P([(rx0, ry0), (bx_c - w_cone * 1.15, by_c), (bx_c - w_cone * 0.25, by_c)]),
                                    fill=lit_col, opacity=0.16))

    # Elevation-following snow cap with sunlit and shadowed facets and valley couloir tongues
    if snow is not None:
        line = []
        for idx_r, (rx_, ry_) in enumerate(r):
            window = [p[1] for p in r[max(0, idx_r - 14):min(len(r), idx_r + 15)]]
            local_min = min(window)
            if local_min > snow + 18:
                # Entire ridge section is well below the snow line -> keep snow_y above the rock ridge
                snow_y = ry_ - 16
            else:
                # Smoothly interpolate snow depth as local_min approaches snow + 18 so snow never drops into low foothills
                t_elev = max(0.0, min(1.0, (snow + 18 - local_min) / 36.0))
                is_valley = ry_ > local_min + 8
                target_y = max(ry_ + (24 if is_valley else 14), snow + (12 if is_valley else -4))
                target_y += 3.5 * math.sin(rx_ * 0.045) + rng.uniform(-3.0, 3.0)
                if is_valley and t_elev > 0.65 and rng.random() < tongue:
                    target_y += rng.uniform(10, 24)
                snow_y = (ry_ - 14) * (1.0 - t_elev) + target_y * t_elev
            line.append((rx_, snow_y))
        snow_d = P([(r[0][0], -20), (r[-1][0], -20)] + line[::-1])
        snow_clip = s.clip(f"{name}-snow", snow_d)
        snow_shades = [el("path", d=snow_d, fill=snow_col)]
        for idx, i in enumerate(sig):
            nxt = sig[idx + 1] if idx + 1 < len(sig) else len(r) - 1
            j = max(range(i, nxt + 1), key=lambda k: r[k][1])
            if j <= i or r[i][1] > snow + 32:
                continue
            px, py = r[i]
            vx, vy = r[j]
            sh_snow = r[i:j + 1] + [(vx + 22, snow + 75), (px + 6, snow + 75)]
            snow_shades.append(el("path", d=P(sh_snow), fill="#9cb8d4", opacity=0.62))
        inner.append(g(snow_shades, clip_path=snow_clip))

    # Rim highlight along sunlit ridge segments
    rim = []
    for k in range(len(r) - 1):
        if r[k + 1][1] < r[k][1]:
            rim.append(f"M{n(r[k][0])},{n(r[k][1])} L{n(r[k + 1][0])},{n(r[k + 1][1])}")
    if rim:
        inner.append(el("path", d=" ".join(rim), fill="none", stroke="#fffdf7", stroke_width=1.2, opacity=0.45))

    return [el("path", d=d, fill=base_grad), g(inner, clip_path=clip)], r


def hill(s: Scene, keys, base, fill, rough=6, depth=4):
    """Volumetric 3D hill ridge with vertical atmospheric gradient, ridge-spur light/shadow facets, and crest highlight."""
    rng = s.rng
    r = ridge(rng, keys, rough, depth)
    d = smooth(r) + f" L{n(r[-1][0])},{n(base)} L{n(r[0][0])},{n(base)}Z"
    h_idx = getattr(s, "_hill_cnt", 0) + 1
    s._hill_cnt = h_idx
    h_name = f"hill-{h_idx}"
    lit_col = mix(fill, "#e8f09c", 0.22)
    sh_col = mix(fill, "#10241e", 0.38)
    grad = s.linear(f"{h_name}-g", [
        (0, mix(fill, "#fff8dc", 0.14)),
        (0.55, fill),
        (1, mix(fill, "#0d2018", 0.32)),
    ])
    clip = s.clip(f"{h_name}-c", d)
    facets = []
    # Find local hill summits and cast soft 3D spur facets down to base
    peaks = [i for i in range(1, len(r) - 1) if r[i][1] <= r[i - 1][1] and r[i][1] <= r[i + 1][1]]
    sig = [i for i in peaks if r[i][1] == min(p[1] for p in r[max(0, i - 3):i + 4])]
    for idx, i in enumerate(sig):
        nxt = sig[idx + 1] if idx + 1 < len(sig) else len(r) - 1
        j = max(range(i, nxt + 1), key=lambda k: r[k][1])
        if j <= i:
            continue
        px, py = r[i]
        vx, vy = r[j]
        foot = px + (base - py) * rng.uniform(0.18, 0.36)
        spine = [(px, py), ((px + foot) * 0.5 + rng.uniform(-6, 6), (py + base) * 0.5), (foot, base)]
        sh_poly = r[i:j + 1] + [(vx + (base - vy) * 0.18, base)] + spine[::-1]
        facets.append(el("path", d=P(sh_poly), fill=sh_col, opacity=0.32))
        lit_poly = [(px - (base - py) * 0.25, base), (px, py), (foot, base)]
        facets.append(el("path", d=P(lit_poly), fill=lit_col, opacity=0.22))
    hi = smooth([(x, y + 1.5) for x, y in r])
    return g([
        el("path", d=d, fill=grad),
        g(facets, clip_path=clip),
        el("path", d=hi, fill="none", stroke=mix(fill, "#fff8d8", 0.30), stroke_width=1.3, opacity=0.45),
    ]), r


def sky(s: Scene, stops, h=None):
    s.add(el("rect", width=s.w, height=h or s.h, fill=s.linear("sky", stops)))


def sun(s: Scene, x, y, r, glow="#fff1c9"):
    """Multi-layered atmospheric solar corona, warm horizon scatter bloom, and brilliant solar disc."""
    s.add(el("circle", cx=x, cy=y, r=r * 9.0, fill=s.radial("sun-atmo", [
        (0, "#fffef8", 0.55),
        (0.22, glow, 0.32),
        (0.55, glow, 0.10),
        (1, glow, 0),
    ])))
    s.add(el("circle", cx=x, cy=y, r=r * 4.5, fill=s.radial("sun-corona", [
        (0, "#ffffff", 0.95),
        (0.18, "#fffdf2", 0.78),
        (0.45, glow, 0.38),
        (0.80, glow, 0.08),
        (1, glow, 0),
    ])))
    s.add(el("circle", cx=x, cy=y, r=r * 1.15, fill=s.radial("sun-core", [
        (0, "#ffffff", 1.0),
        (0.68, "#fffef6", 0.98),
        (0.88, "#fff6d6", 0.65),
        (1, glow, 0.0),
    ])))


def _cloud_billow(rng, cx, cy, rx, ry, lobes=9):
    """Organic scalloped cumulus cloud billow path with soft rounded tops and flatter base."""
    pts = []
    for i in range(lobes):
        a = TAU * i / lobes
        # Flatter along the bottom (sin(a) > 0), puffier along the top (sin(a) < 0)
        y_scale = 0.52 if math.sin(a) > 0.15 else rng.uniform(0.88, 1.16)
        x_scale = rng.uniform(0.88, 1.12)
        pts.append((cx + math.cos(a) * rx * x_scale, cy + math.sin(a) * ry * y_scale))
    return smooth(pts, closed=True, k=0.18)


def cloud(rng, x, y, w, col="#ffffff", shade="#c8d8e8", op=0.94, cls="drift"):
    """Painterly multi-layered tropical cumulus bank with sculpted bezier billows and zero raw ellipse outlines."""
    h = w * 0.26
    n_domes = max(5, int(w / 16))
    base_y = y + h * 0.26
    pts = [(x - w * 0.49, base_y), (x - w * 0.51, base_y - h * 0.12)]
    domes = []
    for i in range(n_domes):
        t = (i + 0.5) / n_domes
        env = math.sin(math.pi * t) ** 0.68
        dx = x + (t - 0.5) * w * 0.86 + rng.uniform(-w * 0.025, w * 0.025)
        dr = w * (0.095 + 0.115 * env) * rng.uniform(0.90, 1.12)
        dy = base_y - h * env * rng.uniform(0.76, 1.06)
        domes.append((dx, dy, dr, env))
        pts.append((dx - dr * 0.56, dy + dr * 0.20))
        pts.append((dx, dy - dr * 0.28))
        pts.append((dx + dr * 0.56, dy + dr * 0.20))
    pts.extend([
        (x + w * 0.51, base_y - h * 0.12),
        (x + w * 0.49, base_y),
        (x + w * 0.25, base_y + h * 0.06),
        (x - w * 0.25, base_y + h * 0.06),
    ])
    main_d = smooth(pts, closed=True, k=0.17)

    deep_shade = mix(shade, "#7a8ea8", 0.32)
    mid_col = mix(col, shade, 0.48)
    warm_lit = mix(col, "#fffef5", 0.45)

    billows_sh, billows_mid, billows_lit = [], [], []
    for dx, dy, dr, env in sorted(domes, key=lambda item: item[1]):
        billows_sh.append(_cloud_billow(rng, dx + dr * 0.12, dy + dr * 0.22, dr * 1.06, dr * 0.68, lobes=8))
        billows_mid.append(_cloud_billow(rng, dx + dr * 0.04, dy + dr * 0.10, dr * 1.00, dr * 0.65, lobes=8))
        billows_lit.append(_cloud_billow(rng, dx - dr * 0.08, dy - dr * 0.02, dr * 0.88, dr * 0.58, lobes=8))

    shade_pts = [
        (x - w * 0.49, base_y - h * 0.02),
        (x - w * 0.28, base_y - h * 0.18),
        (x - w * 0.05, base_y - h * 0.12),
        (x + w * 0.22, base_y - h * 0.20),
        (x + w * 0.49, base_y - h * 0.02),
        (x + w * 0.46, base_y + h * 0.06),
        (x - w * 0.46, base_y + h * 0.06),
    ]
    shade_d = smooth(shade_pts, closed=True, k=0.17)
    under_d = smooth([
        (x - w * 0.42, base_y + h * 0.01),
        (x, base_y - h * 0.06),
        (x + w * 0.42, base_y + h * 0.01),
        (x + w * 0.36, base_y + h * 0.06),
        (x - w * 0.36, base_y + h * 0.06),
    ], closed=True, k=0.16)

    return g([
        el("path", d=main_d, fill=col),
        el("path", d=" ".join(billows_sh), fill=shade, opacity=0.45),
        el("path", d=" ".join(billows_mid), fill=mid_col, opacity=0.38),
        el("path", d=shade_d, fill=shade, opacity=0.68),
        el("path", d=under_d, fill=deep_shade, opacity=0.42),
        el("path", d=" ".join(billows_lit), fill=warm_lit, opacity=0.95),
    ], opacity=op)


def mist(s: Scene, x, y, rx, ry, op=0.55, col="#ffffff", blur="mist", cls="drift"):
    """Multi-layered drifting atmospheric mist bank with soft vapor wisps."""
    return g([
        el("ellipse", cx=x, cy=y, rx=rx, ry=ry, fill=col, opacity=op * 0.72, filter=s.url(blur)),
        el("ellipse", cx=x - rx * 0.18, cy=y - ry * 0.15, rx=rx * 0.68, ry=ry * 0.62, fill=col, opacity=op * 0.52, filter=s.url(blur)),
        el("ellipse", cx=x + rx * 0.22, cy=y + ry * 0.12, rx=rx * 0.62, ry=ry * 0.55, fill=col, opacity=op * 0.45, filter=s.url(blur)),
    ])


# ==============================================================================
# VEGETATION PRIMITIVES
# ==============================================================================
def _foliage_blob(rng, cx, cy, rx, ry, lobes=9):
    """Compact scalloped botanical foliage cluster path using quadratic Bezier lobes."""
    anchors = []
    ctrl = []
    for i in range(lobes):
        a0 = TAU * i / lobes
        am = TAU * (i + 0.5) / lobes
        r0 = rng.uniform(0.74, 0.88)
        rm = rng.uniform(1.08, 1.25)
        anchors.append((cx + math.cos(a0) * rx * r0, cy + math.sin(a0) * ry * r0))
        ctrl.append((cx + math.cos(am) * rx * rm, cy + math.sin(am) * ry * rm))
    segs = [f"M{n(anchors[0][0])},{n(anchors[0][1])}"]
    for i in range(lobes):
        nxt = anchors[(i + 1) % lobes]
        c = ctrl[i]
        segs.append(f"Q{n(c[0])},{n(c[1])} {n(nxt[0])},{n(nxt[1])}")
    segs.append("Z")
    return " ".join(segs)


def _leaf_fan(cx, cy, ang, sz):
    """Three-bladed botanical leaf spray cluster oriented along ang."""
    blades = []
    for da, sc in ((-0.42, 0.85), (0.0, 1.05), (0.42, 0.85)):
        a = ang + da
        ca, sa = math.cos(a), math.sin(a)
        nx_, ny_ = -sa, ca
        L = sz * sc
        W = L * 0.34
        tx, ty = cx + ca * L, cy + sa * L
        mx, my = cx + ca * L * 0.52, cy + sa * L * 0.52
        blades.append(
            f"M{n(cx)},{n(cy)} Q{n(mx + nx_ * W)},{n(my + ny_ * W)} {n(tx)},{n(ty)} "
            f"Q{n(mx - nx_ * W)},{n(my - ny_ * W)} {n(cx)},{n(cy)}Z"
        )
    return " ".join(blades)


def crown(rng, cx, cy, r, cols, k=7, flat=0.76, detail=True):
    """Rich multi-tiered botanical tree crown with deep ambient core, 5 volumetric bough layers, and radiating leaf sprays."""
    dark, mid, light = cols
    deep = mix(dark, "#051008", 0.45)
    mid_dark = mix(dark, mid, 0.48)
    spec = mix(light, "#f4f69e", 0.36)
    d_lobes = 9 if detail else 7
    paths = [[], [], [], [], []]

    # Tier 0: Deep ambient underside boughs
    for i in range(max(3, k // 2 + 1)):
        a = math.pi * (0.08 + 0.84 * i / max(1, k // 2)) + rng.uniform(-0.18, 0.18)
        d = r * rng.uniform(0.34, 0.65)
        rr = r * rng.uniform(0.46, 0.64)
        paths[0].append(_foliage_blob(rng, cx + math.cos(a) * d * 1.16, cy + abs(math.sin(a)) * d * flat + r * 0.15,
                                      rr * 1.16, rr * flat, lobes=d_lobes))

    # Tier 1: Dark structural canopy masses
    for _ in range(k + 1):
        a, d = rng.uniform(0, TAU), rng.uniform(0, r * 0.60)
        rr = r * rng.uniform(0.42, 0.58)
        paths[1].append(_foliage_blob(rng, cx + math.cos(a) * d * 1.18, cy + math.sin(a) * d * flat + r * 0.05,
                                      rr * 1.14, rr * flat, lobes=d_lobes))

    # Tier 2: Mid-dark interior foliage boughs
    for _ in range(max(3, k)):
        a, d = rng.uniform(-math.pi * 1.05, math.pi * 0.45), rng.uniform(0, r * 0.54)
        rr = r * rng.uniform(0.36, 0.52)
        paths[2].append(_foliage_blob(rng, cx + math.cos(a) * d * 1.14 - r * 0.04,
                                      cy + math.sin(a) * d * flat,
                                      rr * 1.12, rr * flat, lobes=d_lobes))

    # Tier 3: Mid-tone sunlit leaf clusters
    for _ in range(max(3, k - 1)):
        a, d = rng.uniform(-math.pi * 0.98, math.pi * 0.30), rng.uniform(0, r * 0.48)
        rr = r * rng.uniform(0.30, 0.46)
        paths[3].append(_foliage_blob(rng, cx + math.cos(a) * d * 1.10 - r * 0.09,
                                      cy + math.sin(a) * d * flat - r * 0.09,
                                      rr * 1.10, rr * flat, lobes=d_lobes))

    # Tier 4: Upper sunlit canopy domes
    for _ in range(max(3, k // 2 + 2)):
        hx_ = cx - r * 0.20 + rng.uniform(-r * 0.42, r * 0.38)
        hy_ = cy - r * 0.24 + rng.uniform(-r * 0.20, r * 0.14)
        rr = r * rng.uniform(0.18, 0.32)
        paths[4].append(_foliage_blob(rng, hx_, hy_, rr * 1.15, rr * flat, lobes=7))

    out = [
        el("path", d=" ".join(paths[0]), fill=deep),
        el("path", d=" ".join(paths[1]), fill=dark),
        el("path", d=" ".join(paths[2]), fill=mid_dark),
        el("path", d=" ".join(paths[3]), fill=mid),
        el("path", d=" ".join(paths[4]), fill=light),
    ]
    if detail and r >= 10:
        fans_mid, fans_spec = [], []
        n_fans = max(5, k + 1)
        for idx_f in range(n_fans):
            a = -math.pi * 1.08 + math.pi * 1.28 * (idx_f / max(1, n_fans - 1)) + rng.uniform(-0.14, 0.14)
            rad = r * rng.uniform(0.58, 0.94)
            px = cx + math.cos(a) * rad * 1.08
            py = cy + math.sin(a) * rad * flat
            sz = max(2.4, r * rng.uniform(0.15, 0.22))
            if idx_f % 2 == 0:
                fans_spec.append(_leaf_fan(px, py, a, sz))
            else:
                fans_mid.append(_leaf_fan(px, py, a, sz * 1.08))
        out.append(el("path", d=" ".join(fans_mid), fill=light, opacity=0.88))
        out.append(el("path", d=" ".join(fans_spec), fill=spec, opacity=0.82))
    return g(out)


def trunk(x, yb, yt, wb, wt, col, bend=0.0, buttress=False):
    shade = mix(col, "#000000", 0.32)
    lit = mix(col, "#d8c3a5", 0.22)
    d = (f"M{n(x - wb / 2)},{n(yb)} Q{n(x - wb / 2 + bend * 0.5)},{n((yb + yt) / 2)} {n(x - wt / 2 + bend)},{n(yt)} "
         f"L{n(x + wt / 2 + bend)},{n(yt)} Q{n(x + wb / 2 + bend * 0.5)},{n((yb + yt) / 2)} {n(x + wb / 2)},{n(yb)}Z")
    d_shade = (f"M{n(x)},{n(yb)} Q{n(x + bend * 0.5)},{n((yb + yt) / 2)} {n(x + bend)},{n(yt)} "
               f"L{n(x + wt / 2 + bend)},{n(yt)} Q{n(x + wb / 2 + bend * 0.5)},{n((yb + yt) / 2)} {n(x + wb / 2)},{n(yb)}Z")
    out = [el("path", d=d, fill=col), el("path", d=d_shade, fill=shade, opacity=0.55)]
    # Bark vertical texture grooves
    for f in (-0.25, 0.05, 0.28):
        out.append(el("path", d=f"M{n(x + wb * f)},{n(yb)} Q{n(x + wb * f + bend * 0.5)},{n((yb + yt) / 2)} {n(x + wt * f + bend)},{n(yt)}",
                      stroke=lit if f < 0 else shade, stroke_width=0.9, fill="none", opacity=0.45))
    if buttress:
        # Multi-fin tropical tabular buttress roots
        out.append(el("path", fill=col, d=(
            f"M{n(x - wb * 2.6)},{n(yb)} Q{n(x - wb * 0.85)},{n(yb - wb * 0.5)} {n(x - wb * 0.38)},{n(yb - wb * 3.4)} "
            f"L{n(x + wb * 0.38)},{n(yb - wb * 3.4)} Q{n(x + wb * 0.85)},{n(yb - wb * 0.5)} {n(x + wb * 2.6)},{n(yb)}Z")))
        out.append(el("path", fill=shade, opacity=0.5, d=(
            f"M{n(x - wb * 0.2)},{n(yb)} Q{n(x - wb * 0.1)},{n(yb - wb * 1.5)} {n(x + wb * 0.15)},{n(yb - wb * 3.2)} "
            f"L{n(x + wb * 0.38)},{n(yb - wb * 3.4)} Q{n(x + wb * 0.85)},{n(yb - wb * 0.5)} {n(x + wb * 2.6)},{n(yb)}Z")))
        out.append(el("path", fill=lit, opacity=0.35, d=(
            f"M{n(x - wb * 2.5)},{n(yb)} Q{n(x - wb * 1.1)},{n(yb - wb * 0.6)} {n(x - wb * 0.38)},{n(yb - wb * 3.2)} "
            f"L{n(x - wb * 0.15)},{n(yb - wb * 2.8)} Q{n(x - wb * 0.6)},{n(yb - wb * 0.4)} {n(x - wb * 1.2)},{n(yb)}Z")))
    return out


def broadleaf_tree(rng, x, yb, h, r, cols, trunk_col="#5b4632", flat=0.76, k=8, emergent=False):
    top = yb - h
    bend = rng.uniform(-r * 0.18, r * 0.18)
    out = trunk(x, yb, top + r * 0.38, max(3.5, r * 0.22), max(2.2, r * 0.11), trunk_col, bend=bend, buttress=emergent)
    if emergent:
        subs = [(-0.85, 0.18, 0.58), (0.85, 0.15, 0.56), (-0.42, -0.12, 0.65), (0.45, -0.10, 0.62), (0.0, -0.26, 0.68)]
        tx = x + bend
        ty = top + r * 0.42
        for dx, dy, sc in subs:
            ex, ey = x + dx * r, top + dy * r + r * 0.12
            cx_, cy_ = tx + dx * r * 0.38, ty - r * 0.08
            w_b = max(2.0, r * 0.08 * sc)
            out.append(el("path", d=f"M{n(tx)},{n(ty)} Q{n(cx_)},{n(cy_)} {n(ex)},{n(ey)}",
                          fill="none", stroke=trunk_col, stroke_width=w_b, stroke_linecap="round"))
            out.append(el("path", d=f"M{n(tx)},{n(ty - 1)} Q{n(cx_)},{n(cy_ - 1.5)} {n(ex)},{n(ey - 1)}",
                          fill="none", stroke=mix(trunk_col, "#dfd0b8", 0.25), stroke_width=w_b * 0.4, stroke_linecap="round"))
        # Hanging aerial roots / vines from emergent boughs
        vines = []
        for dx, dy, _ in subs[:2]:
            vx = x + dx * r * 0.72
            vy = top + dy * r + r * 0.2
            vines.append(f"M{n(vx)},{n(vy)} q{n(rng.uniform(-4, 4))},{n(h * 0.22)} {n(rng.uniform(-6, 6))},{n(h * 0.45)}")
        out.append(el("path", d=" ".join(vines), stroke="#2f4d27", stroke_width=1.1, fill="none", opacity=0.7))
        for dx, dy, sc in subs:
            out.append(crown(rng, x + dx * r, top + dy * r, r * sc, cols, k=k, flat=0.52))
    else:
        out.append(crown(rng, x + bend, top, r, cols, k=k, flat=flat))
    return g(out)


def palm(rng, x, y, h, lean, L, cols=("#24582a", "#4d9140"), trunk_col="#8b6b4c", nfr=13, royal=False,
         coconuts=True, sway=True, wb=None):
    """Botanically detailed coconut or Cuban royal palm with ringed 3D trunk, petiole boots/crownshaft, and lanceolate leaflet blades."""
    dark, light = cols
    hl_leaf = mix(light, "#e2f078", 0.34)
    mid_leaf = mix(dark, light, 0.52)
    deep_leaf = mix(dark, "#0d2210", 0.42)
    lit_trunk = mix(trunk_col, "#e8dac6", 0.32)
    sh_trunk = mix(trunk_col, "#1a120a", 0.42)
    tx, ty = x + lean, y - h
    ctrl = (x + lean * 0.24, y - h * 0.56)
    wb = wb or max(3.4, h * 0.050)
    wt = wb * (0.56 if royal else 0.62)
    left, right, mid_line, lit_line, rings = [], [], [], [], []
    steps = 18
    for i in range(steps + 1):
        t = i / steps
        bx, by = quad((x, y), ctrl, (tx, ty), t)
        w = wb * (1 - t) + wt * t
        if royal:
            w += wb * 0.35 * math.sin(math.pi * min(1, t * 1.45)) * (1 - t * 0.85)
        left.append((bx - w / 2, by))
        right.append((bx + w / 2, by))
        mid_line.append((bx + w * 0.05, by))
        lit_line.append((bx - w * 0.22, by))
        if 0 < i < steps:
            rings.append(f"M{n(bx - w * 0.49)},{n(by)} Q{n(bx)},{n(by + 1.2)} {n(bx + w * 0.49)},{n(by + 0.4)}")
    out = [
        el("ellipse", cx=x, cy=y + 1, rx=wb * 0.85, ry=wb * 0.28, fill=sh_trunk, opacity=0.45),
        el("path", d=P(left + right[::-1]), fill=trunk_col),
        el("path", d=P(left + lit_line[::-1]), fill=lit_trunk, opacity=0.42),
        el("path", d=P(mid_line + right[::-1]), fill=sh_trunk, opacity=0.38),
        el("path", d=" ".join(rings), stroke=sh_trunk, stroke_width=0.72, opacity=0.52, fill="none"),
    ]
    if royal:
        cs = h * 0.14
        cs_w = wt * 0.56
        out.append(el("path", fill="#588c36", d=(
            f"M{n(tx - cs_w)},{n(ty + 1)} Q{n(tx)},{n(ty + 2.2)} {n(tx + cs_w)},{n(ty + 1)} "
            f"L{n(tx + cs_w * 0.82)},{n(ty - cs)} Q{n(tx)},{n(ty - cs - 1.5)} {n(tx - cs_w * 0.82)},{n(ty - cs)}Z"
        )))
        out.append(el("path", fill="#385e20", opacity=0.52, d=(
            f"M{n(tx)},{n(ty + 1.6)} L{n(tx + cs_w)},{n(ty + 1)} "
            f"L{n(tx + cs_w * 0.82)},{n(ty - cs)} L{n(tx)},{n(ty - cs - 0.8)}Z"
        )))
        out.append(el("path", fill="#8cc458", opacity=0.48, d=(
            f"M{n(tx - cs_w * 0.85)},{n(ty + 1)} L{n(tx - cs_w * 0.32)},{n(ty + 1.4)} "
            f"L{n(tx - cs_w * 0.26)},{n(ty - cs)} L{n(tx - cs_w * 0.74)},{n(ty - cs)}Z"
        )))
        ty -= cs * 0.92
    else:
        # Woven fibrous petiole boots at the top of coconut/non-royal palm trunk
        boot_w = wt * 0.65
        out.append(el("path", fill=mix(trunk_col, "#3d2914", 0.35), d=(
            f"M{n(tx - boot_w)},{n(ty + 3)} L{n(tx - boot_w * 1.25)},{n(ty - 2)} "
            f"L{n(tx)},{n(ty - 4)} L{n(tx + boot_w * 1.25)},{n(ty - 2)} L{n(tx + boot_w)},{n(ty + 3)}Z"
        )))

    fronds_back, fronds_mid, fronds_front, fronds_spec = [], [], [], []
    # Central ascending spear leaves
    for sp_ang, sp_col in ((-96, dark), (-89, light), (-83, hl_leaf)):
        sa = math.radians(sp_ang + rng.uniform(-3, 3))
        s_len = L * rng.uniform(0.55, 0.74)
        sx_end = tx + math.cos(sa) * s_len
        sy_end = ty + math.sin(sa) * s_len
        fronds_mid.append(el("path", d=(
            f"M{n(tx - 0.8)},{n(ty + 1)} Q{n((tx + sx_end) * 0.5 - 1.8)},{n((ty + sy_end) * 0.5)} {n(sx_end)},{n(sy_end)} "
            f"Q{n((tx + sx_end) * 0.5 + 0.5)},{n((ty + sy_end) * 0.5)} {n(tx + 0.8)},{n(ty + 1)}Z"
        ), fill=sp_col))

    # Full radial fan of arching pinnate fronds with tapered lanceolate leaflet blades
    n_total = max(nfr, 14)
    for i in range(n_total):
        frac = i / max(1, n_total - 1)
        a_deg = -215 + 250 * frac + rng.uniform(-5.0, 5.0)
        a = math.radians(a_deg)
        dx, dy = math.cos(a), math.sin(a)
        Lf = L * rng.uniform(0.90, 1.14) * (0.86 if abs(frac - 0.5) < 0.16 else 1.0)
        horiz = abs(dx)
        gravity = Lf * (0.35 * (horiz ** 1.32) + (0.24 if dy > -0.15 else 0.05))
        end = (tx + dx * Lf * 0.96, ty + dy * Lf * 0.68 + gravity)
        c = (tx + dx * Lf * 0.52, ty + dy * Lf * 0.56 - Lf * (0.20 + 0.10 * horiz))
        rachis_d = (
            f"M{n(tx - 0.9)},{n(ty + 1)} Q{n(c[0])},{n(c[1] - 0.8)} {n(end[0])},{n(end[1])} "
            f"Q{n(c[0])},{n(c[1] + 0.7)} {n(tx + 0.9)},{n(ty + 1)}Z"
        )
        blade_polys = []
        n_leaflets = 19
        w_pinna = max(0.65, Lf * 0.024)
        for j in range(n_leaflets):
            t = 0.06 + 0.90 * j / (n_leaflets - 1)
            px, py = quad((tx, ty + 1), c, end, t)
            ux, uy = quad_tan((tx, ty + 1), c, end, t)
            nx_, ny_ = -uy, ux
            ln = Lf * 0.26 * math.sin(math.pi * min(1.0, 0.16 + t * 0.85)) * (1.0 - 0.16 * t)
            for side in (1, -1):
                tip_x = px + nx_ * side * ln * 0.72 + ux * ln * 0.44
                tip_y = py + ny_ * side * ln * 0.54 + uy * ln * 0.32 + ln * 0.56
                c1x = (px + tip_x) * 0.5 + ux * (ln * 0.16 + w_pinna) - ny_ * w_pinna * 0.4
                c1y = (py + tip_y) * 0.5 - ln * 0.10 + nx_ * w_pinna * 0.4
                c2x = (px + tip_x) * 0.5 + ux * (ln * 0.06 - w_pinna * 0.6)
                c2y = (py + tip_y) * 0.5 - ln * 0.02 + w_pinna * 0.6
                blade_polys.append(
                    f"M{n(px)},{n(py)} Q{n(c1x)},{n(c1y)} {n(tip_x)},{n(tip_y)} "
                    f"Q{n(c2x)},{n(c2y)} {n(px + ux * w_pinna * 0.5)},{n(py + uy * w_pinna * 0.5)}Z"
                )
        layer_idx = i % 4
        col_f = deep_leaf if layer_idx == 0 else (dark if layer_idx == 1 else (mid_leaf if layer_idx == 2 else (light if i % 2 == 0 else hl_leaf)))
        frond = [
            el("path", d=" ".join(blade_polys), fill=col_f),
            el("path", d=rachis_d, fill=mix(col_f, "#c4d668" if layer_idx >= 2 else "#142610", 0.28)),
        ]
        if layer_idx == 0:
            fronds_back.extend(frond)
        elif layer_idx == 1:
            fronds_mid.extend(frond)
        elif layer_idx == 2:
            fronds_front.extend(frond)
        else:
            fronds_spec.extend(frond)

    crown_g = [g(fronds_back), g(fronds_mid)]
    if coconuts and not royal:
        c_items = []
        for ox, oy in ((-wb * 0.54, 1.2), (wb * 0.54, 1.6), (0, wb * 0.64), (-wb * 0.24, wb * 0.34), (wb * 0.26, wb * 0.38)):
            c_items.append(el("circle", cx=tx + ox, cy=ty + 3.0 + oy, r=wb * 0.46, fill="#4d3214"))
            c_items.append(el("circle", cx=tx + ox - 0.5, cy=ty + 2.4 + oy, r=wb * 0.22, fill="#8f6432"))
        crown_g.append(g(c_items))
    crown_g.extend([g(fronds_front), g(fronds_spec)])
    out.append(g(crown_g))
    return g(out)


def tufts(rng, x0, x1, ground, count, h, col, width=1.1, op=1.0):
    segs = []
    segs_hi = []
    hi_col = mix(col, "#fff6c8", 0.32)
    for idx in range(count):
        x = rng.uniform(x0, x1)
        y = ground(x) + 1
        for b in range(rng.randint(4, 7)):
            dx = rng.uniform(-h * 0.55, h * 0.55)
            hh = h * rng.uniform(0.5, 1.15)
            cmd = f"M{n(x)},{n(y)} q{n(dx * 0.25)},{n(-hh * 0.62)} {n(dx)},{n(-hh)}"
            if b == 0 and idx % 2 == 0:
                segs_hi.append(cmd)
            else:
                segs.append(cmd)
    return g([
        el("path", d=" ".join(segs), stroke=col, stroke_width=width, fill="none", stroke_linecap="round", opacity=op),
        el("path", d=" ".join(segs_hi), stroke=hi_col, stroke_width=width * 0.85, fill="none", stroke_linecap="round", opacity=op * 0.85),
    ])


def canopy_band(s: Scene, x0, x1, ground, count, rmin, rmax, cols, lift=0.0, flat=0.76, k=5, detail=False):
    rng = s.rng
    trees = []
    for _ in range(count):
        x = rng.uniform(x0, x1)
        r = rng.uniform(rmin, rmax)
        trees.append((ground(x) - lift - r * 0.38 + rng.uniform(-r * 0.18, r * 0.18), x, r))
    trees.sort()
    return [crown(rng, x, y, r, cols, k=k, flat=flat, detail=detail) for y, x, r in trees]


def fern(rng, x, y, L, col, n_fronds=7, droop=0.48):
    segs_dark, segs_light = [], []
    dark = mix(col, "#0d2612", 0.3)
    light = mix(col, "#b8e068", 0.25)
    for i in range(n_fronds):
        a = math.radians(-165 + 150 * i / max(1, n_fronds - 1) + rng.uniform(-5, 5))
        Lf = L * rng.uniform(0.78, 1.08)
        end = (x + math.cos(a) * Lf, y + math.sin(a) * Lf * 0.58 + Lf * droop * (1 - abs(math.sin(a))))
        c = (x + math.cos(a) * Lf * 0.5, y + math.sin(a) * Lf * 0.68 - Lf * 0.12)
        target = segs_dark if i % 2 == 0 else segs_light
        target.append(f"M{n(x)},{n(y)} Q{n(c[0])},{n(c[1])} {n(end[0])},{n(end[1])}")
        for j in range(11):
            t = 0.12 + 0.82 * j / 10
            px, py = quad((x, y), c, end, t)
            ux, uy = quad_tan((x, y), c, end, t)
            ln = Lf * 0.15 * math.sin(math.pi * (0.2 + 0.75 * (1 - t)))
            for side in (1, -1):
                target.append(f"M{n(px)},{n(py)} l{n(-uy * side * ln + ux * ln * 0.28)},{n(ux * side * ln + ln * 0.25)}")
    return g([
        el("path", d=" ".join(segs_dark), stroke=dark, stroke_width=1.35, fill="none", stroke_linecap="round"),
        el("path", d=" ".join(segs_light), stroke=light, stroke_width=1.2, fill="none", stroke_linecap="round"),
    ])


def heliconia(x, y, h, stem="#2f5e25", bract="#d93824", tip="#f5c72c"):
    """Detailed tropical Heliconia rostrata / bihai with broad paddle leaves and layered claw bracts."""
    out = [
        # Broad banana-like paddle leaves with central midribs
        el("path", fill="#2b5e24", d=(
            f"M{n(x)},{n(y - h * 0.15)} Q{n(x - h * 0.52)},{n(y - h * 0.45)} {n(x - h * 0.72)},{n(y - h * 0.18)} "
            f"Q{n(x - h * 0.38)},{n(y - h * 0.02)} {n(x)},{n(y - h * 0.12)}Z")),
        el("path", fill="#428236", d=(
            f"M{n(x)},{n(y - h * 0.25)} Q{n(x + h * 0.55)},{n(y - h * 0.58)} {n(x + h * 0.74)},{n(y - h * 0.30)} "
            f"Q{n(x + h * 0.38)},{n(y - h * 0.10)} {n(x)},{n(y - h * 0.22)}Z")),
        el("path", fill="#549842", d=(
            f"M{n(x)},{n(y - h * 0.32)} Q{n(x - h * 0.38)},{n(y - h * 0.72)} {n(x - h * 0.48)},{n(y - h * 0.52)} "
            f"Q{n(x - h * 0.22)},{n(y - h * 0.28)} {n(x)},{n(y - h * 0.30)}Z")),
        el("path", d=f"M{n(x)},{n(y)} Q{n(x - 3)},{n(y - h * 0.5)} {n(x + 2)},{n(y - h)}", stroke=stem, stroke_width=2.2, fill="none"),
    ]
    bracts_red, bracts_tip = [], []
    for i in range(6):
        by = y - h * 0.42 - i * h * 0.095
        side = 1 if i % 2 else -1
        bx = x + 1 + (i * 0.2)
        bracts_red.append(f"M{n(bx)},{n(by)} Q{n(bx + side * 8)},{n(by - 1)} {n(bx + side * 12)},{n(by - 5)} Q{n(bx + side * 5)},{n(by - 7)} {n(bx)},{n(by - 4.5)}Z")
        bracts_tip.append(f"M{n(bx + side * 7)},{n(by - 3.2)} L{n(bx + side * 12)},{n(by - 5)} L{n(bx + side * 8)},{n(by - 5.8)}Z")
    out.append(el("path", d=" ".join(bracts_red), fill=bract))
    out.append(el("path", d=" ".join(bracts_tip), fill=tip))
    return g(out)


def bromeliad(rng, x, y, s, col="#689a38", flower="#e63e2b"):
    leaves_back, leaves_front = [], []
    for i in range(11):
        a = math.radians(-175 + 170 * i / 10)
        ex, ey = x + math.cos(a) * s * 1.15, y + math.sin(a) * s * 0.65
        cx_, cy_ = x + math.cos(a) * s * 0.55, y + math.sin(a) * s * 1.05
        d = f"M{n(x - 1.5)},{n(y)} Q{n(cx_)},{n(cy_)} {n(ex)},{n(ey)} Q{n(cx_)},{n(cy_ + 2.5)} {n(x + 1.5)},{n(y)}Z"
        (leaves_back if i % 2 == 0 else leaves_front).append(el("path", d=d, fill=mix(col, "#1e3d14", 0.25) if i % 2 == 0 else col))
    spike = [
        el("path", d=f"M{n(x - 2.5)},{n(y - 1)} Q{n(x - 3)},{n(y - s * 0.6)} {n(x)},{n(y - s * 1.05)} Q{n(x + 3)},{n(y - s * 0.6)} {n(x + 2.5)},{n(y - 1)}Z", fill=flower),
        el("circle", cx=x, cy=y - s * 0.95, r=1.4, fill="#ffdf4f"),
    ]
    return g([*leaves_back, *spike, *leaves_front])


def ipe(rng, x, y, h, bloom="#f4c424", bloom2="#d99412", trunk_col="#473628"):
    """Twisted Cerrado Handroanthus (Ipê-amarelo / Ipê-rosa) with gnarled bark, forked boughs, and trumpet-flower crown."""
    tx = x + rng.uniform(-h * 0.08, h * 0.08)
    ty = y - h * 0.56
    lit_bark = mix(trunk_col, "#c8b294", 0.28)
    out = [el("ellipse", cx=x, cy=y + 1, rx=h * 0.24, ry=h * 0.035, fill="#000000", opacity=0.2)]
    out += trunk(x, y, ty, max(4.2, h * 0.09), max(2.8, h * 0.05), trunk_col, bend=tx - x)
    subs = [
        (-0.48, -0.26, 0.56),
        (0.46, -0.24, 0.54),
        (-0.20, -0.40, 0.66),
        (0.22, -0.36, 0.62),
        (0.0, -0.44, 0.58),
    ]
    for dx, dy, sc in subs:
        bx, by = tx + dx * h, ty + dy * h
        c1x, c1y = tx + dx * h * 0.25 + rng.uniform(-5, 5), ty - h * 0.14
        c2x, c2y = tx + dx * h * 0.72 + rng.uniform(-5, 5), by + h * 0.08
        wb = max(1.8, h * 0.042 * sc)
        d_b = f"M{n(tx)},{n(ty + 3)} C{n(c1x)},{n(c1y)} {n(c2x)},{n(c2y)} {n(bx)},{n(by)}"
        out.append(el("path", d=d_b, stroke=trunk_col, stroke_width=wb, fill="none", stroke_linecap="round"))
        out.append(el("path", d=d_b, stroke=lit_bark, stroke_width=wb * 0.35, fill="none", stroke_linecap="round", opacity=0.55))
        # Secondary twig fork
        tx2, ty2 = bx + dx * h * 0.18, by - h * 0.08
        out.append(el("path", d=f"M{n(( tx + bx ) * 0.5)},{n(( ty + by ) * 0.5)} Q{n(bx)},{n(by)} {n(tx2)},{n(ty2)}",
                      stroke=trunk_col, stroke_width=wb * 0.55, fill="none", stroke_linecap="round"))
    for dx, dy, sc in subs:
        out.append(crown(rng, tx + dx * h, ty + dy * h, h * 0.25 * sc,
                         (mix(bloom2, "#6e3400", 0.28), bloom2, mix(bloom, "#ffffff", 0.38)), k=7, flat=0.60))
    # Fallen golden/pink blossoms carpeting the ground beneath the tree
    petals = [el("ellipse", cx=x + rng.uniform(-h * 0.44, h * 0.44), cy=y + rng.uniform(-2, 5),
                 rx=rng.uniform(1.6, 2.8), ry=rng.uniform(0.7, 1.2), fill=bloom if i % 2 == 0 else bloom2)
              for i in range(14)]
    out.append(g(petals, opacity=0.85))
    return g(out)


def gnarled_tree(rng, x, y, h, leaf=("#2f4f22", "#4c7232", "#789e4c"), trunk_col="#3d2f24"):
    """Tortuous fire-adapted Cerrado tree (Qualea / Caryocar) with corky S-curved trunk and umbrella crown."""
    tx = x + rng.uniform(-h * 0.14, h * 0.14)
    ty = y - h * 0.54
    lit_bark = mix(trunk_col, "#ccb89e", 0.28)
    out = [el("ellipse", cx=x, cy=y + 1, rx=h * 0.22, ry=h * 0.035, fill="#000000", opacity=0.2)]
    out += trunk(x, y, ty, max(3.8, h * 0.085), max(2.4, h * 0.048), trunk_col, bend=tx - x)
    branches = [
        (-0.46, -0.82, 0.21),
        (0.42, -0.84, 0.20),
        (-0.14, -0.96, 0.23),
        (0.18, -0.93, 0.19),
    ]
    for dx, dy, r_sc in branches:
        cx, cy = tx + dx * h, y + dy * h
        c1x = tx - dx * h * 0.15 + rng.uniform(-6, 6)
        c1y = ty + (cy - ty) * 0.35
        c2x = tx + dx * h * 0.78 + rng.uniform(-6, 6)
        c2y = ty + (cy - ty) * 0.72
        wb = max(1.6, h * 0.038)
        d_b = f"M{n(tx)},{n(ty + 3)} C{n(c1x)},{n(c1y)} {n(c2x)},{n(c2y)} {n(cx)},{n(cy)}"
        out.append(el("path", d=d_b, stroke=trunk_col, stroke_width=wb, fill="none", stroke_linecap="round"))
        out.append(el("path", d=d_b, stroke=lit_bark, stroke_width=wb * 0.35, fill="none", stroke_linecap="round", opacity=0.5))
    for dx, dy, r_sc in branches:
        cx, cy = tx + dx * h, y + dy * h
        out.append(crown(rng, cx, cy, h * r_sc, leaf, k=6, flat=0.58))
    return g(out)


def cactus(x, y, h, col="#4f7d52", rib="#2f5236"):
    """Realistic Mandacaru / Cereus columnar cactus with constricted arm joints, fluted 3D ribs, fine radial spines, and cupped blooms."""
    w = max(5.4, h * 0.125)
    lit = mix(col, "#c4e2a4", 0.32)
    shade = mix(col, "#152b1a", 0.42)
    out = [
        # Ground shadow
        el("ellipse", cx=x + 2, cy=y + 1, rx=w * 1.55, ry=w * 0.34, fill="#000000", opacity=0.24),
    ]
    # Arms with constricted joint attachment, upward elbow, and 3D fluted ribs
    arms = [
        (-1, 0.38, 0.38, 2.02),
        (1, 0.48, 0.36, 1.86),
        (-1, 0.67, 0.24, 1.32),
        (1, 0.75, 0.19, 1.20),
    ]
    arm_w = w * 0.72
    r_arm = arm_w * 0.5
    for idx, (side, at, ah, reach) in enumerate(arms):
        ay = y - h * at
        ax = x + side * w * reach
        top_y = ay - h * ah
        jx = x + side * w * 0.32
        # Sculpted arm polygon with constricted joint neck and rounded apex
        arm_poly = (
            f"M{n(jx)},{n(ay - r_arm * 0.55)} "
            f"C{n(x + side * w * reach * 0.65)},{n(ay - r_arm * 0.52)} {n(ax - side * r_arm)},{n(ay - r_arm * 0.9)} {n(ax - side * r_arm)},{n(ay - r_arm * 1.6)} "
            f"L{n(ax - side * r_arm)},{n(top_y + r_arm)} "
            f"A{n(r_arm)},{n(r_arm)} 0 0 {1 if side > 0 else 0} {n(ax + side * r_arm)},{n(top_y + r_arm)} "
            f"L{n(ax + side * r_arm)},{n(ay - r_arm * 1.1)} "
            f"C{n(ax + side * r_arm)},{n(ay + r_arm * 0.55)} {n(x + side * w * reach * 0.68)},{n(ay + r_arm * 0.62)} {n(jx)},{n(ay + r_arm * 0.52)}Z"
        )
        out.append(el("path", d=arm_poly, fill=col))
        # Shaded right side of arm and sunlit left side
        sh_x = ax + r_arm * 0.15
        lit_x = ax - r_arm * 0.35
        out.append(el("rect", x=ax if side > 0 else ax, y=top_y + r_arm * 0.5, width=r_arm * 0.85, height=max(4, ay - top_y - r_arm),
                      rx=r_arm * 0.35, fill=shade, opacity=0.38))
        out.append(el("rect", x=lit_x - r_arm * 0.35, y=top_y + r_arm * 0.6, width=r_arm * 0.45, height=max(4, ay - top_y - r_arm * 1.2),
                      rx=r_arm * 0.2, fill=lit, opacity=0.45))
        # Fluted rib grooves & marginal spines along arm
        out.append(el("path", d=f"M{n(ax - arm_w * 0.17)},{n(ay - arm_w * 0.65)} L{n(ax - arm_w * 0.17)},{n(top_y + r_arm * 0.9)} "
                                f"M{n(ax + arm_w * 0.17)},{n(ay - arm_w * 0.65)} L{n(ax + arm_w * 0.17)},{n(top_y + r_arm * 0.9)}",
                      stroke=rib, stroke_width=0.68, fill="none", opacity=0.68))
        # Cupped side-profile nocturnal Cereus flower on the first two major arms
        if idx < 2 and h >= 50:
            fx, fy = ax + side * r_arm * 0.65, top_y + r_arm * 1.2
            out.append(g([
                el("path", d=f"M{n(fx - side * 1.5)},{n(fy + 0.8)} Q{n(fx + side * 1.2)},{n(fy - 1.2)} {n(fx + side * 3.2)},{n(fy - 2.2)} "
                             f"L{n(fx + side * 2.6)},{n(fy + 0.5)}Z", fill="#6b944c"),
                el("path", d=f"M{n(fx + side * 2.4)},{n(fy - 1.6)} C{n(fx + side * 4.5)},{n(fy - 4.2)} {n(fx + side * 6.2)},{n(fy - 3.2)} "
                             f"{n(fx + side * 5.2)},{n(fy - 0.6)} C{n(fx + side * 6.0)},{n(fy + 0.8)} {n(fx + side * 3.8)},{n(fy + 1.2)} "
                             f"{n(fx + side * 2.2)},{n(fy + 0.2)}Z", fill="#fffdf7"),
                el("circle", cx=fx + side * 4.2, cy=fy - 1.4, r=w * 0.08, fill="#f2c938"),
            ]))

    # Main central stem with tapered base, 3D cylindrical shading, and fluted ribs
    hw = w * 0.5
    stem_d = (
        f"M{n(x - hw * 0.88)},{n(y)} L{n(x - hw)},{n(y - h + hw)} "
        f"A{n(hw)},{n(hw)} 0 0 1 {n(x + hw)},{n(y - h + hw)} "
        f"L{n(x + hw * 0.88)},{n(y)} Q{n(x)},{n(y + 1.5)} {n(x - hw * 0.88)},{n(y)}Z"
    )
    out.append(el("path", d=stem_d, fill=col))
    out.append(el("rect", x=x + w * 0.04, y=y - h + 1, width=w * 0.44, height=h - 1, rx=w * 0.20, fill=shade, opacity=0.42))
    out.append(el("rect", x=x - w * 0.36, y=y - h + 2, width=w * 0.22, height=h - 4, rx=w * 0.1, fill=lit, opacity=0.50))
    # Fluted vertical ribs and delicate areole spine tufts
    ribs, areoles, spines = [], [], []
    for f in (-0.28, -0.04, 0.22):
        rx_ = x + w * f
        ribs.append(f"M{n(rx_)},{n(y - h + w * 0.42)} L{n(rx_)},{n(y - 2)}")
        step_y = max(7, int(h * 0.10))
        for sy in range(int(y - h + w * 0.65), int(y - 5), step_y):
            areoles.append(el("circle", cx=rx_, cy=sy, r=0.65, fill="#d8ccb8", opacity=0.75))
            spines.append(f"M{n(rx_)},{n(sy)} l-1.8,-0.9 M{n(rx_)},{n(sy)} l1.8,-0.8 M{n(rx_)},{n(sy)} l-1.6,0.8")
    # Marginal profile spines along left and right edges
    for sy in range(int(y - h + w * 0.7), int(y - 6), max(8, int(h * 0.11))):
        spines.append(f"M{n(x - w * 0.5)},{n(sy)} l-2.0,-0.8 M{n(x + w * 0.5)},{n(sy)} l2.0,-0.8")
    out.append(el("path", d=" ".join(ribs), stroke=rib, stroke_width=0.85, fill="none", opacity=0.72))
    out.append(el("path", d=" ".join(spines), stroke="#e6dcc8", stroke_width=0.45, fill="none", opacity=0.58))
    out.extend(areoles)
    # Sculpted nocturnal Mandacaru blossom on upper crown
    bx, by = x - w * 0.18, y - h + 1.2
    out.append(g([
        el("path", d=f"M{n(bx - w * 0.12)},{n(by + 2)} Q{n(bx - w * 0.25)},{n(by - w * 0.25)} {n(bx)},{n(by - w * 0.32)} "
                     f"Q{n(bx + w * 0.25)},{n(by - w * 0.25)} {n(bx + w * 0.12)},{n(by + 2)}Z", fill="#8ab068"),
        el("ellipse", cx=bx - w * 0.14, cy=by - w * 0.22, rx=w * 0.22, ry=w * 0.11,
           transform=f"rotate(-28 {n(bx - w * 0.14)} {n(by - w * 0.22)})", fill="#f5f0e2"),
        el("ellipse", cx=bx + w * 0.14, cy=by - w * 0.22, rx=w * 0.22, ry=w * 0.11,
           transform=f"rotate(28 {n(bx + w * 0.14)} {n(by - w * 0.22)})", fill="#fffdf7"),
        el("ellipse", cx=bx, cy=by - w * 0.26, rx=w * 0.15, ry=w * 0.22, fill="#ffffff"),
        el("circle", cx=bx, cy=by - w * 0.20, r=w * 0.10, fill="#f2c938"),
    ]))
    return g(out)


def thorn_bush(rng, x, y, s, col="#786b56", leaf="#9aa66e"):
    segs_main, segs_twigs = [], []
    dots = []
    for _ in range(10):
        a = math.radians(rng.uniform(-168, -12))
        L = s * rng.uniform(0.55, 1.08)
        ex, ey = x + math.cos(a) * L, y + math.sin(a) * L * 0.78
        cx_, cy_ = (x + ex) * 0.5 + rng.uniform(-4, 4), (y + ey) * 0.5 - rng.uniform(1, 5)
        segs_main.append(f"M{n(x)},{n(y)} Q{n(cx_)},{n(cy_)} {n(ex)},{n(ey)}")
        for _ in range(3):
            t = rng.uniform(0.35, 0.92)
            px, py = quad((x, y), (cx_, cy_), (ex, ey), t)
            tx_, ty_ = px + rng.uniform(-s * 0.28, s * 0.28), py - rng.uniform(2, s * 0.28)
            segs_twigs.append(f"M{n(px)},{n(py)} L{n(tx_)},{n(ty_)}")
            dots.append(el("circle", cx=tx_, cy=ty_, r=rng.uniform(1.1, 2.2)))
    return g([
        el("ellipse", cx=x, cy=y + 1, rx=s * 0.65, ry=s * 0.14, fill="#000000", opacity=0.18),
        el("path", d=" ".join(segs_main), stroke=col, stroke_width=1.35, fill="none", stroke_linecap="round"),
        el("path", d=" ".join(segs_twigs), stroke=mix(col, "#3b3228", 0.3), stroke_width=0.8, fill="none", stroke_linecap="round"),
        g(dots, fill=leaf, opacity=0.85),
    ])


def termite_mound(x, y, h, col="#a85d34"):
    """Sculpted cathedral termite mound with buttressed flutes, vents, and warm laterite shading."""
    w = h * 0.58
    lit = mix(col, "#f0b478", 0.28)
    shade = mix(col, "#2e1508", 0.42)
    return g([
        el("ellipse", cx=x + 2, cy=y + 1, rx=w * 1.15, ry=w * 0.22, fill="#000000", opacity=0.24),
        # Main multi-spired silhouette
        el("path", d=(
            f"M{n(x - w)},{n(y)} Q{n(x - w * 0.85)},{n(y - h * 0.45)} {n(x - w * 0.52)},{n(y - h * 0.72)} "
            f"Q{n(x - w * 0.35)},{n(y - h * 0.62)} {n(x - w * 0.14)},{n(y - h)} "
            f"Q{n(x + w * 0.12)},{n(y - h * 0.96)} {n(x + w * 0.25)},{n(y - h * 0.68)} "
            f"Q{n(x + w * 0.48)},{n(y - h * 0.78)} {n(x + w * 0.58)},{n(y - h * 0.48)} "
            f"Q{n(x + w * 0.82)},{n(y - h * 0.22)} {n(x + w)},{n(y)}Z"), fill=col),
        # Sunlit left buttress ridges
        el("path", d=(
            f"M{n(x - w * 0.88)},{n(y)} Q{n(x - w * 0.7)},{n(y - h * 0.42)} {n(x - w * 0.52)},{n(y - h * 0.72)} "
            f"Q{n(x - w * 0.3)},{n(y - h * 0.35)} {n(x - w * 0.35)},{n(y)}Z"), fill=lit, opacity=0.55),
        # Shadowed right face
        el("path", d=(
            f"M{n(x - w * 0.05)},{n(y)} Q{n(x + w * 0.05)},{n(y - h * 0.55)} {n(x - w * 0.14)},{n(y - h)} "
            f"Q{n(x + w * 0.12)},{n(y - h * 0.96)} {n(x + w * 0.25)},{n(y - h * 0.68)} "
            f"Q{n(x + w * 0.48)},{n(y - h * 0.78)} {n(x + w * 0.58)},{n(y - h * 0.48)} "
            f"Q{n(x + w * 0.82)},{n(y - h * 0.22)} {n(x + w)},{n(y)}Z"), fill=shade, opacity=0.52),
        # Ventilation pores
        el("ellipse", cx=x - w * 0.18, cy=y - h * 0.45, rx=w * 0.08, ry=h * 0.05, fill=shade, opacity=0.7),
        el("ellipse", cx=x + w * 0.15, cy=y - h * 0.32, rx=w * 0.09, ry=h * 0.055, fill=shade, opacity=0.7),
        el("ellipse", cx=x - w * 0.42, cy=y - h * 0.24, rx=w * 0.07, ry=h * 0.045, fill=shade, opacity=0.7),
    ])


def water_lily(rng, x, y, r, flower=False):
    """Giant Amazonian Victoria amazonica water lily pad with upturned crimson rim and radiating venation."""
    notch = rng.uniform(0, TAU)
    ry = r * 0.32
    veins = []
    for k in range(10):
        a = TAU * k / 10
        if abs((a - notch + math.pi) % TAU - math.pi) < 0.25:
            continue
        veins.append(f"M{n(x)},{n(y - 1)} L{n(x + math.cos(a) * r * 0.88)},{n(y - 1 + math.sin(a) * ry * 0.88)}")
    out = [
        # Drop shadow on water
        el("ellipse", cx=x + 1, cy=y + 2.2, rx=r * 1.03, ry=ry * 1.06, fill="#0c1f14", opacity=0.38),
        # Crimson-bronze outer upturned rim wall
        el("ellipse", cx=x, cy=y + 0.8, rx=r, ry=ry, fill="#8c322b"),
        el("ellipse", cx=x, cy=y - 0.5, rx=r, ry=ry, fill="#a84438"),
        # Lush green inner tray
        el("ellipse", cx=x, cy=y - 1.0, rx=r * 0.92, ry=ry * 0.86, fill="#3c7d36"),
        el("ellipse", cx=x - r * 0.08, cy=y - 1.2, rx=r * 0.78, ry=ry * 0.72, fill="#5ca044"),
        # Radial rib veins
        el("path", d=" ".join(veins), stroke="#7ec258", stroke_width=0.75, opacity=0.75),
        # Drainage notch
        el("path", d=f"M{n(x)},{n(y - 1)} L{n(x + math.cos(notch) * r * 1.02)},{n(y + math.sin(notch) * ry * 1.02)}",
           stroke="#2a4d24", stroke_width=1.2),
    ]
    if flower or r > 25:
        fx, fy = x + r * 0.25, y - 2
        out.append(g([
            el("ellipse", cx=fx, cy=fy, rx=r * 0.22, ry=r * 0.11, fill="#f7e6ee"),
            el("ellipse", cx=fx, cy=fy - 1, rx=r * 0.16, ry=r * 0.08, fill="#fff7fa"),
            el("circle", cx=fx, cy=fy - 1.2, r=r * 0.06, fill="#e87ca8"),
        ]))
    return g(out)


def water_lines(rng, x0, x1, y0, y1, count, col="#ffffff", op=0.35, w=1.0):
    """Perspective-graded water surface shimmer bands, broken specular sun-glitter facets, and gentle wavelets."""
    shimmer_bands, segs, glints = [], [], []
    span_x = max(10, x1 - x0)
    for i in range(count):
        x = rng.uniform(x0, x1)
        y = rng.uniform(y0, y1)
        t = (y - y0) / max(1, (y1 - y0))
        L = rng.uniform(12, 48) * (0.40 + 0.85 * t)
        x_end = min(x1 + 8, x + L)
        L_act = max(6.0, x_end - x)
        if i % 4 == 0:
            # Soft horizontal lenticular shimmer ribbon
            rx = L_act * 0.48
            ry = max(0.45, (0.45 + 0.65 * t) * w)
            cx = x + rx
            shimmer_bands.append(
                f"M{n(cx - rx)},{n(y)} Q{n(cx)},{n(y - ry * 1.4)} {n(cx + rx)},{n(y)} "
                f"Q{n(cx)},{n(y + ry * 1.1)} {n(cx - rx)},{n(y)}Z"
            )
        else:
            segs.append(f"M{n(x)},{n(y)} q{n(L_act * 0.25)},{n(-0.75 * (0.6 + 0.5 * t))} {n(L_act * 0.5)},0 t{n(L_act * 0.5)},0")
            if i % 3 == 1 and span_x > 30:
                gx = x + L_act * rng.uniform(0.2, 0.8)
                glints.append(f"M{n(gx)},{n(y - 1.1)} L{n(gx + 3.5 + 3 * t)},{n(y - 1.1)}")
    return g([
        el("path", d=" ".join(shimmer_bands), fill=col, opacity=op * 0.52),
        el("path", d=" ".join(segs), stroke=col, stroke_width=w * 0.92, fill="none", opacity=op, stroke_linecap="round"),
        el("path", d=" ".join(glints), stroke="#ffffff", stroke_width=w * 1.15, fill="none", opacity=min(0.95, op * 1.35), stroke_linecap="round"),
    ])


def waterfall(s: Scene, x, y_top, y_bot, w, col="#e8f6fc"):
    """Dramatic multi-layered cataract with wet recessed rock chute, turquoise-emerald brink lip, split rock ledges, lacy spray veils, and radiating plunge foam rings."""
    rng = s.rng
    h = y_bot - y_top
    wb = w * 1.54
    wf_id = f"wf-{int(x)}-{int(y_top)}-{rng.randint(10, 99)}"
    wf_grad = s.linear(wf_id, [
        (0, "#5ad2df", 0.86),
        (0.12, "#a8eef7", 0.90),
        (0.28, col, 0.92),
        (0.78, "#ffffff", 0.88),
        (1, "#ffffff", 0.14),
    ])
    core_grad = s.linear(f"{wf_id}-core", [
        (0, "#d4fbff", 0.78),
        (0.25, "#ffffff", 0.94),
        (0.82, "#ecf9fe", 0.80),
        (1, "#ffffff", 0.10),
    ])
    out = [
        # Deep wet dark rock chute & glistening cliff margin behind the falling water
        el("path", d=(
            f"M{n(x - w * 0.62)},{n(y_top)} Q{n(x)},{n(y_top - 2.0)} {n(x + w * 0.62)},{n(y_top)} "
            f"C{n(x + w * 0.70)},{n(y_top + h * 0.42)} {n(x + wb * 0.68)},{n(y_top + h * 0.78)} {n(x + wb * 0.70)},{n(y_bot)} "
            f"L{n(x - wb * 0.70)},{n(y_bot)} "
            f"C{n(x - wb * 0.68)},{n(y_top + h * 0.78)} {n(x - w * 0.70)},{n(y_top + h * 0.42)} {n(x - w * 0.62)},{n(y_top)}Z"
        ), fill="#121e24", opacity=0.56),
        # Outer gossamer spray veil
        el("path", d=(
            f"M{n(x - w * 0.52)},{n(y_top + 1)} Q{n(x)},{n(y_top - 1.0)} {n(x + w * 0.52)},{n(y_top + 1)} "
            f"C{n(x + w * 0.62)},{n(y_top + h * 0.44)} {n(x + wb * 0.60)},{n(y_top + h * 0.80)} {n(x + wb * 0.64)},{n(y_bot)} "
            f"L{n(x - wb * 0.64)},{n(y_bot)} "
            f"C{n(x - wb * 0.60)},{n(y_top + h * 0.80)} {n(x - w * 0.62)},{n(y_top + h * 0.44)} {n(x - w * 0.52)},{n(y_top + 1)}Z"
        ), fill="#bfeef7", opacity=0.28),
        # Main sculpted turquoise-to-white water curtain
        el("path", d=(
            f"M{n(x - w * 0.48)},{n(y_top)} Q{n(x)},{n(y_top - 1.2)} {n(x + w * 0.48)},{n(y_top)} "
            f"C{n(x + w * 0.54)},{n(y_top + h * 0.42)} {n(x + wb * 0.52)},{n(y_top + h * 0.78)} {n(x + wb * 0.56)},{n(y_bot)} "
            f"L{n(x - wb * 0.56)},{n(y_bot)} "
            f"C{n(x - wb * 0.52)},{n(y_top + h * 0.78)} {n(x - w * 0.54)},{n(y_top + h * 0.42)} {n(x - w * 0.48)},{n(y_top)}Z"
        ), fill=wf_grad),
    ]
    # Multi-tongue whitewater plumes inside the curtain for natural volumetric flow
    for p_off, p_scale in ((-0.26, 0.34), (0.0, 0.38), (0.24, 0.36)):
        px0 = x + w * p_off
        px1 = x + wb * p_off * 1.06
        pw0 = w * p_scale * 0.48
        pw1 = wb * p_scale * 0.52
        out.append(el("path", d=(
            f"M{n(px0 - pw0)},{n(y_top + 1)} Q{n(px0)},{n(y_top - 0.5)} {n(px0 + pw0)},{n(y_top + 1)} "
            f"C{n(px0 + pw0 * 1.1)},{n(y_top + h * 0.45)} {n(px1 + pw1)},{n(y_top + h * 0.78)} {n(px1 + pw1)},{n(y_bot)} "
            f"L{n(px1 - pw1)},{n(y_bot)} "
            f"C{n(px1 - pw1)},{n(y_top + h * 0.78)} {n(px0 - pw0 * 1.1)},{n(y_top + h * 0.45)} {n(px0 - pw0)},{n(y_top + 1)}Z"
        ), fill=core_grad))

    # Wet dark craggy rock dividers peeking through the upper lip and mid-face of cataracts
    if w >= 16:
        for r_off, r_y_frac in ((-0.16, 0.02), (0.17, 0.02), (-0.04, 0.38)):
            rx_ = x + w * r_off + rng.uniform(-1.2, 1.2)
            ry_ = y_top + h * r_y_frac
            rh_ = min(24, h * rng.uniform(0.14, 0.22))
            rw_ = max(1.6, w * 0.062)
            out.append(el("path", d=(
                f"M{n(rx_ - rw_)},{n(ry_)} L{n(rx_)},{n(ry_ - 2)} L{n(rx_ + rw_)},{n(ry_)} "
                f"L{n(rx_ + rw_ * 0.3)},{n(ry_ + rh_)} L{n(rx_ - rw_ * 0.4)},{n(ry_ + rh_ * 0.85)}Z"
            ), fill="#1b2830", opacity=0.58))
            out.append(el("path", d=f"M{n(rx_ - rw_ * 0.8)},{n(ry_)} L{n(rx_ - rw_ * 0.2)},{n(ry_ + rh_ * 0.7)}",
                          stroke="#5d7582", stroke_width=0.8, fill="none", opacity=0.45))

    # Mid-cliff rock shelf rebound splash plumes
    for frac in (0.34, 0.66):
        ly = y_top + h * frac + rng.uniform(-2, 2)
        lw = (w * (1 - frac) + wb * frac) * 0.46
        step_pts = [(x + (j / 6 - 0.5) * lw * 1.65, ly + rng.uniform(-1.2, 1.4)) for j in range(7)]
        out.append(el("path", d=smooth(step_pts), stroke="#ffffff", stroke_width=max(1.4, w * 0.065),
                      fill="none", stroke_linecap="round", opacity=0.48))

    # Continuous cascading water ribbons and fine silky threads
    ribbons_bg, strands_mid, strands_fg = [], [], []
    n_strands = int(w / 1.5) + 8
    for i in range(n_strands):
        t = (i / max(1, n_strands - 1)) - 0.5
        sx = x + t * w * 0.90 + rng.uniform(-1.0, 1.0)
        ex = x + t * wb * 0.96 + rng.uniform(-3.0, 3.0)
        mx1 = sx + (ex - sx) * 0.33 + rng.uniform(-2.2, 2.2)
        mx2 = sx + (ex - sx) * 0.68 + rng.uniform(-3.0, 3.0)
        y_start = y_top + (0 if i % 3 != 2 else h * rng.uniform(0.05, 0.28))
        y_end = y_bot - (0 if i % 4 != 3 else h * rng.uniform(0.04, 0.18))
        path_d = f"M{n(sx)},{n(y_start)} C{n(mx1)},{n(y_top + h * 0.34)} {n(mx2)},{n(y_top + h * 0.68)} {n(ex)},{n(y_end)}"
        if i % 3 == 0:
            ribbons_bg.append(path_d)
        elif i % 3 == 1:
            strands_mid.append(path_d)
        else:
            strands_fg.append(path_d)

    out.append(el("path", d=" ".join(ribbons_bg), stroke="#9ce0f5", stroke_width=1.9, opacity=0.65, fill="none", stroke_linecap="round"))
    out.append(el("path", d=" ".join(strands_mid), stroke="#e4f7ff", stroke_width=1.2, opacity=0.82, fill="none", stroke_linecap="round"))
    out.append(el("path", d=" ".join(strands_fg), stroke="#ffffff", stroke_width=0.85, opacity=0.94, fill="none", stroke_linecap="round"))

    # Emerald-turquoise over-the-brink lip & boiling aerated plunge pool foam rings
    lip_pts = [(x + (i / 8 - 0.5) * w * 0.96, y_top + rng.uniform(-0.6, 1.5)) for i in range(9)]
    base_pts = [(x + (i / 10 - 0.5) * wb * 1.15, y_bot + rng.uniform(-2.2, 1.8)) for i in range(11)]
    out.append(el("path", d=smooth(lip_pts), stroke="#b8f5fa", stroke_width=max(2.2, min(4.2, w * 0.14)),
                  fill="none", stroke_linecap="round", opacity=0.85))
    out.append(el("path", d=smooth(lip_pts), stroke="#ffffff", stroke_width=max(1.2, min(2.4, w * 0.08)),
                  fill="none", stroke_linecap="round", opacity=0.95))
    out.append(el("ellipse", cx=x, cy=y_bot + 1.5, rx=wb * 0.68, ry=max(2.2, w * 0.08), fill="#8cecf5", opacity=0.45))
    out.append(el("path", d=smooth(base_pts), stroke="#ffffff", stroke_width=max(2.4, min(5.2, w * 0.16)),
                  fill="none", stroke_linecap="round", opacity=0.82))
    out.append(el("ellipse", cx=x, cy=y_bot + 2.8, rx=wb * 0.78, ry=2.4, fill="none", stroke="#ffffff", stroke_width=0.95, opacity=0.58))
    out.append(el("ellipse", cx=x, cy=y_bot + 5.2, rx=wb * 0.98, ry=3.2, fill="none", stroke="#d8f8fc", stroke_width=0.75, opacity=0.38))
    out.append(mist(s, x, y_bot - 2, wb * 1.18, max(8, min(20, w * 0.42)), op=0.72, blur="mist"))
    return out


# ==============================================================================
# FAUNA PRIMITIVES (ANATOMICALLY DETAILED)
# ==============================================================================
def fish(x, y, s, body, fin=None, stripe=None, flip=False, tall=0.45):
    """Detailed tropical reef fish with dorsal/pectoral/caudal fins, gill operculum, and countershading."""
    fin = fin or mix(body, "#001428", 0.28)
    belly = mix(body, "#ffffff", 0.42)
    sx = -1 if flip else 1
    parts = [
        # Dorsal and anal fins
        el("path", d=f"M{n(-s * 0.45)},{n(-s * tall * 0.45)} Q{n(s * 0.05)},{n(-s * tall * 1.45)} {n(s * 0.48)},{n(-s * tall * 0.35)}Z", fill=fin),
        el("path", d=f"M{n(-s * 0.1)},{n(s * tall * 0.45)} Q{n(s * 0.25)},{n(s * tall * 1.3)} {n(s * 0.52)},{n(s * tall * 0.3)}Z", fill=fin),
        # Forked caudal fin
        el("path", d=f"M{n(s * 0.58)},0 L{n(s * 1.24)},{n(-s * 0.44)} Q{n(s * 0.96)},0 {n(s * 1.24)},{n(s * 0.44)}Z", fill=fin),
        # Main fusiform body + belly countershading
        el("path", d=f"M{n(-s)},0 Q{n(-s * 0.25)},{n(-s * tall * 1.2)} {n(s * 0.72)},0 Q{n(-s * 0.25)},{n(s * tall * 1.2)} {n(-s)},0Z", fill=body),
        el("path", d=f"M{n(-s * 0.92)},{n(s * 0.05)} Q{n(-s * 0.2)},{n(s * tall * 1.1)} {n(s * 0.65)},{n(s * 0.04)} Q{n(-s * 0.2)},{n(s * tall * 0.4)} {n(-s * 0.92)},{n(s * 0.05)}Z", fill=belly, opacity=0.55),
    ]
    if stripe:
        parts.append(el("path", d=f"M{n(-s * 0.65)},{n(s * 0.02)} Q{n(0)},{n(-s * 0.08)} {n(s * 0.75)},0",
                        stroke=stripe, stroke_width=max(0.9, s * 0.15), fill="none", stroke_linecap="round"))
        parts.append(el("path", d=f"M{n(-s * 0.15)},{n(-s * tall * 0.68)} Q{n(-s * 0.05)},0 {n(-s * 0.15)},{n(s * tall * 0.68)}",
                        stroke=stripe, stroke_width=max(0.7, s * 0.11), fill="none", opacity=0.75))
    # Gill arch, pectoral fin, and eye with iris ring
    parts += [
        el("path", d=f"M{n(-s * 0.42)},{n(-s * tall * 0.45)} Q{n(-s * 0.32)},0 {n(-s * 0.42)},{n(s * tall * 0.45)}",
           stroke=mix(body, "#000000", 0.38), stroke_width=max(0.6, s * 0.06), fill="none"),
        el("path", d=f"M{n(-s * 0.28)},{n(s * 0.08)} L{n(-s * 0.02)},{n(s * 0.26)} L{n(-s * 0.08)},{n(s * 0.04)}Z", fill=fin, opacity=0.85),
        el("circle", cx=-s * 0.64, cy=-s * 0.07, r=max(0.8, s * 0.11), fill="#f4f7f9"),
        el("circle", cx=-s * 0.65, cy=-s * 0.07, r=max(0.5, s * 0.065), fill="#0c1824"),
    ]
    return g(parts, transform=f"translate({n(x)} {n(y)}) scale({sx} 1)")


def school(rng, cx, cy, count, spread, s, body, stripe=None, flip=False, cls="swim"):
    fishes = [fish(cx + rng.uniform(-spread, spread), cy + rng.uniform(-spread * 0.35, spread * 0.35), s * rng.uniform(0.8, 1.15),
                   body, stripe=stripe, flip=flip) for _ in range(count)]
    return g(fishes)


def turtle(x, y, s, flip=False):
    """Hawksbill / Green sea turtle with detailed hexagonal carapace scutes, scaled flippers, and beak."""
    sx = -1 if flip else 1
    scutes = [
        # Central vertebral scutes
        "M-9,-3 L-3,-5 L3,-3 L3,3 L-3,5 L-9,3Z",
        "M3,-3 L8,-5 L13,-2 L13,2 L8,5 L3,3Z",
        "M-14,-1 L-9,-3 L-9,3 L-14,1Z",
        # Costal scutes (upper & lower)
        "M-8,-4 L-3,-9 L4,-9 L3,-3 L-3,-5Z",
        "M4,-9 L11,-8 L13,-2 L8,-5 L3,-3Z",
        "M-8,4 L-3,9 L4,9 L3,3 L-3,5Z",
        "M4,9 L11,8 L13,2 L8,5 L3,3Z",
    ]
    return g([
        # Rear flippers
        el("path", d="M-12,-4 Q-22,-11 -26,-8 Q-22,-3 -14,-1Z M-12,4 Q-22,11 -26,8 Q-22,3 -14,1Z", fill="#56693a"),
        # Front wing-like flippers with leading-edge scales
        el("path", d="M10,-6 C16,-19 26,-25 32,-22 C28,-13 20,-7 14,-3Z", fill="#667b44"),
        el("path", d="M10,6 C16,19 26,25 32,22 C28,13 20,7 14,3Z", fill="#56693a"),
        el("path", d="M14,-9 L17,-11 M18,-14 L21,-15 M23,-18 L26,-19 M14,9 L17,11 M18,14 L21,15", stroke="#3d4b28", stroke_width=1, fill="none"),
        # Head and neck
        el("path", d="M15,-3 Q24,-5 28,-1 Q29,2 25,4 Q20,5 15,3Z", fill="#73874f"),
        el("path", d="M18,-2 L22,-3 L24,-1", stroke="#4d5c33", stroke_width=0.7, fill="none"),
        el("circle", cx=24.5, cy=-1.4, r=1.1, fill="#121810"),
        el("circle", cx=24.8, cy=-1.7, r=0.35, fill="#ffffff"),
        # Carapace dome with golden-amber scute pattern
        el("ellipse", cx=0, cy=0, rx=17.5, ry=11.8, fill="#4b3a1e"),
        el("ellipse", cx=0, cy=-0.4, rx=16.5, ry=10.8, fill="#876633"),
        g([el("path", d=sd, fill="#6b4c21", stroke="#cfa658", stroke_width=0.75) for sd in scutes]),
        # Sunlit dorsal highlight on shell
        el("ellipse", cx=-1, cy=-4, rx=11, ry=4, fill="#e6c47a", opacity=0.28),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def manta(x, y, s):
    """Giant oceanic manta ray with cephalic lobes, countershaded pectoral wings, and whip tail."""
    return g([
        # Whip tail
        el("path", d="M0,12 Q-1,26 -4,38", stroke="#172636", stroke_width=1.4, fill="none", stroke_linecap="round"),
        # Main diamond wings
        el("path", d=(
            "M-5,-7 C-8,-14 -10,-18 -8,-20 C-5,-19 -4,-13 -2,-9 "
            "C0,-9 0,-9 2,-9 C4,-13 5,-19 8,-20 C10,-18 8,-14 5,-7 "
            "C18,-6 38,-18 58,-12 C42,-4 24,5 7,12 L0,16 L-7,12 C-24,5 -42,-4 -58,-12 C-38,-18 -18,-6 -5,-7Z"
        ), fill="#1c2f42"),
        # Pale ventral underbelly edge & white shoulder patches
        el("path", d="M-54,-11 C-36,-4 -20,4 -6,10 L0,13 L6,10 C20,4 36,-4 54,-11 C36,-6 18,2 0,8 C-18,2 -36,-6 -54,-11Z",
           fill="#cfdce6", opacity=0.65),
        el("path", d="M-4,-6 C-14,-5 -24,-9 -30,-8 C-22,-3 -12,-1 -3,-2Z M4,-6 C14,-5 24,-9 30,-8 C22,-3 12,-1 3,-2Z",
           fill="#dbe7f0", opacity=0.55),
        # Gill slits
        el("path", d="M-5,-1 L-2,0 M-5,1 L-2,2 M-5,3 L-2,4 M5,-1 L2,0 M5,1 L2,2 M5,3 L2,4",
           stroke="#0d1824", stroke_width=0.7, fill="none", opacity=0.6),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})")


def shark(x, y, s, flip=False):
    """Caribbean reef shark (Carcharhinus perezi) with streamlined countershading, gill slits, and heterocercal tail."""
    sx = -1 if flip else 1
    inner = g([
        # Pectoral fin (far side)
        el("path", d="M8,3 C12,13 18,18 22,17 C19,10 15,5 12,3Z", fill="#132c47"),
        # First & second dorsal fins
        el("path", d="M-2,-5 C3,-21 11,-24 14,-22 C11,-14 9,-8 7,-5Z", fill="#193859"),
        el("path", d="M-24,-3 L-21,-9 L-18,-3Z", fill="#193859"),
        # Heterocercal caudal fin
        el("path", d="M-36,0 C-44,-8 -52,-18 -56,-17 C-52,-9 -46,-3 -43,0 C-47,4 -51,10 -53,13 C-47,10 -41,4 -36,1Z", fill="#15314f"),
        # Torpedo body
        el("path", d="M-40,0 C-24,-7 6,-9 28,-4 C39,-2 46,1 48,2.5 C43,5 32,7 14,7.5 C-8,8 -24,4 -40,0Z", fill="#1e446b"),
        # White ventral countershading
        el("path", d="M-36,1 C-18,4 10,5 28,2.5 C38,1.5 44,2 47,3 C41,5.5 30,7.5 14,7.5 C-8,8 -22,5 -36,1Z", fill="#d4e3ed", opacity=0.88),
        # Near pectoral fin
        el("path", d="M12,4 C16,17 24,22 29,21 C26,13 21,6 17,4Z", fill="#193859"),
        # Five gill slits, eye, and mouth line
        el("path", d="M22,-1 L21,4 M24,-1 L23,4 M26,-1 L25,4 M28,-1 L27,4 M30,-0.5 L29,3.5",
           stroke="#0c2036", stroke_width=0.75, fill="none", opacity=0.75),
        el("path", d="M34,4.2 Q39,3.2 43,4.5", stroke="#0c2036", stroke_width=0.8, fill="none"),
        el("circle", cx=38, cy=0.6, r=1.3, fill="#08121e"),
        el("circle", cx=38.3, cy=0.3, r=0.4, fill="#ffffff"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")
    return g(inner)


def macaw(x, y, s, flip=False, palette=("#d62828", "#1d56b8", "#f5c428")):
    """Detailed Scarlet or Hyacinth Macaw in flight with layered wing coverts, primaries, tail streamers, and facial patch."""
    red, blue, yellow = palette
    sx = -1 if flip else 1
    inner = g([
        # Far wing (upbeat/downbeat)
        el("path", d="M-2,2 C-8,14 -18,22 -28,24 C-20,16 -12,8 4,2Z", fill=mix(blue, "#081838", 0.32)),
        el("path", d="M-1,1 C-5,9 -11,14 -17,15 C-11,9 -6,4 3,1Z", fill=mix(yellow, "#8a6800", 0.2)),
        # Long graduated tail streamers
        el("path", d="M-10,1 L-52,11 L-50,13.5 L-9,4Z", fill=red),
        el("path", d="M-12,2.5 L-44,13 L-42,14.8 L-10,4.5Z", fill=blue),
        # Streamlined body and breast
        el("path", d="M-14,0 C-8,-5 6,-6 15,-2 C18,0 16,5 10,5 C2,6 -8,4 -14,0Z", fill=red),
        # Near wing: primaries (blue), median coverts (yellow), lesser coverts (red)
        el("path", d="M-3,-2 C-10,-20 -24,-30 -36,-33 C-28,-22 -18,-10 5,-2Z", fill=blue),
        el("path", d="M-12,-14 L-33,-30 M-9,-11 L-28,-24 M-6,-8 L-23,-19", stroke=mix(blue, "#000000", 0.35), stroke_width=0.75, fill="none"),
        el("path", d="M-2,-2 C-7,-13 -15,-20 -22,-22 C-15,-13 -8,-6 5,-2Z", fill=yellow),
        el("path", d="M0,-2 C-4,-8 -9,-12 -14,-13 C-8,-7 -3,-3 5,-2Z", fill=red),
        # Head, bare white facial patch with feather lines, and hooked maxilla/mandible
        el("circle", cx=14.5, cy=-2.2, r=5.2, fill=red),
        el("path", d="M13.5,-4.8 C16.5,-5.2 18.8,-3.5 18.2,-0.5 C16.5,0.2 14,-0.5 13.5,-2.5Z", fill="#faf5eb"),
        el("circle", cx=16.0, cy=-2.8, r=1.0, fill="#1a1a1a"),
        el("path", d="M18.2,-4.5 C23,-4.2 25.5,-1.2 23.5,2.5 C21.5,1.2 19.5,0 18.2,-1.2Z", fill="#f2ead8"),
        el("path", d="M17.5,-1.2 C19.5,1.2 21,1.8 21.8,0.5 C20.2,-0.5 18.8,-1 17.5,-1.2Z", fill="#222222"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")
    return g(inner)


def toucan(x, y, s):
    """Ramphastos toco toucan perched with serrated gradient bill, blue periorbital ring, and crimson tail."""
    return g([
        # Long squared tail and crimson undertail coverts
        el("path", d="M-1,6 L-7,30 L1,31 L5,8Z", fill="#101216"),
        el("ellipse", cx=3, cy=11, rx=4, ry=3, fill="#d62828"),
        # Glossy black body & folded wing with blue-grey sheen
        el("path", d="M-3,2 C-5,-6 2,-10 7,-7 C11,-2 11,10 6,15 C1,16 -3,10 -3,2Z", fill="#14171c"),
        el("path", d="M-1,1 C2,-2 6,1 6,9 C3,11 -1,7 -1,1Z", fill="#252c38"),
        # Golden-white throat bib with scarlet border
        el("path", d="M2,-6 C6,-7 9,-4 8,2 C5,4 1,2 2,-6Z", fill="#fff8e6"),
        el("path", d="M2,-5 C5,-6 8,-3 7,1 C5,2 2,1 2,-5Z", fill="#f7c838", opacity=0.45),
        el("path", d="M2,2 Q5,4 8,2", stroke="#d62828", stroke_width=1.2, fill="none"),
        # Blue eye ring and dark eye
        el("circle", cx=5.2, cy=-4.2, r=2.0, fill="#2978d8"),
        el("circle", cx=5.2, cy=-4.2, r=1.1, fill="#111111"),
        el("circle", cx=5.5, cy=-4.5, r=0.35, fill="#ffffff"),
        # Enormous curved orange-yellow bill with black base band and terminal spot
        el("path", d="M8,-7.5 C18,-9.5 27,-6.5 30,0.5 C22,2 14,1.5 8,0.5Z", fill="#f27d16"),
        el("path", d="M8,-7.5 C16,-9 23,-7 26,-3 C19,-2.5 13,-3 8,-3.5Z", fill="#f9c62c"),
        el("path", d="M25,-5.2 C28,-3.8 29.5,-1.5 30,0.5 C27.5,1 26,0.5 24.5,-1Z", fill="#141414"),
        el("path", d="M8,-7.5 L8,0.5", stroke="#141414", stroke_width=1.4),
        el("path", d="M8,-2.2 L29,0.2", stroke="#b84a08", stroke_width=0.6, opacity=0.7),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})")


def condor(x, y, s, cls="fly"):
    """Soaring Andean Condor (Vultur gryphus) with slotted primary feathers, white wing panels, and neck ruff."""
    inner = g([
        # Broad wings with slotted primary fingertips
        el("path", d=(
            "M0,0 C-14,-6 -32,-8 -46,-5 L-58,-4 L-51,-1.5 L-60,0.5 L-51,2 L-58,4.5 L-48,4.8 L-53,7 L-42,6.5 "
            "C-26,6 -12,5 -5,6.5 L-8,12 L0,10.5 L8,12 L5,6.5 C12,5 26,6 42,6.5 "
            "L53,7 L48,4.8 L58,4.5 L51,2 L60,0.5 L51,-1.5 L58,-4 L46,-5 C32,-8 14,-6 0,0Z"
        ), fill="#17181f"),
        # Silvery-white secondary wing panels
        el("path", d="M-38,-2.5 C-25,-4.5 -12,-3.5 -5,-0.5 C-14,1.5 -26,1.5 -38,-2.5Z", fill="#e9edf2", opacity=0.9),
        el("path", d="M38,-2.5 C25,-4.5 12,-3.5 5,-0.5 C14,1.5 26,1.5 38,-2.5Z", fill="#e9edf2", opacity=0.9),
        # Downy white neck collar and carunculated head
        el("ellipse", cx=0, cy=-1.2, rx=3.8, ry=2.0, fill="#f5f7fa"),
        el("ellipse", cx=0, cy=-4.2, rx=2.2, ry=2.6, fill="#b5544a"),
        el("path", d="M-0.8,-6.5 L0,-8.5 L0.8,-6.5Z", fill="#d9c8b2"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})")
    return g(inner)


def bird_v(x, y, s, col="#2b3440"):
    return el("path", d=(
        f"M{n(x - s)},{n(y - s * 0.28)} Q{n(x - s * 0.45)},{n(y - s * 0.65)} {n(x)},{n(y)} "
        f"Q{n(x + s * 0.45)},{n(y - s * 0.65)} {n(x + s)},{n(y - s * 0.28)} "
        f"Q{n(x + s * 0.45)},{n(y - s * 0.42)} {n(x)},{n(y + s * 0.14)} "
        f"Q{n(x - s * 0.45)},{n(y - s * 0.42)} {n(x - s)},{n(y - s * 0.28)}Z"
    ), fill=col)


def flamingo(x, y, s, flip=False, pose="stand"):
    """American/Caribbean Flamingo (Phoenicopterus ruber) with S-neck or filter-feeding pose, two-tone bill, and water ripples."""
    sx = -1 if flip else 1
    parts = [
        # Water ripple ring around legs
        el("ellipse", cx=1, cy=28, rx=9.5, ry=2.2, fill="none", stroke="#ffffff", stroke_width=0.8, opacity=0.55),
        # Long slender wading legs with pink tarsal joints
        el("path", d="M2,0 L2.5,15 L3,28 M-2,0 L-3.5,14 L2.5,19" if pose == "stand" else "M2,0 L3,15 L3.5,28 M-2,0 L-3,15 L-3.5,28",
           stroke="#d46a70", stroke_width=1.3, fill="none", stroke_linecap="round"),
        el("circle", cx=2.5 if pose == "stand" else 3.0, cy=15, r=1.3, fill="#b84850"),
        el("circle", cx=-3.5 if pose == "stand" else -3.0, cy=14.5, r=1.3, fill="#b84850"),
        # Sculpted body, crimson wing coverts, and black primary tips
        el("path", d="M-14,-2 C-12,-11 -2,-13 8,-8 C12,-6 11,0 5,1.5 C-2,2.5 -9,1 -14,-2Z", fill="#f57c73"),
        el("path", d="M-9,-6.5 C-3,-10.5 4,-9.5 6,-4 C2,-1 -5,-1 -9,-6.5Z", fill="#ff9e94"),
        el("path", d="M-11,-3.5 C-6,-4.5 -1,-3.5 3,-1.5 L-13,-1.5Z", fill="#d94b43", opacity=0.7),
        el("path", d="M-14,-2 L-18,2.5 L-11,0.5Z", fill="#1c1c1c"),
    ]
    if pose == "feed":
        # Arching neck dipping bill into the water for filter-feeding
        parts += [
            el("path", d="M8,-6 C16,-4 19,10 16,23 C15,26 13,27 11,26", stroke="#f57c73", stroke_width=3.1, fill="none", stroke_linecap="round"),
            el("path", d="M8,-6.5 C15,-4.5 18,9 15.2,22", stroke="#ffb2a8", stroke_width=1.0, fill="none", stroke_linecap="round"),
            el("circle", cx=12.5, cy=25.5, r=2.7, fill="#f57c73"),
            el("path", d="M11,26.5 C8,27.5 6.5,26 7.5,24 C9,24.5 10.5,25.5 11.5,26Z", fill="#181818"),
            el("ellipse", cx=11, cy=27.5, rx=6.5, ry=1.5, fill="none", stroke="#ffffff", stroke_width=0.7, opacity=0.6),
        ]
    else:
        # Classic S-curved neck
        parts += [
            el("path", d="M7,-6 C15,-14 7,-24 6,-31 C5,-35 8,-37 10,-36", stroke="#f57c73", stroke_width=3.0, fill="none", stroke_linecap="round"),
            el("path", d="M6.2,-6.5 C13.5,-14 6,-24 5.2,-31", stroke="#ffb2a8", stroke_width=1.0, fill="none", stroke_linecap="round"),
            el("circle", cx=10, cy=-35.5, r=2.9, fill="#f57c73"),
            el("circle", cx=10.8, cy=-36, r=0.65, fill="#f7e248"),
            el("path", d="M12.2,-36.5 C15.5,-36 16.8,-33.5 15.5,-30.5 C14,-31.5 13,-33.5 11.8,-34.5Z", fill="#fce8e6"),
            el("path", d="M14.2,-34 C16.2,-33 16.5,-31.5 15.5,-30.5 C14.2,-31.2 13.8,-32.5 14.2,-34Z", fill="#181818"),
        ]
    return g(parts, transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def jabiru(x, y, s, flip=False):
    """Pantanal Jabiru Stork (Jabiru mycteria) with sculpted plumage, black neck, scarlet throat band, and heavy upturned bill."""
    sx = -1 if flip else 1
    return g([
        el("ellipse", cx=1, cy=26, rx=10.5, ry=2.2, fill="none", stroke="#fff5dc", stroke_width=0.8, opacity=0.55),
        # Long stilt legs with tarsal joints
        el("path", d="M-2,0 L-2.5,13 L-3,26 M3,0 L3.5,13 L4,26", stroke="#1c1c1e", stroke_width=1.5, fill="none", stroke_linecap="round"),
        el("circle", cx=-2.5, cy=13, r=1.1, fill="#2e2e32"),
        el("circle", cx=3.5, cy=13, r=1.1, fill="#2e2e32"),
        # Sculpted white plumage body with layered wing coverts and black tail tip
        el("path", d="M-15,-4 L-19,-1.5 L-12,-0.5Z", fill="#18181a"),
        el("path", d="M-15,-4 C-12,-14 -1,-16 9,-10 C13,-7 12,0 5,1.5 C-3,2.5 -11,0.5 -15,-4Z", fill="#faf8f0"),
        el("path", d="M-13,-3 C-8,0 2,1 8,-2 C4,1.5 -5,2 -13,-3Z", fill="#dedbd0"),
        el("path", d="M-10,-7 C-4,-11 4,-10 7,-4 C1,-1 -6,-2 -10,-7Z", fill="#f0eee4", stroke="#d4d0c2", stroke_width=0.6),
        # Sculpted black neck, inflatable scarlet basal collar, head, and heavy upturned bill
        el("path", d="M5,-9 C7.5,-17 7,-25 6,-32 L9.5,-32 C11,-24 11.5,-16 9.5,-8Z", fill="#18181a"),
        el("path", d="M5,-8.5 C9,-8 11.5,-11 10.5,-15.5 C7.5,-15 5.2,-12 5,-8.5Z", fill="#d9261e"),
        el("path", d="M6.5,-9.5 C9,-9.5 10.5,-11.5 9.8,-14.5", stroke="#ff6359", stroke_width=0.9, fill="none"),
        # Skull & wispy white occipital crown feathers
        el("path", d="M5,-31.5 C4.5,-35 7,-36.8 10,-35.5 C11.5,-34.5 11.5,-31.5 9,-31Z", fill="#18181a"),
        el("path", d="M5,-35 Q2.5,-36.5 3.5,-33.5 M5.5,-35.8 Q3.5,-37.5 4.5,-34.5", stroke="#e2e0d5", stroke_width=1.0, fill="none"),
        el("circle", cx=8.8, cy=-33.8, r=0.65, fill="#2b2018"),
        el("circle", cx=9.0, cy=-34.0, r=0.25, fill="#ffffff"),
        # Massive slightly recurved (upturned) black stork bill
        el("path", d="M10.2,-35 C16,-34.8 22,-34.2 26.5,-33.2 C22,-31.2 15.5,-31.2 9.8,-31.5Z", fill="#141416"),
        el("path", d="M10.5,-33.2 Q18,-33 25.5,-33.1", stroke="#38383d", stroke_width=0.6, fill="none"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def egret(x, y, s, flip=False):
    """Great Egret (Ardea alba) with breeding plumes, S-neck, and dagger yellow bill."""
    sx = -1 if flip else 1
    return g([
        el("path", d="M0,0 L-1,21 M3,0 L4,21", stroke="#1e2022", stroke_width=1.1),
        el("path", d="M-11,-3 C-9,-9 -1,-10 6,-6 C9,-4 8,0 3,1 C-3,1 -8,0 -11,-3Z", fill="#ffffff"),
        # Delicate aigrette back plumes
        el("path", d="M-6,-6 Q-12,-5 -15,-1 M-5,-5 Q-11,-3 -14,1", stroke="#f0f4f8", stroke_width=0.9, fill="none"),
        el("path", d="M6,-5 C11,-13 5,-20 6,-26 C6.5,-28 8,-28 9,-27", stroke="#ffffff", stroke_width=2.2, fill="none", stroke_linecap="round"),
        el("circle", cx=8.8, cy=-27, r=2.1, fill="#ffffff"),
        el("circle", cx=9.5, cy=-27.2, r=0.5, fill="#f2d024"),
        el("path", d="M10.5,-27.8 L18.5,-25.5 L10.5,-25.8Z", fill="#e8ae24"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def capybara(x, y, s, flip=False):
    """Anatomically realistic Capybara (Hydrochoerus hydrochaeris) with sculpted haunches, neck, blunt snout, and coarse fur."""
    sx = -1 if flip else 1
    return g([
        el("ellipse", cx=0, cy=5.2, rx=16.5, ry=2.2, fill="#000000", opacity=0.22),
        # Far-side legs (darker)
        el("path", d="M-9,-2 L-11,4.8 L-9,4.8 L-6.5,-1Z M8.5,-2 L7.5,4.8 L9.5,4.8 L11,-1Z", fill="#422814"),
        # Sculpted barrel torso, rounded rump, shoulder hump, and broad rectangular head
        el("path", d=(
            "M-16,-2 C-17,-9 -12,-14.5 -4,-14.5 C2,-14.5 6,-13 9.5,-10.5 "
            "C11.5,-12.5 15,-13.2 18.5,-12.2 C21.5,-11.2 22.5,-8.5 22,-5.5 "
            "C21.5,-3 18.5,-2.5 15.5,-3.2 C13.5,-2 12,-0.5 11,0.5 "
            "C4,1.2 -6,1.2 -13.5,0.5 C-15.5,0 -16,-1 -16,-2Z"
        ), fill="#8c5832"),
        # Warm sunlit dorsal fur coat & shaded underbelly/haunch
        el("path", d="M-13,-10 C-8,-14 2,-14 9,-10 C12,-12 16,-12.5 19,-11.2 C14,-9 4,-8 -13,-10Z", fill="#b57b4e", opacity=0.65),
        el("path", d="M-15.5,-1.5 C-10,-4.5 4,-4.5 12,-0.5 C14.5,-2.5 18,-3 21,-4.5 C19,-2.5 15,-2 11,0.5 C3,1.2 -8,1.2 -15.5,-1.5Z",
           fill="#59361b", opacity=0.65),
        # Near-side jointed hind leg and foreleg
        el("path", d="M-13.5,-4 C-10.5,-4 -9.5,-1 -10.5,5.2 L-13,5.2 L-12.5,0.5 C-14,0 -14.5,-2 -13.5,-4Z", fill="#6e4324"),
        el("path", d="M9.5,-4 C12,-4 12.8,-1 12.2,5.2 L9.8,5.2 L10.2,0 Z", fill="#6e4324"),
        # Coarse fur hatch strokes
        el("path", d="M-9,-9 l3,1 M-4,-10 l3,1 M2,-9 l3,1 M-6,-6 l3,0.8 M1,-6 l3,0.8", stroke="#59361b", stroke_width=0.75, opacity=0.55),
        # Blunt muzzle plane, dark morrillo scent gland on snout bridge, small rounded ear, eye, and nostril
        el("path", d="M17.5,-11.5 C20.5,-11 22.2,-8.8 22,-5.5 C20,-4.5 17.8,-5.2 17,-7.5Z", fill="#6e4324"),
        el("ellipse", cx=17.5, cy=-11.8, rx=1.6, ry=0.9, fill="#382110"),
        el("path", d="M11.2,-11.5 C10.5,-14.2 12.5,-15 13.5,-12.2Z", fill="#543219"),
        el("circle", cx=15.2, cy=-9.5, r=1.0, fill="#14100c"),
        el("circle", cx=15.5, cy=-9.8, r=0.35, fill="#ffffff"),
        el("circle", cx=20.4, cy=-7.8, r=0.65, fill="#29170b"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def caiman(x, y, s, flip=False):
    """Partially submerged Black Caiman / American Crocodile with osteoderm scutes, periscopic eyes, and water wake."""
    sx = -1 if flip else 1
    return g([
        # Water wake lines
        el("path", d="M-34,1 L28,1 M-26,2.5 L20,2.5", stroke="#ffffff", stroke_width=0.75, opacity=0.45),
        # Armored back, tail crest, and long jaws
        el("path", d="M-34,0 C-22,-4 -6,-5 8,-3 C14,-6 18,-6 20,-3 C26,-3.5 31,-2.5 32,0.5 L-34,0.5Z", fill="#343b26"),
        el("path", d="M-30,0 L-26,-3.5 L-23,0 L-19,-4 L-16,0 L-12,-4 L-9,0 L-5,-3.5 L-2,0 L2,-3 L5,0", fill="#222818"),
        # Jaw line & teeth glint
        el("path", d="M18,-0.5 Q25,-1 31,0", stroke="#1a1f12", stroke_width=0.8, fill="none"),
        el("path", d="M21,-0.6 L21.5,-1.3 M24,-0.7 L24.5,-1.4 M27,-0.6 L27.5,-1.2", stroke="#e8e2ce", stroke_width=0.6),
        # Raised brow ridge and golden slit eye
        el("circle", cx=16.5, cy=-4.0, r=1.8, fill="#454d33"),
        el("circle", cx=16.7, cy=-4.2, r=0.85, fill="#e8c438"),
        el("path", d="M16.7,-4.9 L16.7,-3.5", stroke="#111111", stroke_width=0.45),
        el("circle", cx=29.5, cy=-1.8, r=0.7, fill="#222818"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def dolphin(x, y, s):
    """Amazon Pink River Dolphin (Inia geoffrensis) breaching with bulbous melon, long beak, and low dorsal ridge."""
    inner = g([
        # Surface splash rings
        el("ellipse", cx=0, cy=1, rx=24, ry=2.6, fill="none", stroke="#f4f7ec", stroke_width=0.9, opacity=0.55),
        # Arched body, low keel-like dorsal fin, and beak
        el("path", d=(
            "M-22,1 C-14,-10 -2,-13 10,-8 C13,-9 16,-7 17,-4 C21,-3.5 25,-2.5 26,-1 "
            "C22,-0.5 18,-1 15,-1.5 C6,-4 -8,-3 -22,1Z"
        ), fill="#e898a2"),
        # Lighter rose highlight along melon and back
        el("path", d="M-16,-2 C-8,-9 2,-10 11,-6 C3,-6 -7,-5 -16,-2Z", fill="#f7c2c9", opacity=0.75),
        # Characteristic long low dorsal ridge
        el("path", d="M-6,-8.5 C-1,-13.5 4,-12.5 7,-7.5Z", fill="#d47b86"),
        # Flipper & eye
        el("path", d="M8,-3 C10,1 13,2 14,1 C13,-1 11,-2 10,-3Z", fill="#cf7480"),
        el("circle", cx=14.5, cy=-4.8, r=0.65, fill="#1f1418"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})")
    return g(inner)


def maned_wolf(x, y, s, flip=False):
    """Anatomically sculpted Cerrado Maned Wolf (Chrysocyon brachyurus) with stilt legs, black mane, tucked waist, and fox head."""
    sx = -1 if flip else 1
    return g([
        el("ellipse", cx=0, cy=6.5, rx=16.5, ry=2.2, fill="#000000", opacity=0.22),
        # Far-side stilt legs (upper rufous thigh/arm + black lower stocking)
        el("path", d="M-9.5,-13 L-11,-3.5 L-11.5,5.8", stroke="#17120e", stroke_width=1.9, fill="none", stroke_linecap="round"),
        el("path", d="M7.5,-12.5 L8.5,-3.5 L9,5.8", stroke="#17120e", stroke_width=1.9, fill="none", stroke_linecap="round"),
        # Bushy tail with white terminal brush
        el("path", d="M-14,-18 C-21,-17.5 -26,-12.5 -27.5,-5.5 C-23,-6.5 -18.5,-11 -14,-14.5Z", fill="#c96428"),
        el("path", d="M-23.5,-10 C-26,-7.5 -27.5,-5.5 -27.5,-5.5 C-24,-6 -21.5,-8 -20.5,-9.8Z", fill="#f7f4eb"),
        # Sculpted canid torso with deep chest, tucked flank waist, and muscular hindquarter haunch
        el("path", d=(
            "M-15.5,-15 C-16,-19.5 -12,-22 -6,-21.5 C0,-21 5,-21.5 10,-22.5 "
            "C13,-20 14.5,-15 12.5,-11.5 C9.5,-10.5 6.5,-11 3.5,-12.5 "
            "C-2,-14 -7,-13.5 -10.5,-11.5 C-13.5,-11.5 -15,-13 -15.5,-15Z"
        ), fill="#c96428"),
        el("path", d="M-11,-12 C-6,-14 2,-13.5 7,-11.2 C10,-11 12,-11.5 12.5,-12.5 C7,-13.5 -3,-14.5 -11,-12Z", fill="#964316", opacity=0.55),
        # Near-side jointed hind leg and foreleg (rufous upper + black stocking)
        el("path", d="M-13,-14 L-14.5,-4 L-13.5,6.2", stroke="#1c1612", stroke_width=2.1, fill="none", stroke_linecap="round"),
        el("path", d="M-12.5,-14.5 L-14.2,-5", stroke="#c96428", stroke_width=3.0, fill="none", stroke_linecap="round"),
        el("path", d="M10.5,-12.5 L11.8,-3.5 L12.8,6.2", stroke="#1c1612", stroke_width=2.1, fill="none", stroke_linecap="round"),
        el("path", d="M10.5,-13 L11.5,-4.5", stroke="#c96428", stroke_width=2.8, fill="none", stroke_linecap="round"),
        # Neck, black erectile mane, slender fox-like muzzle, white throat patch, and tall ears
        el("path", d="M8.5,-20.5 C12,-25.5 15.5,-29.5 19,-30.5 L26.5,-27.5 C25,-25 21,-24.2 18,-23.5 C16,-19 14,-15 11,-13Z", fill="#d46c2c"),
        el("path", d="M3.5,-21.2 C8,-24.5 12.5,-28 17,-30 C16,-26 13,-23 9.5,-20.5Z", fill="#1a1410"),
        el("path", d="M17.5,-25.2 C21,-25 24,-25.5 25.5,-26.5 C23.5,-24 20,-23.2 17,-23.5Z", fill="#f7f4eb"),
        el("circle", cx=25.8, cy=-27.2, r=1.0, fill="#1a1410"),
        # Tall upright ears with white inner pinnae
        el("path", d="M15.8,-29.2 L15.2,-36.8 L19.2,-30.2Z M18.8,-29.8 L20.2,-36.2 L22.2,-29.2Z", fill="#c96428"),
        el("path", d="M16.3,-30.2 L16.0,-34.8 L18.4,-30.2Z", fill="#f5ede0"),
        el("circle", cx=20.5, cy=-28.2, r=0.8, fill="#1a1410"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def iguana(x, y, s):
    """Hispaniolan Rhinoceros Iguana (Cyclura cornuta) with dorsal spine crest, dewlap, nasal horns, and banded tail."""
    return g([
        el("ellipse", cx=2, cy=5.5, rx=20, ry=2.4, fill="#000000", opacity=0.22),
        # Muscular legs and clawed toes
        el("path", d="M-4,1 L-8,5.5 L-11,5.5 M9,0 L12,5.5 L15,5.5", stroke="#58563e", stroke_width=2.4, fill="none", stroke_linecap="round"),
        # Heavy tapering tail with dark bands and robust scaly body
        el("path", d="M-34,2.5 C-22,3.5 -12,2 -6,-1 C1,-6 10,-6 16,-3 C20,-4 24,-2 25,1 C20,3 14,2 10,1 C3,3 -10,5 -34,2.5Z", fill="#737052"),
        el("path", d="M-24,2.5 L-22,1 M-18,2.2 L-16,0.2 M-12,1.5 L-10,-0.5", stroke="#454230", stroke_width=1.6),
        el("path", d="M-6,-1 C1,-4 9,-4 14,-1 C8,2 -1,2 -6,-1Z", fill="#94906b", opacity=0.7),
        # Gular dewlap pouch and nasal horn tubercles
        el("path", d="M15,0 Q19,4.8 22.5,1.5Z", fill="#615e44"),
        el("path", d="M21,-2.8 L22,-4.8 L22.8,-2.5 L23.6,-4.2 L24.2,-2.0", fill="#4a4834"),
        # Serrated dorsal crest spines
        el("path", d="M-14,0.5 L-12,-2.5 L-10,0 L-8,-3.5 L-6,-0.5 L-4,-4.5 L-2,-1.5 L0,-5.5 L2,-2 L4,-6 L6,-2.5 L8,-5.5 L10,-2 L12,-4.5 L14,-1.5",
           stroke="#4d4a35", stroke_width=1.1, fill="none", stroke_linejoin="round"),
        el("circle", cx=19.5, cy=-1.5, r=0.85, fill="#1a1812"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})")


def morpho(x, y, s):
    """Iridescent Blue Morpho butterfly (Morpho menelaus) with black wing margins and white marginal spots."""
    inner = g([
        # Forewings and hindwings with dark border and iridescent blue interior
        el("path", d="M0,0 C-3,-6 -9,-8 -11,-3 C-11,1 -6,3 -1,1 C-5,4 -7,8 -4,9 C-1,9 0,5 0,1Z", fill="#182232"),
        el("path", d="M0,0 C3,-6 9,-8 11,-3 C11,1 6,3 1,1 C5,4 7,8 4,9 C1,9 0,5 0,1Z", fill="#182232"),
        el("path", d="M-0.5,0 C-3,-5 -8,-6.5 -9.5,-2.5 C-9.5,0.5 -5,2 -1,0.8 C-4,3.5 -5.5,6.5 -3.5,7.5 C-1.5,7.5 -0.5,4 -0.5,0.8Z", fill="#1f82e8"),
        el("path", d="M0.5,0 C3,-5 8,-6.5 9.5,-2.5 C9.5,0.5 5,2 1,0.8 C4,3.5 5.5,6.5 3.5,7.5 C1.5,7.5 0.5,4 0.5,0.8Z", fill="#46a8ff"),
        el("ellipse", cx=0, cy=1, rx=0.8, ry=3.5, fill="#121820"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})")
    return g(inner)


def hummingbird(x, y, s):
    """Glittering emerald hummingbird hovering with iridescent gorget, blurred wings, and needle bill."""
    inner = g([
        # Motion-blurred upper and lower wing beats
        el("path", d="M-1,-1 C-6,-10 -12,-12 -14,-9 C-12,-4 -6,-1 -1,0Z", fill="#88d4be", opacity=0.72),
        el("path", d="M-2,-1 C-8,-7 -13,-6 -14,-3 C-10,-1 -5,0 -2,0Z", fill="#54a890", opacity=0.55),
        # Forked tail
        el("path", d="M-5,0.5 L-13,4.5 L-11,1.5 L-13,-0.5 L-5,-0.5Z", fill="#114d3b"),
        # Emerald body, ruby-magenta gorget, and needle bill
        el("path", d="M-6,0 C-4,-3 2,-3.5 5,-1.5 C6,0 4,2.5 0,2.5 C-3,2.5 -5,1.5 -6,0Z", fill="#188c68"),
        el("path", d="M1.5,-1.2 C4,-1.5 5.5,-0.2 4.5,1.2 C2.8,1.5 1.2,0.5 1.5,-1.2Z", fill="#e02b68"),
        el("path", d="M5,-1.0 L14,-2.2", stroke="#181818", stroke_width=0.85, stroke_linecap="round"),
        el("circle", cx=3.5, cy=-1.2, r=0.65, fill="#111111"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(s)})")
    return g(inner)


def pitcher_plant(x, y, s, flower=False):
    """Endemic Tepui sun pitcher plant (Heliamphora nutans) with ventricose crimson-flushed pitchers and nodding bloom."""
    tubes = [el("ellipse", cx=0, cy=1.5, rx=13, ry=2.8, fill="#1b1410", opacity=0.42)]
    specs = [
        (-8.5, 19, -15, "#5c8836", "#9c3026"),
        (-2.5, 25, -4, "#74a446", "#b8362a"),
        (3.8, 22, 8, "#68963e", "#a63226"),
        (8.8, 17, 17, "#527a30", "#8a2920"),
    ]
    for dx, h, rot, col, rim_col in specs:
        tubes.append(g([
            # Ventricose (swollen belly, constricted neck, flared oblique mouth) pitcher
            el("path", d=(
                f"M-1.0,0 C-3.6,{-h * 0.24} -2.0,{-h * 0.56} -4.2,{-h * 0.90} "
                f"C-2.2,{-h * 1.03} 2.2,{-h * 1.03} 4.2,{-h * 0.90} "
                f"C2.0,{-h * 0.56} 3.6,{-h * 0.24} 1.0,0Z"
            ), fill=col),
            # Crimson upper flushing & vertical venation
            el("path", d=(
                f"M-2.8,{-h * 0.52} L-4.2,{-h * 0.90} "
                f"C-2.2,{-h * 1.03} 2.2,{-h * 1.03} 4.2,{-h * 0.90} "
                f"L2.8,{-h * 0.52} Q0,{-h * 0.42} -2.8,{-h * 0.52}Z"
            ), fill=rim_col, opacity=0.65),
            el("path", d=f"M0,{-h * 0.12} L0,{-h * 0.86}", stroke="#4a1614", stroke_width=0.55, opacity=0.55),
            # Dark interior throat & rolled crimson peristome lip
            el("ellipse", cx=0, cy=-h * 0.89, rx=3.3, ry=1.5, fill="#3b0d0d"),
            el("path", d=f"M-4.2,{-h * 0.90} Q0,{-h * 1.03} 4.2,{-h * 0.90}", stroke="#751616", stroke_width=1.0, fill="none"),
            # Helmet-like apical nectar spoon (lid)
            el("path", d=f"M-1.3,{-h * 0.96} C-1.8,{-h * 1.12} 1.8,{-h * 1.12} 1.3,{-h * 0.96}Z", fill="#c22828"),
        ], transform=f"translate({n(dx)} 0) rotate({n(rot)})"))
    if flower:
        tubes.append(g([
            el("path", d="M1,0 Q5,-20 2,-34 Q0,-38 -2.5,-35.5", stroke="#8c3228", stroke_width=0.85, fill="none"),
            el("path", d="M-2.5,-35.5 C-5.2,-33.5 -5.0,-30.5 -2.2,-29.8 C0.5,-30.5 0.5,-33.5 -2.5,-35.5Z", fill="#fceef2"),
            el("path", d="M-2.5,-35.5 C-4.2,-33.5 -3.2,-31.0 -1.2,-30.8", stroke="#e89cb0", stroke_width=0.55, fill="none"),
        ]))
    return g(tubes, transform=f"translate({n(x)} {n(y)}) scale({n(s)})")


# ==============================================================================
# REEF PRIMITIVES
# ==============================================================================
def branch_coral(rng, x, y, L, depth, col, width, spread=0.52, up=-math.pi / 2):
    """Sculpted 3D Acropora staghorn/elkhorn coral colony with curved tapering branches, polyp verrucae, and glowing axial tips."""
    sh_col = mix(col, "#06101c", 0.44)
    lit_col = mix(col, "#fff8e8", 0.42)
    tip_col = mix(col, "#ffffff", 0.65)
    polys_sh, polys_main, polys_lit, tips, polyps = [], [], [], [], []

    def rec(px, py, ang, ln, w0, d):
        w1 = max(1.0, w0 * 0.66)
        ex = px + math.cos(ang) * ln
        ey = py + math.sin(ang) * ln
        # Slight upward/organic curve control point
        cx_ = (px + ex) * 0.5 + math.sin(ang) * ln * 0.08
        cy_ = (py + ey) * 0.5 - abs(math.cos(ang)) * ln * 0.10
        nx_, ny_ = -math.sin(ang), math.cos(ang)
        # Tapered 3D branch polygon
        b_d = (
            f"M{n(px - nx_ * w0 * 0.55)},{n(py - ny_ * w0 * 0.55)} "
            f"Q{n(cx_ - nx_ * w0 * 0.42)},{n(cy_ - ny_ * w0 * 0.42)} {n(ex - nx_ * w1 * 0.45)},{n(ey - ny_ * w1 * 0.45)} "
            f"A{n(w1 * 0.48)},{n(w1 * 0.48)} 0 0 1 {n(ex + nx_ * w1 * 0.45)},{n(ey + ny_ * w1 * 0.45)} "
            f"Q{n(cx_ + nx_ * w0 * 0.42)},{n(cy_ + ny_ * w0 * 0.42)} {n(px + nx_ * w0 * 0.55)},{n(py + ny_ * w0 * 0.55)}Z"
        )
        polys_sh.append(
            f"M{n(px)},{n(py + 1.4)} Q{n(cx_)},{n(cy_ + 1.4)} {n(ex)},{n(ey + 1.2)} "
            f"L{n(ex + nx_ * w1 * 0.55)},{n(ey + ny_ * w1 * 0.55 + 1.2)} "
            f"Q{n(cx_ + nx_ * w0 * 0.55)},{n(cy_ + ny_ * w0 * 0.55 + 1.4)} {n(px + nx_ * w0 * 0.6)},{n(py + ny_ * w0 * 0.6 + 1.4)}Z"
        )
        polys_main.append(b_d)
        polys_lit.append(f"M{n(px - nx_ * w0 * 0.18)},{n(py - ny_ * w0 * 0.18)} Q{n(cx_ - nx_ * w0 * 0.18)},{n(cy_ - ny_ * w0 * 0.18)} {n(ex)},{n(ey)}")
        # Tiny radial corallite bumps along the branch
        for t_p in (0.35, 0.70):
            bx_p = px + (ex - px) * t_p + nx_ * w0 * 0.32
            by_p = py + (ey - py) * t_p + ny_ * w0 * 0.32
            polyps.append(el("circle", cx=bx_p, cy=by_p, r=max(0.5, w0 * 0.18)))
        if d > 0:
            for k in (-1, 1):
                rec(ex, ey, ang + k * spread * rng.uniform(0.52, 1.05), ln * rng.uniform(0.66, 0.84), w1, d - 1)
        else:
            tips.append(el("circle", cx=ex, cy=ey, r=max(1.1, w1 * 0.62)))

    for k in range(3):
        rec(x + (k - 1) * width * 0.9, y, up + (k - 1) * 0.40 + rng.uniform(-0.07, 0.07), L * rng.uniform(0.84, 1.04), width * 1.15, depth)
    return g([
        # Encrusting carbonate holdfast base
        el("ellipse", cx=x, cy=y + 1.2, rx=width * 2.4, ry=width * 0.72, fill=sh_col, opacity=0.75),
        el("ellipse", cx=x, cy=y + 0.4, rx=width * 2.0, ry=width * 0.58, fill=col),
        el("path", d=" ".join(polys_sh), fill=sh_col, opacity=0.82),
        el("path", d=" ".join(polys_main), fill=col),
        el("path", d=" ".join(polys_lit), stroke=lit_col, stroke_width=max(0.8, width * 0.36), fill="none", stroke_linecap="round", opacity=0.82),
        g(polyps, fill=lit_col, opacity=0.75),
        g(tips, fill=tip_col),
    ])


def brain_coral(rng, x, y, r, col="#cfa344"):
    """Sculpted 3D Diploria labyrinthiformis brain coral dome with encrusting base, deep Colline valleys, and glowing ambulacral ridges."""
    deep = mix(col, "#140b00", 0.58)
    mid_sh = mix(col, "#2a1804", 0.34)
    lit = mix(col, "#fff9dc", 0.44)
    lines_valley, lines_ridge, lines_spec = [], [], []
    for i in range(1, 7):
        rr = r * (i / 6.4)
        pts, pts_hi, pts_sp = [], [], []
        for j in range(21):
            a = math.pi + math.pi * j / 20
            wob = rr + math.sin(j * 2.1 + i * 1.4) * r * 0.068 + math.cos(j * 3.4 - i) * r * 0.032 + rng.uniform(-r * 0.018, r * 0.018)
            px = x + math.cos(a) * wob
            py = y + math.sin(a) * wob * 0.78
            pts.append((px, py))
            pts_hi.append((px - 0.4, py - 1.0))
            pts_sp.append((px - 0.6, py - 1.3))
        lines_valley.append(smooth(pts))
        lines_ridge.append(smooth(pts_hi))
        if i <= 4:
            lines_spec.append(smooth(pts_sp[3:14]))
    return g([
        el("ellipse", cx=x + 1, cy=y + 1.8, rx=r * 1.08, ry=r * 0.25, fill="#061420", opacity=0.45),
        # Basal skeletal skirt
        el("path", d=f"M{n(x - r * 1.03)},{n(y + 1)} Q{n(x)},{n(y + r * 0.18)} {n(x + r * 1.03)},{n(y + 1)} L{n(x + r * 0.96)},{n(y - 2)} L{n(x - r * 0.96)},{n(y - 2)}Z",
           fill=deep),
        # Main hemispherical dome
        el("path", d=f"M{n(x - r)},{n(y)} A{n(r)},{n(r * 0.80)} 0 0 1 {n(x + r)},{n(y)} Q{n(x)},{n(y + r * 0.14)} {n(x - r)},{n(y)}Z", fill=col),
        # Shadowed right hemisphere
        el("path", d=f"M{n(x - r * 0.12)},{n(y - r * 0.79)} A{n(r)},{n(r * 0.80)} 0 0 1 {n(x + r)},{n(y)} Q{n(x + r * 0.4)},{n(y + r * 0.12)} {n(x - r * 0.05)},{n(y + 1)}Z",
           fill=mid_sh, opacity=0.52),
        # Sunlit upper-left dome glow
        el("path", d=f"M{n(x - r * 0.82)},{n(y - r * 0.14)} A{n(r * 0.68)},{n(r * 0.54)} 0 0 1 {n(x + r * 0.32)},{n(y - r * 0.22)}Z",
           fill=lit, opacity=0.48),
        # Sinuous labyrinthine valleys & ridges
        el("path", d=" ".join(lines_valley), stroke=deep, stroke_width=max(1.2, r * 0.068), fill="none", opacity=0.86, stroke_linecap="round"),
        el("path", d=" ".join(lines_ridge), stroke=lit, stroke_width=max(0.75, r * 0.042), fill="none", opacity=0.78, stroke_linecap="round"),
        el("path", d=" ".join(lines_spec), stroke="#ffffff", stroke_width=0.55, fill="none", opacity=0.52, stroke_linecap="round"),
    ])


def sea_fan(rng, x, y, h, col="#9448b0"):
    """Intricate reticulated Gorgonia ventalina sea fan with organic multi-lobed blade, branching gorgonin veins, cross-meshwork, and polyps."""
    deep = mix(col, "#1e0829", 0.48)
    lit = mix(col, "#ffd6fa", 0.38)
    segs_main, segs_sub, segs_mesh, polyps = [], [], [], []
    n_ribs = 16
    rib_curves = []
    for i in range(n_ribs):
        a = math.radians(-154 + 128 * i / (n_ribs - 1))
        L = h * rng.uniform(0.76, 1.04) * (0.88 + 0.16 * math.sin(math.pi * i / (n_ribs - 1)))
        ex, ey = x + math.cos(a) * L * 0.86, y + math.sin(a) * L
        cx_, cy_ = x + math.cos(a) * L * 0.36 + rng.uniform(-2, 2), y + math.sin(a) * L * 0.62
        rib_curves.append(((x, y), (cx_, cy_), (ex, ey)))
        if i % 2 == 0:
            segs_main.append(f"M{n(x)},{n(y)} Q{n(cx_)},{n(cy_)} {n(ex)},{n(ey)}")
        else:
            segs_sub.append(f"M{n(x)},{n(y)} Q{n(cx_)},{n(cy_)} {n(ex)},{n(ey)}")
        for t in (0.32, 0.54, 0.74, 0.90):
            px, py = quad((x, y), (cx_, cy_), (ex, ey), t)
            if i > 0:
                p_prev = quad(*rib_curves[i - 1], t)
                segs_mesh.append(f"M{n(px)},{n(py)} L{n(p_prev[0])},{n(p_prev[1])}")
            if (i + int(t * 10)) % 3 == 0:
                polyps.append(el("circle", cx=px, cy=py, r=0.65))
    # Organic multi-lobed outer fan silhouette
    rim_pts = [(x, y)] + [c[2] for c in rib_curves] + [(x, y)]
    fan_d = smooth(rim_pts, closed=True, k=0.16)
    return g([
        el("ellipse", cx=x, cy=y + 1, rx=h * 0.14, ry=2.0, fill=deep, opacity=0.65),
        el("path", d=fan_d, fill=col, opacity=0.34),
        el("path", d=" ".join(segs_mesh), stroke=lit, stroke_width=0.55, fill="none", opacity=0.68),
        el("path", d=" ".join(segs_sub), stroke=col, stroke_width=0.95, fill="none", opacity=0.90, stroke_linecap="round"),
        el("path", d=" ".join(segs_main), stroke=deep, stroke_width=1.35, fill="none", opacity=0.88, stroke_linecap="round"),
        el("path", d=f"M{n(x - 1.5)},{n(y + 1)} L{n(x)},{n(y - h * 0.25)} L{n(x + 1.5)},{n(y + 1)}Z", fill=deep),
        g(polyps, fill="#ffe89e", opacity=0.78),
    ])


def tube_sponge(x, y, h, col="#b552bd"):
    """Sculpted 3D cluster of Caribbean stove-pipe / vase sponges (Aplysina archeri) with organic tapering walls, verrucose ridges, and deep oscula."""
    lit = mix(col, "#ffe0ff", 0.36)
    mid_lit = mix(col, "#ffffff", 0.18)
    shade = mix(col, "#1c0626", 0.48)
    deep = mix(col, "#0a0210", 0.72)
    out = [el("ellipse", cx=x, cy=y + 1.5, rx=11.5, ry=2.6, fill="#06121e", opacity=0.42)]
    specs = [
        (-6.8, 0.88, 6.6, -7),
        (5.8, 0.78, 6.2, 8),
        (-0.4, 1.18, 7.8, 1),
    ]
    for dx, hh, w, tilt in specs:
        th = h * hh
        bx = x + dx
        tx = bx + tilt * (th / 28.0)
        ty = y - th
        wb = w * 0.42
        wt = w * 0.54
        # Sculpted vase/tube silhouette (narrower pedicel base, gently swollen belly, flared rim)
        tube_d = (
            f"M{n(bx - wb)},{n(y)} "
            f"C{n(bx - wb * 1.25)},{n(y - th * 0.38)} {n(tx - wt * 1.08)},{n(ty + th * 0.28)} {n(tx - wt)},{n(ty)} "
            f"Q{n(tx)},{n(ty - 1.8)} {n(tx + wt)},{n(ty)} "
            f"C{n(tx + wt * 1.08)},{n(ty + th * 0.28)} {n(bx + wb * 1.25)},{n(y - th * 0.38)} {n(bx + wb)},{n(y)} "
            f"Q{n(bx)},{n(y + 1.6)} {n(bx - wb)},{n(y)}Z"
        )
        # Shadowed right flank
        sh_d = (
            f"M{n(bx)},{n(y + 0.8)} L{n(tx)},{n(ty + 1.0)} L{n(tx + wt)},{n(ty)} "
            f"C{n(tx + wt * 1.08)},{n(ty + th * 0.28)} {n(bx + wb * 1.25)},{n(y - th * 0.38)} {n(bx + wb)},{n(y)}Z"
        )
        # Sunlit left ridge
        lit_d = (
            f"M{n(bx - wb * 0.82)},{n(y - 1)} "
            f"C{n(bx - wb * 1.05)},{n(y - th * 0.38)} {n(tx - wt * 0.90)},{n(ty + th * 0.28)} {n(tx - wt * 0.78)},{n(ty + 1)} "
            f"L{n(tx - wt * 0.22)},{n(ty + 1.5)} "
            f"C{n(tx - wt * 0.30)},{n(ty + th * 0.28)} {n(bx - wb * 0.35)},{n(y - th * 0.38)} {n(bx - wb * 0.28)},{n(y - 1)}Z"
        )
        # Verrucose horizontal sponge rings / folds
        ribs = []
        for rf in (0.22, 0.44, 0.66, 0.84):
            ry_ = y - th * rf
            rx_ = bx + (tx - bx) * rf
            rw_ = (wb * (1 - rf) + wt * rf) * 0.92
            ribs.append(f"M{n(rx_ - rw_)},{n(ry_)} Q{n(rx_)},{n(ry_ + 1.4)} {n(rx_ + rw_)},{n(ry_)}")
        out.extend([
            el("path", d=tube_d, fill=col),
            el("path", d=sh_d, fill=shade, opacity=0.46),
            el("path", d=lit_d, fill=lit, opacity=0.45),
            el("path", d=" ".join(ribs), stroke=shade, stroke_width=0.75, fill="none", opacity=0.45),
            # Flared osculum lip and dark interior cavity
            el("ellipse", cx=tx, cy=ty + 0.5, rx=wt * 0.96, ry=2.2, fill=mid_lit),
            el("ellipse", cx=tx, cy=ty + 0.6, rx=wt * 0.72, ry=1.5, fill=deep),
        ])
    return g(out)


def seagrass(rng, x0, x1, y, count, h, col="#569844"):
    segs_dark, segs_light = [], []
    dark = mix(col, "#183d1c", 0.32)
    light = mix(col, "#a8e06c", 0.28)
    for i in range(count):
        x = rng.uniform(x0, x1)
        hh = h * rng.uniform(0.5, 1.15)
        cmd = f"M{n(x)},{n(y)} q{n(rng.uniform(-6, 6))},{n(-hh * 0.52)} {n(rng.uniform(-8, 8))},{n(-hh)}"
        (segs_dark if i % 2 == 0 else segs_light).append(cmd)
    return g([
        el("path", d=" ".join(segs_dark), stroke=dark, stroke_width=1.9, fill="none", stroke_linecap="round"),
        el("path", d=" ".join(segs_light), stroke=light, stroke_width=1.6, fill="none", stroke_linecap="round"),
    ])


def light_rays(s: Scene, x0, x1, y0, y1, count, op=0.18):
    rng = s.rng
    grad = s.linear(f"ray-{int(y0)}", [
        (0, "#ffffff", 0),
        (0.14, "#fffef6", op),
        (0.58, "#ffffff", op * 0.48),
        (1, "#ffffff", 0),
    ])
    rays = []
    for _ in range(count):
        x = rng.uniform(x0, x1)
        w = rng.uniform(16, 48)
        sk = rng.uniform(42, 115)
        rays.append(el("path", d=P([(x, y0), (x + w, y0), (x + w + sk * 1.45, y1), (x + sk, y1)])))
    return g(rays, fill=grad)


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
    sky(s, [(0, "#5ea8dc"), (0.55, "#b3ddf2"), (1, "#e8f4f8")], h=WL + 4)
    sun(s, 980, 68, 23)
    s.add(cloud(rng, 260, 68, 185), cloud(rng, 690, 52, 135), cloud(rng, 1080, 82, 110, op=0.8))

    # Distant coral cay with beach berm and coconut palms
    s.add(el("path", d=smooth([(765, WL), (835, WL - 15), (930, WL - 22), (1015, WL - 12), (1075, WL)]) + "Z", fill="#eeddb0"))
    s.add(el("path", d=smooth([(800, WL - 6), (880, WL - 18), (970, WL - 15), (1035, WL - 5)]) + "Z", fill="#5b8e3e", opacity=0.65))
    for x, h, lean in ((858, 66, -9), (898, 82, -4), (942, 74, 6), (984, 60, 10), (1022, 48, 13)):
        s.add(palm(rng, x, WL - 13, h * 0.82, lean, 22, nfr=12))

    # Underwater column & Snell's window surface meniscus
    s.add(el("rect", x=0, y=WL, width=W, height=H - WL,
             fill=s.linear("water", [(0, "#35bfd6"), (0.28, "#1b92b8"), (0.68, "#0e5e8a"), (1, "#063254")])))
    s.add(light_rays(s, 360, 1160, WL, H - 50, 14, op=0.19))

    # Distant background reef ridge & pelagic drop-off for underwater depth
    bg_reef = [(320, 610), (450, 520), (590, 495), (740, 510), (900, 475), (1080, 485), (1200, 465), (1200, 620)]
    s.add(el("path", d=smooth(bg_reef[:-1]) + " L1200,620 L320,620Z", fill="#0c4c73", opacity=0.55))

    # Submerged mangrove peat/limestone bank on the left sloping down to the lagoon floor so prop roots anchor naturally
    s.add(el("path", d="M-15,210 L405,210 C385,295 345,415 285,515 C225,575 135,605 -15,610Z",
             fill=s.linear("mangrove-bank", [(0, "#24474e"), (0.5, "#193845"), (1, "#122a38")]), opacity=0.82))
    s.add(el("path", d="M-15,204 Q190,198 395,212 Q415,236 368,268 Q185,292 -15,282Z", fill="#2d261e", opacity=0.65))

    # Sandy lagoon floor & current ripples
    floor = [(0, 595), (150, 608), (330, 588), (520, 560), (700, 575), (880, 545), (1050, 560), (1200, 540)]
    fl = interp(floor)
    s.add(el("path", d=smooth(floor) + f" L{W},{H} L0,{H}Z", fill=s.linear("sand", [(0, "#e8d7aa"), (1, "#b89f6d")])))
    ripples = " ".join(f"M{n(x)},{n(fl(x) + 18 + (x * 7) % 62)} q14,-4 28,0" for x in range(12, 480, 32))
    s.add(el("path", d=ripples, stroke="#9e8756", stroke_width=1.1, fill="none", opacity=0.52))

    # Red Mangrove (Rhizophora mangle) island on the left with arching aerial & seafloor-anchored prop roots
    roots_sub_dark, roots_sub_lit, roots_air_back, roots_air_front, sponges_root = [], [], [], [], []
    bank_y = lambda rx: min(602, 310 + max(0, 360 - rx) * 0.82 + rng.uniform(-12, 14))
    for x in range(-10, 395, 28):
        cx = x + rng.uniform(-5, 5)
        cy = WL - rng.uniform(64, 96)
        roots_air_back.append(f"M{n(cx)},{n(cy)} Q{n(cx + rng.uniform(-12, 12))},{n(WL - 32)} {n(cx + rng.uniform(-8, 8))},{n(WL + 8)}")
        for idx, d in enumerate((-42, -28, -16, -4, 8, 20, 32, 44)):
            water_x = cx + d * 0.85 + rng.uniform(-3, 3)
            end_x = max(-12, min(408, cx + d * 1.25 + rng.uniform(-6, 6)))
            end_y = bank_y(end_x)
            # Aerial prop root arch above water
            cmd_air = f"M{n(cx + d * 0.18)},{n(cy + 16)} Q{n(cx + d * 0.68)},{n(WL - 28)} {n(water_x)},{n(WL + 2)}"
            (roots_air_back if idx % 2 == 0 else roots_air_front).append(cmd_air)
            # Submerged prop root arching down and anchoring into the peat bank / sandy floor
            ctrl_x = (water_x + end_x) * 0.5 + d * 0.22
            ctrl_y = WL + (end_y - WL) * 0.48
            cmd_sub = f"M{n(water_x)},{n(WL + 2)} Q{n(ctrl_x)},{n(ctrl_y)} {n(end_x)},{n(end_y)}"
            (roots_sub_dark if idx % 2 == 0 else roots_sub_lit).append(cmd_sub)
            if idx % 3 == 0:
                fork_x = end_x + (10 if d >= 0 else -10) + rng.uniform(-4, 4)
                fork_y = min(608, end_y + rng.uniform(6, 18))
                mx, my = quad((water_x, WL + 2), (ctrl_x, ctrl_y), (end_x, end_y), 0.55)
                roots_sub_dark.append(f"M{n(mx)},{n(my)} Q{n(fork_x)},{n((my + fork_y) * 0.5)} {n(fork_x)},{n(fork_y)}")
                # Irregular encrusting fire sponge / tunicate clusters wrapping the submerged root
                sp_col = "#d95b43" if (x + idx) % 2 == 0 else "#e09a3e"
                sponges_root.append(el("path", d=(
                    f"M{n(mx - 2.4)},{n(my - 5)} Q{n(mx + 3.2)},{n(my - 2)} {n(mx + 2.2)},{n(my + 5)} "
                    f"Q{n(mx - 2.8)},{n(my + 2)} {n(mx - 2.4)},{n(my - 5)}Z"
                ), fill=sp_col, opacity=0.78))
    s.add(el("path", d=" ".join(roots_sub_dark), stroke="#1a2e2e", stroke_width=2.6, fill="none", stroke_linecap="round", opacity=0.82))
    s.add(el("path", d=" ".join(roots_sub_lit), stroke="#3b523e", stroke_width=2.0, fill="none", stroke_linecap="round", opacity=0.85))
    s.add(g(sponges_root))
    s.add(el("path", d=" ".join(roots_air_back), stroke="#3d2f20", stroke_width=2.6, fill="none", stroke_linecap="round"))
    s.add(el("path", d=" ".join(roots_air_front), stroke="#5c4732", stroke_width=2.1, fill="none", stroke_linecap="round"))
    s.add(g(canopy_band(s, -25, 435, lambda x: WL - 72, 26, 28, 42, ("#1c4424", "#2e6632", "#589644"), flat=0.58, k=7)))
    s.add(egret(250, WL - 108, 0.92), egret(118, WL - 96, 0.82, flip=True))
    s.add(g([bird_v(555, 88, 9), bird_v(588, 78, 7.5), bird_v(620, 94, 8)]))

    # Water surface meniscus ripple wave & caustic network
    surf = [(x, WL + 3.5 * math.sin(x / 24) + 1.5 * math.cos(x / 11)) for x in range(0, W + 1, 16)]
    s.add(el("path", d=smooth(surf) + f" L{W},{WL - 5} L0,{WL - 5}Z", fill="#a8eaf2", opacity=0.78))
    s.add(el("path", d=smooth([(x, y + 3) for x, y in surf]), stroke="#ffffff", stroke_width=1.4, fill="none", opacity=0.65))
    s.add(water_lines(rng, 0, W, WL + 5, WL + 46, 68, op=0.48))
    caust = " ".join(f"M{n(x)},{n(WL + 18 + rng.uniform(0, 42))} q12,-7 24,0 t24,0" for x in range(400, W, 42))
    s.add(el("path", d=caust, stroke="#c8f6fa", stroke_width=1.1, fill="none", opacity=0.38))

    # Juvenile fish nursery sheltering among the submerged mangrove roots
    s.add(school(rng, 165, WL + 82, 16, 58, 4.2, "#d0dee6", stripe="#f2d43b"))
    s.add(school(rng, 285, WL + 148, 12, 45, 4.8, "#f5c428", stripe="#182430", flip=True))

    # Cushion sea stars (Oreaster reticulatus) on the sandy lagoon floor
    for sx_, sy_ in ((140, 655), (275, 635)):
        pts_star = []
        for k in range(10):
            ang = TAU * k / 10 - math.pi / 2
            rr = 9.0 if k % 2 == 0 else 3.8
            pts_star.append((sx_ + math.cos(ang) * rr, sy_ + math.sin(ang) * rr * 0.55))
        s.add(el("path", d=P(pts_star), fill="#d95338", stroke="#a63620", stroke_width=0.6))

    s.add(seagrass(rng, 0, 325, 638, 130, 36, "#549640"))
    s.add(seagrass(rng, 20, 310, 666, 92, 28, "#74ae4e"))

    # Queen Jessica Coral Nursery Frames placed on the open sandy lagoon shelf (x=328..452) with zero overlap!
    nurs = []
    for k in range(2):
        bx = 334 + k * 58
        by = 548 - k * 8
        nurs.append(el("ellipse", cx=bx + 21, cy=by + 44, rx=24, ry=3.5, fill="#0c2838", opacity=0.32))
        nurs.append(el("path", d=(
            f"M{n(bx)},{n(by + 42)} L{n(bx + 4)},{n(by)} L{n(bx + 38)},{n(by)} L{n(bx + 42)},{n(by + 42)} "
            f"M{n(bx + 2)},{n(by + 14)} L{n(bx + 40)},{n(by + 14)} M{n(bx + 1)},{n(by + 28)} L{n(bx + 41)},{n(by + 28)}"
        ), stroke="#dce6ed", stroke_width=1.6, fill="none", opacity=0.88))
        for row_y in (by + 14, by + 28):
            for j in range(4):
                fx = bx + 7 + j * 9.2
                nurs.append(el("path", d=f"M{n(fx)},{n(row_y)} l0,7 M{n(fx - 2.4)},{n(row_y + 5.5)} l2.4,-2.8 l2.4,2.8",
                               stroke="#f28452" if (j + k) % 2 == 0 else "#e8b24c", stroke_width=2.0, stroke_linecap="round", fill="none"))
    s.add(g(nurs))

    # Primary 3D terraced limestone coral reef buttress with overhangs & sandy channels
    reef = [(435, 720), (468, 608), (508, 558), (565, 535), (628, 552), (695, 520), (772, 508),
            (850, 492), (928, 512), (1012, 486), (1110, 500), (1200, 488), (1200, 720)]
    s.add(el("path", d=smooth(reef[:-1]) + " L1200,720Z", fill=s.linear("reefrock", [(0, "#8c7b68"), (0.5, "#635446"), (1, "#3d3229")])))
    rf = interp(reef[1:-1])
    # Sculpted 3D carbonate bommie ledges with irregular rocky facets, undercut cave shadows, and coralline algae crusts
    bommies = [
        (515, 596, 66, 26), (612, 582, 74, 28), (732, 558, 82, 30),
        (855, 542, 78, 28), (968, 565, 72, 26), (1105, 548, 84, 30),
        (560, 648, 84, 32), (702, 635, 92, 34), (848, 622, 88, 32), (1018, 642, 95, 34),
    ]
    for bx, by, bw, bh in bommies:
        top_ledge = [
            (bx - bw * 0.52, by + 2),
            (bx - bw * 0.38, by - bh * 0.72),
            (bx - bw * 0.08, by - bh * 0.95),
            (bx + bw * 0.26, by - bh * 0.82),
            (bx + bw * 0.50, by),
            (bx + bw * 0.22, by + bh * 0.28),
            (bx - bw * 0.24, by + bh * 0.32),
        ]
        s.add(el("path", d=smooth(top_ledge, closed=True, k=0.18), fill="#786856"))
        s.add(el("path", d=smooth(top_ledge[:5] + [(bx + bw * 0.15, by - bh * 0.25), (bx - bw * 0.28, by - bh * 0.22)], closed=True, k=0.16),
                 fill="#9c8a74", opacity=0.65))
        s.add(el("path", d=f"M{n(bx - bw * 0.46)},{n(by + 2)} Q{n(bx)},{n(by + bh * 0.42)} {n(bx + bw * 0.46)},{n(by + 2)} "
                           f"Q{n(bx)},{n(by + bh * 0.78)} {n(bx - bw * 0.46)},{n(by + 2)}Z",
                 fill="#2b221b", opacity=0.65))
        s.add(el("path", d=f"M{n(bx - bw * 0.32)},{n(by - bh * 0.58)} Q{n(bx - bw * 0.05)},{n(by - bh * 0.88)} {n(bx + bw * 0.22)},{n(by - bh * 0.65)} "
                           f"Q{n(bx)},{n(by - bh * 0.38)} {n(bx - bw * 0.32)},{n(by - bh * 0.58)}Z",
                 fill="#a85c82", opacity=0.35))

    # Realistic branching palmate Elkhorn Coral (Acropora palmata) with radiating frond lobes and pale growing rims
    def elkhorn_coral(cx, cy, sc=1.0, col="#d9923b"):
        lit = mix(col, "#fff6d8", 0.48)
        shade = mix(col, "#4a2808", 0.45)
        fronds = []
        # Base calcified trunk pedicel
        fronds.append(el("path", d=(
            f"M{n(cx - 8 * sc)},{n(cy + 8 * sc)} Q{n(cx - 4 * sc)},{n(cy - 4 * sc)} {n(cx - 6 * sc)},{n(cy - 14 * sc)} "
            f"L{n(cx + 6 * sc)},{n(cy - 14 * sc)} Q{n(cx + 4 * sc)},{n(cy - 4 * sc)} {n(cx + 9 * sc)},{n(cy + 8 * sc)}Z"
        ), fill=shade))
        # Sweeping palmate antler branches with white/cream growing margin
        specs_e = [
            (-28, -10, -8, -4, 4.2),
            (-22, -20, -4, -10, 3.8),
            (0, -25, 0, -12, 3.6),
            (22, -21, 4, -10, 3.8),
            (29, -11, 8, -4, 4.2),
            (-14, -14, -3, -6, 3.5),
            (15, -15, 3, -6, 3.5),
        ]
        for tx, ty, bx, by, w_f in specs_e:
            p0x, p0y = cx + bx * sc, cy + by * sc
            p1x, p1y = cx + tx * sc, cy + ty * sc
            c1x, c1y = (p0x + p1x) * 0.5, p1y + 3.5 * sc
            d_f = (
                f"M{n(p0x - 3 * sc)},{n(p0y)} Q{n(c1x)},{n(c1y - w_f * sc)} {n(p1x)},{n(p1y - w_f * 0.55 * sc)} "
                f"A{n(w_f * 0.6 * sc)},{n(w_f * 0.45 * sc)} 0 0 1 {n(p1x)},{n(p1y + w_f * 0.55 * sc)} "
                f"Q{n(c1x)},{n(c1y + w_f * 0.45 * sc)} {n(p0x + 3 * sc)},{n(p0y)}Z"
            )
            fronds.append(el("path", d=d_f, fill=shade, transform=f"translate(0 {n(1.8 * sc)})"))
            fronds.append(el("path", d=d_f, fill=col))
            fronds.append(el("path", d=f"M{n(p0x)},{n(p0y - 0.8 * sc)} Q{n(c1x)},{n(c1y - w_f * 0.65 * sc)} {n(p1x)},{n(p1y - w_f * 0.2 * sc)}",
                             stroke=lit, stroke_width=1.6 * sc, fill="none", stroke_linecap="round"))
        return g(fronds)

    # Organic, naturalistic coral clusters across the upper crest, mid-slope, and deep foreground
    s.add(elkhorn_coral(548, rf(548) + 8, 1.05, "#dba242"))
    s.add(elkhorn_coral(765, rf(765) + 6, 1.18, "#e08b38"))
    s.add(elkhorn_coral(935, rf(935) + 12, 0.95, "#cfa240"))
    s.add(elkhorn_coral(668, 628, 1.12, "#d9923b"))

    # Staghorn & pillar corals at varied natural coordinates and scales (well-spaced from other corals)
    for cx_, cy_, Lc, col_, w_ in (
        (482, rf(482) + 8, 25, "#e26d52", 3.4),
        (602, rf(602) + 14, 30, "#f08452", 3.8),
        (705, rf(705) + 10, 28, "#d95b82", 3.4),
        (842, rf(842) + 8, 34, "#e8b24c", 4.0),
        (1025, rf(1025) + 8, 28, "#e26d52", 3.5),
        (1158, rf(1158) + 10, 30, "#d95b82", 3.6),
        (512, 648, 32, "#f28452", 4.0),
        (782, 618, 36, "#e26d52", 4.2),
        (915, 658, 32, "#e8b24c", 3.8),
    ):
        s.add(branch_coral(rng, cx_, cy_, Lc, 3, col_, w_))

    # Grooved brain corals nestled on rock ledges
    for bx_, by_, br_, bc_ in (
        (512, rf(512) + 20, 20, "#cfa240"),
        (648, rf(648) + 18, 25, "#c29238"),
        (805, rf(805) + 22, 24, "#d4a848"),
        (980, rf(980) + 18, 21, "#c29238"),
        (1108, rf(1108) + 22, 25, "#cfa240"),
        (582, 654, 27, "#b8862d"),
        (735, 668, 25, "#cfa240"),
        (855, 638, 22, "#c29238"),
    ):
        s.add(brain_coral(rng, bx_, by_, br_, bc_))

    # Swaying Gorgonian sea fans & stove-pipe tube sponge clusters
    for fx_, fy_, fh_, fc_ in (
        (465, rf(465) + 18, 44, "#984cb5"),
        (572, rf(572) + 26, 52, "#c94886"),
        (732, rf(732) + 24, 50, "#8c48a8"),
        (888, rf(888) + 16, 56, "#c94886"),
        (1068, rf(1068) + 18, 48, "#984cb5"),
        (628, 642, 56, "#8c48a8"),
        (965, 645, 52, "#c94886"),
    ):
        s.add(sea_fan(rng, fx_, fy_, fh_, fc_))

    for sx_, sy_, sh_, sc_ in (
        (534, rf(534) + 30, 28, "#b552bd"),
        (678, rf(678) + 24, 34, "#e68235"),
        (828, rf(828) + 32, 28, "#d9534f"),
        (948, rf(948) + 30, 32, "#b552bd"),
        (1135, rf(1135) + 32, 28, "#e68235"),
        (542, 682, 32, "#d9534f"),
        (812, 672, 36, "#b552bd"),
    ):
        s.add(tube_sponge(sx_, sy_, sh_, sc_))

    # Marine Fauna
    s.add(manta(820, 298, 1.45))
    s.add(turtle(558, 378, 1.35))
    s.add(school(rng, 960, 418, 20, 72, 6.2, "#327cd6", stripe="#16346e"))
    s.add(school(rng, 700, 458, 12, 42, 6.8, "#f5d236", stripe="#141e2b", flip=True))
    for x, y, c, st in ((638, 468, "#26b8a8", "#e8689c"), (1042, 448, "#f58432", "#ffffff"),
                        (898, 468, "#4ec4e6", "#f5d236"), (518, 498, "#ebca34", "#2e72d4")):
        s.add(g(fish(x, y, 12, c, stripe=st, flip=rng.random() < 0.5)))
    s.add(g([el("circle", cx=562 + rng.uniform(-8, 8), cy=358 - i * 18, r=rng.uniform(1.8, 3.8), fill="#ffffff",
                fill_opacity=0.2, stroke="#e8fbff", stroke_width=0.9, opacity=0.75) for i in range(7)]))
    return s.render()


# ==============================================================================
# SCENE: AMAZONIAN RAINFOREST
# ==============================================================================
def build_rainforest(labels):
    s = Scene("rainforest", 1200, 720, 2006)
    rng = s.rng
    W, H = s.w, s.h
    s.blur("mist", 12)
    s.blur("haze", 4)
    sky(s, [(0, "#9ec8d2"), (0.45, "#d4e6de"), (0.8, "#ebf0e4"), (1, "#f6f2e4")])
    sun(s, 900, 108, 30, glow="#fff5cf")
    s.add(cloud(rng, 320, 82, 190, op=0.78), cloud(rng, 680, 68, 150, op=0.72))

    haze = "#c6dcd2"
    # Four receding atmospheric canopy strata with organic fractal ridge contours and overlapping tree crowns
    layers = [(286, 18, 28, 0.72), (336, 22, 34, 0.54), (388, 26, 38, 0.36), (440, 30, 44, 0.18)]
    base_cols = ("#184224", "#2b6634", "#589848")
    for li, (gy, rmin, rmax, hz) in enumerate(layers):
        cols = tuple(mix(c, haze, hz) for c in base_cols)
        keys_l = [(x, gy + 14 * math.sin(x / (92 + li * 20) + li * 1.2) + rng.uniform(-8, 8)) for x in range(-40, W + 80, 120)]
        r_pts = ridge(rng, keys_l, rough=7, depth=3)
        ground = interp(r_pts)
        s.add(el("path", d=P(r_pts + [(W + 40, H), (-40, H)]), fill=cols[0]))
        s.add(g(canopy_band(s, -35, W + 35, ground, int(W / (rmin + rmax) * 1.45), rmin, rmax, cols, lift=-4, k=5, detail=False)))
        s.add(mist(s, 280 + li * 210, gy + 10, 340, 18, op=0.44 - li * 0.06))

    # Crepuscular sunbeams piercing the canopy (softly fading in at top via upgraded light_rays)
    s.add(light_rays(s, 560, 1020, 118, 640, 7, op=0.22))

    # Giant Emergent Kapok (Ceiba pentandra) trees with tabular buttress roots
    s.add(broadleaf_tree(rng, 248, 558, 362, 95, ("#1c4826", "#357838", "#74b052"), emergent=True, k=8))
    s.add(broadleaf_tree(rng, 982, 576, 332, 86, ("#1f4d29", "#3c803e", "#7cb658"), emergent=True, k=8))

    # Mossy lateral boughs on left and right Kapok trees supporting epiphytic bromeliads and perched Toco Toucan (zero floating items!)
    s.add(el("path", d="M246,326 Q218,314 178,318", stroke="#4d3b28", stroke_width=6.5, fill="none", stroke_linecap="round"))
    s.add(el("path", d="M246,324 Q218,312 180,316", stroke="#5c8a38", stroke_width=2.4, fill="none", stroke_linecap="round"))
    s.add(el("path", d="M982,324 Q1032,306 1088,314", stroke="#4d3b28", stroke_width=7.0, fill="none", stroke_linecap="round"))
    s.add(el("path", d="M984,322 Q1032,304 1084,312", stroke="#5c8a38", stroke_width=2.6, fill="none", stroke_linecap="round"))

    # Draped woody lianas & epiphytes hanging from the emergent boughs
    lianas = []
    for x0, x1 in ((176, 204), (218, 234), (298, 332), (928, 954), (1036, 1072)):
        lianas.append(f"M{n(x0)},248 C{n(x0 - 12)},355 {n(x1 + 12)},422 {n(x1)},548")
    s.add(el("path", d=" ".join(lianas), stroke="#355224", stroke_width=2.0, fill="none", opacity=0.85))

    # Near canopy layer framing the upper river reach so the river emerges from a deep forest bend
    near_cols = ("#12361d", "#20542b", "#46863e")
    s.add(g(canopy_band(s, -45, 525, lambda x: 502 - (525 - x) * 0.07, 18, 34, 52, near_cols, k=6, detail=True)))
    s.add(g(canopy_band(s, 615, 1245, lambda x: 502 - (x - 615) * 0.06, 18, 34, 52, near_cols, k=6, detail=True)))

    # Sinuous S-curved meandering Amazonian river winding from a distant forest bend (y=476) to the wide foreground reach
    river = s.linear("river", [(0, "#b8caa4"), (0.25, "#919e6e"), (0.62, "#6b6e44"), (1, "#4a4a2c")])
    rpts_l = [
        (556, 476), (528, 502), (452, 542), (398, 586),
        (292, 632), (148, 678), (18, 720),
    ]
    rpts_r = [
        (1192, 720), (1035, 682), (848, 636), (762, 590),
        (658, 544), (602, 504), (576, 476),
    ]
    s.add(el("rect", x=0, y=476, width=W, height=H - 476, fill="#19381d"))
    # Exposed golden-ochre alluvial point-bar sandbanks along inner river bends
    s.add(el("path", d="M402,538 Q472,548 442,588 Q358,618 288,634 L252,592Z", fill="#c4a668", opacity=0.85))
    s.add(el("path", d="M752,580 Q828,602 948,656 L985,618 Q845,574 752,580Z", fill="#b8985a", opacity=0.82))
    # Main river water surface
    s.add(el("path", d=smooth(rpts_l) + " L1192,720 " + smooth(rpts_r)[1:] + " L556,476Z", fill=river))
    # Deep emerald canopy reflections shimmering along both riverbanks
    s.add(el("path", d=smooth(rpts_l) + " L265,720 L562,480Z", fill="#16331c", opacity=0.42, filter=s.url("haze")))
    s.add(el("path", d="M570,480 L945,720 " + smooth(rpts_r)[1:] + "Z", fill="#16331c", opacity=0.42, filter=s.url("haze")))
    # Sunlit water path down the center of the channel
    s.add(el("path", d="M562,480 Q582,575 605,720 L668,720 Q612,575 572,480Z", fill="#dce6c6", opacity=0.26, filter=s.url("haze")))
    s.add(water_lines(rng, 220, 990, 505, 708, 72, col="#e8eed8", op=0.48))

    # Vegetated riverbanks with narrow natural clay/earth bank rims and rich lush rainforest undergrowth
    left_mud = [(0, 512), (245, 514), (448, 542), (398, 586), (292, 632), (148, 678), (0, 720)]
    right_mud = [(1200, 512), (885, 514), (662, 544), (762, 590), (848, 636), (1035, 682), (1200, 720)]
    s.add(el("path", d=smooth(left_mud) + "Z", fill="#4a3723"))
    s.add(el("path", d=smooth(right_mud) + "Z", fill="#4a3723"))
    # Lush forest floor turf covering the interior of the banks so only a realistic muddy shoreline rim is exposed
    left_turf = [(0, 508), (245, 510), (432, 536), (368, 578), (255, 624), (105, 672), (0, 708)]
    right_turf = [(1200, 508), (885, 510), (682, 540), (792, 584), (882, 630), (1075, 676), (1200, 708)]
    s.add(el("path", d=smooth(left_turf) + "Z", fill="#1e4422"))
    s.add(el("path", d=smooth(right_turf) + "Z", fill="#1e4422"))

    s.add(g(canopy_band(s, -20, 435, interp(left_mud[1:6]), 24, 18, 32, ("#173e20", "#296330", "#549442"), lift=8, k=5)))
    s.add(g(canopy_band(s, 675, 1220, interp(right_mud[1:6]), 24, 18, 32, ("#173e20", "#296330", "#549442"), lift=8, k=5)))
    # Second foreground shrub & fern tier filling the lower corners with rich botanical detail
    s.add(g(canopy_band(s, -20, 265, lambda x: 645 + x * 0.16, 14, 22, 36, ("#14381c", "#24592b", "#4c8c3c"), k=6)))
    s.add(g(canopy_band(s, 935, 1220, lambda x: 685 - (1200 - x) * 0.16, 14, 22, 36, ("#14381c", "#24592b", "#4c8c3c"), k=6)))
    s.add(tufts(rng, 250, 440, interp(left_mud[2:5]), 42, 12, "#5c8c38"))
    s.add(tufts(rng, 670, 865, interp(right_mud[2:5]), 42, 12, "#5c8c38"))

    # Fallen mossy tree trunk jutting into the river at (295, 624) -> (425, 636)
    s.add(el("ellipse", cx=375, cy=638, rx=58, ry=4.5, fill="#1a2614", opacity=0.45))
    s.add(el("path", d="M292,624 Q358,628 418,636 L416,643 Q356,637 288,634Z", fill="#4d3926"))
    s.add(el("path", d="M295,624 Q355,627 402,633", stroke="#62943c", stroke_width=3.2, fill="none", stroke_linecap="round"))

    # Giant Victoria amazonica water lilies with flowers in calm eddies
    for x, y, r, flw in ((298, 668, 32, True), (368, 650, 23, True), (246, 694, 27, False),
                         (452, 616, 17, False), (848, 660, 25, False), (912, 692, 33, True), (778, 632, 19, False)):
        s.add(water_lily(rng, x, y, r, flower=flw))

    # Foreground botanical details: Tree ferns, Heliconia, Epiphytic Bromeliads (anchored on trunks/boughs!), Açaí palms
    for x, y, L in ((38, 642, 64), (112, 612, 52), (182, 592, 44), (1122, 642, 64), (1058, 602, 48), (985, 628, 42)):
        s.add(fern(rng, x, y, L, "#387830"))
    for x, y, h in ((72, 654, 64), (150, 636, 48), (1148, 662, 68), (1096, 632, 54)):
        s.add(heliconia(x, y, h))
    # Bromeliads anchored directly on the left & right Kapok boughs and trunk forks
    s.add(bromeliad(rng, 212, 315, 15), bromeliad(rng, 248, 322, 14), bromeliad(rng, 982, 320, 15))
    for x, y, h, lean in ((138, 602, 145, 13), (1082, 612, 155, -15), (452, 534, 114, 7), (698, 540, 104, -5)):
        s.add(palm(rng, x, y, h, lean, 40, cols=("#24582a", "#407d36"), coconuts=False, trunk_col="#665540", nfr=13))

    # Fauna: Boto river dolphin, Caiman, Scarlet Macaws, Toco Toucan perched on right Kapok bough (1035, 310), Blue Morphos
    s.add(dolphin(608, 610, 1.65))
    s.add(caiman(488, 596, 0.88))
    s.add(macaw(558, 198, 1.15), macaw(642, 178, 0.98, flip=True), macaw(722, 218, 0.85))
    s.add(toucan(1035, 294, 1.15))
    s.add(morpho(538, 448, 1.5), morpho(762, 478, 1.25), morpho(330, 540, 1.3))
    s.add(mist(s, 565, 476, 220, 18, op=0.42))
    return s.render()


# ==============================================================================
# SCENE: BRAZILIA HIGHLANDS
# ==============================================================================
def build_highlands(labels):
    s = Scene("highlands", 1200, 700, 2890)
    rng = s.rng
    W, H = s.w, s.h
    s.blur("mist", 14)
    s.blur("soft", 3)
    sky(s, [(0, "#4f8cc4"), (0.48, "#9ec6e2"), (0.82, "#dcebf2"), (1, "#eff4f1")])
    sun(s, 260, 98, 24)
    s.add(cloud(rng, 825, 88, 175, op=0.88), cloud(rng, 515, 58, 125, op=0.82))

    # Distant snow-capped cordillera
    r1, _ = mountain(s, "r1", [(0, 330), (120, 246), (240, 288), (360, 186), (470, 238), (600, 146),
                               (720, 208), (860, 126), (980, 198), (1100, 156), (1200, 218)],
                     460, "#9ab2ca", shade="#5c7694", shade_op=0.36, snow=214, rough=10)
    s.add(r1)
    s.add(mist(s, 600, 298, 530, 26, op=0.58))

    # Main Andean / Brazilia Massif
    r2, _ = mountain(s, "r2", [(375, 420), (498, 296), (578, 226), (638, 156), (690, 114), (742, 166),
                               (802, 136), (872, 206), (962, 256), (1062, 326), (1200, 378)],
                     560, "#75685e", shade="#24222e", shade_op=0.45, snow=212, rough=11, tongue=0.28)
    s.add(r2)

    # Realistic branching alpine cirque & valley glacier descending to high cirque basin at y=338
    glac_poly = [
        (690, 116), (715, 148), (742, 164), (772, 150), (800, 138),
        (792, 174), (786, 212), (798, 254), (818, 298), (840, 336),
        (772, 344), (752, 312), (734, 270), (718, 226), (704, 180), (684, 142),
    ]
    s.add(el("path", d=smooth(glac_poly, closed=True),
             fill=s.linear("glacier", [(0, "#f5fafe"), (0.48, "#d8ecf8"), (1, "#8ec2e0")])))
    # 3D blue-ice serac facets and subtle lateral moraine talus shadows (no thick brown strokes or ski chevrons)
    s.add(el("path", d="M742,164 L772,150 L800,138 L792,174 L786,212 L798,254 L818,298 L840,336 L810,340 L768,278 L748,214Z",
             fill="#75aac9", opacity=0.48))
    s.add(el("path", d="M684,142 L704,180 L718,226 L734,270 L752,312 L772,344 L760,345 L724,274 L696,188Z",
             fill="#595048", opacity=0.42))
    # Sculpted transverse icefall serac steps & blue crevasse fissures
    seracs = [
        "M708,184 Q728,191 748,185 L746,190 Q726,196 706,188Z",
        "M754,186 Q769,192 784,185 L782,190 Q768,196 752,190Z",
        "M718,216 Q742,225 768,217 L766,223 Q740,231 716,221Z",
        "M728,250 Q758,261 788,251 L786,257 Q756,267 726,255Z",
        "M742,284 Q774,296 806,286 L804,292 Q772,302 740,290Z",
        "M758,316 Q792,328 824,318 L822,324 Q790,334 756,322Z",
    ]
    s.add(el("path", d=" ".join(seracs), fill="#38789e", opacity=0.68))
    s.add(el("path", d=" ".join(seracs), fill="#ffffff", opacity=0.75, transform="translate(0 -1.5)"))

    # High alpine cirque moraine lake at y=344 (elevated above the waterfall lip at y=374 so the stream flows DOWNHILL!)
    s.add(el("path", d="M724,344 Q768,328 822,330 Q875,332 898,346 Q872,362 812,362 Q750,360 724,344Z", fill="#544d45"))
    s.add(el("ellipse", cx=812, cy=345, rx=74, ry=13.5, fill=s.linear("lake", [(0, "#68d2d8"), (0.5, "#36aebf"), (1, "#1d7a94")])))
    s.add(el("ellipse", cx=808, cy=341, rx=54, ry=5.5, fill="#c8f4f6", opacity=0.48))
    s.add(water_lines(rng, 752, 872, 339, 351, 14, op=0.55))
    for bx_, by_, br_ in ((738, 350, 8), (754, 355, 6), (864, 354, 9), (882, 349, 7)):
        s.add(el("path", d=f"M{bx_ - br_},{by_} L{bx_ - br_ * 0.5},{by_ - br_ * 0.7} L{bx_ + br_ * 0.6},{by_ - br_ * 0.6} L{bx_ + br_},{by_}Z", fill="#665f57"))

    # Multi-layered rolling Páramo alpine grassland ridges sloping downhill from right (y=356) to left cataract lip (y=374)
    paramo1 = [(0, 445), (200, 405), (290, 374), (450, 368), (620, 358), (820, 352), (1000, 378), (1200, 402)]
    pf1 = interp(paramo1)
    s.add(el("path", d=smooth(paramo1) + f" L{W},{H} L0,{H}Z", fill=s.linear("paramo1", [(0, "#a8a460"), (0.5, "#8b944e"), (1, "#6b7a3e")])))
    paramo2 = [(280, 512), (460, 468), (650, 452), (850, 472), (1040, 458), (1200, 482)]
    pf2 = interp(paramo2)
    s.add(el("path", d=smooth(paramo2) + f" L{W},{H} L280,{H}Z", fill=s.linear("paramo2", [(0, "#94994e"), (1, "#627338")])))
    paramo3 = [(340, 572), (540, 524), (740, 534), (940, 514), (1200, 542)]
    pf3 = interp(paramo3)
    s.add(el("path", d=smooth(paramo3) + f" L{W},{H} L340,{H}Z", fill="#768442"))

    # Braided glacial meltwater stream winding DOWNHILL from lake outlet (762, 352) -> (540, 364) -> cataract notch (288, 374)!
    stream_outer = "M764,351 C695,358 610,364 515,367 C425,370 350,372 290,374 L286,379 C350,378 428,376 518,373 C615,370 700,363 772,354Z"
    s.add(el("path", d=stream_outer, fill="#544d44", opacity=0.65))
    stream_water = "M768,352 C698,359 612,365 516,368 C426,371 350,373 288,376"
    s.add(el("path", d=stream_water, stroke="#48aebf", stroke_width=4.6, fill="none", stroke_linecap="round"))
    s.add(el("path", d=stream_water, stroke="#cef6fc", stroke_width=1.5, fill="none", stroke_linecap="round", opacity=0.82))
    # Emerald bofedales cushion-plant bogs along the braided stream & mid-ground depressions
    for cx_, cy_, rx_, ry_ in ((545, 372, 48, 6.0), (665, 364, 42, 5.2), (765, 468, 56, 8.0), (925, 518, 62, 8.5)):
        s.add(el("ellipse", cx=cx_, cy=cy_, rx=rx_, ry=ry_, fill="#4e7836", opacity=0.75))
        s.add(el("ellipse", cx=cx_ - 6, cy=cy_ - 1, rx=rx_ * 0.65, ry=ry_ * 0.65, fill="#6e9c46", opacity=0.7))

    # Varied tussock grass across the páramo slopes (using vertical jitter so tufts never form rigid horizontal lines)
    s.add(tufts(rng, 320, W, lambda x: pf1(x) + rng.uniform(2, 38), 110, 10, "#c7b868", op=0.85))
    s.add(tufts(rng, 340, W, lambda x: pf2(x) + rng.uniform(2, 42), 120, 13, "#bfae5c", op=0.90))
    s.add(tufts(rng, 380, W, lambda x: pf3(x) + rng.uniform(2, 42), 105, 15, "#b3a250", op=0.92))

    # Botanically realistic Espeletia frailejón & Puya raimondii
    def frailejon(fx, fy, sc=1.0):
        # Tapered marcescent dead-leaf skirt trunk
        skirt = [
            el("ellipse", cx=fx + 1, cy=fy + 1, rx=6.5 * sc, ry=1.8 * sc, fill="#000000", opacity=0.22),
            el("path", d=f"M{n(fx - 3.6 * sc)},{n(fy)} L{n(fx - 2.6 * sc)},{n(fy - 21 * sc)} L{n(fx + 2.6 * sc)},{n(fy - 21 * sc)} L{n(fx + 3.6 * sc)},{n(fy)}Z",
               fill="#6e5a44"),
            el("path", d=f"M{n(fx)},{n(fy)} L{n(fx)},{n(fy - 21 * sc)} L{n(fx + 2.6 * sc)},{n(fy - 21 * sc)} L{n(fx + 3.6 * sc)},{n(fy)}Z",
               fill="#47392b", opacity=0.65),
        ]
        for sy_off in (5, 10, 15, 19):
            skirt.append(el("path", d=f"M{n(fx - 3.4 * sc)},{n(fy - sy_off * sc)} Q{n(fx)},{n(fy - (sy_off - 1.8) * sc)} {n(fx + 3.4 * sc)},{n(fy - sy_off * sc)}",
                            stroke="#8f7c64", stroke_width=1.1 * sc, fill="none"))
        # Cupped silvery-sage rosette of lance-shaped leaves (viewed in 3/4 perspective, not a flat pinwheel)
        cy_r = fy - 22 * sc
        leaves_back, leaves_front = [], []
        for i in range(16):
            a = TAU * i / 16
            lx = fx + math.cos(a) * 8.2 * sc
            ly = cy_r + math.sin(a) * 4.2 * sc - (1.8 * sc if math.sin(a) < 0 else 0)
            col_l = "#d2dcc0" if i % 2 == 0 else "#a5b592"
            d_l = f"M{n(fx)},{n(cy_r)} Q{n((fx + lx) * 0.5 - math.sin(a) * 1.4 * sc)},{n((cy_r + ly) * 0.5 - 1.5 * sc)} {n(lx)},{n(ly)} Q{n((fx + lx) * 0.5 + math.sin(a) * 1.4 * sc)},{n((cy_r + ly) * 0.5 + 1.2 * sc)} {n(fx)},{n(cy_r)}Z"
            (leaves_back if math.sin(a) < 0 else leaves_front).append(el("path", d=d_l, fill=col_l))
        # Erect flowering corymb stalks with golden Espeletia capitula
        blooms = [
            el("path", d=f"M{n(fx - 1 * sc)},{n(cy_r)} L{n(fx - 3.2 * sc)},{n(cy_r - 7 * sc)} M{n(fx + 1 * sc)},{n(cy_r)} L{n(fx + 2.8 * sc)},{n(cy_r - 6.5 * sc)} M{n(fx)},{n(cy_r)} L{n(fx)},{n(cy_r - 8 * sc)}",
               stroke="#7d8c68", stroke_width=0.9 * sc, fill="none"),
            el("circle", cx=fx - 3.2 * sc, cy=cy_r - 7 * sc, r=1.6 * sc, fill="#f2ca38"),
            el("circle", cx=fx + 2.8 * sc, cy=cy_r - 6.5 * sc, r=1.5 * sc, fill="#e6bc2e"),
            el("circle", cx=fx, cy=cy_r - 8.2 * sc, r=1.8 * sc, fill="#f7d548"),
        ]
        return g([*skirt, *leaves_back, *blooms, *leaves_front])

    def puya_spike(px, py, sc=1.0):
        # Dense spherical basal rosette of recurved spiny blades
        spiky_base = []
        for d in range(-18, 19, 2):
            ang = math.radians(-90 + d * 4.2)
            ln = (16 - abs(d) * 0.25) * sc
            ex = px + math.cos(ang) * ln * 1.15
            ey = py - 5 * sc + math.sin(ang) * ln * 0.72 + (abs(d) * 0.28 * sc)
            spiky_base.append(f"M{n(px)},{n(py - 4 * sc)} Q{n((px + ex) * 0.5)},{n(ey - 3 * sc)} {n(ex)},{n(ey)}")
        # Continuous tapering cylindrical floral spike with textured floret bracts (no stacked hamburger buns)
        sh_h = 68 * sc
        spike_d = (
            f"M{n(px - 4.8 * sc)},{n(py - 16 * sc)} "
            f"C{n(px - 5.2 * sc)},{n(py - 38 * sc)} {n(px - 2.6 * sc)},{n(py - 60 * sc)} {n(px)},{n(py - sh_h)} "
            f"C{n(px + 2.6 * sc)},{n(py - 60 * sc)} {n(px + 5.2 * sc)},{n(py - 38 * sc)} {n(px + 4.8 * sc)},{n(py - 16 * sc)}Z"
        )
        florets = []
        for k in range(16):
            fy_ = py - (18 + k * 3.0) * sc
            fw_ = (4.6 - k * 0.24) * sc
            florets.append(f"M{n(px - fw_)},{n(fy_)} Q{n(px)},{n(fy_ - 1.6 * sc)} {n(px + fw_)},{n(fy_)}")
        return g([
            el("ellipse", cx=px + 1, cy=py + 1, rx=14 * sc, ry=2.5 * sc, fill="#000000", opacity=0.22),
            el("path", d=f"M{n(px - 3.5 * sc)},{n(py)} L{n(px - 2.2 * sc)},{n(py - 18 * sc)} L{n(px + 2.2 * sc)},{n(py - 18 * sc)} L{n(px + 3.5 * sc)},{n(py)}Z", fill="#5c4e38"),
            el("path", d=" ".join(spiky_base), stroke="#4d6b3c", stroke_width=1.45 * sc, fill="none", stroke_linecap="round"),
            el("path", d=spike_d, fill="#b8b268"),
            el("path", d=f"M{n(px)},{n(py - 16 * sc)} L{n(px)},{n(py - sh_h)} C{n(px + 2.6 * sc)},{n(py - 60 * sc)} {n(px + 5.2 * sc)},{n(py - 38 * sc)} {n(px + 4.8 * sc)},{n(py - 16 * sc)}Z",
               fill="#8a8444", opacity=0.55),
            el("path", d=" ".join(florets), stroke="#dcd68e", stroke_width=1.2 * sc, fill="none", stroke_linecap="round"),
        ])

    # Distant, mid-ground, and near-ground Puya & Frailejón clusters across the 3 páramo ridges
    for x, sc in ((518, 0.72), (582, 0.78), (912, 0.75), (968, 0.68)):
        s.add(puya_spike(x, pf1(x) + 12, sc))
    for x, sc in ((642, 0.68), (678, 0.75), (712, 0.65), (1035, 0.74), (1078, 0.68)):
        s.add(frailejon(x, pf1(x) + 14, sc))
    for x, sc in ((495, 0.95), (615, 1.05), (845, 0.92), (1015, 1.02), (1125, 0.88)):
        s.add(frailejon(x, pf2(x) + 8, sc))
    for x, sc in ((725, 0.98), (1068, 0.94)):
        s.add(puya_spike(x, pf2(x) + 8, sc))
    for x, sc in ((585, 1.22), (632, 1.12), (895, 1.25), (948, 1.15)):
        s.add(frailejon(x, pf3(x) + 10, sc))

    # Sculpted 3D craggy Andean rock cliff on the left with stepped ledges, cloud forest, and multi-stage cataract
    cliff = [(0, 326), (65, 318), (148, 336), (235, 348), (308, 374), (342, 448), (368, 565), (0, 565)]
    cliff_d = smooth(cliff[:-1]) + " L0,565Z"
    s.add(el("path", d=cliff_d, fill="#545048"))
    ccid = s.clip("hl_cliff", cliff_d)
    cliff_facets = [
        el("path", d="M0,320 L165,335 L145,565 L0,565Z", fill="#6e685d", opacity=0.55),
        el("path", d="M215,340 L370,360 L370,565 L245,565Z", fill="#33302b", opacity=0.65),
        el("path", d="M0,388 Q110,398 225,392 Q295,400 345,408 L345,424 Q220,412 0,404Z", fill="#3d3a34", opacity=0.72),
        el("path", d="M0,448 Q125,460 245,452 Q315,460 358,470 L358,486 Q230,472 0,464Z", fill="#36332e", opacity=0.72),
        el("path", d="M0,508 Q140,518 265,512 L365,524 L365,540 L0,522Z", fill="#2b2924", opacity=0.72),
        el("path", d="M72,330 L58,445 L75,555 M155,338 L172,455 L158,555 M232,345 L218,465 L235,555",
           stroke="#262420", stroke_width=1.6, fill="none", opacity=0.6),
    ]
    for lx, ly, lr in ((65, 388, 16), (145, 392, 18), (218, 394, 15), (95, 450, 17), (188, 454, 19), (135, 512, 16)):
        cliff_facets.append(crown(rng, lx, ly, lr, ("#1c3e26", "#2e5c38", "#588c52"), k=4, flat=0.45, detail=False))
    s.add(g(cliff_facets, clip_path=ccid))

    cf = interp(cliff[:5])
    s.add(g(canopy_band(s, -25, 268, cf, 24, 17, 27, ("#22452e", "#36663d", "#649658"), k=5)))
    # Multi-tiered cataract plunging from the downhill stream notch (288, 374) over a mid-cliff rock ledge into the plunge pool
    s.add(waterfall(s, 286, 372, 460, 22))
    s.add(el("path", d="M258,460 Q290,454 322,460 L316,470 L264,470Z", fill="#45413a"))
    s.add(waterfall(s, 292, 458, 560, 26))

    # Lower cloud-forest bank sweeping smoothly into the foreground alpine meadow
    lower = [(0, 560), (200, 545), (360, 560), (485, 608), (620, 680), (650, H)]
    lf = interp(lower[:5])
    s.add(el("path", d=smooth(lower) + f" L0,{H}Z", fill="#345430"))
    s.add(el("ellipse", cx=300, cy=575, rx=94, ry=17, fill=s.linear("pool", [(0, "#7ad0dc"), (1, "#2f829c")])))
    s.add(water_lines(rng, 215, 385, 565, 586, 18, op=0.62))
    s.add(g(canopy_band(s, -30, 232, lf, 15, 21, 33, ("#1c3e26", "#2e5c38", "#588c52"), k=6, detail=True)))
    s.add(g(canopy_band(s, 358, 515, lf, 8, 19, 29, ("#1c3e26", "#2e5c38", "#588c52"), k=6, detail=True)))
    for x, y in ((58, 522), (148, 502), (418, 562)):
        s.add(fern(rng, x, y, 42, "#468640"))
    s.add(heliconia(105, 545, 44))
    s.add(mist(s, 180, 345, 240, 26, op=0.55))
    s.add(mist(s, 295, 460, 125, 18, op=0.52))

    # Foreground alpine meadow overlapping the lower slope naturally with mossy boulders, ferns, & foreground frailejón
    fg = [(380, H), (455, 632), (550, 592), (660, 582), (820, 598), (1000, 585), (1200, 600)]
    fg_fn = interp(fg)
    s.add(el("path", d=smooth(fg) + f" L{W},{H} L380,{H}Z", fill="#63753c"))
    s.add(tufts(rng, 420, W, lambda x: fg_fn(x) + rng.uniform(2, 55), 125, 18, "#bda956", width=1.35))
    for x, y, r in ((465, 648, 26), (522, 668, 18), (620, 642, 30), (702, 662, 19), (1060, 652, 36), (1132, 672, 23)):
        s.add(el("ellipse", cx=x + 2, cy=y + 2, rx=r * 1.08, ry=r * 0.2, fill="#000000", opacity=0.25))
        s.add(el("path", d=f"M{n(x - r)},{n(y)} L{n(x - r * 0.75)},{n(y - r * 0.78)} L{n(x - r * 0.1)},{n(y - r * 0.92)} L{n(x + r * 0.68)},{n(y - r * 0.72)} L{n(x + r)},{n(y)}Z",
                 fill="#858680"))
        s.add(el("path", d=f"M{n(x - r * 0.1)},{n(y - r * 0.92)} L{n(x + r * 0.68)},{n(y - r * 0.72)} L{n(x + r)},{n(y)} L{n(x + r * 0.05)},{n(y)}Z",
                 fill="#52534e"))
        s.add(el("path", d=f"M{n(x - r * 0.75)},{n(y - r * 0.78)} Q{n(x - r * 0.35)},{n(y - r * 0.95)} {n(x + r * 0.2)},{n(y - r * 0.82)}",
                 stroke="#6b8c42", stroke_width=2.5, fill="none", stroke_linecap="round", opacity=0.75))
    s.add(fern(rng, 442, 656, 38, "#468640"))

    # Fauna: Soaring Andean Condors placed against the open sky (no peak/glacier collision!) and hovering Emerald Hummingbird
    s.add(condor(452, 132, 1.48), condor(618, 86, 0.96))
    s.add(hummingbird(218, 488, 1.65))
    s.add(g([bird_v(1000, 120, 8), bird_v(1032, 110, 6.5)]))
    return s.render()


# ==============================================================================
# ATLAS VIGNETTES (480 x 300)
# ==============================================================================
def vignette(key, seed):
    s = Scene(key, 480, 300, seed)
    s.blur("mist", 7)
    s.blur("soft", 2.5)
    return s


def build_mogotes(labels):
    s = vignette("mogotes", 101)
    rng = s.rng
    sky(s, [(0, "#5a98d4"), (0.5, "#a8d4ee"), (1, "#f7ecd8")])
    sun(s, 385, 54, 16, glow="#fff2d0")
    s.add(cloud(rng, 118, 50, 105), cloud(rng, 290, 40, 80, op=0.82))

    # Distant hazy karst hills in atmospheric perspective
    h_far, _ = hill(s, [(0, 192), (90, 162), (210, 182), (340, 155), (480, 178)], 240, "#9bb7a3", rough=6)
    s.add(h_far)
    s.add(mist(s, 240, 180, 260, 14, op=0.45))

    # Three distinct sculpted limestone mogote haystack towers with 3D karst buttresses, vertical solution flutes, & lush jungle domes
    mogote_specs = [
        (-22, 128, 108, "#58865a", "#324f34", "#bdb8a6", "#7a7666"),
        (312, 492, 98, "#4c7a42", "#284622", "#c4bfb0", "#7e7a6a"),
        (114, 296, 68, "#3e6e2e", "#1f3e16", "#ccc7b6", "#858170"),
    ]
    for x0, x1, top, col, shade, rock_lit, rock_sh in mogote_specs:
        mw = x1 - x0
        keys = [
            (x0, 238), (x0 + mw * 0.05, top + 46), (x0 + mw * 0.14, top + 12),
            (x0 + mw * 0.34, top + 2), (x0 + mw * 0.56, top), (x0 + mw * 0.78, top + 8),
            (x1 - mw * 0.07, top + 44), (x1, 238),
        ]
        d = smooth(keys) + "Z"
        s.add(el("path", d=d, fill=rock_lit))
        cid = s.clip(f"m{x0}", d)
        inner = [
            # Multi-faceted 3D limestone buttress shading (no flat orthogonal prison bars!)
            el("path", d=f"M{n(x0 + mw * 0.48)},{n(top)} L{n(x1)},{n(top)} L{n(x1)},240 L{n(x0 + mw * 0.54)},240Z",
               fill=rock_sh, opacity=0.88),
            el("path", d=f"M{n(x0 + mw * 0.28)},{n(top + 10)} L{n(x0 + mw * 0.48)},{n(top)} L{n(x0 + mw * 0.54)},240 L{n(x0 + mw * 0.34)},240Z",
               fill=mix(rock_lit, rock_sh, 0.45), opacity=0.65),
        ]
        # Tapered vertical karst solution flutes & stalactite ribs (speleothem draperies on cliff wall)
        for fx_rel in (0.14, 0.23, 0.33, 0.44, 0.56, 0.67, 0.77, 0.86):
            fx = x0 + mw * fx_rel + rng.uniform(-2.5, 2.5)
            fw = mw * rng.uniform(0.025, 0.048)
            f_bot = rng.uniform(195, 232)
            f_col = "#363830" if fx_rel < 0.5 else "#242620"
            inner.append(el("path", d=(
                f"M{n(fx - fw * 0.5)},{n(top + 22)} Q{n(fx)},{n((top + f_bot) * 0.5)} {n(fx - fw * 0.15)},{n(f_bot)} "
                f"L{n(fx + fw * 0.35)},{n(f_bot - 6)} Q{n(fx + fw * 0.5)},{n((top + f_bot) * 0.5)} {n(fx + fw * 0.5)},{n(top + 22)}Z"
            ), fill=f_col, opacity=0.42))
            # Rust-orange iron-oxide / mineral streak typical of Viñales limestone cliffs
            if fx_rel in (0.23, 0.56, 0.77):
                inner.append(el("path", d=f"M{n(fx + 1.5)},{n(top + 26)} L{n(fx + 0.5)},{n(f_bot - 12)}",
                                stroke="#a8683c", stroke_width=1.6, opacity=0.35, fill="none"))
        # Karst cavern mouths and undercut solution notches at cliff base
        inner.append(el("path", d=f"M{n(x0 + mw * 0.30)},238 Q{n(x0 + mw * 0.39)},208 {n(x0 + mw * 0.49)},238Z",
                        fill="#121a0e", opacity=0.88))
        inner.append(el("path", d=f"M{n(x0 + mw * 0.66)},238 Q{n(x0 + mw * 0.72)},220 {n(x0 + mw * 0.78)},238Z",
                        fill="#121a0e", opacity=0.80))
        # Continuous vegetated horizontal bedding terrace across mid-cliff
        ledge_y = top + (235 - top) * 0.52
        for lx_f in (0.18, 0.28, 0.38, 0.58, 0.68, 0.78):
            lx = x0 + mw * lx_f + rng.uniform(-2, 2)
            ly = ledge_y + rng.uniform(-4, 4)
            inner.append(crown(rng, lx, ly, rng.uniform(6.5, 9.5),
                               (mix(col, "#0d240c", 0.4), col, mix(col, "#a8cc62", 0.25)), k=4, flat=0.52, detail=False))
        # Talus piedmont skirt at cliff base
        for i in range(13):
            vx = x0 + mw * (0.04 + 0.92 * i / 12) + rng.uniform(-2, 2)
            inner.append(crown(rng, vx, rng.uniform(218, 234), rng.uniform(9, 15),
                               (mix(col, "#0d240c", 0.38), col, mix(col, "#a8cc62", 0.25)), k=5, detail=False))
        # Dense rounded tropical jungle cap over the summit dome with hanging vines cascading over the rock rim
        inner.append(el("path", d=f"M{n(x0)},{n(top + 38)} Q{n((x0 + x1) * 0.5)},{n(top + 18)} {n(x1)},{n(top + 38)} L{n(x1)},{n(top)} L{n(x0)},{n(top)}Z",
                        fill=shade))
        for i in range(18):
            vx = x0 + mw * (0.05 + 0.90 * i / 17) + rng.uniform(-2.5, 2.5)
            vy = top + rng.uniform(5, 22) + abs(vx - (x0 + x1) / 2) * 0.14
            inner.append(crown(rng, vx, vy, rng.uniform(9.5, 14.5),
                               (mix(col, "#0d240c", 0.35), col, mix(col, "#c4e078", 0.28)), k=5, detail=False))
        s.add(g(inner, clip_path=cid))
        s.add(mist(s, (x0 + x1) / 2, 234, mw * 0.62, 10, op=0.50))

    # Rich terra-rossa red soil valley floor & grassy farmstead clearing on the right
    s.add(el("rect", x=0, y=232, width=480, height=68, fill=s.linear("soil", [(0, "#8f4e2c"), (1, "#5c2e16")])))
    # Grassy farmstead border on the right (x=255..480) and left (x=0..58) so palms and bohío stand on natural turf, not inside plowed furrows!
    s.add(el("path", d="M0,232 L68,232 L24,300 L0,300Z M245,232 L480,232 L480,300 L278,300Z",
             fill=s.linear("turf-m", [(0, "#567d30"), (1, "#38591e")])))
    # Winding red-earth farm track leading to the bohío doorway
    s.add(el("path", d="M252,300 Q288,282 316,268 L328,268 Q304,284 276,300Z", fill="#9c5834", opacity=0.85))

    # Cultivated perspective tobacco field cleanly framed in the central plot (x=32..268)
    furrows_sh, ridges_soil, plants_dark, plants_lit = [], [], [], []
    for i in range(8):
        bx = 34 + i * 31
        tx = 82 + i * 21
        furrows_sh.append(f"M{n(bx - 3.5)},300 L{n(tx - 1.5)},235")
        ridges_soil.append(f"M{n(bx)},300 L{n(tx)},235")
        for st in range(14):
            t = st / 13
            px = bx + (tx - bx) * t + rng.uniform(-0.9, 0.9)
            py = 299 + (236 - 299) * t
            sc = 1.08 - 0.56 * t
            rw, rh = 6.8 * sc, 3.8 * sc
            plants_dark.append(f"M{n(px - rw)},{n(py)} Q{n(px)},{n(py - rh * 1.65)} {n(px + rw)},{n(py)} Q{n(px)},{n(py + rh * 0.65)} {n(px - rw)},{n(py)}Z")
            plants_lit.append(f"M{n(px - rw * 0.72)},{n(py - 0.5)} Q{n(px - rw * 0.2)},{n(py - rh * 1.45)} {n(px + rw * 0.52)},{n(py - 0.5)}Z")
    s.add(el("path", d=" ".join(furrows_sh), stroke="#3b1b0a", stroke_width=4.5, opacity=0.72, fill="none"))
    s.add(el("path", d=" ".join(ridges_soil), stroke="#a6603a", stroke_width=3.0, opacity=0.65, fill="none"))
    s.add(el("path", d=" ".join(plants_dark), fill="#386920"))
    s.add(el("path", d=" ".join(plants_lit), fill="#689e35"))
    s.add(tufts(rng, 280, 475, lambda x: 242 + rng.uniform(0, 52), 45, 9, "#749e3e", op=0.82))

    # Traditional thatched tobacco curing barn (bohío) with timber framing, overhang eaves, and palm thatch
    s.add(el("polygon", points="288,268 372,268 382,273 296,273", fill="#000000", opacity=0.28))
    s.add(el("rect", x=298, y=247, width=36, height=21, fill="#8a623a"))
    s.add(el("rect", x=334, y=247, width=26, height=21, fill="#593d22"))
    s.add(el("path", d="M306,247 L306,268 M314,247 L314,268 M326,247 L326,268 M342,247 L342,268 M350,247 L350,268",
             stroke="#422c16", stroke_width=0.8, opacity=0.55))
    s.add(el("rect", x=314, y=253, width=10, height=15, fill="#26170a"))
    s.add(el("polygon", points="290,250 328,216 368,250", fill="#b58b52"))
    s.add(el("polygon", points="328,216 368,250 336,250", fill="#7d5d34"))
    s.add(el("path", d="M295,245 L363,245 M301,239 L357,239 M308,233 L350,233 M315,227 L343,227",
             stroke="#5e4424", stroke_width=1.1, opacity=0.65))
    s.add(el("path", d="M322,216 L334,216", stroke="#4a3419", stroke_width=2.0, stroke_linecap="round"))

    # Cuban Royal Palms (Roystonea regia) positioned on grassy field borders flanking the plantation & bohío
    for x, y, h, lean in ((26, 274, 118, 4), (266, 250, 92, -3), (388, 252, 88, 3), (442, 276, 126, -5)):
        s.add(palm(rng, x, y, h, lean, 24 * (h / 110), royal=True, nfr=13, trunk_col="#d6cfc0"))
    s.add(g([bird_v(210, 72, 6.5), bird_v(228, 65, 5.5)]))
    return s.render()


def build_enriquillo(labels):
    s = vignette("enriquillo", 102)
    rng = s.rng
    sky(s, [(0, "#5898cc"), (0.55, "#aed2ea"), (1, "#f7ead2")])
    sun(s, 88, 56, 16, glow="#fff0cc")
    s.add(cloud(rng, 250, 46, 95, op=0.85), cloud(rng, 400, 60, 75, op=0.75))

    # Arid Sierra de Bahoruco / Neiba mountain ranges with stratified rock facets
    m_far, _ = mountain(s, "mf", [(0, 175), (140, 126), (260, 150), (390, 106), (480, 136)], 205,
                        "#cca885", shade="#856b50", shade_op=0.32, rough=6)
    s.add(m_far)
    m, _ = mountain(s, "m", [(0, 166), (92, 114), (182, 146), (292, 84), (382, 126), (480, 104)], 206,
                    "#b89066", shade="#614732", shade_op=0.40, rough=8)
    s.add(m)

    # Hypersaline Lago Enriquillo water body with sparkling mineral salt-crust shoreline
    s.add(el("rect", x=0, y=198, width=480, height=64,
             fill=s.linear("lake", [(0, "#5ec9cc"), (0.45, "#32a4b2"), (1, "#186e85")])))
    salt_far = [(0, 198), (80, 201), (190, 199), (310, 202), (420, 199), (480, 201)]
    s.add(el("path", d=smooth(salt_far) + " L480,196 L0,196Z", fill="#faf7f0", opacity=0.92))
    s.add(water_lines(rng, 0, 480, 204, 254, 38, col="#e6f7f6", op=0.52))

    # Bleached salt-encrusted dead tree snags standing in the hypersaline lake (completely clear of cacti and caiman!)
    s.add(el("ellipse", cx=62, cy=224, rx=10, ry=1.8, fill="#ffffff", opacity=0.45))
    s.add(el("path", d="M62,224 L61,203 L54,193 M61,211 L69,202 M61,216 L53,209",
             stroke="#ede6d8", stroke_width=2.1, fill="none", stroke_linecap="round"))
    s.add(el("ellipse", cx=352, cy=226, rx=11, ry=1.8, fill="#ffffff", opacity=0.45))
    s.add(el("path", d="M352,226 L353,200 L345,189 M353,208 L362,198 M352,214 L344,206",
             stroke="#ede6d8", stroke_width=2.2, fill="none", stroke_linecap="round"))

    # Flock of Caribbean Flamingos in varied wading and filter-feeding poses (spaced cleanly above the salt shoreline!)
    flamingo_specs = [
        (144, 214, 0.90, False, "stand"),
        (176, 219, 0.86, False, "feed"),
        (210, 213, 0.92, True, "stand"),
        (240, 218, 0.86, False, "stand"),
        (274, 215, 0.88, False, "feed"),
        (312, 218, 0.88, True, "stand"),
    ]
    for fx, fy, fs, flp, pose in flamingo_specs:
        s.add(el("ellipse", cx=fx, cy=fy + 28 * fs, rx=7.5 * fs, ry=2.2 * fs, fill="#f58a82", opacity=0.35))
        s.add(flamingo(fx, fy, fs, flip=flp, pose=pose))

    # American Crocodile cruising in the left-foreground shallows clear of the dead snag and shore
    s.add(caiman(104, 238, 0.92))

    # Sun-baked arid shoreline & crystalline white evaporite salt-flat crust
    shore = [(0, 262), (120, 255), (260, 261), (390, 254), (480, 251)]
    s.add(el("path", d=smooth([(x, y - 3.5) for x, y in shore]) + " L480,265 L0,265Z", fill="#f6f3ea"))
    s.add(el("path", d=smooth(shore) + " L480,300 L0,300Z", fill=s.linear("sand", [(0, "#dfcd9e"), (1, "#bfa472")])))

    # Dry scrub & columnar cacti (positioned cleanly with zero overlap with snags or rocks)
    s.add(thorn_bush(rng, 82, 274, 15), thorn_bush(rng, 292, 272, 15))
    for x, y, h in ((34, 278, 52), (416, 272, 54), (452, 278, 42)):
        s.add(cactus(x, y, h, "#547e4e", rib="#32502e"))

    # Sculpted multi-faceted fossil coral limestone outcrop & basking Rhinoceros Iguana
    s.add(el("ellipse", cx=364, cy=286, rx=42, ry=4.5, fill="#000000", opacity=0.22))
    s.add(el("path", d="M322,285 L330,275 L348,269 L374,268 L394,274 L404,285 Q364,288 322,285Z", fill="#b5a488"))
    s.add(el("path", d="M330,275 L348,269 L374,268 L366,276 L336,278Z", fill="#cfc0a6"))
    s.add(el("path", d="M366,276 L374,268 L394,274 L404,285 L362,286Z", fill="#786850"))
    s.add(el("path", d="M334,280 L362,278 L392,281", stroke="#574a38", stroke_width=0.9, fill="none", opacity=0.65))
    s.add(iguana(364, 267, 1.18))
    return s.render()


def build_pantanal(labels):
    s = vignette("pantanal", 103)
    rng = s.rng
    sky(s, [(0, "#d47542"), (0.38, "#eaa25b"), (0.72, "#f6ce8e"), (1, "#f9eacd")])
    sun(s, 330, 138, 22, glow="#ffcc74")
    s.add(cloud(rng, 110, 50, 105, col="#ffe4ba", shade="#d69666", op=0.78))
    s.add(cloud(rng, 390, 42, 85, col="#ffe4ba", shade="#d69666", op=0.72))

    # Distant mountain/gallery horizon
    s.add(el("path", d=smooth([(0, 168), (120, 162), (260, 166), (480, 160)]) + " L480,174 L0,174Z", fill="#9c7a5c", opacity=0.55))

    # Flooded Pantanal wetland mirror water with golden sunset shimmer bands (no circular spotlight blur behind Jabirus!)
    s.add(el("rect", x=0, y=168, width=480, height=132,
             fill=s.linear("water", [(0, "#e3b276"), (0.42, "#b0966e"), (0.78, "#6a8888"), (1, "#446870")])))
    for sy_idx in range(7):
        sy_ = 172 + sy_idx * 8.5
        sw_ = 46 - sy_idx * 4.2
        s.add(el("ellipse", cx=330 + rng.uniform(-4, 4), cy=sy_, rx=sw_, ry=1.6, fill="#ffefc2", opacity=0.42 - sy_idx * 0.04))
    s.add(water_lines(rng, 0, 480, 174, 296, 48, col="#fff3d6", op=0.52))

    # Sculpted flooded savanna cordilheira islands & marsh banks (organic shoreline contours instead of geometric ellipses)
    left_bank = [(-12, 174), (28, 164), (86, 162), (142, 165), (186, 173), (150, 178), (65, 179), (-12, 177)]
    right_bank = [(254, 170), (305, 161), (378, 159), (445, 162), (492, 169), (492, 175), (380, 176), (275, 174)]
    for b_pts in (left_bank, right_bank):
        s.add(el("path", d=smooth([(x, y + 2.5) for x, y in b_pts], closed=True), fill="#2e401b", opacity=0.48))
        s.add(el("path", d=smooth(b_pts, closed=True), fill="#587630"))
    s.add(tufts(rng, 6, 172, lambda x: 169, 36, 9, "#829c42"))
    s.add(tufts(rng, 268, 472, lambda x: 166, 40, 9, "#829c42"))

    # Gallery forest and Carandá palms (Copernicia alba)
    s.add(g(canopy_band(s, 276, 476, lambda x: 158, 10, 13, 22, ("#2f4a20", "#4b6b2f", "#789648"), k=5)))
    for x, h, lean in ((56, 74, -4), (98, 90, 5), (208, 64, -3)):
        s.add(palm(rng, x, 173, h, lean, 20, cols=("#3d5c28", "#628438"), coconuts=False, trunk_col="#544434", nfr=12))

    # Mid-ground cordilheira island where the capybara family rests (soft turf & sedges behind capybaras)
    c_pts = [(84, 219), (122, 209), (165, 207), (206, 211), (228, 220), (196, 226), (145, 227), (94, 224)]
    s.add(el("path", d=smooth(c_pts, closed=True), fill="#4a3b25"))
    c_top = [(88, 217), (126, 208), (165, 206), (203, 210), (222, 218), (192, 222), (145, 223), (96, 221)]
    s.add(el("path", d=smooth(c_top, closed=True), fill="#5c7a30"))
    s.add(tufts(rng, 94, 214, lambda x: 209, 26, 7.5, "#829e3e"))

    # Giant Victoria amazonica water lilies & realistic floating Eichhornia crassipes (water hyacinth) rosettes with multi-floret spikes
    for lx, ly, lr, fl in ((35, 272, 15, True), (72, 278, 18, False), (115, 282, 14, False),
                           (245, 274, 16, True), (288, 280, 20, False), (335, 276, 17, True),
                           (385, 282, 19, False), (435, 275, 15, True),
                           (160, 258, 11, False), (395, 254, 12, False)):
        s.add(water_lily(rng, lx, ly, lr, flower=fl))
    for hx_, hy_ in ((232, 222), (292, 218), (348, 222)):
        s.add(g([
            el("ellipse", cx=hx_, cy=hy_ + 1, rx=9.5, ry=2.4, fill="#243818", opacity=0.35),
            # Glossy bulbous petiole leaf rosette
            el("ellipse", cx=hx_ - 4.5, cy=hy_, rx=4.2, ry=2.2, fill="#457528", transform=f"rotate(-15 {hx_ - 4.5} {hy_})"),
            el("ellipse", cx=hx_ + 4.5, cy=hy_, rx=4.2, ry=2.2, fill="#457528", transform=f"rotate(15 {hx_ + 4.5} {hy_})"),
            el("ellipse", cx=hx_, cy=hy_ + 0.8, rx=4.8, ry=2.0, fill="#5c9136"),
            # Multi-floret lavender-blue flower spike
            el("path", d=f"M{n(hx_)},{n(hy_)} L{n(hx_)},{n(hy_ - 8)}", stroke="#457528", stroke_width=1.1),
            el("circle", cx=hx_ - 1.6, cy=hy_ - 4.2, r=1.8, fill="#9a68d4"),
            el("circle", cx=hx_ + 1.6, cy=hy_ - 4.8, r=1.8, fill="#a878e0"),
            el("circle", cx=hx_, cy=hy_ - 6.8, r=1.9, fill="#b88cf0"),
            el("circle", cx=hx_, cy=hy_ - 6.8, r=0.65, fill="#f5d442"),
        ]))

    # Fauna: Jabiru storks, Capybara family, Yacare Caiman, and flying wetland birds
    s.add(jabiru(328, 200, 1.22), jabiru(374, 205, 1.02, flip=True))
    s.add(capybara(154, 211, 1.24), capybara(114, 213, 0.94, flip=True), capybara(186, 213, 0.68))
    s.add(caiman(242, 250, 1.32))
    s.add(g([bird_v(178, 78, 7.5), bird_v(198, 72, 6.5), bird_v(215, 84, 6.5), bird_v(232, 76, 5.5)]))
    return s.render()


def build_cerrado(labels):
    s = vignette("cerrado", 104)
    rng = s.rng
    sky(s, [(0, "#4a8ec8"), (0.55, "#a2d0ec"), (1, "#f7ecd4")])
    sun(s, 72, 54, 16, glow="#ffeaad")
    s.add(cloud(rng, 358, 54, 118), cloud(rng, 118, 72, 78))

    # Distant stratified sandstone Chapada tableland mesa on the right horizon
    mesa_d = "M258,174 L286,130 L315,128 L412,127 L434,132 L456,174Z"
    s.add(el("path", d=mesa_d, fill="#b59472", opacity=0.88))
    s.add(el("path", d="M315,128 L412,127 L434,132 L456,174 L348,174Z", fill="#75523c", opacity=0.55))
    s.add(el("path", d="M286,130 L434,132 L430,139 L289,138Z", fill="#d2ab86", opacity=0.72))
    s.add(el("path", d="M278,150 L442,150 L440,154 L280,154Z", stroke="#543828", stroke_width=0.9, opacity=0.6))
    s.add(el("path", d="M262,174 L294,148 L352,162 L408,146 L452,174Z", fill="#5a3d2c", opacity=0.45))

    # Rolling Cerrado hills & plateau ridges with a natural valley depression around x=110..240
    h1, r_h1 = hill(s, [(0, 178), (95, 160), (185, 184), (315, 162), (480, 150)], 240, "#c2ad6a")
    s.add(h1)

    # Vereda palm-swamp oasis nestled in the left-center valley depression (x=95..245, clear of the right mesa & Ipê trees!)
    s.add(el("path", d="M92,188 Q165,180 245,188 Q210,196 145,195 Q108,194 92,188Z", fill="#4a7030", opacity=0.72))
    s.add(el("path", d="M102,189 Q168,183 236,189 L228,193 Q165,188 106,192Z", fill="#5eb8bd", opacity=0.82))
    s.add(g(canopy_band(s, 102, 242, lambda x: 185, 9, 7, 12, ("#2a4b20", "#426b30", "#689444"), lift=-2, k=5)))
    for px, py, ph, plean in ((115, 186, 36, -3), (142, 184, 42, 3), (192, 185, 38, -3), (222, 187, 33, 4)):
        s.add(palm(rng, px, py, ph, plean, 11, cols=("#285c2c", "#528e44"), trunk_col="#6a5640", coconuts=False, nfr=11))

    # Golden savanna grassland foreground with continuous tussock distribution (no bare horizontal bands!)
    ground = interp([(0, 226), (240, 216), (480, 224)])
    s.add(el("path", d=smooth([(0, 226), (240, 216), (480, 224)]) + " L480,300 L0,300Z",
             fill=s.linear("sav", [(0, "#cca856"), (1, "#9e7a32")])))
    s.add(tufts(rng, 0, 480, lambda x: ground(x) + rng.uniform(1, 34), 130, 11, "#dec26a"))
    s.add(tufts(rng, 0, 480, lambda x: ground(x) + rng.uniform(32, 72), 110, 14, "#886b28"))

    # Tortuous Cerrado trees, golden & pink Ipê trees (fully inside frame!), and cathedral termite mounds
    for x, h_t in ((46, 58), (158, 56)):
        s.add(gnarled_tree(rng, x, ground(x) + 4, h_t))
    s.add(ipe(rng, 286, ground(286) + 2, 78))
    s.add(ipe(rng, 412, ground(412) + 8, 64, bloom="#e86ca6", bloom2="#c44b84"))
    s.add(termite_mound(106, 264, 35), termite_mound(346, 254, 26))

    # Fauna: Maned Wolf (Chrysocyon brachyurus) on savanna turf & Hyacinth Macaw in flight
    s.add(maned_wolf(222, 268, 1.25))
    s.add(macaw(152, 104, 0.78, palette=("#2452b5", "#193b8a", "#f5c428")))
    return s.render()


def build_lencois(labels):
    """Realistic sweeping barchan quartz sand dunes with S-curved slip-faces and recessed inter-dunal rainwater lagoons."""
    s = vignette("lencois", 105)
    rng = s.rng
    sky(s, [(0, "#3680c6"), (0.55, "#82bee4"), (1, "#dcf0f8")], h=145)
    sun(s, 82, 50, 16, glow="#fff5d8")
    s.add(cloud(rng, 310, 54, 130), cloud(rng, 135, 66, 85, op=0.82))

    # Base quartz sand desert floor
    s.add(el("rect", x=0, y=132, width=480, height=168, fill="#f5f0e2"))
    lag_turq = s.linear("lag1", [(0, "#4ce0d8"), (0.45, "#1fb5c2"), (1, "#0f7894")])
    lag_em = s.linear("lag2", [(0, "#44d8b4"), (0.45, "#1aa898"), (1, "#0c6e72")])

    def barchan_dune(x0, x_crest, x1, y_base, h_crest, y_bot=300, lit="#fcfaf2", shade="#d8d0be"):
        ym = y_base - h_crest
        x_toe = x_crest + (x1 - x_crest) * 0.32
        lit_d = (
            f"M{n(x0)},{n(y_base)} C{n(x0 + (x_crest - x0) * 0.45)},{n(y_base - h_crest * 0.18)} "
            f"{n(x_crest - (x_crest - x0) * 0.24)},{n(ym)} {n(x_crest)},{n(ym)} "
            f"C{n(x_crest + (x1 - x_crest) * 0.16)},{n(ym + h_crest * 0.38)} "
            f"{n(x_crest + (x1 - x_crest) * 0.10)},{n(y_base - h_crest * 0.08)} "
            f"{n(x_toe)},{n(y_bot)} L{n(x0)},{n(y_bot)}Z"
        )
        sh_d = (
            f"M{n(x_crest)},{n(ym)} C{n(x_crest + (x1 - x_crest) * 0.42)},{n(ym + h_crest * 0.08)} "
            f"{n(x1 - (x1 - x_crest) * 0.18)},{n(y_base - h_crest * 0.06)} {n(x1)},{n(y_bot)} "
            f"L{n(x_toe)},{n(y_bot)} "
            f"C{n(x_crest + (x1 - x_crest) * 0.10)},{n(y_base - h_crest * 0.08)} "
            f"{n(x_crest + (x1 - x_crest) * 0.16)},{n(ym + h_crest * 0.38)} {n(x_crest)},{n(ym)}Z"
        )
        ridge_hi = (
            f"M{n(x_crest)},{n(ym)} C{n(x_crest + (x1 - x_crest) * 0.16)},{n(ym + h_crest * 0.38)} "
            f"{n(x_crest + (x1 - x_crest) * 0.10)},{n(y_base - h_crest * 0.08)} {n(x_toe)},{n(y_bot)}"
        )
        return g([
            el("path", d=lit_d, fill=lit),
            el("path", d=sh_d, fill=shade),
            el("path", d=ridge_hi, stroke="#ffffff", stroke_width=1.1, fill="none", opacity=0.85),
        ])

    def dune_lagoon(pts, fill_url, bar_cx=None, bar_cy=None, bar_rx=35):
        wet_margin = [(x, y - 1.6) for x, y in pts]
        out = [
            el("path", d=smooth(wet_margin, closed=True), fill="#d4c79e"),
            el("path", d=smooth(pts, closed=True), fill=fill_url),
        ]
        if bar_cx is not None:
            out.append(el("ellipse", cx=bar_cx, cy=bar_cy, rx=bar_rx, ry=3.8, fill="#80ede2", opacity=0.38))
        return g(out)

    # Layer 1: Far horizon dunes — each lagoon is drawn AFTER its left/rear dune and BEFORE the next overlapping dune!
    s.add(barchan_dune(-30, 52, 165, 160, 26, y_bot=220, lit="#f7f4ea", shade="#dfd7c4"))
    s.add(dune_lagoon([(62, 158), (112, 152), (172, 158), (155, 176), (72, 175)], lag_turq, 114, 162, 26))
    s.add(barchan_dune(115, 215, 335, 162, 30, y_bot=220, lit="#f7f4ea", shade="#dfd7c4"))
    s.add(dune_lagoon([(228, 159), (295, 153), (368, 160), (348, 178), (242, 176)], lag_em, 296, 163, 28))
    s.add(barchan_dune(275, 382, 510, 160, 28, y_bot=220, lit="#f7f4ea", shade="#dfd7c4"))

    # Layer 2: Mid-ground sweeping dunes — lagoons tucked into the inter-dunal troughs and overlapped by the next dune ridge!
    s.add(barchan_dune(-40, 78, 225, 206, 44, y_bot=275, lit="#faf7ef", shade="#dbd2be"))
    s.add(dune_lagoon([(92, 198), (168, 190), (258, 198), (272, 226), (172, 232), (104, 220)], lag_em, 176, 208, 42))
    s.add(water_lines(rng, 112, 232, 198, 218, 10, op=0.50))
    s.add(barchan_dune(178, 308, 455, 210, 48, y_bot=275, lit="#faf7ef", shade="#dbd2be"))
    s.add(dune_lagoon([(322, 202), (388, 195), (462, 204), (448, 228), (338, 230)], lag_turq, 388, 210, 36))
    s.add(water_lines(rng, 338, 432, 202, 220, 9, op=0.50))
    s.add(barchan_dune(378, 462, 540, 206, 36, y_bot=275, lit="#faf7ef", shade="#dbd2be"))

    # Layer 3: Foreground lagoon recessed between the mid-ground slip-faces and the near foreground barchan horns
    s.add(barchan_dune(-50, 108, 285, 268, 60, y_bot=300, lit="#fdfbf5", shade="#d4cbb6"))
    fg_lag = [(126, 260), (218, 250), (332, 252), (425, 264), (448, 286), (345, 296), (205, 296), (138, 282)]
    s.add(dune_lagoon(fg_lag, lag_turq, 278, 272, 85))
    s.add(water_lines(rng, 155, 405, 258, 288, 20, op=0.65))
    # Foreground right dune horn sweeping in front of the right side of the foreground lagoon
    s.add(barchan_dune(288, 412, 535, 278, 52, y_bot=300, lit="#fdfbf5", shade="#d4cbb6"))
    # Wind-sculpted sand ripples on foreground windward slopes
    ripples = " ".join(f"M{n(16 + i * 13)},{n(252 - i * 2.4)} q18,-3.2 36,0.8" for i in range(6))
    ripples += " " + " ".join(f"M{n(315 + i * 14)},{n(264 - i * 2.0)} q18,-3.2 36,0.8" for i in range(5))
    s.add(el("path", d=ripples, stroke="#dfd6c0", stroke_width=1.15, fill="none", opacity=0.8))

    s.add(g([bird_v(210, 88, 6.5), bird_v(232, 80, 5.5), bird_v(250, 90, 5.5)]))
    return s.render()


def build_caatinga(labels):
    s = vignette("caatinga", 106)
    rng = s.rng
    sky(s, [(0, "#7aaad2"), (0.55, "#d2cfb8"), (1, "#f7dec0")])
    sun(s, 400, 64, 20, glow="#ffdfa0")

    # Distant Sertão granite inselberg bornhardt dome with clipped 3D exfoliation facets (no stroke sticking into sky!)
    insel_d = "M32,176 C42,148 70,130 104,128 C134,130 154,150 168,176Z"
    insel_clip = s.clip("insel-clip", insel_d)
    s.add(el("path", d=insel_d, fill="#bca286"))
    s.add(g([
        el("path", d="M98,126 C118,142 124,158 118,176 L168,176 L168,126Z", fill="#755e4c", opacity=0.58),
        el("path", d="M32,176 C48,148 74,132 104,128 C82,138 64,156 54,176Z", fill="#d9c2a6", opacity=0.55),
        el("path", d="M48,158 Q102,138 152,160 M56,166 Q104,148 158,168", stroke="#5a4535", stroke_width=1.0, fill="none", opacity=0.48),
        el("path", d="M36,176 L74,162 L114,168 L162,176Z", fill="#5a4232", opacity=0.38),
    ], clip_path=insel_clip))

    h1, _ = hill(s, [(0, 170), (120, 148), (260, 174), (360, 138), (480, 164)], 232, "#c4986e")
    s.add(h1)

    # Baked ochre-terracotta soil with granite lajedo outcrops and dry riverbed desiccation cracks
    ground = interp([(0, 232), (240, 220), (480, 228)])
    s.add(el("path", d=smooth([(0, 232), (240, 220), (480, 228)]) + " L480,300 L0,300Z",
             fill=s.linear("caat", [(0, "#c28e5c"), (1, "#8f5e36")])))
    cracks = (
        "M135,266 l18,4 l12,-3 l15,5 M153,270 l6,9 l-4,7 "
        "M205,280 l22,3 l14,-4 l12,4 M325,274 l19,5 l15,-2 l10,4"
    )
    s.add(el("path", d=cracks, stroke="#5e3b1e", stroke_width=0.9, fill="none", opacity=0.55))

    # Gnarled silvery-grey Caatinga trees (Umbuzeiro / Catingueira)
    for tx, ty, th in ((195, 232, 54), (368, 228, 48)):
        s.add(gnarled_tree(rng, tx, ty, th, leaf=("#828260", "#9ea078", "#bcc096"), trunk_col="#6e6254"))

    # Deliberately placed dry thorn bushes (clear of cacti and Opuntia pads!)
    for bx, by, bs in (
        (24, 246, 16), (54, 238, 14), (128, 236, 17), (168, 248, 18),
        (238, 238, 16), (268, 250, 15), (332, 236, 16), (392, 244, 15), (456, 242, 17),
    ):
        s.add(thorn_bush(rng, bx, by, bs))

    # Prickly-pear (Opuntia palmadora) & Turk's-cap cactus (Melocactus zehntneri) on rocky soil
    for ox, oy in ((142, 260), (338, 264)):
        s.add(g([
            el("ellipse", cx=ox, cy=oy + 1, rx=9, ry=2, fill="#000000", opacity=0.2),
            el("ellipse", cx=ox, cy=oy - 5, rx=5.5, ry=7, fill="#4e7a48"),
            el("ellipse", cx=ox - 6, cy=oy - 12, rx=4.5, ry=6, fill="#5c8c54", transform=f"rotate(-24 {ox - 6} {oy - 12})"),
            el("ellipse", cx=ox + 6, cy=oy - 11, rx=4.5, ry=5.5, fill="#5c8c54", transform=f"rotate(22 {ox + 6} {oy - 11})"),
            el("circle", cx=ox - 8, cy=oy - 17, r=2.0, fill="#e85d24"),
        ]))
    # Melocactus (coroa-de-frade) with crimson cephalium cap
    s.add(g([
        el("ellipse", cx=222, cy=278, rx=8, ry=6.5, fill="#4d7a49"),
        el("path", d="M218,272 L217,283 M222,271 L222,284 M226,272 L227,283", stroke="#2f5230", stroke_width=0.8, fill="none"),
        el("ellipse", cx=222, cy=271.5, rx=4.2, ry=2.6, fill="#c92e2e"),
        el("circle", cx=222, cy=269.5, r=1.1, fill="#f78ca2"),
    ]))

    # Iconic Mandacaru columnar cacti (with 3D fluted ribs and cupped nocturnal white blossoms)
    for x, h in ((88, 112), (298, 132), (422, 84)):
        s.add(cactus(x, ground(x) + 32, h, "#4c7748", rib="#2c4e2a"))

    # Weathered exfoliating granite boulders & angular desert stone fragments (no random oval polka dots!)
    for rx_, ry_, rr in ((42, 282, 16), (252, 276, 15), (362, 286, 18), (122, 288, 11), (448, 288, 12)):
        s.add(el("ellipse", cx=rx_ + 1, cy=ry_ + 1, rx=rr * 1.1, ry=rr * 0.2, fill="#000000", opacity=0.22))
        s.add(el("path", d=f"M{rx_ - rr},{ry_} L{rx_ - rr * 0.65},{ry_ - rr * 0.72} L{rx_ + rr * 0.18},{ry_ - rr * 0.68} L{rx_ + rr},{ry_}Z",
                 fill="#967b60"))
        s.add(el("path", d=f"M{rx_ + rr * 0.18},{ry_ - rr * 0.68} L{rx_ + rr},{ry_} L{rx_ - rr * 0.05},{ry_}Z",
                 fill="#5e4936"))

    # Fauna: Pair of Indigo / Lear's Macaws (Anodorhynchus leari) in flight
    s.add(macaw(198, 98, 0.82, palette=("#2255a8", "#173c7d", "#f5c428")))
    s.add(macaw(145, 114, 0.62, flip=True, palette=("#2255a8", "#173c7d", "#f5c428")))
    return s.render()


def build_bluehole(labels):
    s = vignette("bluehole", 107)
    rng = s.rng
    sky(s, [(0, "#3e8ed0"), (0.6, "#90c7e6"), (1, "#e6f4f8")], h=96)
    sun(s, 400, 44, 14, glow="#fff4d4")
    s.add(cloud(rng, 138, 40, 95), cloud(rng, 308, 48, 76))

    # Distant coral keys, coastal vegetation berm, and evenly spaced coconut palms on horizon
    s.add(el("path", d="M-10,92 Q70,85 160,90 Q280,83 410,90 L490,92 L490,96 L-10,96Z", fill="#e6dab4"))
    s.add(el("path", d="M10,91 Q70,84 140,90 Z M330,90 Q395,83 465,91 Z", fill="#4a7d3a", opacity=0.75))
    for x, h, lean in ((26, 25, -4), (56, 29, 3), (86, 24, -2), (116, 26, 5),
                       (348, 26, -5), (380, 31, 3), (412, 25, -2), (444, 27, 5)):
        s.add(palm(rng, x, 92, h, lean, 10, cols=("#285c30", "#488440"), nfr=11, coconuts=False, trunk_col="#826b4e"))

    # Turquoise shallow coral lagoon surrounding the sinkhole (filling bottom corners completely)
    s.add(el("rect", x=0, y=94, width=480, height=206,
             fill=s.linear("water", [(0, "#45d0d8"), (0.38, "#20a8ba"), (1, "#14829a")])))
    s.add(water_lines(rng, 0, 480, 96, 122, 28, op=0.48))
    s.add(el("path", d="M0,114 Q68,114 106,142 Q118,188 92,248 Q64,284 110,300 L0,300Z", fill="#78d0ca", opacity=0.78))
    s.add(el("path", d="M480,114 Q412,114 374,142 Q362,188 388,248 Q416,284 370,300 L480,300Z", fill="#78d0ca", opacity=0.78))

    # The Great Blue Hole circular karst sinkhole with stepped limestone ledges, overhanging ceiling, & deep abyss
    cx, cy = 240, 196
    chasm_grad = s.radial("chasm", [
        (0, "#010610", 1),
        (0.42, "#051530", 1),
        (0.68, "#0b2e5e", 1),
        (0.86, "#145c8c", 0.96),
        (0.95, "#249cb5", 0.85),
        (1, "#38c6d4", 0.15),
    ])
    s.add(el("ellipse", cx=cx, cy=cy, rx=158, ry=90, fill=chasm_grad))
    s.add(el("ellipse", cx=cx, cy=cy + 2, rx=138, ry=76, fill="#041126", opacity=0.88))
    s.add(el("ellipse", cx=cx, cy=cy + 5, rx=104, ry=56, fill="#010714", opacity=0.96))

    # Submerged karst cliff overhang along upper inner wall with drowned stalactite columns hanging down from the ledge
    overhang_d = (
        f"M{cx - 136},{cy - 6} A138,76 0 0 1 {cx + 136},{cy - 6} "
        f"A132,64 0 0 0 {cx - 136},{cy - 6}Z"
    )
    s.add(el("path", d=overhang_d, fill="#0c2b4f", opacity=0.85))
    stal_paths = []
    for i in range(15):
        sx_ = cx - 112 + i * 16
        arch_y = cy - 66 + ((sx_ - cx) / 118) ** 2 * 36
        sh_len = rng.uniform(9, 20)
        sw_ = rng.uniform(1.6, 2.8)
        stal_paths.append(f"M{n(sx_ - sw_)},{n(arch_y)} L{n(sx_)},{n(arch_y + sh_len)} L{n(sx_ + sw_)},{n(arch_y)}Z")
    s.add(el("path", d=" ".join(stal_paths), fill="#0a2444", opacity=0.82))

    # Organic, multi-lobed shallow carbonate sand & coral reef rim dropping off into the deep abyss
    rim_outer = [(cx + 162 * math.cos(a), cy + 94 * math.sin(a) + 3 * math.sin(5 * a)) for a in [i * math.pi / 16 for i in range(32)]]
    rim_inner = [(cx + 148 * math.cos(a), cy + 84 * math.sin(a) + 2 * math.sin(5 * a)) for a in [i * math.pi / 16 for i in range(32)]]
    s.add(el("path", d=smooth(rim_outer, closed=True), fill="none", stroke="#a2e8df", stroke_width=6.0, opacity=0.72))
    s.add(el("path", d=smooth(rim_inner, closed=True), fill="none", stroke="#dcf8f4", stroke_width=2.4, opacity=0.82))

    # Diagonal sunbeams piercing into the abyss (softly fading at top via upgraded light_rays)
    s.add(light_rays(s, 135, 345, 98, 286, 8, op=0.20))

    # Well-spaced coral gardens along the sinkhole rim (zero collisions between sponges, fans, and corals!)
    s.add(sea_fan(rng, 68, 194, 25, "#8c48a8"), sea_fan(rng, 412, 174, 24, "#c94886"), sea_fan(rng, 376, 244, 21, "#8c48a8"))
    for x, y, Lc, c in ((82, 150, 17, "#e26d52"), (108, 182, 15, "#cfa240"), (368, 152, 18, "#d95b82"),
                        (396, 188, 14, "#e8b24c"), (116, 246, 16, "#f08452"), (348, 252, 15, "#e26d52"),
                        (172, 272, 13, "#d95b82"), (298, 270, 14, "#e8b24c")):
        s.add(branch_coral(rng, x, y, Lc, 2, c, 2.2))
    for bx, by, br, bc in ((96, 212, 13, "#c29238"), (146, 260, 11, "#cfa240"),
                           (384, 216, 14, "#cfa240"), (324, 262, 12, "#b8862d")):
        s.add(brain_coral(rng, bx, by, br, bc))
    s.add(tube_sponge(126, 228, 15, "#b552bd"), tube_sponge(356, 230, 16, "#e68235"), tube_sponge(92, 166, 13, "#e68235"))

    # Marine Fauna: Reef Sharks, Manta Ray, Sea Turtle, Schooling Fish
    s.add(shark(232, 194, 0.98))
    s.add(shark(282, 232, 0.68, flip=True))
    s.add(manta(195, 156, 0.52))
    s.add(turtle(142, 144, 0.68))
    s.add(school(rng, 332, 144, 11, 34, 3.8, "#dff6f5", stripe="#1e948b"))

    # Electric Eco-Research Catamaran on the surface with reflection
    s.add(g([
        el("ellipse", cx=212, cy=115, rx=22, ry=2.5, fill="#0c4c66", opacity=0.35),
        el("path", d="M192,107 L232,107 L227,113.5 L195,113.5Z", fill="#ffffff"),
        el("path", d="M194,110.5 L229,110.5", stroke="#1a528f", stroke_width=1.2),
        el("path", d="M200,107 L203,102 L221,102 L224,107Z", fill="#1a528f"),
        el("rect", x=204, y=103, width=15, height=2.5, rx=0.8, fill="#8cd2f0"),
        el("line", x1=212, y1=102, x2=212, y2=96, stroke="#444444", stroke_width=0.9),
    ]))
    return s.render()


def build_tepui(labels):
    """Majestic flat-topped sandstone Tepui (Monte Roraima style) with sheer fluted cliffs, twin waterfalls, cloud sea, and Heliamphora."""
    s = vignette("tepui", 108)
    rng = s.rng
    sky(s, [(0, "#d9885b"), (0.36, "#f2bfa0"), (0.72, "#cde2ee"), (1, "#a2cae0")])
    sun(s, 86, 56, 16, glow="#ffdfb0")
    s.add(cloud(rng, 390, 46, 90, col="#fff2e2", shade="#d4b29c", op=0.8))

    # Distant sister tepui silhouette on the left horizon shrouded in mist
    sis_d = "M-20,130 L18,127 L48,128 L78,126 L86,132 L96,172 L106,242 L-20,242Z"
    s.add(el("path", d=sis_d, fill="#a48379", opacity=0.68))
    sis_clip = s.clip("sis_tepui", sis_d)
    s.add(g([
        el("path", d="M-20,126 L44,126 L38,242 L-20,242Z", fill="#ba988c", opacity=0.45),
        el("path", d="M56,126 L108,126 L108,242 L62,242Z", fill="#6e544e", opacity=0.48),
        el("path", d="M-20,148 L96,148 L96,155 L-20,155Z", fill="#c29e90", opacity=0.42),
        el("path", d="M-20,174 L100,174 L100,181 L-20,181Z", fill="#7d6058", opacity=0.40),
        el("path", d="M12,128 L10,220 M38,128 L36,220 M64,128 L66,220", stroke="#5c443e", stroke_width=1.4, fill="none", opacity=0.45),
    ], clip_path=sis_clip))
    s.add(mist(s, 42, 214, 96, 18, op=0.68))

    # Main Tepui Tabletop Fortress with craggy sandstone battlements
    tabletop = [
        (112, 88), (126, 83), (144, 85), (165, 81), (185, 86), (204, 80),
        (232, 81), (258, 85), (284, 79), (316, 81), (345, 85), (372, 80),
        (398, 82), (418, 86),
    ]
    cliff_l = [(112, 88), (109, 118), (114, 152), (104, 192), (92, 238)]
    cliff_r = [(418, 86), (422, 122), (416, 158), (424, 198), (434, 238)]
    tepui_pts = tabletop + cliff_r[1:] + [(456, 262), (72, 262)] + list(reversed(cliff_l))
    tepui_d = P(tepui_pts)
    s.add(el("path", d=tepui_d, fill="#6e5046"))
    cid = s.clip("tepui_body", tepui_d)

    # Multi-faceted 3D Precambrian Roraima quartzite buttresses, irregular chimney chasms, and broken horizontal ledges (no plaid grid!)
    strata = [
        # Major 3D projecting rock buttress pillars with sunlit left faces and deep shadowed right flanks
        el("path", d="M110,80 L158,80 L152,250 L92,250Z", fill="#a67563", opacity=0.38),
        el("path", d="M158,80 L186,80 L182,250 L152,250Z", fill="#38241f", opacity=0.48),
        el("path", d="M186,80 L244,80 L238,250 L182,250Z", fill="#966858", opacity=0.32),
        el("path", d="M244,80 L282,80 L278,250 L238,250Z", fill="#2e1d19", opacity=0.52),
        el("path", d="M282,80 L344,80 L338,250 L278,250Z", fill="#875c4e", opacity=0.28),
        el("path", d="M344,80 L456,80 L456,262 L338,262Z", fill="#291a16", opacity=0.56),
    ]
    # Broken, stepped horizontal sandstone bedding ledges with dark overhang shadows
    for yb, col, sh_op in (
        (104, "#9c7262", 0.45), (132, "#875f50", 0.50),
        (164, "#785244", 0.48), (194, "#634338", 0.45),
    ):
        pts_b = [(x, yb + 3.0 * math.sin(x * 0.055 + yb) + rng.uniform(-2, 2)) for x in range(70, 460, 26)]
        strata.append(el("path", d=smooth(pts_b) + f" L460,{yb + 9} L70,{yb + 9}Z", fill=col, opacity=0.55))
        strata.append(el("path", d=smooth([(x, y + 8) for x, y in pts_b]), stroke="#241512", stroke_width=1.6, fill="none", opacity=sh_op))

    # Irregular vertical quartzite chimneys and fracture gorges (varied spacing & widths, not 8px stripes!)
    chimney_xs = (128, 146, 162, 185, 206, 224, 246, 268, 292, 314, 345, 368, 392, 408)
    for idx_c, cx_ in enumerate(chimney_xs):
        top_y = rng.uniform(81, 90)
        bot_y = rng.uniform(210, 245)
        cw = rng.uniform(1.4, 3.6) if idx_c not in (3, 10) else 5.2
        mx = cx_ + rng.uniform(-3, 3)
        strata.append(el("path", d=f"M{n(cx_ - cw * 0.5)},{n(top_y)} Q{n(mx)},{n((top_y + bot_y) * 0.5)} {n(cx_ - cw * 0.2)},{n(bot_y)} "
                                   f"L{n(cx_ + cw * 0.5)},{n(bot_y)} Q{n(mx + cw * 0.6)},{n((top_y + bot_y) * 0.5)} {n(cx_ + cw * 0.5)},{n(top_y)}Z",
                         fill="#1f120f", opacity=0.68))
        strata.append(el("path", d=f"M{n(cx_ - cw * 0.6)},{n(top_y + 4)} Q{n(mx - 1)},{n((top_y + bot_y) * 0.5)} {n(cx_ - cw * 0.3)},{n(bot_y - 8)}",
                         stroke="#b88c78", stroke_width=0.85, fill="none", opacity=0.42))

    # Talus slope ramp at base of sheer wall
    strata.append(el("path", d="M72,262 L115,192 L180,220 L265,198 L355,218 L418,190 L456,262Z", fill="#3d2f2a", opacity=0.72))
    s.add(g(strata, clip_path=cid))

    # Organic Bonnetia roraimae shrub mats along the summit plateau rim (replacing flat ellipses)
    for vx, vy, vr in ((132, 85, 10), (164, 83, 9), (218, 82, 12), (252, 85, 9),
                       (296, 81, 12), (326, 84, 9), (378, 82, 11), (404, 85, 8)):
        s.add(crown(rng, vx, vy, vr, ("#1e3d1a", "#325e2a", "#588c44"), k=4, flat=0.36, detail=False))

    # Twin horsetail waterfalls (Angel Falls / Kukenán style) plunging from tabletop into mist
    s.add(waterfall(s, 185, 86, 242, 9))
    s.add(waterfall(s, 345, 85, 244, 10))

    # Continuous dense cloud forest foundation & multi-layered canopy at base of Tepui
    s.add(el("rect", x=0, y=242, width=480, height=58, fill="#152b19"))
    s.add(g(canopy_band(s, -20, 500, lambda x: 238 + 5 * math.sin(x / 28), 28, 14, 24, ("#1c4222", "#2e6330", "#528e42"), k=5)))
    s.add(mist(s, 175, 232, 130, 16, op=0.72))
    s.add(mist(s, 355, 230, 135, 16, op=0.70))
    s.add(mist(s, 250, 242, 230, 16, op=0.68))
    s.add(g(canopy_band(s, 135, 500, lambda x: 254 + 4 * math.sin(x / 22 + 1), 22, 15, 25, ("#14361a", "#255726", "#4a843a"), k=5)))

    # Foreground sandstone boulder terrace with endemic Heliamphora pitcher plants & Oreophrynella pebble toad
    fg_rock = [(0, 238), (95, 240), (144, 248), (164, 278), (138, 300), (0, 300)]
    s.add(el("path", d=smooth(fg_rock) + "Z", fill="#453832"))
    s.add(el("path", d="M0,238 Q70,239 142,248 L128,256 Q60,248 0,248Z", fill="#69554c", opacity=0.65))
    s.add(el("ellipse", cx=55, cy=268, rx=42, ry=7, fill="#335428", opacity=0.65))
    s.add(el("ellipse", cx=105, cy=278, rx=30, ry=5.5, fill="#335428", opacity=0.6))
    s.add(bromeliad(rng, 18, 252, 11))
    s.add(pitcher_plant(42, 268, 1.12, flower=True))
    s.add(pitcher_plant(78, 275, 0.90, flower=False))
    s.add(pitcher_plant(110, 280, 1.02, flower=True))

    # Detailed endemic Roraima Black Pebble Toad (Oreophrynella quelchii) on mossy rock
    fx, fy = 138, 264
    s.add(g([
        el("ellipse", cx=fx, cy=fy + 3.2, rx=7.5, ry=2.0, fill="#000000", opacity=0.35),
        el("path", d=f"M{fx - 4},{fy + 1} L{fx - 8},{fy + 3} L{fx - 5},{fy + 3.5} M{fx + 4},{fy + 1} L{fx + 7},{fy + 3.5}",
           stroke="#1e1c1a", stroke_width=1.6, fill="none", stroke_linecap="round"),
        el("path", d=f"M{fx - 6},{fy + 1} C{fx - 6},{fy - 4} {fx + 2},{fy - 5} {fx + 6},{fy - 1} C{fx + 7},{fy + 2} {fx - 5},{fy + 3} {fx - 6},{fy + 1}Z",
           fill="#1c1b1a"),
        el("circle", cx=fx - 2, cy=fy - 1.5, r=0.8, fill="#383532"),
        el("circle", cx=fx + 1, cy=fy - 2.0, r=0.7, fill="#383532"),
        el("circle", cx=fx - 0.5, cy=fy, r=0.7, fill="#383532"),
        el("circle", cx=fx + 3.8, cy=fy - 2.2, r=1.3, fill="#e8b828"),
        el("circle", cx=fx + 4.0, cy=fy - 2.2, r=0.6, fill="#111111"),
    ]))
    s.add(condor(290, 48, 0.62))
    return s.render()


def build_cataracts(labels):
    """Multi-tiered roaring basalt cataracts (Iguazú / Rio Esmeralda style) with 3D columnar basalt cliffs, spray cauldron, rainbow, and toucan."""
    s = vignette("cataracts", 109)
    rng = s.rng
    sky(s, [(0, "#468cc8"), (0.55, "#94c6e4"), (1, "#dcf0f6")], h=118)
    s.add(cloud(rng, 108, 44, 88), cloud(rng, 362, 48, 98))

    # Distant subtropical rainforest canopy along the upper river rim
    s.add(g(canopy_band(s, -10, 490, lambda x: 88 + 3 * math.sin(x / 25), 24, 9, 15, ("#1c4624", "#2e6832", "#569444"), k=5)))

    # Upper emerald river approaching the precipice
    s.add(el("rect", x=0, y=88, width=480, height=26, fill=s.linear("upriv", [(0, "#2f6359"), (1, "#488c7e")])))
    s.add(water_lines(rng, 0, 480, 91, 110, 26, col="#e0f4f0", op=0.55))

    # Columnar flood-basalt canyon wall with varied 3D polygonal basalt columns and stepped rock ledges (no uniform barcode bars!)
    canyon_lip = [(0, 112), (90, 115), (180, 110), (270, 114), (370, 110), (480, 114)]
    s.add(el("path", d=smooth(canyon_lip) + " L480,242 L0,242Z", fill="#26201d"))
    col_sh, col_mid, col_lit, col_caps = [], [], [], []
    cx_b = 0
    while cx_b < 480:
        w1 = rng.uniform(5.5, 9.5)
        w2 = rng.uniform(5.0, 8.5)
        y_top_b = 112 + rng.uniform(-1.5, 2.5)
        y_step = rng.uniform(158, 182) if rng.random() < 0.45 else 238
        col_sh.append(f"M{n(cx_b)},{n(y_top_b)} L{n(cx_b + w1)},{n(y_top_b)} L{n(cx_b + w1)},{n(y_step)} L{n(cx_b)},{n(y_step)}Z")
        col_lit.append(f"M{n(cx_b + w1)},{n(y_top_b)} L{n(cx_b + w1 + w2)},{n(y_top_b)} L{n(cx_b + w1 + w2)},238 L{n(cx_b + w1)},238Z")
        if y_step < 230:
            col_mid.append(f"M{n(cx_b - 1)},{n(y_step)} L{n(cx_b + w1 + 2)},{n(y_step)} L{n(cx_b + w1 + 2)},238 L{n(cx_b - 1)},238Z")
            col_caps.append(f"M{n(cx_b - 1)},{n(y_step)} L{n(cx_b + w1 * 0.5)},{n(y_step - 3)} L{n(cx_b + w1 + 2)},{n(y_step)}Z")
        cx_b += w1 + w2 + rng.uniform(0.5, 2.0)
    s.add(el("path", d=" ".join(col_sh), fill="#1b1614", opacity=0.82))
    s.add(el("path", d=" ".join(col_lit), fill="#3d332d", opacity=0.65))
    s.add(el("path", d=" ".join(col_mid), fill="#2e2622", opacity=0.78))
    s.add(el("path", d=" ".join(col_caps), fill="#52453d", opacity=0.75))

    # Irregular basalt cliff ledges with clinging subtropical mosses and ferns
    for rx_, ry_, rw_ in ((34, 152, 32), (82, 164, 28), (168, 168, 34), (242, 172, 30), (348, 166, 32), (418, 170, 26)):
        s.add(el("path", d=f"M{rx_ - rw_ * 0.5},{ry_} L{rx_ - rw_ * 0.32},{ry_ - 4} L{rx_ + rw_ * 0.35},{ry_ - 3} L{rx_ + rw_ * 0.5},{ry_} L{rx_ + rw_ * 0.28},{ry_ + 5} L{rx_ - rw_ * 0.28},{ry_ + 4}Z",
                 fill="#4a3f3a"))
        s.add(crown(rng, rx_, ry_ - 3, rw_ * 0.30, ("#1d4422", "#346e34", "#5c9c46"), k=4, flat=0.52, detail=False))

    # Left basalt cliff face kept dark & fern-draped behind the perched Toucan (x=0..98), while 5 cataracts thunder across x=126..455!
    s.add(crown(rng, 28, 114, 16, ("#183d1e", "#2b612e", "#528e42"), k=5, flat=0.55, detail=False))
    s.add(crown(rng, 68, 114, 15, ("#183d1e", "#2b612e", "#528e42"), k=5, flat=0.55, detail=False))
    s.add(waterfall(s, 126, 112, 236, 34))
    s.add(waterfall(s, 194, 111, 238, 40))
    s.add(waterfall(s, 282, 108, 242, 64))
    s.add(waterfall(s, 378, 111, 236, 40))
    s.add(waterfall(s, 446, 113, 234, 28))

    # Lush emerald rock islands along the canyon brink dividing the falls
    for x, w in ((152, 20), (226, 24), (326, 26), (410, 18)):
        s.add(el("path", d=f"M{x},118 L{x + 3},106 L{x + w - 3},106 L{x + w},118Z", fill="#3b322c"))
        s.add(crown(rng, x + w / 2, 106, 11, ("#1b4622", "#326e32", "#609e48"), k=5, detail=False))

    # Boiling mist cauldron at base of gorge
    s.add(mist(s, 275, 230, 215, 25, op=0.86))
    s.add(mist(s, 165, 226, 135, 20, op=0.76))
    s.add(mist(s, 385, 226, 145, 20, op=0.76))

    # Luminous optical double rainbow arching through the cataract spray
    rainbow_colors = ["#ff5e5e", "#ffa502", "#f6e58d", "#2ed573", "#1e90ff", "#5352ed"]
    for i, col in enumerate(rainbow_colors):
        r = 136 - i * 2.8
        s.add(el("path", d=f"M{272 - r},240 A{r},{r * 0.84} 0 0 1 {272 + r},240",
                 stroke=col, stroke_width=3.2, fill="none", opacity=0.36, filter=s.url("soft")))

    # Lower emerald plunge pool river with turbulent foam lines
    s.add(el("rect", x=0, y=236, width=480, height=64,
             fill=s.linear("pool", [(0, "#429688"), (0.45, "#368073"), (1, "#1e5248")])))
    s.add(water_lines(rng, 0, 480, 240, 296, 42, col="#dcf6f0", op=0.58))

    # Foreground basalt cliff promontory with overarching mossy tree limb, ferns, Heliconia, and perched Toucan (clear of waterfalls!)
    fg_bank = [(0, 206), (56, 222), (88, 258), (64, 300), (0, 300)]
    s.add(el("path", d=smooth(fg_bank) + "Z", fill="#26201d"))
    s.add(el("path", d="M0,206 C22,210 44,216 56,222 L42,232 C25,222 10,216 0,214Z", fill="#453a34", opacity=0.85))
    s.add(el("path", d="M0,192 Q42,190 88,198 Q100,200 108,195", stroke="#4d3928", stroke_width=5.0, fill="none", stroke_linecap="round"))
    s.add(el("path", d="M0,190 Q42,188 88,196", stroke="#759c44", stroke_width=2.0, fill="none", stroke_linecap="round"))
    s.add(fern(rng, 22, 232, 38, "#387c34"))
    s.add(fern(rng, 52, 250, 44, "#4da048"))
    s.add(heliconia(18, 274, 44))
    s.add(bromeliad(rng, 78, 195, 10))
    # Toco Toucan perched against the dark basalt cliff on the left with zero waterfall collision
    s.add(toucan(46, 182, 0.98))

    # White-collared swifts (Streptoprocne zonaris) darting across the falls
    for bx, by, bs in ((208, 164, 5.8), (244, 152, 4.8), (282, 168, 5.8), (312, 158, 4.5)):
        s.add(bird_v(bx, by, bs, "#ffffff"))
    return s.render()


def cuban_trogon(x, y, s, flip=False):
    """Endemic Cuban Trogon / Tocororo (Priotelus temnurus) perched with scalloped tail, metallic green back, white breast, crimson belly, and blue crown."""
    sx = -1 if flip else 1
    return g([
        # Distinctive scalloped/toothed long tail feathers (dark blue-green with white-edged lateral rectrices)
        el("path", d="M-2,6 L-9,33 L-6,31 L-4,34 L-1,31 L2,34 L4,8Z", fill="#193b52"),
        el("path", d="M-5.5,14 L-8.5,31 L-6,30 L-3.5,14Z M1.5,14 L2,31 L0,30 L-0.5,14Z", fill="#eef4f8", opacity=0.88),
        # Crimson-scarlet lower belly and undertail coverts
        el("path", d="M-2,3 C0,1 6,2 7.5,8 C6.5,14 2.5,16 -1,13 C-3,10 -3,6 -2,3Z", fill="#d92626"),
        # Pure white throat and upper breast collar
        el("path", d="M0,-4 C4,-5 8,-2 7.5,4 C4,5.5 -0.5,4.5 -1.5,1 C-2,-2 -1,-3.5 0,-4Z", fill="#f7f9fc"),
        # Iridescent bronze-emerald back & folded wing with fine white tertial vermiculations
        el("path", d="M-4,-3 C-5,2 -4,10 0,13 C2,8 2.5,1 0,-4Z", fill="#1d7848"),
        el("path", d="M-3.5,-1 C-1,0 1,4 0,10 C-2.5,9 -4,4 -3.5,-1Z", fill="#2da060"),
        el("path", d="M-2.5,2 L0,3 M-2.8,4.5 L0,5.5 M-2.5,7 L-0.2,8", stroke="#e8f2ee", stroke_width=0.75, opacity=0.8),
        # Violet-blue crown and nape, dark mask, crimson iris with white orbital ring, and stout coral-red bill
        el("path", d="M-3.5,-4 C-4,-9 1,-11.5 5,-9.5 C6.5,-8 6,-4.5 3.5,-3.5 C0.5,-3 -2.5,-3 -3.5,-4Z", fill="#1f448c"),
        el("path", d="M0.5,-7.5 C3.5,-8 5.8,-6.5 5.5,-4 C3.5,-3.5 1,-4 0.5,-7.5Z", fill="#161c24"),
        el("circle", cx=3.2, cy=-6.0, r=1.35, fill="#ffffff"),
        el("circle", cx=3.2, cy=-6.0, r=0.85, fill="#b81d1d"),
        el("path", d="M5.2,-7.2 C8.5,-7.0 9.8,-5.5 8.8,-4.2 C7.2,-4.0 5.8,-4.2 5.2,-4.8Z", fill="#e03c32"),
    ], transform=f"translate({n(x)} {n(y)}) scale({n(sx * s)} {n(s)})")


def build_elnicho(labels):
    """El Nicho Travertine Cascades (Topes de Collantes, Escambray Mountains, Cuba): stepped turquoise travertine pools, lacy veil cascades, royal palms, tree ferns, and Cuban trogon."""
    s = vignette("elnicho", 110)
    rng = s.rng
    sky(s, [(0, "#4f97c9"), (0.5, "#9ed2e6"), (1, "#e6f5ec")], h=110)
    sun(s, 395, 42, 16, glow="#fff2c2")

    # Misty Sierra del Escambray mountain ridges in the background
    m_far, _ = hill(s, [(0, 86), (95, 54), (205, 74), (320, 48), (425, 68), (480, 58)], 125, "#6b998b")
    s.add(m_far)
    s.add(mist(s, 240, 82, 210, 14, op=0.55))

    # Lush Escambray cloud-forest canopy & Cuban royal palms along the upper canyon rim
    s.add(g(canopy_band(s, -15, 495, lambda x: 96 + 4 * math.sin(x / 28), 24, 11, 18, ("#174223", "#2b6933", "#589c49"), k=5)))
    for px, py, ph, plean in ((88, 96, 52, -5), (124, 98, 44, 4), (358, 94, 54, 6), (402, 96, 46, -4)):
        s.add(palm(rng, px, py, ph, plean, 17, cols=("#1f5727", "#488e3e"), trunk_col="#cfc9bc", royal=True, coconuts=False, nfr=12))

    # Upper emerald stream feeding the travertine ledges
    s.add(el("rect", x=0, y=96, width=480, height=22, fill=s.linear("uppool", [(0, "#1d6b63"), (1, "#359c8e")])))
    s.add(water_lines(rng, 10, 470, 99, 114, 22, col="#dcf7f2", op=0.55))

    # Stepped limestone & calcified travertine canyon walls
    canyon_top = [(0, 102), (35, 96), (72, 112), (175, 110), (245, 113), (315, 110), (408, 112), (445, 98), (480, 104)]
    s.add(el("path", d=smooth(canyon_top) + " L480,235 L0,235Z", fill="#3d342b"))
    # Upper travertine dam rim (y ~ 112..156) with sculpted 3D calcified tufa draperies and mineral ledges
    for tx, tw, th, col in ((74, 106, 42, "#8c7b65"), (170, 146, 46, "#9e8c74"), (306, 112, 42, "#877660")):
        s.add(el("path", d=(
            f"M{tx},112 Q{tx + tw * 0.25},108 {tx + tw * 0.5},111 Q{tx + tw * 0.75},108 {tx + tw},112 "
            f"Q{tx + tw + 6},{112 + th * 0.5} {tx + tw - 4},{112 + th} "
            f"L{tx + 4},{112 + th} Q{tx - 6},{112 + th * 0.5} {tx},112Z"
        ), fill=col))
        # Tapered calcified dripstone lobes (instead of uniform vertical stripes)
        lobes_d = []
        for lx_ in range(tx + 8, tx + tw - 8, 9):
            lw_ = rng.uniform(2.5, 4.5)
            lh_ = rng.uniform(th * 0.45, th * 0.88)
            lobes_d.append(f"M{n(lx_)},113 L{n(lx_ + lw_ * 0.5)},{n(113 + lh_)} L{n(lx_ + lw_)},113Z")
        s.add(el("path", d=" ".join(lobes_d), fill=mix(col, "#4a3e30", 0.38), opacity=0.65))
        s.add(el("path", d=f"M{tx + 2},112 Q{tx + tw * 0.5},109 {tx + tw - 2},112", stroke="#d8cbb8", stroke_width=2.0, fill="none", opacity=0.7))
        s.add(crown(rng, tx + tw * 0.24, 111, 11, ("#1d4720", "#316e2d", "#5c9e48"), k=4, flat=0.45, detail=False))
        s.add(crown(rng, tx + tw * 0.78, 112, 10, ("#1d4720", "#316e2d", "#5c9e48"), k=4, flat=0.45, detail=False))

    # Tier 1 lacy white-water veil cascades plunging into the middle travertine pool
    for wx, ww in ((118, 22), (195, 28), (248, 34), (298, 22), (355, 24)):
        s.add(waterfall(s, wx, 111, 158, ww))

    # Middle turquoise-jade travertine terrace basin (y = 152..188, starting at x=78 so left grotto branch never overlaps it!)
    mid_pool_d = "M76,156 Q160,149 250,152 Q345,149 422,156 Q436,174 414,188 Q250,195 84,188 Q64,174 76,156Z"
    s.add(el("path", d=mid_pool_d, fill=s.linear("midpool", [(0, "#3fd4c0"), (0.55, "#1ea898"), (1, "#12736a")])))
    s.add(water_lines(rng, 92, 402, 158, 184, 24, col="#e4fcf8", op=0.62))
    s.add(mist(s, 250, 156, 140, 10, op=0.55))

    # Scalloped calcified travertine rim dam of the middle pool (y = 182..224) with multi-stepped tufa shelves
    for sx_, sw_, sy_, sh_ in ((78, 108, 183, 40), (174, 148, 185, 42), (308, 114, 183, 40)):
        s.add(el("path", d=(
            f"M{sx_},{sy_} Q{sx_ + sw_ * 0.5},{sy_ + 6} {sx_ + sw_},{sy_} "
            f"Q{sx_ + sw_ + 8},{sy_ + sh_ * 0.6} {sx_ + sw_ - 6},{sy_ + sh_} "
            f"L{sx_ + 6},{sy_ + sh_} Q{sx_ - 8},{sy_ + sh_ * 0.6} {sx_},{sy_}Z"
        ), fill="#a8947a"))
        s.add(el("path", d=f"M{sx_},{sy_} Q{sx_ + sw_ * 0.5},{sy_ + 6} {sx_ + sw_},{sy_}",
                 stroke="#dfd2be", stroke_width=2.6, fill="none", opacity=0.82))
        lobes2 = []
        for lx_ in range(sx_ + 8, sx_ + sw_ - 8, 8):
            lw_ = rng.uniform(2.4, 4.2)
            lh_ = rng.uniform(sh_ * 0.45, sh_ * 0.88)
            lobes2.append(f"M{n(lx_)},{sy_ + 3} L{n(lx_ + lw_ * 0.5)},{n(sy_ + 3 + lh_)} L{n(lx_ + lw_)},{sy_ + 3}Z")
        s.add(el("path", d=" ".join(lobes2), fill="#695947", opacity=0.6))
        s.add(crown(rng, sx_ + sw_ * 0.5, sy_ + 2, 12, ("#1d4720", "#316e2d", "#5c9e48"), k=4, flat=0.42, detail=False))

    # Tier 2 bridal-veil travertine cascades spilling into the crystal lower swimming lagoon (shifted right of x=104 so left branch/bird are clear!)
    for wx, ww in ((110, 20), (158, 25), (216, 32), (272, 30), (328, 24), (382, 18)):
        s.add(waterfall(s, wx, 185, 226, ww))
    s.add(mist(s, 248, 224, 160, 12, op=0.60))

    # Lower crystal-clear emerald-turquoise natural swimming lagoon (y = 220..300)
    s.add(el("rect", x=0, y=220, width=480, height=80,
             fill=s.linear("lowpool", [(0, "#4ce0cc"), (0.38, "#22b5a4"), (0.78, "#0f7d73"), (1, "#084f4a")])))
    s.add(el("ellipse", cx=195, cy=252, rx=78, ry=12, fill="#8cebe0", opacity=0.32))
    s.add(el("ellipse", cx=310, cy=268, rx=65, ry=10, fill="#8cebe0", opacity=0.25))
    s.add(water_lines(rng, 25, 455, 226, 294, 38, col="#e8fffb", op=0.65))

    # Framing limestone grotto banks with giant Cuban tree ferns, heliconias, and perched Cuban Trogon
    left_bank = [(0, 122), (56, 140), (74, 192), (84, 248), (64, 300), (0, 300)]
    right_bank = [(480, 134), (432, 152), (416, 202), (404, 254), (422, 300), (480, 300)]
    s.add(el("path", d=smooth(left_bank) + "Z", fill="#29241e"))
    s.add(el("path", d=smooth(right_bank) + "Z", fill="#29241e"))
    s.add(crown(rng, 24, 134, 30, ("#153b1e", "#28612e", "#4e8f42"), k=6))
    s.add(crown(rng, 456, 148, 30, ("#153b1e", "#28612e", "#4e8f42"), k=6))
    s.add(fern(rng, 32, 222, 42, "#3b8236"))
    s.add(fern(rng, 58, 256, 46, "#52a348"))
    s.add(fern(rng, 442, 228, 44, "#3b8236"))
    s.add(fern(rng, 418, 264, 42, "#52a348"))
    s.add(heliconia(22, 286, 46))
    s.add(heliconia(454, 288, 42))

    # Mossy overhanging branch positioned at y=148..154 over the dark left grotto bank so Cuban Trogon never overlaps pool rim or waterfall!
    s.add(el("path", d="M0,150 Q42,146 82,153 Q94,155 102,150", stroke="#4a3727", stroke_width=4.6, fill="none", stroke_linecap="round"))
    s.add(el("path", d="M0,148 Q42,144 80,151", stroke="#6c963e", stroke_width=1.8, fill="none", stroke_linecap="round"))
    s.add(bromeliad(rng, 76, 151, 9.0))
    s.add(cuban_trogon(44, 141, 0.94))
    return s.render()


def build_anavilhanas(labels):
    """Anavilhanas Fluvial Archipelago and Encontro das Águas (Amazonas): emerald igapó islands in dark mirror Rio Negro channels meeting golden-ochre Solimões water with pink river dolphins."""
    s = vignette("anavilhanas", 111)
    rng = s.rng
    sky(s, [(0, "#3675b2"), (0.45, "#82b8dc"), (0.82, "#dfeef2"), (1, "#f7e6c4")], h=96)
    sun(s, 392, 42, 16, glow="#ffebb5")
    s.add(cloud(rng, 118, 38, 92), cloud(rng, 275, 44, 82))

    # Distant continuous Amazonian rainforest horizon line
    s.add(g(canopy_band(s, -15, 495, lambda x: 92 + 2.5 * math.sin(x / 35), 28, 8, 13, ("#1c4228", "#2d6136", "#4a8244"), k=4)))

    # Base river water: deep tea-black Rio Negro mirror water across upper/left channels
    negro_grad = s.linear("negro", [(0, "#1d2e3a"), (0.45, "#122028"), (1, "#0a141a")])
    s.add(el("rect", x=0, y=92, width=480, height=208, fill=negro_grad))

    # Encontro das Águas (Meeting of Waters): sandy golden-ochre Solimões current sweeping across the right/lower basin
    solimoes_grad = s.linear("solimoes", [(0, "#c99b56"), (0.5, "#b88642"), (1, "#9c6d2e")])
    encontro_pts = [
        (480, 148), (418, 156), (354, 170), (304, 188),
        (268, 210), (228, 236), (186, 264), (144, 286), (118, 300), (480, 300),
    ]
    s.add(el("path", d=smooth(encontro_pts) + "Z", fill=solimoes_grad))

    # Soft hydrodynamic mixing eddies & swirling sediment lobes along the Rio Negro / Solimões interface (no sticks crossing dolphins!)
    seam_pts = encontro_pts[:-1]
    s.add(el("path", d=smooth(seam_pts), stroke="#dfb572", stroke_width=7.0, fill="none", opacity=0.45, filter=s.url("mist")))
    s.add(el("path", d=smooth([(x - 4, y - 2) for x, y in seam_pts]), stroke="#102028", stroke_width=4.0, fill="none", opacity=0.58, filter=s.url("soft")))
    # Interlocking fluid eddy lobes along the boundary (kept clear of dolphin (246, 218))
    for ex, ey, rx_, ry_, rot_, col_e, op_e in (
        (392, 160, 18, 4.5, -12, "#122028", 0.55),
        (366, 168, 16, 4.0, -14, "#d8ab68", 0.55),
        (322, 182, 15, 3.8, -18, "#122028", 0.52),
        (288, 198, 14, 3.6, -22, "#d8ab68", 0.52),
        (206, 248, 16, 4.2, -25, "#122028", 0.52),
        (172, 272, 15, 4.0, -24, "#d8ab68", 0.52),
    ):
        s.add(el("ellipse", cx=ex, cy=ey, rx=rx_, ry=ry_, fill=col_e, opacity=op_e,
                 transform=f"rotate({rot_} {ex} {ey})"))
    s.add(el("path", d=smooth([(x + 2, y + 1) for x, y in seam_pts]), stroke="#f4dfb2", stroke_width=1.4, fill="none", opacity=0.70))

    # Helper to draw an elongated Anavilhanas flooded igapó forest island with soft water reflection (no hard black boat hull!)
    def igapo_island(x0, x1, y_base, h_canopy, n_crowns, palms=()):
        w = x1 - x0
        # Soft blurred mirror reflection in the blackwater Rio Negro
        refl_d = (f"M{n(x0 + 6)},{n(y_base)} L{n(x1 - 6)},{n(y_base)} "
                  f"Q{n(x1 - w * 0.16)},{n(y_base + h_canopy * 0.45)} {n((x0 + x1) * 0.5)},{n(y_base + h_canopy * 0.50)} "
                  f"Q{n(x0 + w * 0.16)},{n(y_base + h_canopy * 0.45)} {n(x0 + 6)},{n(y_base)}Z")
        items = [
            el("path", d=refl_d, fill="#0c2218", opacity=0.42, filter=s.url("soft")),
            # Subtle submerged root bank
            el("path", d=f"M{n(x0 + 2)},{n(y_base)} Q{n((x0 + x1) * 0.5)},{n(y_base - 4)} {n(x1 - 2)},{n(y_base)} "
                         f"Q{n((x0 + x1) * 0.5)},{n(y_base + 1.8)} {n(x0 + 2)},{n(y_base)}Z", fill="#243820"),
        ]
        # Dense rounded emerald archipelago canopy extending right down to the water surface
        for i in range(n_crowns):
            t = (i + 0.5) / n_crowns
            cx_ = x0 + w * (0.08 + 0.84 * t)
            arch = math.sin(math.pi * t)
            r_ = h_canopy * (0.44 + 0.44 * arch) * rng.uniform(0.92, 1.06)
            cy_ = y_base - r_ * 0.42 - arch * h_canopy * 0.18
            items.append(crown(rng, cx_, cy_, r_, ("#143b20", "#26632e", "#529944"), k=6, flat=0.70))
        for px_, ph_, plean_ in palms:
            items.append(palm(rng, px_, y_base - 2, ph_, plean_, 12, cols=("#1f5727", "#4c9140"),
                              trunk_col="#6e5842", coconuts=False, nfr=11))
        # Delicate broken water-line shimmer at the island margin
        rip_d = f"M{n(x0 + w * 0.12)},{n(y_base + 1.2)} L{n(x0 + w * 0.42)},{n(y_base + 1.2)} M{n(x0 + w * 0.56)},{n(y_base + 1.2)} L{n(x1 - w * 0.14)},{n(y_base + 1.2)}"
        items.append(el("path", d=rip_d, stroke="#6aa8a0", stroke_width=0.75, fill="none", opacity=0.38))
        return g(items)

    # Well-separated Anavilhanas archipelago islands with open Rio Negro channels between front and back rows (zero island/palm overlaps!)
    s.add(igapo_island(28, 156, 118, 20, 6, palms=((74, 26, -3), (122, 24, 3))))
    s.add(igapo_island(225, 368, 116, 20, 7, palms=((272, 26, 3), (332, 24, -3))))
    s.add(igapo_island(382, 474, 134, 20, 5, palms=((428, 26, -3),)))
    s.add(igapo_island(-12, 178, 178, 26, 7, palms=((46, 32, 4), (132, 30, -3))))
    s.add(igapo_island(202, 308, 164, 22, 5, palms=((252, 26, 3),)))

    # Shimmering water lines on both the dark Rio Negro and golden Solimões currents
    s.add(water_lines(rng, 10, 250, 184, 275, 26, col="#6fa8a4", op=0.35))
    s.add(water_lines(rng, 230, 470, 175, 292, 30, col="#fae3b4", op=0.52))

    # Giant Victoria amazonica water lilies floating cleanly inside the calm Rio Negro blackwater bay on the lower left
    for lx, ly, lr, fl in ((38, 244, 16, False), (84, 256, 21, True), (34, 276, 25, True), (90, 284, 17, False)):
        s.add(water_lily(rng, lx, ly, lr, flower=fl))

    # Pair of Amazonian Pink River Dolphins (Boto / Inia geoffrensis) breaching cleanly across the Encontro das Águas!
    s.add(dolphin(246, 218, 1.05))
    s.add(dolphin(342, 252, 0.82))

    # Scarlet Macaws flying over the archipelago channels
    s.add(macaw(168, 62, 0.72))
    s.add(macaw(212, 74, 0.56))
    return s.render()


def build_chapada(labels):
    """Chapada Diamantina Mesas and Poço Encantado Crystal Grotto (Brazil): flat-topped Morro do Pai Inácio tablelands above and subterranean cobalt cavern lake pierced by a diagonal sunbeam below."""
    s = vignette("chapada", 112)
    rng = s.rng
    sky(s, [(0, "#4384bf"), (0.5, "#8ec2e2"), (1, "#f5dec0")], h=128)
    sun(s, 118, 42, 15, glow="#ffeaad")
    s.add(cloud(rng, 372, 38, 84))

    # Upper Vista: Iconic flat-topped sandstone mesas of Chapada Diamantina
    # Far mesa on left (x=4..92) leaving x=94..162 as an open sunlit valley above the cavern skylight!
    s.add(el("path", d="M4,106 L16,68 L24,65 L76,64 L84,68 L94,106Z", fill="#9e7462", opacity=0.84))
    s.add(el("path", d="M16,68 L24,65 L76,64 L84,68 L87,77 L13,77Z", fill="#c49378", opacity=0.68))
    s.add(el("path", d="M52,65 L76,64 L84,68 L94,106 L62,106Z", fill="#69483b", opacity=0.42))

    # Main Morro do Pai Inácio tableland on center-right (x=168..366) with craggy battlements and 3D strata
    mesa_top = [(190, 47), (206, 43), (232, 44), (260, 42), (290, 44), (318, 43), (334, 47)]
    mesa_pts = [(168, 108), (182, 74)] + mesa_top + [(348, 74), (366, 108)]
    mesa_d = P(mesa_pts)
    s.add(el("path", d=mesa_d, fill="#7d5243"))
    mcid = s.clip("pai_inacio", mesa_d)
    mesa_details = [
        el("path", d="M165,40 L258,40 L244,110 L165,110Z", fill="#b87e63", opacity=0.48),
        el("path", d="M274,40 L370,40 L370,110 L286,110Z", fill="#3d241c", opacity=0.45),
        el("path", d="M165,54 L368,54 L368,63 L165,63Z", fill="#c98e70", opacity=0.55),
        el("path", d="M165,72 L368,72 L368,81 L165,81Z", fill="#59362b", opacity=0.52),
        el("path", d="M168,108 L198,78 L235,96 L278,76 L320,95 L346,80 L366,108Z", fill="#4a2e24", opacity=0.65),
    ]
    mesa_flutes = " ".join(f"M{n(x)},43 L{n(x + rng.uniform(-2, 2))},102" for x in range(192, 332, 9))
    mesa_details.append(el("path", d=mesa_flutes, stroke="#3d241c", stroke_width=1.2, fill="none", opacity=0.62))
    s.add(g(mesa_details, clip_path=mcid))
    for vx, vr in ((208, 14), (240, 18), (276, 16), (310, 15)):
        s.add(crown(rng, vx, 43.5, vr * 0.65, ("#244a1e", "#3b6e30", "#62994a"), k=4, flat=0.35, detail=False))

    # Undulating campos rupestres highland ridge Dipping down at the natural karst sinkhole skylight (x=96..154)
    ridge_l = [(0, 98), (42, 92), (78, 96), (98, 106)]
    ridge_r = [(152, 106), (195, 94), (265, 90), (345, 94), (415, 88), (480, 96)]
    s.add(el("path", d=smooth(ridge_l) + " L98,122 L0,122Z", fill="#4d6932"))
    s.add(el("path", d=smooth(ridge_r) + " L480,122 L152,122Z", fill="#4d6932"))
    s.add(tufts(rng, 0, 92, interp(ridge_l), 14, 7, "#769c48", op=0.78))
    s.add(tufts(rng, 158, 480, interp(ridge_r), 32, 7, "#769c48", op=0.78))

    # Lower Cutaway: Vaulted Quartzite Cavern of Poço Encantado (y = 104..300)
    # Cavern interior background starts at x=88 so the skylight opening (x=96..154) stays open to the sunlit sky at y=98..112!
    s.add(el("path", d="M0,114 L92,106 L156,106 L480,104 L480,300 L0,300Z", fill="#0c0e16"))
    # Back cavern wall with 3D rocky quartzite buttresses and natural ledges (no purple brick stripes!)
    s.add(el("path", d="M40,114 L448,112 L456,212 L32,212Z", fill="#1d1a24"))
    for bx_w, bw_w, col_w in ((65, 68, "#2c2636"), (145, 82, "#352d40"), (235, 78, "#282232"), (320, 86, "#30283a"), (398, 58, "#241e2c")):
        s.add(el("path", d=(
            f"M{bx_w},114 L{bx_w + bw_w * 0.5},112 L{bx_w + bw_w},116 "
            f"L{bx_w + bw_w - 8},210 L{bx_w + 6},210Z"
        ), fill=col_w, opacity=0.75))
        s.add(el("path", d=f"M{bx_w + 4},114 L{bx_w + bw_w * 0.42},112 L{bx_w + bw_w * 0.36},210 L{bx_w + 6},210Z",
                 fill=mix(col_w, "#6e5c78", 0.25), opacity=0.45))
    # Irregular stepped quartzite bedding ledges on the back wall
    for yb in (138, 166, 190):
        pts_w = [(x, yb + 3.5 * math.sin(x * 0.05 + yb) + rng.uniform(-2, 2)) for x in range(40, 455, 28)]
        s.add(el("path", d=smooth(pts_w), stroke="#110e16", stroke_width=2.2, fill="none", opacity=0.75))
        s.add(el("path", d=smooth([(x, y - 1.5) for x, y in pts_w]), stroke="#4d4056", stroke_width=1.0, fill="none", opacity=0.5))

    # Subterranean Crystal-Clear Cobalt Lake (Poço Encantado, y = 206..300)
    lake_grad = s.radial("poco", [
        (0, "#42eeff", 1),
        (0.26, "#189cf7", 1),
        (0.56, "#0b4ec4", 1),
        (0.82, "#062570", 1),
        (1, "#031033", 1),
    ], cx=0.50, cy=0.42, r=0.62)
    s.add(el("rect", x=0, y=206, width=480, height=94, fill=lake_grad))

    # Organic 3D Submerged Quartzite Boulders & Ledges visible 60m below through the crystal-clear cobalt water (not origami boats!)
    def submerged_rock(rx, ry, rw, rh, lit_c="#36bcf7", mid_c="#1262c4", dark_c="#072c69"):
        pts_base = [
            (rx - rw * 0.50, ry + rh * 0.15),
            (rx - rw * 0.36, ry - rh * 0.52),
            (rx - rw * 0.06, ry - rh * 0.72),
            (rx + rw * 0.28, ry - rh * 0.58),
            (rx + rw * 0.50, ry + rh * 0.12),
            (rx + rw * 0.32, ry + rh * 0.38),
            (rx - rw * 0.28, ry + rh * 0.40),
        ]
        pts_lit = pts_base[:4] + [(rx + rw * 0.08, ry + rh * 0.05), (rx - rw * 0.32, ry + rh * 0.10)]
        pts_sh = [pts_base[2], pts_base[3], pts_base[4], pts_base[5], (rx + rw * 0.02, ry + rh * 0.12)]
        return g([
            el("ellipse", cx=rx, cy=ry + rh * 0.25, rx=rw * 0.54, ry=rh * 0.28, fill="#031233", opacity=0.55),
            el("path", d=smooth(pts_base, closed=True, k=0.14), fill=mid_c, opacity=0.72),
            el("path", d=smooth(pts_lit, closed=True, k=0.14), fill=lit_c, opacity=0.55),
            el("path", d=smooth(pts_sh, closed=True, k=0.14), fill=dark_c, opacity=0.68),
        ])

    for rx_, ry_, rw_, rh_ in ((145, 276, 46, 15), (196, 262, 52, 16), (256, 278, 64, 19),
                               (318, 260, 48, 15), (282, 246, 36, 11), (366, 276, 44, 14)):
        s.add(submerged_rock(rx_, ry_, rw_, rh_))

    # Iconic Diagonal Shaft of Sunlight streaming from the open skylight (x=98..152, y=106) into the cobalt pool
    beam_grad = s.linear("poco_beam", [
        (0, "#fff9de", 0.55),
        (0.35, "#aef0ff", 0.42),
        (0.75, "#38b6ff", 0.25),
        (1, "#1678f0", 0.0),
    ], x1=0.2, y1=0, x2=0.65, y2=1)
    # Soft backlit quartzite cavern rim at the back of the skylight sinkhole (x=96..154, y=104..114)
    s.add(el("path", d="M92,105 Q125,112 156,105 L156,115 L92,115Z", fill="#543c34"))
    s.add(el("path", d="M96,106 L154,106 L368,288 L175,288Z", fill=beam_grad, filter=s.url("soft")))
    s.add(el("path", d="M108,106 L142,106 L322,278 L208,278Z", fill=beam_grad))
    s.add(light_rays(s, 100, 144, 106, 272, 6, op=0.22))
    # Brilliant turquoise-white surface caustic reflection where the sunbeam enters the water
    s.add(el("ellipse", cx=238, cy=218, rx=66, ry=8.5, fill="#8cf4ff", opacity=0.52, filter=s.url("soft")))
    s.add(el("ellipse", cx=238, cy=218, rx=40, ry=4.2, fill="#e6ffff", opacity=0.75))
    s.add(water_lines(rng, 90, 400, 210, 294, 30, col="#a8f0ff", op=0.54))

    # Vaulted Cavern Roof Arch & Framing Quartzite Walls with Natural Skylight Window at x=96..154
    left_arch = [
        (0, 98), (42, 92), (78, 96), (98, 104), (96, 118), (84, 140), (72, 170),
        (76, 206), (62, 248), (74, 300), (0, 300),
    ]
    right_arch = [
        (152, 104), (195, 94), (265, 90), (345, 94), (415, 88), (480, 96), (480, 300),
        (402, 300), (418, 258), (396, 214), (408, 172), (376, 140),
        (322, 126), (255, 120), (195, 116), (164, 114),
    ]
    l_arch_d = P(left_arch)
    r_arch_d = P(right_arch)
    s.add(el("path", d=l_arch_d, fill="#2b1e1b"))
    s.add(el("path", d=r_arch_d, fill="#241816"))
    # Clipped 3D stratified sandstone rock ledges inside the left and right cavern walls (no floating brown plates!)
    l_clip = s.clip("chap-l", l_arch_d)
    r_clip = s.clip("chap-r", r_arch_d)
    s.add(g([
        el("path", d="M62,96 L98,104 L96,120 L84,142 L72,172 L52,162 L64,126Z", fill="#8c5840", opacity=0.68),
        el("path", d="M48,162 L72,172 L76,208 L62,248 L38,238 L52,198Z", fill="#593728", opacity=0.58),
        el("path", d="M0,126 Q45,132 92,124 M0,162 Q40,168 74,160 M0,202 Q42,208 76,202", stroke="#170f0d", stroke_width=1.8, fill="none", opacity=0.65),
    ], clip_path=l_clip))
    s.add(g([
        el("path", d="M152,104 L265,90 L255,120 L195,116 L164,114Z", fill="#7a4c36", opacity=0.62),
        el("path", d="M396,140 L445,135 L445,260 L418,258 L396,214 L408,172Z", fill="#472c22", opacity=0.58),
        el("path", d="M160,108 Q290,118 480,110 M375,142 Q430,148 480,142 M402,184 Q445,190 480,184", stroke="#140d0c", stroke_width=1.8, fill="none", opacity=0.65),
    ], clip_path=r_clip))

    # Vertical stalactites and craggy rock pendants hanging straight down from the cavern ceiling arch
    stal_list = []
    for x in range(168, 382, 16):
        sy0 = 113 + (x - 165) * 0.06
        sh_ = rng.uniform(8, 18)
        sw_ = rng.uniform(2.0, 3.4)
        stal_list.append(f"M{n(x - sw_)},{n(sy0)} L{n(x)},{n(sy0 + sh_)} L{n(x + sw_)},{n(sy0)}Z")
    s.add(el("path", d=" ".join(stal_list), fill="#1f1514"))

    # Upper rim foliage, Vellozia rosettes, ferns, and magenta Chapada rock orchids framing the skylight & foreground ledges
    s.add(crown(rng, 38, 94, 15, ("#1f471e", "#366b2d", "#5e9646"), k=5, flat=0.55, detail=False))
    s.add(crown(rng, 438, 92, 17, ("#1f471e", "#366b2d", "#5e9646"), k=5, flat=0.55, detail=False))
    s.add(fern(rng, 82, 100, 24, "#3e8438"))
    s.add(fern(rng, 162, 100, 24, "#4d9844"))
    s.add(fern(rng, 38, 252, 36, "#2e6b2b"))
    s.add(fern(rng, 438, 254, 36, "#2e6b2b"))
    s.add(bromeliad(rng, 64, 97, 9.0, col="#5c8f36", flower="#e0367a"))
    s.add(bromeliad(rng, 184, 96, 9.0, col="#5c8f36", flower="#e0367a"))
    s.add(condor(405, 56, 0.55))
    return s.render()


# ==============================================================================
# LOCALIZATION & INJECTION
# ==============================================================================
LABELS = {
    "en": {
        "alt": {
            "reef": "Split-level view of a Waikiki mangrove coast and the coral reef beneath it, with sea turtle, manta ray, reef fish and coral nursery frames",
            "rainforest": "Amazonian river scene with layered canopy, emergent kapok trees, giant water lilies, pink river dolphin, macaws and a toucan",
            "highlands": "Brazilia highlands with glacier, turquoise glacial lake, paramo grassland, cloud forest waterfall and soaring Andean condors",
            "mogotes": "Karst mogote towers rising over a tobacco valley with royal palms",
            "enriquillo": "Hypersaline Lago Enriquillo with flamingos, cacti, a rhinoceros iguana and an American crocodile",
            "pantanal": "Flooded Pantanal savanna at sunset with jabiru storks, capybaras and a caiman",
            "cerrado": "Cerrado savanna with flowering ipe trees, termite mounds and a maned wolf",
            "lencois": "White sand dunes with turquoise rain lagoons",
            "caatinga": "Dry Caatinga thorn forest with mandacaru cacti and a hyacinth macaw",
            "bluehole": "Submarine blue hole sinkhole dropping into deep indigo water surrounded by turquoise coral flats with a reef shark and sea turtle",
            "tepui": "Flat-topped sandstone tepui mesa with sheer vertical cliffs, waterfalls plunging into cloud forest and endemic pitcher plants",
            "cataracts": "Multi-tiered roaring waterfalls cascading over dark basalt cliffs with a mist rainbow, lush subtropical ferns and toucan",
            "elnicho": "Stepped turquoise travertine waterfall pools in the Escambray cloud forest of Cuba with royal palms, giant tree ferns and a perched Cuban trogon",
            "anavilhanas": "Flooded emerald igapo forest islands of the Anavilhanas Archipelago above the Meeting of Waters where dark Rio Negro and golden Solimoes currents flow side by side with pink river dolphins",
            "chapada": "Flat-topped sandstone mesas of Chapada Diamantina above the subterranean Poco Encantado cavern lake illuminated in glowing cobalt blue by a diagonal shaft of sunlight",
        },
    },
    "hu": {
        "alt": {
            "reef": "Waikiki mangrovepartja és az alatta húzódó korallzátony osztott nézetben, tengeri teknőssel, ördögrájával, zátonyhalakkal és korallkertekkel",
            "rainforest": "Amazóniai folyó rétegzett lombkoronával, kiemelkedő kapokfákkal, óriás tündérrózsákkal, rózsaszín folyami delfinnel, arákkal és tukánnal",
            "highlands": "Brazília hegyvidéke gleccserrel, türkiz gleccsertóval, páramo füves pusztával, köderdei vízeséssel és köröző andoki kondorokkal",
            "mogotes": "Dohányvölgy fölé magasodó karsztos mogote-tornyok királypálmákkal",
            "enriquillo": "A sós Enriquillo-tó flamingókkal, kaktuszokkal, orrszarvúleguánnal és hegyesorrú krokodillal",
            "pantanal": "Elárasztott Pantanal szavanna naplementében jabiru gólyákkal, vízidisznókkal és kajmánnal",
            "cerrado": "Cerrado szavanna virágzó ipéfákkal, termeszvárakkal és sörényes farkassal",
            "lencois": "Fehér homokdűnék türkiz esővíz-lagúnákkal",
            "caatinga": "Száraz Caatinga tüskeerdő mandacaru kaktuszokkal és jácintarával",
            "bluehole": "Mély kobaltkékbe vesző tenger alatti víznyelő türkiz korallzátonyokkal, szirti cápával és tengeri teknőssel",
            "tepui": "Függőleges homokkősziklákkal a felhők fölé magasodó lapos tetejű tepui vízesésekkel és húsevő növényekkel",
            "cataracts": "Bazaltsziklákon lezúduló hatalmas vízesésrendszer szivárvánnyal, szubtrópusi páfrányokkal és tukánnal",
            "elnicho": "Lépcsőzetes türkizkék mésztufa-vízesések és medencék a kubai Escambray-hegység köderdejében királypálmákkal, páfrányfákkal és kubai trogonnal",
            "anavilhanas": "Az Anavilhanas folyami szigetvilág smaragdzöld ártéri szigetei és a fekete Rio Negro, valamint az okkersárga Solimões folyók találkozása rózsaszín folyami delfinekkel",
            "chapada": "A Chapada Diamantina lapos tetejű homokkő táblahegyei és a beszűrődő napsugártól kobaltkéken ragyogó földalatti Poço Encantado barlangi tó",
        },
    },
}

BUILDERS = {
    "reef": build_reef,
    "rainforest": build_rainforest,
    "highlands": build_highlands,
    "mogotes": build_mogotes,
    "enriquillo": build_enriquillo,
    "pantanal": build_pantanal,
    "cerrado": build_cerrado,
    "lencois": build_lencois,
    "caatinga": build_caatinga,
    "bluehole": build_bluehole,
    "tepui": build_tepui,
    "cataracts": build_cataracts,
    "elnicho": build_elnicho,
    "anavilhanas": build_anavilhanas,
    "chapada": build_chapada,
}

CONTAINER_RE = r'(<div[^>]*\bdata-nature-svg="{key}"[^>]*>\s*)(?:<svg\b.*?</svg>|<img\b[^>]*>)?(\s*</div>)'


def validate(svg: str, key: str) -> None:
    try:
        ET.fromstring(svg)
    except ET.ParseError as exc:
        sys.exit(f"Error: generated SVG '{key}' is invalid XML: {exc}")


def update_pages(rendered: dict[str, dict[str, str]]) -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from build_pages import format_and_remove_empty_lines

    dims = {
        "reef": (1200, 720),
        "rainforest": (1200, 720),
        "highlands": (1200, 700),
    }
    default_dim = (480, 300)

    for lang in ("en", "hu"):
        path = ROOT / lang / "nature.html"
        text = path.read_text(encoding="utf-8")
        for key in BUILDERS.keys():
            w, h = dims.get(key, default_dim)
            alt_txt = LABELS[lang]["alt"].get(key, "")
            src_file = f"{key}.svg"
            img_tag = f'<img class="nature-ill" src="../icons/nature/{src_file}" alt="{html.escape(alt_txt, quote=True)}" width="{w}" height="{h}" />'
            pattern = re.compile(CONTAINER_RE.format(key=key), re.S)
            match = pattern.search(text)
            if not match:
                print(f"  ! no data-nature-svg=\"{key}\" container in {path.relative_to(ROOT)}")
                continue
            text = text[: match.start()] + match.group(1) + img_tag + match.group(2) + text[match.end():]
        formatted = format_and_remove_empty_lines(text)
        path.write_text(formatted, encoding="utf-8")
        print(f"Updated and formatted {path.relative_to(ROOT)}")


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
