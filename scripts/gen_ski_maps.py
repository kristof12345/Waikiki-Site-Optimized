#!/usr/bin/env python3
"""
Procedural generator for Waikiki Ski Paradise realistic 3D panoramic alpine trail maps:
  - Tab 1: Grand Andes Massif (icons/ski/andes-map.svg)
  - Tab 2: Haiti Highland Glacier (icons/ski/haiti-map.svg)

Generates standalone SVG files in icons/ski/ and injects localized inline SVGs
into en/ski-paradise.html and hu/ski-paradise.html.
"""

import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKI_ICONS_DIR = ROOT / "icons" / "ski"
ANDES_SVG_PATH = SKI_ICONS_DIR / "andes-map.svg"
HAITI_SVG_PATH = SKI_ICONS_DIR / "haiti-map.svg"


def n(v: float) -> str:
    """Format number compactly to 1 decimal place."""
    if isinstance(v, int):
        return str(v)
    rv = round(v, 1)
    if rv == int(rv):
        return str(int(rv))
    s = f"{rv:.1f}"
    return "0" if s == "-0.0" else s


def pt(p) -> str:
    return f"{n(p[0])},{n(p[1])}"


def poly(points, close=True) -> str:
    d = "M" + " L".join(pt(p) for p in points)
    return d + (" Z" if close else "")


def catmull_rom_svg(points, closed=False) -> str:
    """Convert a list of (x, y) points into a smooth cubic Bezier SVG path."""
    if len(points) < 2:
        return ""
    if len(points) == 2:
        return f"M{pt(points[0])} L{pt(points[1])}"
    pts = list(points)
    if closed:
        pts = [pts[-1]] + pts + [pts[0], pts[1]]
    else:
        pts = [pts[0]] + pts + [pts[-1]]

    d = [f"M{pt(pts[1])}"]
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        c1x = p1[0] + (p2[0] - p0[0]) / 6.0
        c1y = p1[1] + (p2[1] - p0[1]) / 6.0
        c2x = p2[0] - (p3[0] - p1[0]) / 6.0
        c2y = p2[1] - (p3[1] - p1[1]) / 6.0
        d.append(f"C{n(c1x)},{n(c1y)} {n(c2x)},{n(c2y)} {pt(p2)}")
    if closed:
        d.append("Z")
    return " ".join(d)


def subdiv_ridge(p1, p2, roughness=12.0, seed=1, steps=8):
    """Create a realistic craggy mountain arête between p1 and p2 (from p1 to p2)."""
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = p1[0] + (p2[0] - p1[0]) * t
        y = p1[1] + (p2[1] - p1[1]) * t
        if 0 < i < steps:
            env = math.sin(math.pi * t)
            off = roughness * env * (
                0.62 * math.sin(i * 2.7 + seed * 1.3)
                + 0.38 * math.cos(i * 4.9 + seed * 2.1)
            )
            y += off
            x += off * 0.28 * math.cos(i * 3.1 + seed)
        pts.append((x, y))
    return pts


def draw_3d_peak(
    peak_xy,
    left_base,
    right_base,
    center_base,
    lit_fill,
    shade_fill,
    rock_dark="#122b4a",
    rock_mid="#1f4570",
    seed=1,
):
    """
    Render a non-overlapping, solid 3D multi-faceted mountain massif:
      - Sunlit western face (left_base -> peak_xy -> center_base)
      - Shadowed eastern face (peak_xy -> right_base -> center_base)
      - Secondary sub-ridges, rock cliff bands, snow chutes, and arête highlights
    """
    out = []
    # 1. Outer skyline and central ridge spine
    left_edge = subdiv_ridge(left_base, peak_xy, roughness=10.0, seed=seed, steps=8)
    right_edge = subdiv_ridge(peak_xy, right_base, roughness=10.0, seed=seed + 3, steps=8)
    spine = subdiv_ridge(peak_xy, center_base, roughness=11.0, seed=seed + 7, steps=9)

    # Closed sunlit western face: left_base -> peak_xy -> center_base -> close
    lit_poly = left_edge + spine[1:]
    out.append(f'<path d="{poly(lit_poly)}" fill="{lit_fill}" />')

    # Closed shadowed eastern face: peak_xy -> right_base -> center_base -> close
    shade_poly = right_edge + list(reversed(spine[:-1]))
    out.append(f'<path d="{poly(shade_poly)}" fill="{shade_fill}" />')

    # 2. Sunlit snow facets and exposed granite crags on the western slope
    for k in (2, 4, 6):
        if k < len(spine) - 1 and (len(left_edge) - 1 - k) >= 1:
            sp_pt = spine[k]
            sp_next = spine[k + 1]
            le_pt = left_edge[len(left_edge) - 1 - k]
            mid_pt = (
                0.55 * sp_pt[0] + 0.45 * le_pt[0],
                0.55 * sp_pt[1] + 0.45 * le_pt[1] + 18,
            )
            low_pt = (
                0.35 * sp_pt[0] + 0.65 * le_pt[0],
                0.35 * sp_pt[1] + 0.65 * le_pt[1] + 38,
            )
            rib = [sp_pt, mid_pt, low_pt, sp_next]
            out.append(f'<path d="{poly(rib)}" fill="#d2e7f9" opacity="0.65" />')
            # Exposed sunlit rock crag anchored along the central spine
            crag = [
                sp_pt,
                (0.75 * sp_pt[0] + 0.25 * le_pt[0], 0.75 * sp_pt[1] + 0.25 * le_pt[1] + 10),
                sp_next,
            ]
            out.append(f'<path d="{poly(crag)}" fill="{rock_mid}" opacity="0.52" />')

    # 3. Stratified granite rock faces and snow couloirs on the shadowed eastern slope
    for k in (1, 3, 5, 7):
        if k < len(spine) - 1 and k < len(right_edge) - 1:
            a = spine[k]
            b = spine[k + 1]
            re_a = right_edge[k]
            re_b = right_edge[k + 1]
            c = (0.48 * b[0] + 0.52 * re_b[0], 0.48 * b[1] + 0.52 * re_b[1] + 6)
            d_pt = (0.58 * a[0] + 0.42 * re_a[0], 0.58 * a[1] + 0.42 * re_a[1] - 4)
            out.append(f'<path d="{poly([a, b, c, d_pt])}" fill="{rock_dark}" opacity="0.78" />')
            # Diagonal snow couloir / gully
            out.append(
                f'<path d="M{pt(a)} Q{n((a[0]+c[0])/2)},{n((a[1]+c[1])/2 + 6)} {pt(c)}" fill="none" stroke="#8ab8e6" stroke-width="1.5" opacity="0.65" />'
            )

    # 4. Crisp sunlit arête highlight along the central spine and western skyline
    out.append(
        f'<path d="{poly(left_edge, close=False)}" fill="none" stroke="#ffffff" stroke-width="1.8" opacity="0.9" />'
    )
    out.append(
        f'<path d="{poly(spine, close=False)}" fill="none" stroke="#ffffff" stroke-width="2.2" opacity="0.92" />'
    )
    return out


def draw_glacier_bowl(points, ice_fill, seed=1):
    """Render a realistic concave glacial cirque with serac crevasse lines."""
    out = [
        f'<path d="{catmull_rom_svg(points, closed=True)}" fill="{ice_fill}" opacity="0.46" />'
    ]
    # Add transverse crevasse arcs inside the glacier
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    cx = sum(xs) / len(xs)
    min_y, max_y = min(ys), max(ys)
    w = (max(xs) - min(xs)) * 0.30
    out.append('<g fill="none" stroke="#ffffff" stroke-width="1.2" opacity="0.65">')
    for i in range(1, 6):
        yy = min_y + (max_y - min_y) * (i / 6.5)
        ww = w * math.sin(math.pi * (i / 6.0))
        out.append(
            f'<path d="M{n(cx - ww)},{n(yy)} Q{n(cx)},{n(yy + 9)} {n(cx + ww)},{n(yy - 2)}" />'
        )
    out.append("</g>")
    return out


def draw_conifer_forest(clusters):
    """Render realistic layered alpine spruce trees with shadows and snow caps."""
    out = ['<g class="alpine-forest">']
    for cx, cy, count, spread_x, spread_y, scale_base, seed in clusters:
        # Sort trees top-to-bottom (by y) so foreground trees overlap background trees naturally
        trees = []
        for i in range(count):
            ang = (i * 2.39996) + seed
            r = math.sqrt((i + 0.5) / count)
            tx = cx + math.cos(ang) * spread_x * r
            ty = cy + math.sin(ang) * spread_y * r
            sc = scale_base * (0.72 + 0.48 * ((i * 37 + seed * 13) % 10) / 10.0)
            trees.append((ty, tx, sc))
        trees.sort()
        for ty, tx, sc in trees:
            h = 17.0 * sc
            w = 6.2 * sc
            # Shadow on snow
            out.append(
                f'<ellipse cx="{n(tx + 2.5)}" cy="{n(ty + 1)}" rx="{n(w * 0.95)}" ry="{n(w * 0.32)}" fill="#0f2947" opacity="0.3" />'
            )
            # Dark pine base tier
            out.append(
                f'<path d="M{n(tx)},{n(ty - h)} L{n(tx - w)},{n(ty)} L{n(tx + w)},{n(ty)} Z" fill="#0f3d3e" />'
            )
            # Mid pine tier
            out.append(
                f'<path d="M{n(tx)},{n(ty - h * 1.04)} L{n(tx - w * 0.76)},{n(ty - h * 0.36)} L{n(tx + w * 0.76)},{n(ty - h * 0.36)} Z" fill="#195959" />'
            )
            # Sunlit snow crown on left side of tree
            out.append(
                f'<path d="M{n(tx)},{n(ty - h * 1.04)} L{n(tx - w * 0.48)},{n(ty - h * 0.62)} L{n(tx + w * 0.18)},{n(ty - h * 0.66)} Z" fill="#eef7ff" opacity="0.9" />'
            )
    out.append("</g>")
    return out


