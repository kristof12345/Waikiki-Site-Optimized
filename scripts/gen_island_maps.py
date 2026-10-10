#!/usr/bin/env python3
"""Regenerate the three artificial-island SVG maps on en/hu infrastructure pages.

Design principles (matching Dubai artificial islands):
- Palm Island: real palm tree crown (16 curved fronds fanning from the upper trunk),
  with trunk and roads seamlessly connected.
- World Islands: archipelago of multiple distinct islands (larger continent cores + smaller islands)
  forming an instantly recognizable world map with zero overlapping islands.
- Chameleon Islands: archipelago of multiple distinct islands (larger body/head/limbs + smaller stepping stones)
  forming an instantly recognizable chameleon silhouette (spiral tail, arched back, casque, turret eye, tongue)
  with zero overlapping islands.
"""
import math
import re
import sys

ROOT = "/Volumes/Samsung X5 SSD/Projektek/Site"


def n(v):
    s = f"{v:.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    return "0" if s == "-0" else s


def pt(p):
    return f"{n(p[0])},{n(p[1])}"


def poly_path(points, close=True):
    d = "M" + " L".join(pt(p) for p in points)
    return d + (" Z" if close else "")


def smooth_island(cx, cy, rx, ry, rot=0, seed=1, n_pts=10):
    """Generate an organic rounded dredged-island polygon with natural beach curve."""
    rad = math.radians(rot)
    cr, sr = math.cos(rad), math.sin(rad)
    pts = []
    for i in range(n_pts):
        ang = 2 * math.pi * i / n_pts
        rf = 1.0 + 0.08 * math.sin(2 * ang + seed) + 0.05 * math.cos(3 * ang + seed * 2)
        lx = rx * math.cos(ang) * rf
        ly = ry * math.sin(ang) * rf
        gx = cx + lx * cr - ly * sr
        gy = cy + lx * sr + ly * cr
        pts.append((gx, gy))
    d = [f"M{n(pts[0][0])},{n(pts[0][1])}"]
    for i in range(n_pts):
        p0 = pts[(i - 1) % n_pts]
        p1 = pts[i]
        p2 = pts[(i + 1) % n_pts]
        p3 = pts[(i + 2) % n_pts]
        cp1x = p1[0] + (p2[0] - p0[0]) / 6.0
        cp1y = p1[1] + (p2[1] - p0[1]) / 6.0
        cp2x = p2[0] - (p3[0] - p1[0]) / 6.0
        cp2y = p2[1] - (p3[1] - p1[1]) / 6.0
        d.append(f"C{n(cp1x)},{n(cp1y)} {n(cp2x)},{n(cp2y)} {n(p2[0])},{n(p2[1])}")
    d.append("Z")
    return " ".join(d)


def hotspot(i, x, y, color, r=11):
    return [
        f'<g class="map-hotspot" data-spot="{i}" transform="translate({n(x)}, {n(y)})">',
        f'<circle class="hotspot-pulse" r="{r + 5}" fill="{color}" opacity="0.6" />',
        f'<circle class="hotspot-core" r="{r}" />',
        f"<text>{i}</text>",
        "</g>",
    ]


L = {
    "en": {
        "palm_aria": "Detailed map of Palm Island infrastructure: curved palm leaves fanning from crown, central trunk and protective crescent",
        "world_aria": "Detailed map of World Islands infrastructure: archipelago of multiple distinct islands arranged into the seven continents",
        "cham_aria": "Detailed map of Chameleon Islands infrastructure: archipelago of multiple distinct islands forming a giant chameleon silhouette",
        "crescent": "Crescent Barrier",
        "mainland": "Nova Aurelia Mainland",
        "hotel": "Hotel Khalifa",
        "west_fronds": "West Fronds",
        "east_fronds": "East Fronds",
        "perimeter": "Perimeter Storm Defense Reef",
        "west_gate": "Pacific Gate",
        "east_gate": "North Atlantic Gate",
        "pavilion": "Grand Central Pavilion",
        "marina": "Spiral Tail Marina",
        "villas": "Paradise Islands Villas",
    },
    "hu": {
        "palm_aria": "A Pálma-sziget részletes infrastruktúra-térképe: koronából kinyíló ívelt pálmalevelek, központi törzs és védő félhold",
        "world_aria": "A Világ-szigetek részletes infrastruktúra-térképe: több különálló szigetből álló kontinens alakú szigetcsoport",
        "cham_aria": "A Kaméleon-szigetek részletes infrastruktúra-térképe: több különálló szigetből álló óriás kaméleon alakú szigetcsoport",
        "crescent": "Félhold védőgát",
        "mainland": "Nova Aurelia szárazföld",
        "hotel": "Hotel Khalifa",
        "west_fronds": "Nyugati levelek",
        "east_fronds": "Keleti levelek",
        "perimeter": "Külső Védelmi Zátony és Vihargát",
        "west_gate": "Csendes-óceáni Kapu",
        "east_gate": "Észak-Atlanti Kapu",
        "pavilion": "Központi Nagypavilon",
        "marina": "Spirál Farok Jachtkikötő",
        "villas": "Paradise Islands Villák",
    },
}