def draw_palm_tree(x, y, scale=1.0, tilt=1.0):
    """Render a realistic tropical coconut palm tree for Haiti Island's beach zone."""
    tx = x + 7 * tilt * scale
    ty = y - 25 * scale
    out = [
        f'<ellipse cx="{n(x + 3)}" cy="{n(y + 1)}" rx="{n(8 * scale)}" ry="{n(2.5 * scale)}" fill="#bfa06a" opacity="0.45" />',
        f'<path d="M{n(x)},{n(y)} Q{n(x + 2.5 * tilt * scale)},{n(y - 13 * scale)} {n(tx)},{n(ty)}" fill="none" stroke="#6b4423" stroke-width="{n(2.6 * scale)}" stroke-linecap="round" />',
    ]
    fronds = [
        (-15, -3, -8, -8, "#15803d"),
        (-13, 6, -7, -1, "#166534"),
        (15, -3, 8, -8, "#22c55e"),
        (14, 6, 7, -1, "#15803d"),
        (-5, -12, -2, -9, "#22c55e"),
        (7, -11, 3, -8, "#16a34a"),
    ]
    for dx, dy, cx_off, cy_off, fcol in fronds:
        out.append(
            f'<path d="M{n(tx)},{n(ty)} Q{n(tx + cx_off * scale)},{n(ty + cy_off * scale)} {n(tx + dx * scale)},{n(ty + dy * scale)}" fill="none" stroke="{fcol}" stroke-width="{n(2.1 * scale)}" stroke-linecap="round" />'
        )
    return out