# ==========================================================================
# 1. PALM ISLAND (REAL PALM TREE CROWN WITH CURVED FRONDS & CONNECTED ROADS)
# ==========================================================================
def palm_svg(t):
    cx, cy = 600, 350
    R_CRES = 315
    o = []
    o.append(f'<svg class="ill" viewBox="0 0 1200 700" role="img" aria-label="{t["palm_aria"]}">')
    o += [
        "<defs>",
        '<linearGradient id="palm-sea" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" stop-color="#0c3461" />',
        '<stop offset="40%" stop-color="#185694" />',
        '<stop offset="100%" stop-color="#2c7ebd" />',
        "</linearGradient>",
        '<radialGradient id="lagoon-glow" cx="50%" cy="50%" r="50%">',
        '<stop offset="0%" stop-color="#73c7ea" stop-opacity="0.5" />',
        '<stop offset="100%" stop-color="#19558e" stop-opacity="0" />',
        "</radialGradient>",
        '<filter id="glow-gold" x="-20%" y="-20%" width="140%" height="140%">',
        '<feGaussianBlur stdDeviation="3" result="blur" />',
        '<feComposite in="SourceGraphic" in2="blur" operator="over" />',
        "</filter>",
        "</defs>",
        "<!-- Deep Ocean Water Base -->",
        '<rect width="1200" height="700" fill="url(#palm-sea)" />',
        "<!-- Shallow Lagoon inside the Crescent -->",
        f'<circle cx="{cx}" cy="{cy}" r="310" fill="url(#lagoon-glow)" />',
        "<!-- Bathymetric and Navigational Grid Lines -->",
        '<g stroke="rgba(255,255,255,0.08)" stroke-width="1" stroke-dasharray="3 6" fill="none">',
        f'<circle cx="{cx}" cy="{cy}" r="200" />',
        f'<circle cx="{cx}" cy="{cy}" r="380" />',
        f'<circle cx="{cx}" cy="{cy}" r="470" />',
        '<line x1="150" y1="350" x2="1050" y2="350" />',
        "</g>",
    ]

    # Crescent Breakwater with two navigation channels (East and West)
    def arc_d(deg1, deg2, r):
        a1, a2 = math.radians(deg1), math.radians(deg2)
        p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
        p2 = (cx + r * math.cos(a2), cy + r * math.sin(a2))
        return f"M{pt(p1)} A{r},{r} 0 0 1 {pt(p2)}"

    west_cres = arc_d(150, 264, R_CRES)
    east_cres = arc_d(276, 390, R_CRES)
    cres_all = f"{west_cres} {east_cres}"

    outer_r = R_CRES + 34
    outer_west = arc_d(146, 264, outer_r)
    outer_east = arc_d(276, 394, outer_r)

    o += [
        "<!-- Outer Crescent Breakwater with Living Coral Reef -->",
        f'<path d="{outer_west} {outer_east}" fill="none" stroke="#2ba29e" stroke-width="2.5" stroke-dasharray="8 6" opacity="0.65" />',
        f'<path d="{cres_all}" fill="none" stroke="#2ba29e" stroke-width="40" stroke-linecap="round" opacity="0.45" />',
        f'<path class="map-frond-edge" d="{cres_all}" stroke-width="26" />',
        f'<path class="map-frond" d="{cres_all}" stroke-width="22" />',
        f'<path class="map-frond-core" d="{cres_all}" />',
        f'<path class="map-frond-villas" d="{cres_all}" />',
    ]

    # 16 CURVED PALM LEAVES (8 West, 8 East)
    # Fronds radiate from the upper crown (y=425 down to y=215), making it a true palm tree crown!
    # Bases start right on trunk centerline (x=600), ensuring 100% connected sand and roads.
    palm_frond_paths = []
    frond_roads = []
    frond_villas = []

    tips = [
        (360, 455),  # 0: lowest frond curves out and slightly downwards
        (335, 400),  # 1
        (325, 345),  # 2: sweeps outward horizontally
        (330, 290),  # 3
        (350, 235),  # 4: sweeps upward
        (385, 185),  # 5
        (440, 145),  # 6
        (515, 115),  # 7: top frond curves up towards crown
    ]
    y_bases = [425 - k * 30 for k in range(8)]
    w_mid_spot = (340, 290)
    e_mid_spot = (860, 290)

    for k in range(8):
        y0 = y_bases[k]
        tx_l, ty_l = tips[k]
        cp1_lx = 520
        cp1_ly = y0 + 10 - k * 3
        cp2_lx = tx_l + 45
        cp2_ly = ty_l + 25 + k * 2

        tx_r = 2 * cx - tx_l
        ty_r = ty_l
        cp1_rx = 2 * cx - cp1_lx
        cp1_ry = cp1_ly
        cp2_rx = 2 * cx - cp2_lx
        cp2_ry = cp2_ly

        d_l = f"M600,{y0} C{cp1_lx},{cp1_ly} {cp2_lx},{cp2_ly} {tx_l},{ty_l}"
        d_r = f"M600,{y0} C{cp1_rx},{cp1_ry} {cp2_rx},{cp2_ry} {tx_r},{ty_r}"

        palm_frond_paths.append(d_l)
        palm_frond_paths.append(d_r)
        frond_roads.append(d_l)
        frond_roads.append(d_r)
        frond_villas.append(d_l)
        frond_villas.append(d_r)

        if k == 3:
            w_mid_spot = (tx_l + 35, ty_l + 8)
            e_mid_spot = (2 * cx - w_mid_spot[0], w_mid_spot[1])

    fronds_d = " ".join(palm_frond_paths)
    roads_d = " ".join(frond_roads)
    villas_d = " ".join(frond_villas)

    o += [
        "<!-- 16 CURVED PALM FRONDS (Seamlessly connected to trunk) -->",
        f'<path class="map-frond-edge" d="{fronds_d}" stroke-width="24" />',
        f'<path class="map-frond" d="{fronds_d}" stroke-width="20" />',
        f'<path class="map-frond-core" d="{fronds_d}" stroke-width="5" />',
        f'<path class="map-frond-villas" d="{villas_d}" stroke-width="3" stroke-dasharray="0.1 7" />',
    ]

    # The Central Trunk (Base and Spine)
    o += [
        "<!-- The Central Trunk: wide stem base and slender upper crown spine -->",
        "<!-- Sand mass of trunk uniting with the fronds -->",
        '<path class="map-sand" d="M570,640 L570,425 L582,215 Q600,200 618,215 L630,425 L630,640 Z" />',
        '<rect x="586" y="215" width="28" height="420" rx="8" class="map-greenery" />',
        "<!-- Gateway Marina Lobe (West) and Golden Mile Lobe (East) on the lower trunk -->",
        '<path class="map-sand" d="M572,550 L532,550 C514,550 506,562 506,578 L506,598 C506,612 516,618 532,618 L572,618 Z" />',
        '<path class="map-sand" d="M628,550 L668,550 C686,550 694,562 694,578 L694,598 C694,612 684,618 668,618 L628,618 Z" />',
        '<rect x="518" y="560" width="44" height="48" rx="6" class="map-sea-deep" />',
        '<g stroke="#ffffff" stroke-width="1.6">',
        '<line x1="524" y1="572" x2="556" y2="572" />',
        '<line x1="524" y1="584" x2="556" y2="584" />',
        '<line x1="524" y1="596" x2="556" y2="596" />',
        "</g>",
        "<!-- Solar Canopy and Seawater Cooling Hub -->",
        '<g fill="#1f4f7a" stroke="#9fd3f5" stroke-width="0.8">',
    ]
    for r in range(3):
        for c in range(3):
            o.append(f'<rect x="{646 + c * 14}" y="{562 + r * 14}" width="11" height="11" rx="1.5" />')
    o.append("</g>")

    # Connected Road Network: Trunk boulevard branching into each leaf!
    o += [
        "<!-- Connected Road Network (Mainland to Trunk, branching into each leaf) -->",
        '<path class="map-road" d="M592,664 L592,425 M608,664 L608,425" />',
        f'<path class="map-road" d="{roads_d}" stroke-width="2.2" />',
        "<!-- Sub-Sea Tunnel Link to the Crescent -->",
        '<path d="M600,205 L600,48" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4 4" fill="none" opacity="0.85" />',
        "<!-- The Elevated Monorail Line along the central spine -->",
        '<path class="map-rail" d="M600,690 L600,205" />',
    ]
    for y in (664, 580, 425, 315, 210):
        o.append(f'<circle cx="600" cy="{y}" r="5" fill="#c29a57" stroke="#ffffff" stroke-width="1.8" />')

    # Hotel platform at crescent apex
    hx, hy = cx, cy - R_CRES
    wx, wy = cx + 80, cy - R_CRES + 6
    o += [
        "<!-- Crescent Apex Crown Platform (Hotel Khalifa) -->",
        f'<ellipse cx="{hx}" cy="{hy}" rx="54" ry="24" class="map-sand" />',
        f'<ellipse cx="{hx}" cy="{hy}" rx="42" ry="16" class="map-greenery" />',
        f'<g transform="translate({hx}, {hy})">',
        '<ellipse cx="0" cy="2" rx="22" ry="9" fill="#002244" opacity="0.75" />',
        '<path d="M-14,4 L0,-22 L14,4 Z" fill="#c29a57" filter="url(#glow-gold)" />',
        '<path d="M-6,4 L0,-18 L6,4 Z" fill="#ffffff" />',
        '<circle cx="0" cy="-22" r="3" fill="#e3735a" class="twinkle" />',
        "</g>",
        "<!-- Palm Islands Waterpark on the Crescent -->",
        f'<g transform="translate({n(wx)}, {n(wy)})">',
        '<ellipse cx="0" cy="0" rx="30" ry="17" class="map-sand" />',
        '<path d="M-16,-5 C-5,-13 14,-10 17,0 C19,9 5,14 -7,10 Z" fill="#38bdf8" stroke="#ffffff" stroke-width="1.2" />',
        '<path d="M-2,-2 C8,-5 9,6 0,7" fill="none" stroke="#7dd3fc" stroke-width="2.2" />',
        "</g>",
    ]

    # Mainland Nova Aurelia Coastline (Bottom)
    o += [
        "<!-- Mainland Nova Aurelia Coastline (Bottom) -->",
        '<path class="map-sand" d="M0,650 Q300,634 600,638 Q900,634 1200,650 L1200,700 L0,700 Z" />',
        '<rect x="0" y="664" width="1200" height="36" class="map-urban" />',
        '<line x1="0" y1="664" x2="1200" y2="664" stroke="#ffffff" stroke-width="2.5" />',
        "<!-- Causeway Bridge connecting mainland to trunk -->",
        '<path class="map-road" d="M585,664 L585,618 M615,664 L615,618" />',
    ]

    # Navigation beacons at the crescent tips
    p1 = (cx + R_CRES * math.cos(math.radians(150)), cy + R_CRES * math.sin(math.radians(150)))
    p2 = (cx + R_CRES * math.cos(math.radians(390)), cy + R_CRES * math.sin(math.radians(390)))
    o += [
        "<!-- Marine Navigation Beacons at the Crescent Passages -->",
        f'<circle cx="{n(p1[0])}" cy="{n(p1[1])}" r="4.5" fill="#22c55e" class="twinkle" />',
        f'<circle cx="{n(p2[0])}" cy="{n(p2[1])}" r="4.5" fill="#ef4444" class="twinkle" />',
        "<!-- Map Geographic Labels -->",
        '<g class="map-label-group">',
        f'<text class="map-label-text" x="260" y="104">{t["crescent"]}</text>',
        f'<text class="map-label-text" x="600" y="690">{t["mainland"]}</text>',
        f'<text class="map-label-text" x="600" y="84">{t["hotel"]}</text>',
        f'<text class="map-label-text" x="300" y="470">{t["west_fronds"]}</text>',
        f'<text class="map-label-text" x="900" y="470">{t["east_fronds"]}</text>',
        "</g>",
    ]

    # Hotspots
    a4 = math.radians(205)
    spots = [
        (1, hx, hy, "#c29a57", "Hotel Khalifa"),
        (2, wx, wy, "#38bdf8", "Waterpark"),
        (3, 600, 480, "#c29a57", "Elevated Monorail Spine"),
        (4, cx + R_CRES * math.cos(a4), cy + R_CRES * math.sin(a4), "#2ba29e", "Crescent Barrier Reef"),
        (5, w_mid_spot[0], w_mid_spot[1], "#c29a57", "West Fronds Estates"),
        (6, e_mid_spot[0], e_mid_spot[1], "#c29a57", "East Fronds Villas"),
        (7, 540, 582, "#38bdf8", "Gateway Marina"),
        (8, 660, 582, "#22c55e", "Solar and Seawater Cooling Hub"),
    ]
    o.append("<!-- 8 INTERACTIVE HOTSPOT PINS -->")
    for i, x, y, col, name in spots:
        o.append(f"<!-- Hotspot {i}: {name} -->")
        o += hotspot(i, x, y, col)
    o.append("</svg>")
    return o


# ==========================================================================
# 2. WORLD ISLANDS (RECOGNIZABLE CONTINENTS: MAJOR CORES + SATELLITE ISLES)
# ==========================================================================
WORLD_ISLES = [
    # --- NORTH AMERICA (Recognizable triangular continent + Arctic & Caribbean) ---
    {"name": "Canada Arctic Core", "cx": 355, "cy": 140, "rx": 55, "ry": 20, "rot": -5, "green": True},
    {"name": "Alaska Peninsula", "cx": 260, "cy": 165, "rx": 28, "ry": 18, "rot": -15, "green": True},
    {"name": "Greenland Isle", "cx": 465, "cy": 120, "rx": 24, "ry": 28, "rot": 15, "sand_light": True},
    {"name": "US Pacific Coast", "cx": 295, "cy": 235, "rx": 26, "ry": 30, "rot": 25},
    {"name": "North America Mainland Hub", "cx": 385, "cy": 225, "rx": 44, "ry": 26, "rot": -5, "hub": "na", "green": True},
    {"name": "Florida and Bahamas", "cx": 445, "cy": 295, "rx": 16, "ry": 12, "rot": -30},
    {"name": "Mexico and Central America", "cx": 320, "cy": 315, "rx": 26, "ry": 15, "rot": 25},

    # --- SOUTH AMERICA (Recognizable tapering continent shape) ---
    {"name": "Amazon Basin Core", "cx": 430, "cy": 380, "rx": 48, "ry": 28, "rot": -10, "green": True},
    {"name": "Brazil Atlantic Coast", "cx": 475, "cy": 445, "rx": 30, "ry": 24, "rot": 15, "green": True},
    {"name": "Andes Spine", "cx": 370, "cy": 445, "rx": 16, "ry": 34, "rot": 15},
    {"name": "Southern Cone Argentina", "cx": 420, "cy": 520, "rx": 24, "ry": 34, "rot": 10},
    {"name": "Tierra del Fuego Isle", "cx": 408, "cy": 575, "rx": 14, "ry": 10, "rot": 10},

    # --- EUROPE (Recognizable UK, Scandinavia, Mediterranean) ---
    {"name": "Great Britain", "cx": 530, "cy": 190, "rx": 15, "ry": 22, "rot": -15},
    {"name": "Ireland Isle", "cx": 490, "cy": 198, "rx": 11, "ry": 14, "rot": 10},
    {"name": "Scandinavia Peninsula", "cx": 585, "cy": 140, "rx": 20, "ry": 30, "rot": 20, "green": True},
    {"name": "European Summit Hub", "cx": 565, "cy": 225, "rx": 34, "ry": 20, "rot": 5, "hub": "eu", "green": True},
    {"name": "Iberia Isle", "cx": 515, "cy": 268, "rx": 18, "ry": 15, "rot": -10},
    {"name": "Italy Peninsula Boot", "cx": 565, "cy": 275, "rx": 12, "ry": 18, "rot": 35},
    {"name": "Greece and Aegean", "cx": 605, "cy": 270, "rx": 16, "ry": 15, "rot": 15},
    {"name": "Eastern Europe Plains", "cx": 635, "cy": 210, "rx": 26, "ry": 20, "rot": 10},

    # --- AFRICA (Recognizable bulge, horn and southern cape) ---
    {"name": "Sahara North Core", "cx": 565, "cy": 340, "rx": 52, "ry": 24, "rot": 0},
    {"name": "West Africa Bulge", "cx": 505, "cy": 395, "rx": 24, "ry": 16, "rot": -15},
    {"name": "Congo Rainforest Core", "cx": 585, "cy": 420, "rx": 40, "ry": 26, "rot": 5, "green": True},
    {"name": "Horn of Africa", "cx": 650, "cy": 390, "rx": 20, "ry": 22, "rot": 30},
    {"name": "Southern Africa Cape", "cx": 595, "cy": 500, "rx": 34, "ry": 26, "rot": 5},
    {"name": "Madagascar Isle", "cx": 670, "cy": 475, "rx": 14, "ry": 26, "rot": -20, "green": True},

    # --- ASIA (Recognizable vast landmass, Arabia, India, East Asia, Japan) ---
    {"name": "Siberia West Core", "cx": 700, "cy": 140, "rx": 55, "ry": 22, "rot": 5},
    {"name": "Siberia East Core", "cx": 815, "cy": 135, "rx": 50, "ry": 22, "rot": -10},
    {"name": "Kamchatka Peninsula", "cx": 885, "cy": 150, "rx": 14, "ry": 20, "rot": 30},
    {"name": "Central Asia Steppe", "cx": 710, "cy": 215, "rx": 34, "ry": 18, "rot": 0},
    {"name": "Arabian Peninsula", "cx": 675, "cy": 325, "rx": 24, "ry": 20, "rot": -25},
    {"name": "Indian Subcontinent", "cx": 755, "cy": 310, "rx": 28, "ry": 32, "rot": 15, "green": True},
    {"name": "Sri Lanka Isle", "cx": 770, "cy": 365, "rx": 9, "ry": 11, "rot": 10},
    {"name": "Asian Innovation Hub Core", "cx": 820, "cy": 235, "rx": 46, "ry": 28, "rot": 5, "hub": "asia", "green": True},
    {"name": "Korea Peninsula", "cx": 880, "cy": 230, "rx": 11, "ry": 16, "rot": 20},
    {"name": "Japan Hokkaido", "cx": 915, "cy": 200, "rx": 13, "ry": 13, "rot": -20},
    {"name": "Japan Honshu Arc", "cx": 915, "cy": 240, "rx": 13, "ry": 24, "rot": 35},
    {"name": "Indochina Peninsula", "cx": 840, "cy": 320, "rx": 22, "ry": 20, "rot": 15},
    {"name": "Indonesia Archipelago", "cx": 860, "cy": 380, "rx": 34, "ry": 15, "rot": -20, "green": True},

    # --- OCEANIA (Recognizable Australia continent + NZ) ---
    {"name": "Australia Mainland Hub", "cx": 920, "cy": 475, "rx": 48, "ry": 32, "rot": 0, "hub": "oc", "green": True},
    {"name": "Tasmania Isle", "cx": 945, "cy": 535, "rx": 11, "ry": 9, "rot": 0},
    {"name": "New Zealand North", "cx": 1015, "cy": 505, "rx": 11, "ry": 16, "rot": -35},
    {"name": "New Zealand South", "cx": 1005, "cy": 542, "rx": 11, "ry": 18, "rot": -30},

    # --- ANTARCTICA (Recognizable south polar arc) ---
    {"name": "Antarctica Ice 1", "cx": 470, "cy": 600, "rx": 22, "ry": 11, "sand_light": True},
    {"name": "Antarctica Ice 2", "cx": 530, "cy": 595, "rx": 24, "ry": 12, "sand_light": True},
    {"name": "Antarctic Dome Hub", "cx": 595, "cy": 592, "rx": 26, "ry": 13, "hub": "an", "sand_light": True},
    {"name": "Antarctica Ice 4", "cx": 660, "cy": 595, "rx": 24, "ry": 12, "sand_light": True},
    {"name": "Antarctica Ice 5", "cx": 720, "cy": 600, "rx": 22, "ry": 11, "sand_light": True},
]