def draw_lift_line(lift_id, points, col="#dfba76", cabin_col="#c95a41", dur="11s", pylons=4):
    """Render a realistic dual-cable gondola/chairlift with lattice pylons and animated cabins."""
    d_path = poly(points, close=False)
    out = [
        f"<!-- Lift Corridor: {lift_id} -->",
        # Ground shadow of lift cable
        f'<path d="{d_path}" transform="translate(0, 6)" fill="none" stroke="#091e38" stroke-width="2.5" opacity="0.28" />',
        # Main haul cable
        f'<path id="{lift_id}" d="{d_path}" fill="none" stroke="{col}" stroke-width="1.9" stroke-dasharray="6 3" />',
    ]
    # Interpolate steel lattice pylon towers along segments
    out.append('<g stroke="#e2e8f0" stroke-width="1.3">')
    total_segs = len(points) - 1
    per_seg = max(2, pylons // total_segs)
    for seg_i in range(total_segs):
        p0, p1 = points[seg_i], points[seg_i + 1]
        for k in range(1, per_seg + 1):
            u = k / (per_seg + 1)
            px = p0[0] + (p1[0] - p0[0]) * u
            py = p0[1] + (p1[1] - p0[1]) * u
            out.append(f'<line x1="{n(px)}" y1="{n(py - 4)}" x2="{n(px)}" y2="{n(py + 11)}" />')
            out.append(
                f'<line x1="{n(px - 5.5)}" y1="{n(py - 4)}" x2="{n(px + 5.5)}" y2="{n(py - 4)}" stroke="{col}" stroke-width="1.8" />'
            )
            out.append(
                f'<polygon points="{n(px - 3.5)},{n(py + 11)} {n(px + 3.5)},{n(py + 11)} {n(px)},{n(py + 3)}" fill="#0f2542" />'
            )
    out.append("</g>")

    # Animated uphill and downhill cabins
    rev_path = poly(list(reversed(points)), close=False)
    out += [
        "<g>",
        f'<animateMotion dur="{dur}" repeatCount="indefinite" path="{d_path}" />',
        '<line x1="0" y1="0" x2="0" y2="6" stroke="#fcedc7" stroke-width="1.2" />',
        f'<rect x="-7" y="6" width="14" height="9" rx="3" fill="{cabin_col}" stroke="#fcedc7" stroke-width="1.1" />',
        '<rect x="-4.5" y="7.5" width="9" height="4" rx="1" fill="#e0f2fe" />',
        "</g>",
        "<g>",
        f'<animateMotion dur="{dur}" begin="-5.2s" repeatCount="indefinite" path="{rev_path}" />',
        '<line x1="0" y1="0" x2="0" y2="6" stroke="#fcedc7" stroke-width="1.2" />',
        '<rect x="-7" y="6" width="14" height="9" rx="3" fill="#0b2342" stroke="#dfba76" stroke-width="1.1" />',
        '<rect x="-4.5" y="7.5" width="9" height="4" rx="1" fill="#5ce1cf" />',
        "</g>",
    ]
    return out


def piste_badge(x, y, code, bg):
    """Render an authentic ski-map numbered trail shield."""
    return [
        f'<g transform="translate({n(x)}, {n(y)})">',
        f'<circle r="8" fill="{bg}" stroke="#ffffff" stroke-width="1.2" />',
        f'<text y="0.5" fill="#ffffff" font-family="sans-serif" font-size="7" font-weight="800" text-anchor="middle" dominant-baseline="central">{code}</text>',
        "</g>",
    ]


def hotspot_pin(idx, x, y, pin_dx=0, pin_dy=-26, active=False):
    """
    Place the interactive numbered pin slightly offset from the architectural landmark
    with a leader line so the building illustration is 100% visible!
    """
    px = x + pin_dx
    py = y + pin_dy
    cls = "map-hotspot is-active" if active else "map-hotspot"
    return [
        f'<line x1="{n(x)}" y1="{n(y)}" x2="{n(px)}" y2="{n(py)}" stroke="#fcedc7" stroke-width="1.4" stroke-dasharray="2 2" opacity="0.85" />',
        f'<circle cx="{n(x)}" cy="{n(y)}" r="3.2" fill="#fcedc7" stroke="#0b2342" stroke-width="1" />',
        f'<g class="{cls}" data-spot="{idx}" transform="translate({n(px)}, {n(py)})">',
        '<circle class="hotspot-pulse" r="14" fill="#e3735a" opacity="0.45" />',
        '<circle class="hotspot-core" r="10.5" fill="#003366" stroke="#ffffff" stroke-width="2" />',
        f'<text fill="#ffffff" font-family="sans-serif" font-size="10" font-weight="800" text-anchor="middle" dominant-baseline="central">{idx}</text>',
        "</g>",
    ]


# ==============================================================================
# MAP 1: GRAND ANDES MASSIF (1200 x 700)
# ==============================================================================
def build_andes_svg() -> str:
    o = [
        '<svg xmlns="http://www.w3.org/2000/svg" class="ill" viewBox="0 0 1200 700" role="img" aria-label="Detailed 3D panoramic ski trail map of the Grand Andes Massif in Waikiki">',
        "<defs>",
        '<linearGradient id="andes-sky" x1="0%" y1="0%" x2="0%" y2="100%">',
        '<stop offset="0%" stop-color="#06162e" />',
        '<stop offset="40%" stop-color="#12386b" />',
        '<stop offset="75%" stop-color="#2b6cb0" />',
        '<stop offset="100%" stop-color="#f3d5a0" />',
        "</linearGradient>",
        '<linearGradient id="andes-snow-lit" x1="0%" y1="0%" x2="25%" y2="100%">',
        '<stop offset="0%" stop-color="#ffffff" />',
        '<stop offset="50%" stop-color="#ebf5ff" />',
        '<stop offset="85%" stop-color="#c3def4" />',
        '<stop offset="100%" stop-color="#8bb6de" />',
        "</linearGradient>",
        '<linearGradient id="andes-face-shadow" x1="0%" y1="0%" x2="100%" y2="100%">',
        '<stop offset="0%" stop-color="#2e639e" />',
        '<stop offset="55%" stop-color="#183f6e" />',
        '<stop offset="100%" stop-color="#0c2240" />',
        "</linearGradient>",
        '<linearGradient id="andes-glacier-ice" x1="0%" y1="0%" x2="0%" y2="100%">',
        '<stop offset="0%" stop-color="#e0f7fe" />',
        '<stop offset="55%" stop-color="#7dd3fc" />',
        '<stop offset="100%" stop-color="#2563eb" />',
        "</linearGradient>",
        '<linearGradient id="andes-valley-snow" x1="0%" y1="0%" x2="0%" y2="100%">',
        '<stop offset="0%" stop-color="#d2e8f8" />',
        '<stop offset="50%" stop-color="#e6f2fc" />',
        '<stop offset="100%" stop-color="#b8d4ec" />',
        "</linearGradient>",
        "</defs>",
        "<!-- 1. Atmospheric Alpine Sky Backdrop -->",
        '<rect width="1200" height="700" fill="#12386b" />',
        '<rect width="1200" height="360" fill="url(#andes-sky)" />',
    ]

    # Starfield in upper zenith
    o.append('<g fill="#ffffff">')
    for i in range(28):
        sx = (i * 139 + 43) % 1160 + 20
        sy = (i * 53 + 11) % 90 + 10
        sr = 1.0 if i % 3 else 1.6
        cls = ' class="twinkle"' if i % 4 == 0 else ' opacity="0.5"'
        o.append(f'<circle cx="{sx}" cy="{sy}" r="{sr}"{cls} />')
    o.append("</g>")

    # Golden Andean Sun and Alpenglow behind Pico Soberano East Shoulder
    o += [
        '<g transform="translate(655, 112)">',
        '<circle r="76" fill="#fef3c7" opacity="0.18" />',
        '<circle r="46" fill="#fde68a" opacity="0.32" />',
        '<circle r="24" fill="#fffbeb" opacity="0.95" />',
        "</g>",
    ]

    # Distant Background Cordillera Horizon (Continuous across x = 0..1200)
    bg_skyline = [
        (0, 235), (55, 178), (115, 210), (195, 128), (275, 198),
        (355, 148), (435, 185), (525, 64), (615, 182), (695, 138),
        (785, 188), (875, 106), (965, 184), (1055, 148), (1135, 195), (1200, 168),
        (1200, 700), (0, 700)
    ]
    o.append("<!-- 2. Continuous Solid Alpine Massif Base (Zero Gaps) -->")
    o.append(f'<path d="{poly(bg_skyline)}" fill="#1d487a" />')

    # Far Distant Horizon Peaks peeking between main summits
    o.append(
        '<path d="M55,178 L92,202 L22,210 Z M275,198 L310,162 L338,192 Z M615,182 L645,146 L675,178 Z M965,184 L995,148 L1025,182 Z" fill="#6b9fd1" opacity="0.55" />'
    )

    # 3. Eight Overlapping 3D Multi-Faceted Peaks and Ridges
    o.append("<!-- 3. 3D Multi-Faceted Mountain Peaks, Rock Buttresses and Arêtes -->")
    # Background/Mid-ground ridges first
    o += draw_3d_peak(
        peak_xy=(75, 182),
        left_base=(-40, 450),
        right_base=(190, 450),
        center_base=(82, 460),
        lit_fill="url(#andes-snow-lit)",
        shade_fill="url(#andes-face-shadow)",
        seed=11,
    )
    o += draw_3d_peak(
        peak_xy=(355, 148),
        left_base=(215, 445),
        right_base=(495, 445),
        center_base=(362, 455),
        lit_fill="url(#andes-snow-lit)",
        shade_fill="url(#andes-face-shadow)",
        seed=22,
    )
    o += draw_3d_peak(
        peak_xy=(695, 138),
        left_base=(555, 445),
        right_base=(835, 445),
        center_base=(702, 455),
        lit_fill="url(#andes-snow-lit)",
        shade_fill="url(#andes-face-shadow)",
        seed=33,
    )
    o += draw_3d_peak(
        peak_xy=(1055, 148),
        left_base=(910, 455),
        right_base=(1235, 465),
        center_base=(1065, 465),
        lit_fill="url(#andes-snow-lit)",
        shade_fill="url(#andes-face-shadow)",
        seed=44,
    )

    # Primary Foreground Summits: Condor Peak (4,420 m), Monte Rosa (3,200 m), Pico Soberano (4,850 m)
    o += draw_3d_peak(
        peak_xy=(195, 128),
        left_base=(10, 480),
        right_base=(380, 475),
        center_base=(205, 485),
        lit_fill="url(#andes-snow-lit)",
        shade_fill="url(#andes-face-shadow)",
        seed=2,
    )
    o += draw_3d_peak(
        peak_xy=(875, 106),
        left_base=(675, 480),
        right_base=(1115, 485),
        center_base=(885, 490),
        lit_fill="url(#andes-snow-lit)",
        shade_fill="url(#andes-face-shadow)",
        seed=5,
    )
    o += draw_3d_peak(
        peak_xy=(525, 64),
        left_base=(275, 490),
        right_base=(775, 490),
        center_base=(538, 495),
        lit_fill="url(#andes-snow-lit)",
        shade_fill="url(#andes-face-shadow)",
        seed=9,
    )

    # Continuous Snow-Covered Mid-Mountain Bowls and Valley Floor (y = 390..700)
    o += [
        "<!-- 4. Continuous Valley Snow Blanket and Glacial Cirques -->",
        '<path d="M0,435 Q180,398 395,418 Q590,438 815,412 Q1020,392 1200,425 L1200,700 L0,700 Z" fill="url(#andes-valley-snow)" />',
        '<path d="M0,520 Q300,495 600,515 T1200,505 L1200,700 L0,700 Z" fill="#d4e7f7" />',
        '<path d="M0,595 Q350,575 700,590 T1200,582 L1200,700 L0,700 Z" fill="#bfd9f0" />',
    ]

    # Hanging Glaciers with Crevasse Fields
    o += draw_glacier_bowl(
        [(195, 145), (162, 235), (168, 345), (218, 348), (225, 240)],
        "url(#andes-glacier-ice)",
        seed=1,
    )
    o += draw_glacier_bowl(
        [(525, 84), (482, 195), (478, 340), (548, 345), (556, 200)],
        "url(#andes-glacier-ice)",
        seed=2,
    )
    o += draw_glacier_bowl(
        [(875, 122), (838, 210), (842, 325), (902, 328), (908, 215)],
        "url(#andes-glacier-ice)",
        seed=3,
    )

    # Topographic Elevation Contours & Labels
    o.append("<!-- Topographic Relief Contours -->")
    o.append('<g fill="none" stroke="#477eb3" stroke-width="0.9" stroke-dasharray="6 5" opacity="0.38">')
    for cy_base in (215, 265, 315, 365, 415, 465, 515):
        c_pts = [
            (0, cy_base + 18),
            (195, cy_base - 24),
            (355, cy_base + 10),
            (525, cy_base - 34),
            (695, cy_base + 12),
            (875, cy_base - 20),
            (1055, cy_base + 8),
            (1200, cy_base + 20),
        ]
        o.append(f'<path d="{catmull_rom_svg(c_pts)}" />')
    o.append("</g>")

    # Rio Aurelia Glacial River in the Valley Floor
    river_pts = [
        (0, 615), (145, 604), (295, 594), (455, 586), (585, 578),
        (735, 588), (890, 582), (1045, 592), (1200, 585)
    ]
    o += [
        "<!-- Rio Aurelia Glacial River -->",
        f'<path d="{catmull_rom_svg(river_pts)}" fill="none" stroke="#1e4e79" stroke-width="14" stroke-linecap="round" opacity="0.55" />',
        f'<path d="{catmull_rom_svg(river_pts)}" fill="none" stroke="#38bdf8" stroke-width="8" stroke-linecap="round" />',
        f'<path d="{catmull_rom_svg(river_pts)}" fill="none" stroke="#e0f2fe" stroke-width="2" stroke-dasharray="10 8" stroke-linecap="round" />',
    ]

    # Dense Sub-Alpine Conifer Forests (Tree-lined glades)
    forest_clusters = [
        (75, 475, 30, 62, 32, 0.95, 1),
        (148, 535, 24, 52, 24, 1.05, 2),
        (312, 475, 32, 65, 34, 0.92, 3),
        (468, 492, 28, 56, 26, 1.0, 4),
        (665, 475, 32, 60, 32, 0.95, 5),
        (835, 490, 30, 62, 28, 1.02, 6),
        (1088, 478, 34, 72, 36, 0.98, 7),
        (1130, 545, 24, 54, 24, 1.08, 8),
    ]
    o += draw_conifer_forest(forest_clusters)

    # 5. Intricate Braided Piste Network
    o.append("<!-- 5. Braided Piste Network (36 Interconnected Runs) -->")
    azure_pistes = [
        [(525, 76), (480, 135), (415, 185), (445, 245), (385, 295), (410, 355), (345, 415), (370, 465), (295, 510), (235, 548)],
        [(525, 76), (565, 140), (530, 205), (585, 265), (540, 330), (595, 395), (555, 460), (585, 528)],
        [(195, 138), (150, 195), (210, 250), (165, 315), (225, 375), (185, 445), (235, 548)],
        [(195, 138), (255, 205), (310, 265), (355, 315), (410, 355)],
        [(410, 355), (455, 405), (495, 445), (535, 490), (585, 528)],
        [(875, 114), (815, 175), (845, 235), (785, 290), (755, 352), (685, 425), (635, 480), (585, 528)],
        [(875, 114), (925, 180), (890, 245), (955, 310), (915, 380), (975, 445), (985, 515)],
        [(1055, 158), (1010, 225), (1065, 290), (1015, 360), (1045, 435), (985, 515)],
        [(355, 156), (325, 225), (375, 285), (410, 355)],
        [(695, 146), (665, 220), (715, 285), (755, 352)],
    ]
    crimson_pistes = [
        [(875, 114), (835, 168), (795, 228), (775, 290), (755, 352), (720, 425), (665, 485), (585, 528)],
        [(525, 76), (505, 155), (475, 235), (495, 315), (465, 395), (525, 465), (585, 528)],
        [(355, 156), (305, 235), (275, 315), (295, 395), (265, 470), (235, 548)],
        [(195, 138), (215, 215), (190, 295), (245, 370), (215, 455), (235, 548)],
        [(875, 114), (885, 195), (860, 275), (905, 355), (945, 435), (985, 515)],
        [(695, 146), (645, 225), (620, 305), (645, 385), (610, 460), (585, 528)],
        [(1055, 158), (1085, 240), (1040, 320), (1075, 405), (985, 515)],
    ]
    obsidian_pistes = [
        [(525, 76), (538, 155), (552, 235), (535, 315), (565, 415), (585, 528)],
        [(195, 138), (135, 210), (115, 295), (145, 385), (185, 470), (235, 548)],
        [(695, 146), (735, 220), (710, 295), (755, 352)],
        [(875, 114), (955, 175), (985, 255), (955, 345), (985, 515)],
    ]
    gold_heliski = [
        [(195, 138), (95, 185), (65, 265), (95, 355), (145, 445), (235, 548)],
        [(525, 76), (435, 115), (355, 156), (275, 144), (195, 138)],
        [(875, 114), (965, 132), (1055, 158), (1125, 245), (1095, 365), (985, 515)],
    ]

    # Groomed snow track bed under all runs
    o.append('<g fill="none" stroke="#ffffff" stroke-linecap="round" opacity="0.68">')
    for p in azure_pistes + crimson_pistes:
        o.append(f'<path d="{catmull_rom_svg(p)}" stroke-width="5.5" />')
    o.append("</g>")

    o.append('<g fill="none" stroke="#2563eb" stroke-width="2.8" stroke-linecap="round">')
    for p in azure_pistes:
        o.append(f'<path d="{catmull_rom_svg(p)}" />')
    o.append("</g>")
    o.append('<g fill="none" stroke="#e11d48" stroke-width="2.8" stroke-linecap="round">')
    for p in crimson_pistes:
        o.append(f'<path d="{catmull_rom_svg(p)}" />')
    o.append("</g>")
    o.append('<g fill="none" stroke="#0f172a" stroke-width="2.6" stroke-dasharray="7 3" stroke-linecap="round">')
    for p in obsidian_pistes:
        o.append(f'<path d="{catmull_rom_svg(p)}" />')
    o.append("</g>")
    o.append('<g fill="none" stroke="#d97706" stroke-width="2.5" stroke-dasharray="4 5" stroke-linecap="round">')
    for p in gold_heliski:
        o.append(f'<path d="{catmull_rom_svg(p)}" />')
    o.append("</g>")

    # FIS Slalom Gates along Olympic Downhill Course (#7)
    olympic_gates = [(825, 182), (802, 215), (784, 252), (772, 288), (762, 322), (735, 392), (695, 452)]
    for idx, (gx, gy) in enumerate(olympic_gates):
        gcol = "#e11d48" if idx % 2 == 0 else "#2563eb"
        dx = -7 if idx % 2 == 0 else 7
        o.append(
            f'<g transform="translate({n(gx + dx)}, {n(gy)})">'
            f'<line x1="0" y1="0" x2="0" y2="-8" stroke="{gcol}" stroke-width="1.4" />'
            f'<rect x="0" y="-8" width="5" height="3.5" fill="{gcol}" />'
            "</g>"
        )

    # Numbered Piste Shields
    for bx, by, bcode, bcol in [
        (430, 195, "A1", "#2563eb"),
        (355, 415, "A2", "#2563eb"),
        (560, 235, "A3", "#2563eb"),
        (182, 265, "A4", "#2563eb"),
        (825, 235, "A5", "#2563eb"),
        (935, 295, "A6", "#2563eb"),
        (485, 255, "R1", "#e11d48"),
        (788, 255, "R2", "#e11d48"),
        (285, 325, "R3", "#e11d48"),
        (632, 315, "R4", "#e11d48"),
        (882, 295, "R5", "#e11d48"),
        (548, 215, "N1", "#0f172a"),
        (125, 275, "N2", "#0f172a"),
        (85, 235, "H1", "#d97706"),
        (395, 128, "H2", "#d97706"),
    ]:
        o += piste_badge(bx, by, bcode, bcol)

    # Elevation Zone Pills (Rendered above pistes for 100% legibility)
    o += [
        '<g font-family="sans-serif" font-size="9" font-weight="700">',
        '<rect x="12" y="42" width="210" height="18" rx="4" fill="#071930" opacity="0.86" stroke="#477eb3" stroke-width="0.6" />',
        '<text x="18" y="54" fill="#e0f2fe">4,800 M · DEATH-ZONE SUMMIT CREST</text>',
        '<rect x="12" y="178" width="218" height="18" rx="4" fill="#071930" opacity="0.86" stroke="#477eb3" stroke-width="0.6" />',
        '<text x="18" y="190" fill="#e0f2fe">4,000 M · HIGH GLACIER AMPHITHEATER</text>',
        '<rect x="12" y="296" width="218" height="18" rx="4" fill="#071930" opacity="0.86" stroke="#477eb3" stroke-width="0.6" />',
        '<text x="18" y="308" fill="#e0f2fe">3,200 M · OBSERVATORY AND CHALET BELT</text>',
        '<rect x="12" y="411" width="184" height="18" rx="4" fill="#071930" opacity="0.86" stroke="#477eb3" stroke-width="0.6" />',
        '<text x="18" y="423" fill="#e0f2fe">2,500 M · SUB-ALPINE TIMBERLINE</text>',
        '<rect x="12" y="564" width="234" height="18" rx="4" fill="#071930" opacity="0.86" stroke="#477eb3" stroke-width="0.6" />',
        '<text x="18" y="576" fill="#e0f2fe">1,900 M · IMPERIAL VALLEY AND MAGLEV BASE</text>',
        "</g>",
    ]

    # 6. Lift Corridors with Steel Lattice Pylons and Animated Gondolas
    o += draw_lift_line("andes-lift-1", [(235, 548), (410, 355), (525, 76)], col="#dfba76", cabin_col="#c95a41", dur="12s", pylons=6)
    o += draw_lift_line("andes-lift-2", [(585, 528), (525, 76)], col="#dfba76", cabin_col="#0b2342", dur="10s", pylons=5)
    o += draw_lift_line("andes-lift-3", [(585, 528), (755, 352), (875, 114)], col="#dfba76", cabin_col="#c95a41", dur="11s", pylons=6)
    o += draw_lift_line("andes-lift-4", [(985, 515), (875, 114)], col="#dfba76", cabin_col="#0b2342", dur="10.5s", pylons=4)
    o += draw_lift_line("andes-lift-5", [(235, 548), (195, 138)], col="#5ce1cf", cabin_col="#165953", dur="11.5s", pylons=4)
    o += draw_lift_line("andes-skybridge", [(195, 138), (525, 76), (875, 114)], col="#5ce1cf", cabin_col="#c95a41", dur="13s", pylons=6)

    # 7. Trans-Andean High-Speed Maglev Viaduct at Valley Base
    o += [
        "<!-- 7. Trans-Andean Maglev Viaduct -->",
        '<g fill="#64748b" stroke="#1e293b" stroke-width="1">',
    ]
    for vx in range(40, 1180, 55):
        o.append(f'<rect x="{vx - 4}" y="642" width="8" height="24" rx="2" />')
        o.append(f'<path d="M{vx + 4},646 Q{vx + 27},636 {vx + 51},646" fill="none" stroke="#475569" stroke-width="2" />')
    o += [
        "</g>",
        '<path d="M0,642 L1200,642" stroke="#0f172a" stroke-width="8" />',
        '<path d="M0,642 L1200,642" stroke="#5ce1cf" stroke-width="2" stroke-dasharray="12 8" class="dash" />',
        "<g>",
        '<animateMotion dur="11s" repeatCount="indefinite" path="M-140,642 L1340,642" />',
        '<rect x="-68" y="-7" width="136" height="12" rx="6" fill="#0b2342" stroke="#dfba76" stroke-width="1.5" />',
        '<path d="M56,-7 L76,-1 L56,5 Z" fill="#c95a41" />',
        '<rect x="-54" y="-4" width="102" height="4" rx="2" fill="#5ce1cf" />',
        "</g>",
    ]

    # 8. Detailed Architectural Landmarks (Unobstructed by Pins!)
    o += [
        "<!-- 8. Architectural Landmarks -->",
        "<!-- Hub 1: Pico Soberano Crown Station (4,850 m) -->",
        '<g transform="translate(525, 72)">',
        '<polygon points="-32,14 32,14 22,26 -22,26" fill="#0f2542" stroke="#dfba76" stroke-width="1.2" />',
        '<rect x="-26" y="2" width="52" height="12" rx="4" fill="#1e3a5f" stroke="#fcedc7" stroke-width="1.4" />',
        '<path d="M-18,2 A18,13 0 0,1 18,2 Z" fill="#38bdf8" stroke="#dfba76" stroke-width="1.4" />',
        '<line x1="0" y1="-11" x2="0" y2="-22" stroke="#fcedc7" stroke-width="1.8" />',
        '<circle cx="0" cy="-22" r="3" fill="#e3735a" class="pulse" />',
        "</g>",
        "<!-- Hub 2: Monte Rosa Sky Observatory (3,200 m) -->",
        '<g transform="translate(875, 112)">',
        '<ellipse cx="0" cy="14" rx="38" ry="9" fill="#0f2542" stroke="#dfba76" stroke-width="1.2" />',
        '<path d="M-26,12 A15,15 0 0,1 4,12 Z" fill="#38bdf8" stroke="#ffffff" stroke-width="1.3" />',
        '<path d="M2,12 A12,12 0 0,1 26,12 Z" fill="#f5c46e" stroke="#ffffff" stroke-width="1.2" />',
        '<ellipse cx="20" cy="18" rx="13" ry="4.5" fill="#2dd4bf" stroke="#fcedc7" stroke-width="1" />',
        "</g>",
        "<!-- Hub 3: Condor Royal Heliport and Glacier Hangar (4,420 m) -->",
        '<g transform="translate(195, 136)">',
        '<ellipse cx="0" cy="10" rx="28" ry="9" fill="#1e293b" stroke="#dfba76" stroke-width="1.5" />',
        '<ellipse cx="0" cy="10" rx="19" ry="6" fill="none" stroke="#5ce1cf" stroke-width="1.2" stroke-dasharray="3 2" />',
        '<path d="M-5,7 L-5,13 M5,7 L5,13 M-5,10 L5,10" stroke="#fcedc7" stroke-width="1.5" />',
        '<g class="bob" transform="translate(-34, -14)">',
        '<ellipse cx="0" cy="0" rx="12" ry="4.5" fill="#0b2342" stroke="#dfba76" stroke-width="1.2" />',
        '<line x1="-16" y1="-5" x2="16" y2="-5" stroke="#ffffff" stroke-width="1.4" />',
        '<line x1="0" y1="-5" x2="0" y2="-2" stroke="#dfba76" stroke-width="1.4" />',
        "</g>",
        "</g>",
        "<!-- Hub 4: Ski Paradise Royal Chalets Hamlet (3,100 m) -->",
        '<g transform="translate(410, 355)">',
        '<ellipse cx="0" cy="12" rx="44" ry="12" fill="#c3def4" opacity="0.7" />',
        '<rect x="-32" y="2" width="18" height="11" rx="1.5" fill="#5c2d0c" stroke="#fcedc7" stroke-width="1" />',
        '<polygon points="-35,2 -23,-8 -11,2" fill="#c95a41" stroke="#ffffff" stroke-width="1.2" />',
        '<rect x="-9" y="-2" width="22" height="14" rx="1.5" fill="#5c2d0c" stroke="#fcedc7" stroke-width="1" />',
        '<polygon points="-12,-2 2,-13 16,-2" fill="#dfba76" stroke="#ffffff" stroke-width="1.2" />',
        '<rect x="16" y="3" width="18" height="11" rx="1.5" fill="#5c2d0c" stroke="#fcedc7" stroke-width="1" />',
        '<polygon points="13,3 25,-6 37,3" fill="#c95a41" stroke="#ffffff" stroke-width="1.2" />',
        "</g>",
        "<!-- Hub 5: Grand Palace Val d'Aurelia 10-Star Complex (2,150 m) -->",
        '<g transform="translate(585, 528)">',
        '<ellipse cx="0" cy="24" rx="62" ry="13" fill="#2dd4bf" stroke="#fcedc7" stroke-width="1.6" />',
        '<rect x="-48" y="-4" width="96" height="24" rx="3" fill="#0b2342" stroke="#dfba76" stroke-width="1.6" />',
        '<rect x="-28" y="-16" width="56" height="14" rx="2" fill="#163b68" stroke="#dfba76" stroke-width="1.4" />',
        '<path d="M-16,-16 A16,14 0 0,1 16,-16 Z" fill="#dfba76" stroke="#ffffff" stroke-width="1.2" />',
        '<polygon points="-48,-4 -36,-14 -24,-4" fill="#c95a41" />',
        '<polygon points="24,-4 36,-14 48,-4" fill="#c95a41" />',
        '<g fill="#fde68a">',
        '<rect x="-40" y="3" width="5" height="9" rx="1" />',
        '<rect x="-30" y="3" width="5" height="9" rx="1" />',
        '<rect x="-20" y="3" width="5" height="9" rx="1" />',
        '<rect x="-8" y="1" width="16" height="14" rx="2" />',
        '<rect x="15" y="3" width="5" height="9" rx="1" />',
        '<rect x="25" y="3" width="5" height="9" rx="1" />',
        '<rect x="35" y="3" width="5" height="9" rx="1" />',
        "</g>",
        "</g>",
        "<!-- Hub 6: Andes Maglev Grand Terminal (1,900 m) -->",
        '<g transform="translate(235, 548)">',
        '<path d="M-40,14 Q0,-14 40,14 Z" fill="#1e3a5f" stroke="#5ce1cf" stroke-width="1.6" />',
        '<rect x="-36" y="14" width="72" height="12" rx="3" fill="#0b2342" stroke="#dfba76" stroke-width="1.4" />',
        '<rect x="-24" y="17" width="48" height="5" rx="2" fill="#5ce1cf" />',
        "</g>",
        "<!-- Hub 7: Aurelia Olympic Downhill Finish Arena (2,450 m) -->",
        '<g transform="translate(755, 352)">',
        '<path d="M-30,8 A30,15 0 0,0 30,8 L22,18 A22,10 0 0,1 -22,18 Z" fill="#1e293b" stroke="#dfba76" stroke-width="1.4" />',
        '<rect x="-18" y="-10" width="36" height="7" rx="2" fill="#e11d48" stroke="#ffffff" stroke-width="1.1" />',
        '<line x1="-15" y1="-3" x2="-15" y2="10" stroke="#ffffff" stroke-width="1.6" />',
        '<line x1="15" y1="-3" x2="15" y2="10" stroke="#ffffff" stroke-width="1.6" />',
        "</g>",
        "<!-- Hub 8: Edelweiss Thermal Grotto Village (2,250 m) -->",
        '<g transform="translate(985, 515)">',
        '<ellipse cx="0" cy="18" rx="38" ry="10" fill="#38bdf8" stroke="#bae6fd" stroke-width="1.4" />',
        '<rect x="-28" y="-2" width="18" height="14" fill="#1e3a5f" stroke="#dfba76" stroke-width="1" />',
        '<polygon points="-30,-2 -19,-12 -8,-2" fill="#c95a41" />',
        '<rect x="-5" y="-14" width="10" height="26" fill="#0b2342" stroke="#dfba76" stroke-width="1" />',
        '<polygon points="-7,-14 0,-26 7,-14" fill="#dfba76" />',
        '<rect x="10" y="0" width="18" height="12" fill="#1e3a5f" stroke="#dfba76" stroke-width="1" />',
        '<polygon points="8,0 19,-9 30,0" fill="#c95a41" />',
        "</g>",
    ]

    # 9. Peak Callout Plaques, Compass Rose & Scale Bar
    o += [
        '<g font-family="sans-serif" font-size="9.5" font-weight="700">',
        '<rect x="440" y="14" width="170" height="22" rx="11" fill="#071930" opacity="0.9" stroke="#dfba76" stroke-width="1.2" />',
        '<text x="525" y="28" fill="#fcedc7" text-anchor="middle">▲ PICO SOBERANO · 4,850 M</text>',
        '<rect x="115" y="76" width="160" height="22" rx="11" fill="#071930" opacity="0.9" stroke="#5ce1cf" stroke-width="1.2" />',
        '<text x="195" y="90" fill="#ffffff" text-anchor="middle">▲ CONDOR PEAK · 4,420 M</text>',
        '<rect x="795" y="54" width="160" height="22" rx="11" fill="#071930" opacity="0.9" stroke="#dfba76" stroke-width="1.2" />',
        '<text x="875" y="68" fill="#fcedc7" text-anchor="middle">▲ MONTE ROSA · 3,200 M</text>',
        "</g>",
        '<g transform="translate(1142, 54)">',
        '<circle r="24" fill="#071930" opacity="0.86" stroke="#dfba76" stroke-width="1.2" />',
        '<polygon points="0,-18 4,-4 0,-7 -4,-4" fill="#e3735a" />',
        '<polygon points="0,18 4,4 0,7 -4,4" fill="#93c5fd" />',
        '<polygon points="-18,0 -4,-4 -7,0 -4,4" fill="#93c5fd" />',
        '<polygon points="18,0 4,-4 7,0 4,4" fill="#93c5fd" />',
        '<text y="-28" fill="#fcedc7" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle">N</text>',
        "</g>",
        '<g transform="translate(940, 678)">',
        '<rect x="0" y="-14" width="236" height="22" rx="6" fill="#071930" opacity="0.88" stroke="#6ba4d9" stroke-width="1" />',
        '<line x1="14" y1="-3" x2="94" y2="-3" stroke="#fcedc7" stroke-width="2" />',
        '<line x1="14" y1="-7" x2="14" y2="1" stroke="#fcedc7" stroke-width="1.5" />',
        '<line x1="54" y1="-6" x2="54" y2="0" stroke="#fcedc7" stroke-width="1.2" />',
        '<line x1="94" y1="-7" x2="94" y2="1" stroke="#fcedc7" stroke-width="1.5" />',
        '<text x="106" y="0" fill="#e2e8f0" font-family="sans-serif" font-size="8.5" font-weight="700">0 — 5 KM · 880 KM PISTES</text>',
        "</g>",
    ]

    # 10. 8 Interactive Hotspot Pins with Leader Lines (Offset so buildings are clearly visible)
    andes_spots = [
        (1, 525, 72, 42, -12, True),
        (2, 875, 112, 46, -8, False),
        (3, 195, 136, 42, -8, False),
        (4, 410, 355, -48, -16, False),
        (5, 585, 528, 64, -18, False),
        (6, 235, 548, -54, -14, False),
        (7, 755, 352, 44, -14, False),
        (8, 985, 515, -48, -16, False),
    ]
    o.append("<!-- 10. Interactive Hotspot Pins -->")
    for idx, sx, sy, dx, dy, act in andes_spots:
        o += hotspot_pin(idx, sx, sy, pin_dx=dx, pin_dy=dy, active=act)

    o.append("</svg>")
    return "\n".join(o)


# ==============================================================================
# MAP 2: HAITI HIGHLAND GLACIER (1200 x 700)
# ==============================================================================
def build_haiti_svg() -> str:
    o = [
        '<svg xmlns="http://www.w3.org/2000/svg" class="ill" viewBox="0 0 1200 700" role="img" aria-label="Detailed 3D panoramic Sea-to-Summit ski map of Haiti Highland Glacier rising from the Caribbean Sea">',
        "<defs>",
        '<linearGradient id="haiti-sky" x1="0%" y1="0%" x2="0%" y2="100%">',
        '<stop offset="0%" stop-color="#071f3d" />',
        '<stop offset="48%" stop-color="#1d5f9e" />',
        '<stop offset="82%" stop-color="#68b5dd" />',
        '<stop offset="100%" stop-color="#fae5b8" />',
        "</linearGradient>",
        '<linearGradient id="haiti-snow-lit" x1="0%" y1="0%" x2="25%" y2="100%">',
        '<stop offset="0%" stop-color="#ffffff" />',
        '<stop offset="55%" stop-color="#e8f4fe" />',
        '<stop offset="100%" stop-color="#a3ccec" />',
        "</linearGradient>",
        '<linearGradient id="haiti-face-shadow" x1="0%" y1="0%" x2="100%" y2="100%">',
        '<stop offset="0%" stop-color="#2b639e" />',
        '<stop offset="60%" stop-color="#173e6e" />',
        '<stop offset="100%" stop-color="#0b213d" />',
        "</linearGradient>",
        '<linearGradient id="haiti-jungle" x1="0%" y1="0%" x2="0%" y2="100%">',
        '<stop offset="0%" stop-color="#1f7a5c" />',
        '<stop offset="55%" stop-color="#145942" />',
        '<stop offset="100%" stop-color="#0c3b2b" />',
        "</linearGradient>",
        '<linearGradient id="haiti-carib-sea" x1="0%" y1="0%" x2="0%" y2="100%">',
        '<stop offset="0%" stop-color="#38bdf8" />',
        '<stop offset="35%" stop-color="#0ea5e9" />',
        '<stop offset="72%" stop-color="#0369a1" />',
        '<stop offset="100%" stop-color="#082f49" />',
        "</linearGradient>",
        "</defs>",
        "<!-- 1. Tropical-to-Alpine Sky Backdrop -->",
        '<rect width="1200" height="700" fill="#1d5f9e" />',
        '<rect width="1200" height="440" fill="url(#haiti-sky)" />',
        "<!-- Warm Caribbean Sun -->",
        '<g transform="translate(155, 118)">',
        '<circle r="76" fill="#fef3c7" opacity="0.24" />',
        '<circle r="46" fill="#fde68a" opacity="0.4" />',
        '<circle r="26" fill="#fffbeb" opacity="0.96" />',
        "</g>",
    ]

    # Continuous Island Massif Silhouette (Zero gaps between peaks and jungle)
    island_base = [
        (65, 535), (175, 315), (335, 178), (445, 225), (565, 76),
        (735, 220), (890, 118), (1045, 275), (1155, 535)
    ]
    o.append("<!-- 2. Solid Haiti Island Mountain Core -->")
    o.append(f'<path d="{poly(island_base)}" fill="#1d4d82" />')

    # 3D Multi-Faceted Peaks of the Haiti Highland Massif
    o += draw_3d_peak(
        peak_xy=(335, 178),
        left_base=(125, 455),
        right_base=(515, 445),
        center_base=(330, 455),
        lit_fill="url(#haiti-snow-lit)",
        shade_fill="url(#haiti-face-shadow)",
        seed=14,
    )
    o += draw_3d_peak(
        peak_xy=(890, 118),
        left_base=(670, 455),
        right_base=(1135, 465),
        center_base=(895, 460),
        lit_fill="url(#haiti-snow-lit)",
        shade_fill="url(#haiti-face-shadow)",
        seed=21,
    )
    o += draw_3d_peak(
        peak_xy=(565, 76),
        left_base=(295, 460),
        right_base=(835, 460),
        center_base=(575, 465),
        lit_fill="url(#haiti-snow-lit)",
        shade_fill="url(#haiti-face-shadow)",
        seed=28,
    )

    # Continuous Cryo-Cooled Snow Apron down to 1,200 m Snowline (y = 425)
    o += [
        '<path d="M145,428 Q350,388 575,412 Q800,388 1095,432 L1035,280 L890,118 L735,220 L565,76 L445,225 L335,178 L205,315 Z" fill="url(#haiti-snow-lit)" opacity="0.45" />',
        "<!-- Sub-Surface Cryo-Grid 3.0 Titanium Cooling Matrix Blueprint under Mid-Mountain -->",
        '<g stroke="#0ea5e9" stroke-width="1.1" stroke-dasharray="4 3" opacity="0.5" fill="none">',
        '<path d="M535,265 L695,265 M525,280 L705,280 M515,295 L715,295 M505,310 L725,310" />',
        '<path d="M555,255 L525,320 M595,255 L575,320 M635,255 L635,320 M675,255 L695,320" />',
        "</g>",
    ]

    # 3. Emerald Tropical Cloud Forest Belt & Waterfalls (1,200 m down to Coast)
    jungle_poly = [
        (55, 538), (145, 428), (265, 408), (385, 424), (505, 410),
        (625, 428), (755, 412), (885, 428), (1010, 415), (1095, 432),
        (1175, 542)
    ]
    o += [
        "<!-- 3. Emerald Tropical Cloud Forest Belt -->",
        f'<path d="{poly(jungle_poly)}" fill="url(#haiti-jungle)" />',
        '<path d="M95,492 Q260,452 410,480 T710,475 T990,485 L1155,538 L75,538 Z" fill="#0f4c3a" opacity="0.72" />',
        "<!-- 1,200 m Snowline Mist Border -->",
        '<path d="M145,428 Q265,408 385,424 T625,428 T885,428 T1095,432" fill="none" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity="0.65" />',
        "<!-- Glacial Meltwater Waterfalls Plunging through the Cloud Forest -->",
        '<path d="M465,420 C460,455 448,485 442,524" fill="none" stroke="#bae6fd" stroke-width="4.5" stroke-linecap="round" opacity="0.9" />',
        '<ellipse cx="442" cy="525" rx="16" ry="5" fill="#38bdf8" opacity="0.85" />',
        '<path d="M795,420 C802,458 812,488 818,526" fill="none" stroke="#bae6fd" stroke-width="4" stroke-linecap="round" opacity="0.88" />',
        '<ellipse cx="818" cy="527" rx="14" ry="4.5" fill="#38bdf8" opacity="0.85" />',
    ]

    o += draw_conifer_forest([
        (275, 388, 16, 45, 16, 0.85, 11),
        (495, 390, 18, 50, 16, 0.85, 12),
        (765, 390, 18, 50, 16, 0.85, 13),
        (985, 395, 16, 45, 16, 0.85, 14),
    ])

    # 4. Golden Coral Sand Beach, Turquoise Lagoon, Barrier Reef & Coral Bay Marina
    beach_poly = [
        (0, 518), (165, 524), (350, 536), (570, 528), (795, 538), (1020, 526), (1200, 534),
        (1200, 585), (0, 585)
    ]
    sea_poly = [
        (0, 544), (175, 550), (365, 560), (575, 552), (805, 562), (1030, 550), (1200, 558),
        (1200, 700), (0, 700)
    ]
    o += [
        "<!-- 4. Golden Coral Beach and 28°C Caribbean Sea -->",
        f'<path d="{poly(beach_poly)}" fill="#f3dfb6" />',
        f'<path d="{poly(sea_poly)}" fill="url(#haiti-carib-sea)" />',
        '<path d="M0,552 Q280,570 585,560 T1200,566 L1200,618 Q880,605 585,615 T0,608 Z" fill="#2dd4bf" opacity="0.4" />',
        '<path d="M0,546 Q175,552 365,562 T805,564 T1200,560" fill="none" stroke="#ffffff" stroke-width="2.4" stroke-dasharray="14 6" opacity="0.88" />',
        '<path d="M60,648 Q380,628 680,642 T1140,634" fill="none" stroke="#5eead4" stroke-width="9" stroke-linecap="round" opacity="0.32" />',
        '<path d="M60,648 Q380,628 680,642 T1140,634" fill="none" stroke="#ffffff" stroke-width="1.6" stroke-dasharray="6 8" opacity="0.7" />',
    ]

    for px, py, psc, ptilt in [
        (85, 536, 0.95, -1), (125, 539, 1.05, 1), (310, 548, 0.9, 1),
        (355, 550, 1.0, -1), (515, 544, 0.95, 1), (645, 546, 0.9, -1),
        (865, 552, 1.0, 1), (915, 550, 0.9, -1), (1095, 544, 1.05, -1),
    ]:
        o += draw_palm_tree(px, py, scale=psc, tilt=ptilt)

    # Elevation Guidelines & Labels
    o += [
        '<g stroke="#e0f2fe" stroke-width="0.7" stroke-dasharray="4 7" opacity="0.32">',
        '<line x1="0" y1="85" x2="1200" y2="85" />',
        '<line x1="0" y1="245" x2="1200" y2="245" />',
        '<line x1="0" y1="415" x2="1200" y2="415" />',
        '<line x1="0" y1="540" x2="1200" y2="540" />',
        "</g>",
        '<g font-family="sans-serif" font-size="9" font-weight="700">',
        '<rect x="12" y="66" width="236" height="18" rx="4" fill="#071930" opacity="0.78" />',
        '<text x="18" y="78" fill="#ffffff">3,180 M · CRYO-GLACIER SUMMIT ZONE (-4°C)</text>',
        '<rect x="12" y="226" width="242" height="18" rx="4" fill="#071930" opacity="0.78" />',
        '<text x="18" y="238" fill="#ffffff">2,100 M · SUB-SURFACE CRYO-GRID 3.0 SLOPES</text>',
        '<rect x="12" y="396" width="246" height="18" rx="4" fill="#071930" opacity="0.78" />',
        '<text x="18" y="408" fill="#ffffff">1,200 M · CLOUD FOREST SNOWLINE TRANSITION</text>',
        '<rect x="12" y="494" width="268" height="18" rx="4" fill="#071930" opacity="0.78" />',
        '<text x="18" y="506" fill="#ffffff">0 M · CORAL BAY MARINA AND 28°C CARIBBEAN REEF</text>',
        "</g>",
    ]

    # 5. Haiti Highland Glacier Braided Piste Network
    haiti_azure = [
        [(565, 86), (505, 145), (445, 205), (430, 255), (380, 315), (405, 368), (355, 420)],
        [(565, 86), (595, 155), (560, 225), (615, 285), (665, 355), (710, 425)],
        [(890, 128), (835, 188), (785, 245), (745, 325), (710, 425)],
        [(335, 185), (295, 245), (335, 310), (305, 368), (355, 420)],
        [(890, 128), (935, 195), (895, 255), (825, 305), (765, 365), (710, 425)],
    ]
    haiti_crimson = [
        [(565, 86), (535, 165), (505, 245), (465, 335), (355, 420)],
        [(565, 86), (635, 165), (615, 285), (575, 355), (710, 425)],
        [(890, 128), (865, 215), (825, 305), (855, 368), (710, 425)],
        [(335, 185), (385, 225), (430, 255), (485, 335), (355, 420)],
    ]
    haiti_obsidian = [
        [(565, 86), (568, 175), (545, 265), (515, 345), (355, 420)],
        [(890, 128), (965, 205), (995, 295), (935, 365), (710, 425)],
    ]

    o.append('<g fill="none" stroke="#ffffff" stroke-width="5.5" stroke-linecap="round" opacity="0.68">')
    for p in haiti_azure + haiti_crimson:
        o.append(f'<path d="{catmull_rom_svg(p)}" />')
    o.append("</g>")
    o.append('<g fill="none" stroke="#0284c7" stroke-width="3.0" stroke-linecap="round">')
    for p in haiti_azure:
        o.append(f'<path d="{catmull_rom_svg(p)}" />')
    o.append("</g>")
    o.append('<g fill="none" stroke="#e11d48" stroke-width="2.8" stroke-linecap="round">')
    for p in haiti_crimson:
        o.append(f'<path d="{catmull_rom_svg(p)}" />')
    o.append("</g>")
    o.append('<g fill="none" stroke="#0f172a" stroke-width="2.6" stroke-dasharray="7 3" stroke-linecap="round">')
    for p in haiti_obsidian:
        o.append(f'<path d="{catmull_rom_svg(p)}" />')
    o.append("</g>")

    for bx, by, bcode, bcol in [
        (465, 185, "H1", "#0284c7"),
        (392, 335, "H2", "#0284c7"),
        (582, 195, "H3", "#0284c7"),
        (805, 225, "H4", "#0284c7"),
        (518, 215, "R1", "#e11d48"),
        (628, 225, "R2", "#e11d48"),
        (872, 215, "R3", "#e11d48"),
        (555, 175, "N1", "#0f172a"),
        (975, 235, "N2", "#0f172a"),
    ]:
        o += piste_badge(bx, by, bcode, bcol)

    # 6. 18-Minute Sea-to-Summit Vacuum Funicular & Aerial Lift Network
    o += [
        '<path d="M215,575 L355,420 L565,86" fill="none" stroke="#0f172a" stroke-width="6.5" opacity="0.65" />',
        '<path id="haiti-funicular" d="M215,575 L355,420 L565,86" fill="none" stroke="#dfba76" stroke-width="3.0" stroke-dasharray="8 5" />',
        "<g>",
        '<animateMotion dur="9s" repeatCount="indefinite" path="M215,575 L355,420 L565,86" />',
        '<rect x="-14" y="-6" width="28" height="11" rx="5.5" fill="#c95a41" stroke="#fcedc7" stroke-width="1.4" />',
        '<rect x="-8" y="-3" width="16" height="4.5" rx="2" fill="#fef08a" />',
        "</g>",
        "<g>",
        '<animateMotion dur="9s" begin="-4.5s" repeatCount="indefinite" path="M565,86 L355,420 L215,575" />',
        '<rect x="-14" y="-6" width="28" height="11" rx="5.5" fill="#0b2342" stroke="#5ce1cf" stroke-width="1.4" />',
        '<rect x="-8" y="-3" width="16" height="4.5" rx="2" fill="#5ce1cf" />',
        "</g>",
    ]
    o += draw_lift_line("haiti-skylink", [(565, 86), (890, 128)], col="#5ce1cf", cabin_col="#c95a41", dur="9.5s", pylons=3)
    o += draw_lift_line("haiti-founders-lift", [(710, 425), (615, 285), (565, 86)], col="#dfba76", cabin_col="#0b2342", dur="10.5s", pylons=4)
    o += draw_lift_line("haiti-east-lift", [(710, 425), (825, 305), (890, 128)], col="#dfba76", cabin_col="#c95a41", dur="10s", pylons=4)

    # 7. Detailed Architectural Landmarks
    o += [
        "<!-- Hub 1: Haiti Glacier Crown 7-Star Resort (3,180 m) -->",
        '<g transform="translate(565, 76)">',
        '<polygon points="-34,16 34,16 24,28 -24,28" fill="#0f2542" stroke="#dfba76" stroke-width="1.2" />',
        '<rect x="-28" y="2" width="56" height="14" rx="7" fill="#1e3a5f" stroke="#fcedc7" stroke-width="1.4" />',
        '<rect x="18" y="6" width="26" height="6" rx="3" fill="#38bdf8" stroke="#ffffff" stroke-width="1.1" />',
        '<path d="M-16,2 A16,12 0 0,1 16,2 Z" fill="#dfba76" />',
        "</g>",
        "<!-- Hub 2: Cryo-Dome Snowsphere (2,940 m) -->",
        '<g transform="translate(890, 118)">',
        '<ellipse cx="0" cy="14" rx="44" ry="11" fill="#0f2542" stroke="#5ce1cf" stroke-width="1.4" />',
        '<path d="M-38,14 A38,32 0 0,1 38,14 Z" fill="#38bdf8" fill-opacity="0.55" stroke="#ffffff" stroke-width="1.5" />',
        '<path d="M-22,14 A22,30 0 0,1 22,14 M-38,14 H38 M0,-18 V14" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.8" />',
        "</g>",
        "<!-- Hub 3: Caribbean Horizon Terrace (2,200 m) -->",
        '<g transform="translate(430, 255)">',
        '<ellipse cx="0" cy="8" rx="28" ry="9" fill="#0b2342" stroke="#dfba76" stroke-width="1.4" />',
        '<ellipse cx="0" cy="6" rx="22" ry="6" fill="#fde68a" />',
        "</g>",
        "<!-- Hub 4: Cryo-Grid 3.0 Command Vault (2,050 m) -->",
        '<g transform="translate(615, 285)">',
        '<rect x="-24" y="-6" width="48" height="18" rx="4" fill="#0f2542" stroke="#5ce1cf" stroke-width="1.5" />',
        '<circle cx="-12" cy="3" r="4" fill="#2dd4bf" class="pulse" />',
        '<circle cx="0" cy="3" r="4" fill="#2dd4bf" />',
        '<circle cx="12" cy="3" r="4" fill="#2dd4bf" />',
        "</g>",
        "<!-- Hub 5: Royal Halfpipe and Snowpark (1,850 m) -->",
        '<g transform="translate(825, 305)">',
        '<path d="M-26,-4 L-14,14 L18,14 L28,-4 Z" fill="#bae6fd" stroke="#0284c7" stroke-width="1.5" />',
        '<path d="M-20,-2 Q0,10 22,-2" fill="none" stroke="#ffffff" stroke-width="2.5" />',
        "</g>",
        "<!-- Hub 6: Cloud Forest Transition Lodge (1,200 m) -->",
        '<g transform="translate(355, 420)">',
        '<rect x="-26" y="-4" width="52" height="16" rx="3" fill="#14532d" stroke="#dfba76" stroke-width="1.4" />',
        '<rect x="-18" y="0" width="36" height="8" rx="2" fill="#7dd3fc" />',
        "</g>",
        "<!-- Hub 7: 2011 Founders Pavilion (1,150 m) -->",
        '<g transform="translate(710, 425)">',
        '<rect x="-26" y="0" width="52" height="16" rx="2" fill="#fef3c7" stroke="#b45309" stroke-width="1.3" />',
        '<polygon points="-30,0 0,-15 30,0" fill="#dfba76" stroke="#0b2342" stroke-width="1.2" />',
        "</g>",
        "<!-- Hub 8: Coral Bay Sea-to-Summit Superyacht Marina (0 m) -->",
        '<g transform="translate(215, 575)">',
        '<path d="M-85,10 L65,10 L85,38 L-75,38 Z" fill="#0c4a6e" stroke="#dfba76" stroke-width="1.8" />',
        '<g stroke="#fcedc7" stroke-width="2">',
        '<line x1="-55" y1="10" x2="-55" y2="32" />',
        '<line x1="-20" y1="10" x2="-20" y2="32" />',
        '<line x1="15" y1="10" x2="15" y2="32" />',
        '<line x1="50" y1="10" x2="50" y2="32" />',
        "</g>",
        '<g fill="#ffffff" stroke="#0284c7" stroke-width="1">',
        '<polygon points="-48,16 -28,16 -31,28 -45,28" />',
        '<polygon points="-12,16 8,16 5,28 -9,28" />',
        '<polygon points="22,16 42,16 39,28 25,28" />',
        "</g>",
        '<path d="M-24,10 A24,16 0 0,1 24,10 Z" fill="#0b2342" stroke="#5ce1cf" stroke-width="1.6" />',
        "</g>",
        "<!-- Animated Sovereign Superyacht and Sailing Regatta in Coral Bay -->",
        '<g class="bob" transform="translate(520, 625)">',
        '<polygon points="-42,4 42,4 30,16 -34,16" fill="#ffffff" stroke="#0b2342" stroke-width="1.5" />',
        '<rect x="-22" y="-5" width="38" height="9" rx="2" fill="#e0f2fe" stroke="#0284c7" stroke-width="1" />',
        '<rect x="-10" y="-11" width="20" height="6" rx="1.5" fill="#ffffff" />',
        '<line x1="2" y1="-18" x2="2" y2="-11" stroke="#dfba76" stroke-width="1.8" />',
        "</g>",
        '<g class="bob" transform="translate(885, 615)">',
        '<polygon points="-20,6 20,6 14,13 -16,13" fill="#ffffff" stroke="#0b2342" stroke-width="1.2" />',
        '<polygon points="0,-24 0,4 -14,4" fill="#fef3c7" />',
        '<polygon points="2,-22 2,4 15,4" fill="#f8fafc" />',
        "</g>",
    ]

    # 8. Peak Callout Plaques & Compass Rose
    o += [
        '<g font-family="sans-serif" font-size="9.5" font-weight="700">',
        '<rect x="475" y="22" width="180" height="22" rx="11" fill="#071930" opacity="0.9" stroke="#dfba76" stroke-width="1.2" />',
        '<text x="565" y="36" fill="#fcedc7" text-anchor="middle">▲ GLACIER CROWN · 3,180 M</text>',
        '<rect x="805" y="60" width="170" height="22" rx="11" fill="#071930" opacity="0.9" stroke="#5ce1cf" stroke-width="1.2" />',
        '<text x="890" y="74" fill="#ffffff" text-anchor="middle">▲ CRYO-DOME PEAK · 2,940 M</text>',
        "</g>",
        '<g transform="translate(1142, 54)">',
        '<circle r="24" fill="#071930" opacity="0.86" stroke="#dfba76" stroke-width="1.2" />',
        '<polygon points="0,-18 4,-4 0,-7 -4,-4" fill="#e3735a" />',
        '<polygon points="0,18 4,4 0,7 -4,4" fill="#93c5fd" />',
        '<polygon points="-18,0 -4,-4 -7,0 -4,4" fill="#93c5fd" />',
        '<polygon points="18,0 4,-4 7,0 4,4" fill="#93c5fd" />',
        '<text y="-28" fill="#fcedc7" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle">N</text>',
        "</g>",
        '<g transform="translate(920, 678)">',
        '<rect x="0" y="-14" width="256" height="22" rx="6" fill="#071930" opacity="0.88" stroke="#5ce1cf" stroke-width="1" />',
        '<text x="128" y="0" fill="#e2e8f0" font-family="sans-serif" font-size="8.5" font-weight="700" text-anchor="middle">18 MIN SEA-TO-SUMMIT · 370 KM PISTES</text>',
        "</g>",
    ]

    # 9. 8 Interactive Hotspot Pins with Offset Leader Lines
    haiti_spots = [
        (1, 565, 76, -54, -8, True),
        (2, 890, 118, 56, -12, False),
        (3, 430, 255, -46, -14, False),
        (4, 615, 285, 46, -14, False),
        (5, 825, 305, 48, -14, False),
        (6, 355, 420, -48, -16, False),
        (7, 710, 425, 48, -16, False),
        (8, 215, 575, -62, -16, False),
    ]
    o.append("<!-- 9. Interactive Hotspot Pins -->")
    for idx, sx, sy, dx, dy, act in haiti_spots:
        o += hotspot_pin(idx, sx, sy, pin_dx=dx, pin_dy=dy, active=act)

    o.append("</svg>")
    return "\n".join(o)


# ==============================================================================
# LOCALIZATION & HTML INJECTION
# ==============================================================================
EN_TO_HU = [
    (
        'aria-label="Detailed 3D panoramic ski trail map of the Grand Andes Massif in Waikiki"',
        'aria-label="A Magas-Andok Masszívum részletes 3D panoráma sítérképe"',
    ),
    (
        'aria-label="Detailed 3D panoramic Sea-to-Summit ski map of Haiti Highland Glacier rising from the Caribbean Sea"',
        'aria-label="A Karib-tengerből kiemelkedő Haiti Gleccserfennsík részletes 3D panoráma sítérképe"',
    ),
    (">4,800 M · DEATH-ZONE SUMMIT CREST<", ">4800 M · MAGASHEGYI CSÚCSGERINC<"),
    (">4,000 M · HIGH GLACIER AMPHITHEATER<", ">4000 M · FELSŐ GLECCSERKATLAN<"),
    (">3,200 M · OBSERVATORY AND CHALET BELT<", ">3200 M · OBSZERVATÓRIUM ÉS CHALET ÖVEZET<"),
    (">2,500 M · SUB-ALPINE TIMBERLINE<", ">2500 M · HAVASI ERDŐHATÁR<"),
    (">1,900 M · IMPERIAL VALLEY AND MAGLEV BASE<", ">1900 M · BIRODALMI VÖLGY ÉS MAGLEV BÁZIS<"),
    (">▲ PICO SOBERANO · 4,850 M<", ">▲ PICO SOBERANO · 4850 M<"),
    (">▲ CONDOR PEAK · 4,420 M<", ">▲ CONDOR-CSÚCS · 4420 M<"),
    (">▲ MONTE ROSA · 3,200 M<", ">▲ MONTE ROSA · 3200 M<"),
    (">0 — 5 KM · 880 KM PISTES<", ">0 — 5 KM · 880 KM SÍPÁLYA<"),
    (">3,180 M · CRYO-GLACIER SUMMIT ZONE (-4°C)<", ">3180 M · KRIOGLECCSER CSÚCSZÓNA (-4°C)<"),
    (">2,100 M · SUB-SURFACE CRYO-GRID 3.0 SLOPES<", ">2100 M · FELSZÍN ALATTI CRYO-GRID 3.0 LEJTŐK<"),
    (">1,200 M · CLOUD FOREST SNOWLINE TRANSITION<", ">1200 M · KÖDERDŐ ÉS HÓHATÁR ÁTMENET<"),
    (">0 M · CORAL BAY MARINA AND 28°C CARIBBEAN REEF<", ">0 M · CORAL BAY KIKÖTŐ ÉS 28°C KARIBI ZÁTONY<"),
    (">▲ GLACIER CROWN · 3,180 M<", ">▲ GLECCSERKORONA · 3180 M<"),
    (">▲ CRYO-DOME PEAK · 2,940 M<", ">▲ KRIO-KUPOLA CSÚCS · 2940 M<"),
    (">18 MIN SEA-TO-SUMMIT · 370 KM PISTES<", ">18 PERC TENGERTŐL A CSÚCSIG · 370 KM PÁLYA<"),
]


def localize_svg(raw_svg: str, lang: str) -> str:
    try:
        ET.fromstring(raw_svg)
    except ET.ParseError as exc:
        sys.exit(f"Error: generated SVG is invalid XML: {exc}")

    inline_svg = re.sub(r'\s+xmlns="http://www\.w3\.org/2000/svg"', "", raw_svg, count=1)
    if lang == "hu":
        for en_s, hu_s in EN_TO_HU:
            inline_svg = inline_svg.replace(en_s, hu_s)
    return inline_svg


PANEL_SVG_RE_TEMPLATE = (
    r'(<div class="island-panel[^"]*" id="{panel_id}"[^>]*>.*?<div class="island-map-canvas">\s*)'
    r"<svg\b[^>]*>.*?</svg>"
    r"(\s*</div>)"
)


def update_ski_pages(andes_raw: str, haiti_raw: str) -> None:
    try:
        from build_pages import format_and_remove_empty_lines
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from build_pages import format_and_remove_empty_lines

    for lang in ("en", "hu"):
        html_path = ROOT / lang / "ski-paradise.html"
        html = html_path.read_text(encoding="utf-8")

        html = re.sub(r'data-spot="(?:andes|haiti)-(\d+)"', r'data-spot="\1"', html)

        for panel_id, raw_svg in (("panel-andes", andes_raw), ("panel-haiti", haiti_raw)):
            pattern = re.compile(PANEL_SVG_RE_TEMPLATE.format(panel_id=panel_id), re.S)
            match = pattern.search(html)
            if not match:
                sys.exit(f"Error: could not find <svg> inside #{panel_id} in {html_path}")
            svg_inline = localize_svg(raw_svg, lang)
            html = html[: match.start()] + f"{match.group(1)}{svg_inline}{match.group(2)}" + html[match.end() :]

        cleaned = format_and_remove_empty_lines(html)
        html_path.write_text(cleaned, encoding="utf-8")
        print(f"Updated {html_path.relative_to(ROOT)} with realistic Andes and Haiti SVG maps")


def main() -> None:
    SKI_ICONS_DIR.mkdir(parents=True, exist_ok=True)
    andes_svg = build_andes_svg()
    haiti_svg = build_haiti_svg()

    ANDES_SVG_PATH.write_text(andes_svg + "\n", encoding="utf-8")
    HAITI_SVG_PATH.write_text(haiti_svg + "\n", encoding="utf-8")
    print(f"Generated {ANDES_SVG_PATH.relative_to(ROOT)} ({len(andes_svg) / 1024:.1f} KB)")
    print(f"Generated {HAITI_SVG_PATH.relative_to(ROOT)} ({len(haiti_svg) / 1024:.1f} KB)")

    update_ski_pages(andes_svg, haiti_svg)


if __name__ == "__main__":
    main()