def world_svg(t):
    ecx, ecy, erx, ery = 600, 345, 540, 305
    o = []
    o.append(f'<svg class="ill" viewBox="0 0 1200 700" role="img" aria-label="{t["world_aria"]}">')
    o += [
        "<defs>",
        '<linearGradient id="world-sea" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" stop-color="#0a2a4e" />',
        '<stop offset="50%" stop-color="#144d85" />',
        '<stop offset="100%" stop-color="#236ca9" />',
        "</linearGradient>",
        '<radialGradient id="world-lagoon" cx="50%" cy="50%" r="50%">',
        '<stop offset="0%" stop-color="#69c3eb" stop-opacity="0.45" />',
        '<stop offset="85%" stop-color="#124b82" stop-opacity="0.12" />',
        '<stop offset="100%" stop-color="#0a2a4e" stop-opacity="0" />',
        "</radialGradient>",
        "</defs>",
        "<!-- Deep Water Base -->",
        '<rect width="1200" height="700" fill="url(#world-sea)" />',
        "<!-- Lagoon Shallows -->",
        f'<ellipse cx="{ecx}" cy="{ecy}" rx="{erx}" ry="{ery}" fill="url(#world-lagoon)" />',
        "<!-- Wave Break Line -->",
        f'<ellipse cx="{ecx}" cy="{ecy}" rx="{erx + 25}" ry="{ery + 23}" fill="none" stroke="rgba(255,255,255,0.14)" stroke-dasharray="6 8" />',
    ]

    # Oval flood defense breakwater (4 storm gates: N, S, E, W)
    arcs = []
    gap = 5
    for start in (0, 90, 180, 270):
        a = math.radians(start + gap)
        b = math.radians(start + 90 - gap)
        pa = (ecx + erx * math.cos(a), ecy + ery * math.sin(a))
        pb = (ecx + erx * math.cos(b), ecy + ery * math.sin(b))
        arcs.append(f"M{pt(pa)} A{erx},{ery} 0 0 1 {pt(pb)}")
    ring = " ".join(arcs)
    o += [
        "<!-- Outer Oval Flood Defense Breakwater (4 Storm Gates: N, S, E, W) -->",
        f'<path d="{ring}" fill="none" stroke="#2ba29e" stroke-width="26" stroke-linecap="round" opacity="0.45" />',
        f'<path class="map-frond-edge" d="{ring}" stroke-width="15" />',
        f'<path class="map-frond" d="{ring}" stroke-width="12.5" />',
    ]

    # Gate beacons
    o.append('<g class="twinkle">')
    for start in (0, 90, 180, 270):
        for s, col in ((-1, "#ef4444"), (1, "#22c55e")):
            a = math.radians(start + s * gap)
            o.append(f'<circle cx="{n(ecx + erx * math.cos(a))}" cy="{n(ecy + ery * math.sin(a))}" r="3.5" fill="{col}" />')
    o.append("</g>")

    # MULTIPLE DISTINCT NON-OVERLAPPING ISLANDS
    o.append("<!-- RECOGNIZABLE WORLD CONTINENTS (ZERO OVERLAPS, CLEAR WATERWAYS) -->")
    o.append('<g id="world-islands-group">')
    for i, isle in enumerate(WORLD_ISLES):
        cls = "map-sand-light" if isle.get("sand_light") else "map-sand"
        d = smooth_island(isle["cx"], isle["cy"], isle["rx"], isle["ry"], rot=isle.get("rot", 0), seed=i + 1)
        o.append(f'<!-- {isle["name"]} -->')
        o.append(f'<path class="{cls}" d="{d}" />')
        if isle.get("green"):
            d_grn = smooth_island(isle["cx"], isle["cy"], isle["rx"] * 0.65, isle["ry"] * 0.65, rot=isle.get("rot", 0), seed=i + 10)
            o.append(f'<path class="map-greenery" d="{d_grn}" />')
    o.append("</g>")

    # Hub architectures on main continental islands
    us_hub = (385, 225)
    eu_hub = (565, 225)
    asia_hub = (820, 235)
    oc_hub = (920, 475)
    an_hub = (595, 592)

    o += [
        "<!-- Continental Hub Pavilions and Features -->",
        f'<rect x="{us_hub[0] - 16}" y="{us_hub[1] - 9}" width="32" height="18" rx="3" class="map-urban" />',
        f'<rect x="{eu_hub[0] - 14}" y="{eu_hub[1] - 8}" width="28" height="16" rx="3" class="map-urban" />',
        f'<rect x="{asia_hub[0] - 18}" y="{asia_hub[1] - 9}" width="36" height="18" rx="3" class="map-urban" />',
        f'<ellipse cx="{an_hub[0]}" cy="{an_hub[1]}" rx="24" ry="9" fill="#38bdf8" stroke="#ffffff" stroke-width="1.6" opacity="0.85" />',
    ]

    # Inter-island footbridges connecting close satellite pairs
    bridges = [
        ((355, 140), (385, 225)),  # Canada to US
        ((430, 380), (475, 445)),  # Amazon to Brazil East
        ((530, 190), (565, 225)),  # UK to Western Europe
        ((565, 340), (585, 420)),  # Sahara to Congo
        ((700, 140), (820, 235)),  # Siberia to China
        ((840, 320), (860, 380)),  # Indochina to Indonesia
    ]
    o.append("<!-- Inter-Island Arched Footbridges -->")
    o.append('<g stroke="#ffffff" stroke-width="2.2" stroke-linecap="round">')
    for b1, b2 in bridges:
        o.append(f'<line x1="{b1[0]}" y1="{b1[1]}" x2="{b2[0]}" y2="{b2[1]}" />')
    o.append("</g>")

    # Continental Teleferic (Sky-Way Aerial Cable Car) connecting major continental hubs
    tele_path = [us_hub, eu_hub, asia_hub, oc_hub]
    o += [
        "<!-- Continental Teleferic (Sky-Way Aerial Cable Car) -->",
        f'<path class="map-cableway" d="{poly_path(tele_path, close=False)}" />',
    ]
    for p in tele_path:
        o.append(f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="5" fill="#f43f5e" stroke="#ffffff" stroke-width="1.8" />')

    # Water-Taxi routes connecting through the storm gates
    o += [
        "<!-- Electric Water Taxi Marine Corridors from the Storm Gates -->",
        '<g class="map-ferry">',
        f'<path d="M{ecx},{ecy + ery} L595,605 L595,530" />',
        '<path d="M565,340 Q515,310 445,295" />',
        f'<path d="M{ecx - erx},{ecy} C140,345 220,300 295,235" />',
        f'<path d="M{ecx + erx},{ecy} C1060,380 980,440 920,475" />',
        f'<path d="M{ecx},{ecy - ery} L600,120" />',
        "</g>",
    ]

    # Submerged suites in coral lagoon (Indian Ocean)
    sub_suites = (690, 410)
    o += ["<!-- Submerged Reef Observation Suites -->"]
    for ddx, ddy in ((-12, -10), (14, 12)):
        o += [
            f'<g transform="translate({sub_suites[0] + ddx}, {sub_suites[1] + ddy})">',
            '<circle cx="0" cy="0" r="7" fill="#0284c7" stroke="#38bdf8" stroke-width="2" />',
            '<circle cx="0" cy="0" r="2.6" fill="#ffffff" class="twinkle" />',
            "</g>",
        ]

    # Geographic Map Labels
    o += [
        "<!-- Geographic Map Labels -->",
        '<g class="map-label-group">',
        f'<text class="map-label-text" x="600" y="690">{t["perimeter"]}</text>',
        f'<text class="map-label-text" x="130" y="328">{t["west_gate"]}</text>',
        f'<text class="map-label-text" x="1060" y="328">{t["east_gate"]}</text>',
        "</g>",
    ]

    # 8 Interactive Hotspots
    tele_mid = ((eu_hub[0] + asia_hub[0]) / 2, (eu_hub[1] + asia_hub[1]) / 2)
    spots = [
        (1, us_hub[0], us_hub[1], "#f43f5e", "NA Casino and Theme Park"),
        (2, eu_hub[0], eu_hub[1], "#c29a57", "European Summit and Diplomatic Pavilions"),
        (3, asia_hub[0], asia_hub[1], "#38bdf8", "Asian Innovation Hub"),
        (4, tele_mid[0], tele_mid[1], "#f43f5e", "Continental Teleferic"),
        (5, sub_suites[0], sub_suites[1], "#0284c7", "Submerged Reef Suites"),
        (6, an_hub[0], an_hub[1], "#38bdf8", "Antarctic Climate Dome"),
        (7, oc_hub[0], oc_hub[1], "#22c55e", "Oceania Dolphin Sanctuary"),
        (8, ecx, ecy - ery, "#2ba29e", "Flood Barrier Storm Gates"),
    ]
    o.append("<!-- 8 INTERACTIVE HOTSPOT PINS -->")
    for i, x, y, col, name in spots:
        o.append(f"<!-- Hotspot {i}: {name} -->")
        o += hotspot(i, x, y, col)
    o.append("</svg>")
    return o


# ==========================================================================
# 3. CHAMELEON ISLANDS (RECOGNIZABLE CHAMELEON: ZERO OVERLAPS)
# ==========================================================================
CHAM_ISLES = [
    # --- 1. SPIRAL TAIL HARBOR (9 distinct curving islands in an inward circular spiral) ---
    {"name": "Tail Base Isle", "cx": 430, "cy": 375, "rx": 24, "ry": 15, "rot": 25},
    {"name": "Tail Arc 1", "cx": 385, "cy": 420, "rx": 22, "ry": 14, "rot": 45},
    {"name": "Tail Arc 2", "cx": 330, "cy": 455, "rx": 22, "ry": 14, "rot": 15},
    {"name": "Tail South Curl", "cx": 270, "cy": 460, "rx": 22, "ry": 14, "rot": -20},
    {"name": "Tail Outer West 1", "cx": 220, "cy": 430, "rx": 20, "ry": 14, "rot": -55},
    {"name": "Tail Outer West 2", "cx": 205, "cy": 375, "rx": 18, "ry": 14, "rot": -85},
    {"name": "Tail Inner West", "cx": 225, "cy": 325, "rx": 18, "ry": 13, "rot": -125},
    {"name": "Tail Inner Top", "cx": 275, "cy": 305, "rx": 16, "ry": 13, "rot": -165},
    {"name": "Tail Spiral Marina Isle", "cx": 315, "cy": 335, "rx": 16, "ry": 13, "rot": 130, "hub": "marina"},

    # --- 2. MAIN BODY (Arched Back, Dorsal Ridge, Grand Pavilion) ---
    {"name": "Dorsal Crest Isle 1", "cx": 490, "cy": 285, "rx": 24, "ry": 16, "rot": -30, "dorsal": True},
    {"name": "Dorsal Crest Isle 2", "cx": 550, "cy": 250, "rx": 28, "ry": 17, "rot": -15, "dorsal": True},
    {"name": "Dorsal Crest Isle 3", "cx": 620, "cy": 235, "rx": 30, "ry": 18, "rot": 0, "dorsal": True},
    {"name": "Dorsal Crest Isle 4", "cx": 690, "cy": 245, "rx": 28, "ry": 17, "rot": 15, "dorsal": True},
    {"name": "Torso Posterior Isle", "cx": 495, "cy": 340, "rx": 32, "ry": 24, "rot": 15, "green": True},
    {"name": "Grand Pavilion Master Core", "cx": 585, "cy": 305, "rx": 40, "ry": 28, "rot": 0, "hub": "pavilion", "green": True},
    {"name": "Torso Anterior Shoulder", "cx": 675, "cy": 310, "rx": 36, "ry": 26, "rot": -5, "green": True},
    {"name": "Abdomen Metro Hub Isle", "cx": 585, "cy": 375, "rx": 42, "ry": 22, "rot": 0, "hub": "metro"},

    # --- 3. HEAD, CASQUE & REVOLVING TURRET EYE ---
    {"name": "Head Core Isle", "cx": 765, "cy": 270, "rx": 36, "ry": 26, "rot": -10, "green": True},
    {"name": "Casque Helmet Spire", "cx": 760, "cy": 195, "rx": 18, "ry": 28, "rot": -10, "casque": True},
    {"name": "Turret Eye Dome Isle", "cx": 800, "cy": 230, "rx": 18, "ry": 18, "rot": 0, "hub": "eye"},
    {"name": "Snout and Mouth Isle", "cx": 840, "cy": 285, "rx": 24, "ry": 16, "rot": 10},

    # --- 4. FOUR DISTINCT LIMBS & CLAWS ---
    {"name": "Hindlimb West Thigh", "cx": 445, "cy": 435, "rx": 18, "ry": 14, "rot": 35},
    {"name": "Floating Eco-District Foot", "cx": 400, "cy": 510, "rx": 24, "ry": 18, "rot": 25, "hub": "eco"},
    {"name": "Hindlimb East Thigh", "cx": 530, "cy": 445, "rx": 18, "ry": 14, "rot": 15},
    {"name": "Marine Power Hub Foot", "cx": 505, "cy": 525, "rx": 24, "ry": 18, "rot": 10, "hub": "power"},
    {"name": "Forelimb West Shoulder", "cx": 710, "cy": 390, "rx": 18, "ry": 14, "rot": -20},
    {"name": "Marine Biology Foot", "cx": 725, "cy": 480, "rx": 24, "ry": 18, "rot": -15, "hub": "bio"},
    {"name": "Forelimb East Shoulder", "cx": 795, "cy": 370, "rx": 18, "ry": 14, "rot": -35},
    {"name": "Youth Innovation Foot", "cx": 840, "cy": 450, "rx": 24, "ry": 18, "rot": -25, "hub": "youth"},

    # --- 5. PROJECTING TONGUE ARCHIPELAGO (Stepping stones to Paradise Villas) ---
    {"name": "Tongue Stepping Isle 1", "cx": 895, "cy": 295, "rx": 14, "ry": 10, "rot": 12},
    {"name": "Tongue Stepping Isle 2", "cx": 935, "cy": 310, "rx": 14, "ry": 10, "rot": 15},
    {"name": "Tongue Stepping Isle 3", "cx": 980, "cy": 330, "rx": 15, "ry": 11, "rot": 18},
    {"name": "Tongue Stepping Isle 4", "cx": 1030, "cy": 355, "rx": 16, "ry": 12, "rot": 22},
    {"name": "Tongue Stepping Isle 5", "cx": 1085, "cy": 385, "rx": 18, "ry": 13, "rot": 25},
    {"name": "Paradise Atoll Lagoon Tip", "cx": 1145, "cy": 425, "rx": 26, "ry": 24, "rot": 15, "hub": "villas"},
]


def chameleon_svg(t):
    o = []
    o.append(f'<svg class="ill" viewBox="0 0 1200 700" role="img" aria-label="{t["cham_aria"]}">')
    o += [
        "<defs>",
        '<linearGradient id="cham-sea" x1="0" y1="0" x2="0" y2="1">',
        '<stop offset="0%" stop-color="#093153" />',
        '<stop offset="45%" stop-color="#114e7a" />',
        '<stop offset="100%" stop-color="#1d739d" />',
        "</linearGradient>",
        '<radialGradient id="cham-glow" cx="50%" cy="50%" r="50%">',
        '<stop offset="0%" stop-color="#4ade80" stop-opacity="0.32" />',
        '<stop offset="60%" stop-color="#38bdf8" stop-opacity="0.2" />',
        '<stop offset="100%" stop-color="#093153" stop-opacity="0" />',
        "</radialGradient>",
        '<filter id="glass-glow" x="-20%" y="-20%" width="140%" height="140%">',
        '<feGaussianBlur stdDeviation="4" result="blur" />',
        '<feComposite in="SourceGraphic" in2="blur" operator="over" />',
        "</filter>",
        "</defs>",
        "<!-- Coastal Bay Water Background -->",
        '<rect width="1200" height="700" fill="url(#cham-sea)" />',
        "<!-- Biological Eco-Glow in Lagoon -->",
        '<ellipse cx="640" cy="360" rx="520" ry="290" fill="url(#cham-glow)" />',
        "<!-- Outer Protective Bio-Dyke Reef Buffer -->",
        '<ellipse cx="650" cy="365" rx="535" ry="275" class="map-reef" opacity="0.45" stroke-dasharray="10 8" stroke-width="2.5" fill="none" />',
        "<!-- Mainland Nova Aurelia Coastline (Bottom) -->",
        '<path class="map-sand" d="M0,656 Q300,642 600,646 Q900,642 1200,656 L1200,700 L0,700 Z" />',
        '<rect x="0" y="670" width="1200" height="30" class="map-urban" />',
        '<line x1="0" y1="670" x2="1200" y2="670" stroke="#ffffff" stroke-width="2.5" />',
    ]

    # MULTIPLE DISTINCT CHAMELEON ISLANDS (ZERO OVERLAPS)
    o.append("<!-- 35 DISTINCT ISLANDS FORMING AN ICONIC CHAMELEON (ZERO OVERLAPS) -->")
    o.append('<g id="chameleon-islands-group">')
    for i, isle in enumerate(CHAM_ISLES):
        d = smooth_island(isle["cx"], isle["cy"], isle["rx"], isle["ry"], rot=isle.get("rot", 0), seed=i + 3)
        o.append(f'<!-- {isle["name"]} -->')
        o.append(f'<path class="map-sand" d="{d}" />')
        if isle.get("green"):
            d_grn = smooth_island(isle["cx"], isle["cy"], isle["rx"] * 0.65, isle["ry"] * 0.65, rot=isle.get("rot", 0), seed=i + 20)
            o.append(f'<path class="map-greenery" d="{d_grn}" />')
    o.append("</g>")

    # Dorsal solar spikes along the back islands
    o.append("<!-- Dorsal Ridge Crest Spikes on the Back Islands -->")
    o.append('<g class="map-reef" opacity="0.85">')
    for isle in CHAM_ISLES:
        if isle.get("dorsal"):
            x, y = isle["cx"], isle["cy"] - isle["ry"] + 2
            o.append(f'<polygon points="{x - 8},{y + 3} {x},{y - 12} {x + 8},{y + 3}" />')
    o.append("</g>")

    # Casque Peak Spire on Head
    o += [
        "<!-- Golden Casque Crest Spire -->",
        '<path class="map-reef" d="M752,175 L760,135 L768,175 Z" />',
        '<circle cx="760" cy="135" r="3.5" fill="#c29a57" class="twinkle" />',
    ]

    # Spiral Tail Marina Basin inside the spiral curl
    o += [
        "<!-- Spiral Tail Deepwater Harbor Basin -->",
        '<ellipse cx="270" cy="380" rx="36" ry="36" class="map-sea-deep" />',
        '<g stroke="#ffffff" stroke-width="1.8">',
        '<line x1="250" y1="380" x2="290" y2="380" />',
        '<line x1="270" y1="360" x2="270" y2="400" />',
        "</g>",
    ]

    # Glass-Domed Central Grand Pavilion (Hotspot 1) on the central body island
    pav = (585, 305)
    o += [
        "<!-- Glass-Domed Central Grand Pavilion -->",
        f'<g transform="translate({pav[0]}, {pav[1]})">',
        '<ellipse cx="0" cy="0" rx="36" ry="20" fill="#002244" opacity="0.8" />',
        '<ellipse cx="0" cy="0" rx="30" ry="16" fill="#38bdf8" filter="url(#glass-glow)" opacity="0.85" />',
        '<ellipse cx="0" cy="0" rx="20" ry="11" fill="none" stroke="#ffffff" stroke-width="1.4" />',
        '<line x1="-30" y1="0" x2="30" y2="0" stroke="#ffffff" stroke-width="1.6" />',
        '<line x1="0" y1="-16" x2="0" y2="16" stroke="#ffffff" stroke-width="1.6" />',
        '<circle cx="0" cy="0" r="4.5" fill="#f5c46e" class="twinkle" />',
        "</g>",
    ]

    # Revolving 360° Observation Eye Dome (Hotspot 2) on the eye island
    eye = (800, 230)
    o += [
        "<!-- Revolving 360 Degree Observation Eye Dome -->",
        f'<g transform="translate({eye[0]}, {eye[1]})">',
        '<circle cx="0" cy="0" r="16" fill="#0f172a" stroke="#ffffff" stroke-width="1.5" />',
        '<circle cx="0" cy="0" r="11" fill="#38bdf8" opacity="0.9" />',
        '<circle cx="3" cy="-3" r="3.5" fill="#ffffff" />',
        "</g>",
    ]

    # Foot District Features
    # Youth Innovation Center (Hotspot 3)
    youth = (840, 450)
    o += [
        "<!-- International Youth Innovation Center Campus -->",
        f'<rect x="{youth[0] - 14}" y="{youth[1] - 8}" width="28" height="16" rx="3" class="map-urban" />',
        f'<rect x="{youth[0] - 8}" y="{youth[1] - 4}" width="16" height="8" rx="2" class="map-greenery" />',
    ]

    # Marine Biology and Dolphin Station (Hotspot 6)
    bio = (725, 480)
    o += [
        "<!-- Marine Biology and Dolphin Station -->",
        f'<circle cx="{bio[0]}" cy="{bio[1]}" r="12" class="map-sea-lagoon" stroke="#ffffff" stroke-width="1.6" />',
        f'<path d="M{bio[0] - 4},{bio[1] - 3} C{bio[0] + 4},{bio[1] - 7} {bio[0] + 7},{bio[1] + 4} {bio[0]},{bio[1] + 6}" stroke="#0284c7" stroke-width="2" fill="none" />',
    ]

    # Floating Eco-District (Hotspot 7)
    eco = (400, 510)
    o += [
        "<!-- Experimental Floating Eco-Communities -->",
        '<g fill="#2dd4bf" stroke="#ffffff" stroke-width="1">',
        f'<rect x="{eco[0] - 12}" y="{eco[1] - 10}" width="10" height="10" rx="2" />',
        f'<rect x="{eco[0] + 4}" y="{eco[1] - 8}" width="10" height="10" rx="2" />',
        f'<rect x="{eco[0] - 6}" y="{eco[1] + 4}" width="10" height="10" rx="2" />',
        "</g>",
    ]

    # Tidal Power Hub
    power = (505, 525)
    o += [
        "<!-- Renewable Marine Power Hub -->",
        f'<g transform="translate({power[0]}, {power[1]})">',
        '<circle cx="0" cy="0" r="11" fill="#0284c7" stroke="#ffffff" stroke-width="1.4" />',
        '<path d="M0,-8 L0,8 M-8,0 L8,0" stroke="#ffffff" stroke-width="1.8" class="spin" />',
        "</g>",
    ]

    # Paradise Islands Overwater Villas on the Tongue Tip (Hotspot 5)
    villas = (1145, 425)
    o += [
        "<!-- Paradise Islands Overwater Bungalows and Coral Nursery -->",
        f'<ellipse cx="{villas[0]}" cy="{villas[1]}" rx="28" ry="24" fill="none" stroke="#c29a57" stroke-width="2.5" stroke-dasharray="3 4" />',
        f'<ellipse cx="{villas[0]}" cy="{villas[1]}" rx="14" ry="12" class="map-sea-lagoon" stroke="#2dd4bf" stroke-width="1.6" />',
        f'<circle cx="{villas[0]}" cy="{villas[1]}" r="3.5" fill="#38bdf8" class="bob" />',
    ]

    # Boardwalk connecting the tongue stepping stones
    tongue_pts = [(840, 285), (895, 295), (935, 310), (980, 330), (1030, 355), (1085, 385), villas]
    o += [
        "<!-- Overwater Boardwalk linking Tongue Atolls -->",
        f'<path d="{poly_path(tongue_pts, close=False)}" fill="none" stroke="#c29a57" stroke-width="2" stroke-linecap="round" />',
    ]

    # Sub-Sea Metro Tunnel Track
    metro_portal = (585, 375)
    o += [
        "<!-- Sub-Sea Metro Tunnel (Nova Aurelia to Portal, Pavilion, Eye Dome and Spiral Marina) -->",
        '<g fill="none" stroke="#f5c46e" stroke-dasharray="8 4">',
        f'<path d="M585,670 L{metro_portal[0]},{metro_portal[1]} L{pav[0]},{pav[1]}" stroke-width="3" />',
        f'<path d="M{pav[0]},{pav[1]} C680,290 740,260 {eye[0]},{eye[1]}" stroke-width="2.5" />',
        f'<path d="M{metro_portal[0]},{metro_portal[1]} C490,380 400,350 315,335" stroke-width="2.5" />',
        "</g>",
    ]
    for x, y in (metro_portal, pav, eye, (315, 335)):
        o.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="5" fill="#f5c46e" stroke="#ffffff" stroke-width="2" />')

    # Water-Taxi Paths
    o += [
        "<!-- Autonomous Electric Water Taxi Marine Paths -->",
        '<g class="map-ferry">',
        '<path d="M205,375 C160,460 250,580 400,510" />',
        '<path d="M725,480 C840,550 980,500 1085,385" />',
        '<path d="M760,195 C860,140 1020,200 1085,385" />',
        "</g>",
        "<!-- Geographic Labels -->",
        '<g class="map-label-group">',
        f'<text class="map-label-text" x="{pav[0]}" y="{pav[1] + 36}">{t["pavilion"]}</text>',
        f'<text class="map-label-text" x="270" y="445">{t["marina"]}</text>',
        f'<text class="map-label-text" x="1080" y="315">{t["villas"]}</text>',
        "</g>",
    ]

    # 8 Interactive Hotspots
    spots = [
        (1, pav[0], pav[1], "#38bdf8", "Glass-Domed Central Grand Pavilion", 12),
        (2, eye[0], eye[1], "#f5c46e", "Revolving 360 Degree Eye Dome", 11),
        (3, youth[0], youth[1], "#38bdf8", "Youth Innovation Center", 11),
        (4, 270, 380, "#0284c7", "Spiral Tail Marina", 11),
        (5, villas[0], villas[1], "#c29a57", "Paradise Islands Overwater Villas", 11),
        (6, bio[0], bio[1], "#22c55e", "Marine Biology and Dolphin Station", 11),
        (7, eco[0], eco[1], "#2dd4bf", "Floating Eco-District", 11),
        (8, metro_portal[0], metro_portal[1], "#f5c46e", "Sub-Sea Metro Tunnel Portal", 11),
    ]
    o.append("<!-- 8 INTERACTIVE HOTSPOT PINS -->")
    for i, x, y, col, name, r in spots:
        o.append(f"<!-- Hotspot {i}: {name} -->")
        o += hotspot(i, x, y, col, r)
    o.append("</svg>")
    return o


# ==========================================================================
# RUNNER
# ==========================================================================
SVG_RE = re.compile(r'<svg class="ill" viewBox="0 0 1200 700".*?</svg>', re.S)
SCRIPT_RE = re.compile(r'(<script src="\.\./js/common\.js"></script>)\s*<script>.*?</script>', re.S)


def main():
    for lang in ("en", "hu"):
        path = f"{ROOT}/{lang}/infrastructure.html"
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        t = L[lang]
        maps = ["\n".join(palm_svg(t)), "\n".join(world_svg(t)), "\n".join(chameleon_svg(t))]
        found = SVG_RE.findall(html)
        if len(found) != 3:
            sys.exit(f"{lang}: expected 3 island maps, found {len(found)}")
        it = iter(maps)
        html = SVG_RE.sub(lambda m: next(it), html)
        html, k = SCRIPT_RE.subn(r'\1\n<script src="../js/infrastructure.js"></script>', html)
        if k == 0 and "../js/infrastructure.js" not in html:
            sys.exit(f"{lang}: inline island script not found")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"updated {path}")


if __name__ == "__main__":
    main()
