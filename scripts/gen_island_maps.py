#!/usr/bin/env python3
"""Regenerate the three artificial-island SVG maps on en/hu infrastructure pages.

Design principles (Dubai-inspired artificial islands):
- Palm Island: real palm tree crown (16 curved fronds fanning from the central spine as leaves),
  with trunk and roads seamlessly connected.
- World Islands: archipelago of multiple distinct islands (larger continent cores + smaller islands)
  forming an instantly recognizable world map with zero overlapping islands.
- Chameleon Islands: a chameleon gripping a branch, modelled as one continuous silhouette (snout, casque,
  turret eye, arched back, spiral tail, four limbs) cut by narrow channels into many tightly grouped larger
  and smaller islands, plus crest islets, tongue stepping stones and a branch breakwater (zero overlaps).
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


def smooth_island(cx, cy, rx, ry, rot=0, seed=1, shape="organic", n_pts=16):
    """Generate rich, varied organic dredged islands with natural coastlines."""
    rad = math.radians(rot)
    cr, sr = math.cos(rad), math.sin(rad)
    pts = []
    for i in range(n_pts):
        ang = 2 * math.pi * i / n_pts
        c_a = math.cos(ang)
        s_a = math.sin(ang)

        # Multi-harmonic variation for natural sand bank curves
        rf = 1.0 + 0.07 * math.sin(2 * ang + seed) + 0.05 * math.cos(3 * ang + seed * 2) + 0.03 * math.sin(5 * ang + seed)

        lx = rx * c_a * rf
        ly = ry * s_a * rf

        if shape == "taper":  # Tapers along +y (like South America, India, Snout)
            taper_factor = max(0.28, 1.0 - 0.45 * (s_a + 0.2)) if s_a > -0.2 else 1.0 + 0.15 * s_a
            lx *= taper_factor
        elif shape == "arc":  # Curves along y axis
            lx += (ly * ly) / (ry * 3.6)
        elif shape == "casque":  # Swept back casque crest
            if s_a < 0:
                lx -= (ly * ly) / (ry * 2.6)
                rf *= 1.2
        elif shape == "spine":  # Triangular dorsal crest spike
            if s_a < 0:
                ly *= 1.35
                lx *= 0.65

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
        "palm_aria": "Detailed map of Palm Island infrastructure: curved palm leaves branching from central spine, trunk and protective crescent",
        "world_aria": "Detailed map of World Islands infrastructure: archipelago of multiple distinct islands arranged into the seven continents",
        "cham_aria": "Detailed map of Chameleon Islands infrastructure: tightly grouped larger and smaller islands forming a chameleon gripping a branch",
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
        "branch": "Branch Breakwater",
    },
    "hu": {
        "palm_aria": "A Pálma-sziget részletes infrastruktúra-térképe: központi törzsből kinyíló ívelt pálmalevelek, törzs és védő félhold",
        "world_aria": "A Világ-szigetek részletes infrastruktúra-térképe: több különálló szigetből álló kontinens alakú szigetcsoport",
        "cham_aria": "A Kaméleon-szigetek részletes infrastruktúra-térképe: szorosan csoportosuló kisebb és nagyobb szigetekből álló, ágon kapaszkodó kaméleon",
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
        "branch": "Ág-hullámtörő",
    },
}


# ==========================================================================
# 1. PALM ISLAND (REAL PALM TREE LEAVES BRANCHING UPWARD FROM MAIN STEM)
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

    # 16 CURVED PALM LEAVES (8 West, 8 East)
    # Merged Quadratic Bezier curves fanning out smoothly into the crown
    palm_frond_paths = []
    frond_roads = []
    frond_villas = []

    tips = [
        (360, 480),  # 0
        (350, 440),  # 1
        (340, 400),  # 2
        (330, 360),  # 3
        (340, 320),  # 4
        (350, 280),  # 5
        (360, 240),  # 6
        (370, 200),  # 7
        (400, 150),  # 8
        (480, 100),   # 9
    ]

    y_bases = [465, 430, 395, 360, 325, 290, 255, 220, 180, 150]

    w_mid_spot = (410, 320)
    e_mid_spot = (790, 320)

    for k in range(len(tips)):
        y0 = y_bases[k]
        tx_l, ty_l = tips[k]

        # Merged single control point for smooth quadratic arch
        cp_lx = (600 + tx_l) // 2 + 3
        cp_ly = (y0 + ty_l) // 2 - 68

        tx_r = 2 * cx - tx_l
        ty_r = ty_l
        cp_rx = 2 * cx - cp_lx
        cp_ry = cp_ly

        d_l = f"M600,{y0} Q{cp_lx},{cp_ly} {tx_l},{ty_l}"
        d_r = f"M600,{y0} Q{cp_rx},{cp_ry} {tx_r},{ty_r}"

        palm_frond_paths.append(d_l)
        palm_frond_paths.append(d_r)
        frond_roads.append(d_l)
        frond_roads.append(d_r)
        frond_villas.append(d_l)
        frond_villas.append(d_r)

    fronds_d = " ".join(palm_frond_paths)
    roads_d = " ".join(frond_roads)
    villas_d = " ".join(frond_villas)

    # Hotel platform at crescent apex
    hx, hy = cx, cy - R_CRES
    wx, wy = cx + 80, cy - R_CRES + 6

    # --------------------------------------------------------------------------
    # LAYER 0: WATER AND CORAL REEF
    # --------------------------------------------------------------------------
    o += [
        "<!-- Outer Coral Reef outside the Crescent Breakwater -->",
        f'<path d="{outer_west} {outer_east}" fill="none" stroke="#2ba29e" stroke-width="2.5" stroke-dasharray="8 6" opacity="0.65" />',
        f'<path d="{cres_all}" fill="none" stroke="#2ba29e" stroke-width="40" stroke-linecap="round" opacity="0.45" />',
    ]

    # --------------------------------------------------------------------------
    # LAYER 1: SAND (All Landmasses: Breakwater, Trunk to Barrier, Fronds, Mainland)
    # --------------------------------------------------------------------------
    o += [
        "<!-- === LAYER 1: SAND === -->",
        "<!-- Crescent Breakwater Sand -->",
        f'<path class="map-frond-edge" d="{cres_all}" stroke-width="26" />',
        f'<path class="map-frond" d="{cres_all}" stroke-width="22" />',
        "<!-- Crescent Apex Crown Platform Sand -->",
        f'<ellipse cx="{hx}" cy="{hy}" rx="54" ry="24" class="map-sand" />',
        "<!-- Central Trunk Sand reaching all the way to the barrier -->",
        '<path class="map-sand" d="M570,648 L570,465 Q572,240 582,38 L618,38 Q628,240 630,465 L630,648 Z" />',
        "<!-- Gateway Marina Lobe (West) and Golden Mile Lobe (East) on Trunk -->",
        '<path class="map-sand" d="M572,550 L532,550 C514,550 506,562 506,578 L506,598 C506,612 516,618 532,618 L572,618 Z" />',
        '<path class="map-sand" d="M628,550 L668,550 C686,550 694,562 694,578 L694,598 C694,612 684,618 668,618 L628,618 Z" />',
        '<rect x="518" y="560" width="44" height="48" rx="6" class="map-sea-deep" />',
        '<g stroke="#ffffff" stroke-width="1.6">',
        '<line x1="524" y1="572" x2="556" y2="572" />',
        '<line x1="524" y1="584" x2="556" y2="584" />',
        '<line x1="524" y1="596" x2="556" y2="596" />',
        "</g>",
        "<!-- 16 Palm Fronds Sand -->",
        f'<path class="map-frond-edge" d="{fronds_d}" stroke-width="21" />',
        f'<path class="map-frond" d="{fronds_d}" stroke-width="17" />',
        "<!-- Mainland Nova Aurelia Coastline Sand -->",
        '<path class="map-sand" d="M0,650 Q300,634 600,638 Q900,634 1200,650 L1200,700 L0,700 Z" />',
    ]

    # --------------------------------------------------------------------------
    # LAYER 2: GREEN (All Vegetation, Parks, and Leaf Cores)
    # --------------------------------------------------------------------------
    o += [
        "<!-- === LAYER 2: GREEN === -->",
        "<!-- Crescent Breakwater Greenery -->",
        f'<path class="map-frond-core" d="{cres_all}" stroke-width="4.5" />',
        "<!-- Crescent Apex Crown Platform Greenery -->",
        f'<ellipse cx="{hx}" cy="{hy}" rx="42" ry="16" class="map-greenery" />',
        "<!-- Central Trunk Green Park Spine reaching to the barrier -->",
        '<rect x="588" y="38" width="24" height="610" rx="8" class="map-greenery" />',
        "<!-- 16 Palm Fronds Green Core -->",
        f'<path class="map-frond-core" d="{fronds_d}" stroke-width="4.5" />',
    ]

    # --------------------------------------------------------------------------
    # LAYER 3: ROAD (All Roads, Rails, Villas, and Built Structures)
    # --------------------------------------------------------------------------
    o += [
        "<!-- === LAYER 3: ROAD === -->",
        "<!-- Palm Fronds Waterfront Villas -->",
        f'<path class="map-frond-villas" d="{villas_d}" stroke-width="2.6" stroke-dasharray="0.1 7" />',
        "<!-- Crescent Waterfront Villas -->",
        f'<path class="map-frond-villas" d="{cres_all}" stroke-width="2.6" stroke-dasharray="0.1 7" />',
        "<!-- Connected Road Network (Mainland through Trunk to Barrier and Fronds) -->",
        '<path class="map-road" d="M592,664 L592,42 M608,664 L608,42" />',
        '<path class="map-road" d="M592,42 C592,30 608,30 608,42" />',
        f'<path class="map-road" d="{roads_d}" stroke-width="2.2" />',
        "<!-- The Elevated Monorail Line along the central spine to the barrier -->",
        '<path class="map-rail" d="M600,690 L600,42" />',
    ]
    for y in (664, 580, 465, 325, 210, 42):
        o.append(f'<circle cx="600" cy="{y}" r="5" fill="#c29a57" stroke="#ffffff" stroke-width="1.8" />')

    o += [
        "<!-- Solar Canopy and Seawater Cooling Hub -->",
        '<g fill="#1f4f7a" stroke="#9fd3f5" stroke-width="0.8">',
    ]
    for r in range(3):
        for c in range(3):
            o.append(f'<rect x="{640 + c * 14}" y="{566 + r * 14}" width="11" height="11" rx="1.5" />')
    o.append("</g>")

    o += [
        "<!-- Mainland Waterfront Urban Strip -->",
        '<rect x="0" y="664" width="1200" height="36" class="map-urban" />',
        '<line x1="0" y1="664" x2="1200" y2="664" stroke="#ffffff" stroke-width="2.5" />',
        "<!-- Crescent Apex Hotel Architecture (Hotel Khalifa) -->",
        f'<g transform="translate({hx}, {hy})">',
        '<ellipse cx="0" cy="2" rx="22" ry="9" fill="#002244" opacity="0.75" />',
        '<path d="M-14,4 L0,-22 L14,4 Z" fill="#c29a57" filter="url(#glow-gold)" />',
        '<path d="M-6,4 L0,-18 L6,4 Z" fill="#ffffff" />',
        '<circle cx="0" cy="-22" r="3" fill="#e3735a" class="twinkle" />',
        "</g>",
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
        f'<text class="map-label-text" x="280" y="470">{t["west_fronds"]}</text>',
        f'<text class="map-label-text" x="920" y="470">{t["east_fronds"]}</text>',
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
    # === NORTH AMERICA (27 Islands: Arctic, Canada, US, Florida, Baja, Mexico, Central America, Caribbean) ===
    {'name': 'Alaska North Slope', 'cx': 238.5, 'cy': 161.1, 'rx': 17, 'ry': 12, 'rot': -10, 'green': True},
    {'name': 'Alaska Peninsula and Aleutians', 'cx': 209.9, 'cy': 180.9, 'rx': 14, 'ry': 8, 'rot': -25},
    {'name': 'Yukon and Northwest Territories', 'cx': 273.7, 'cy': 147.5, 'rx': 17, 'ry': 13, 'rot': 10, 'green': True},
    {'name': 'Canadian Arctic Islands', 'cx': 312.0, 'cy': 126.0, 'rx': 21, 'ry': 12, 'rot': 5, 'sand_light': True},
    {'name': 'Baffin Island', 'cx': 358.8, 'cy': 122.9, 'rx': 17, 'ry': 13, 'rot': 25, 'sand_light': True},
    {'name': 'Greenland Isle', 'cx': 424.0, 'cy': 112.0, 'rx': 25, 'ry': 26, 'rot': 20, 'sand_light': True},
    {'name': 'Western Canada Alberta', 'cx': 266.0, 'cy': 186.0, 'rx': 15, 'ry': 14, 'rot': -15, 'green': True},
    {'name': 'Canadian Rockies and British Columbia', 'cx': 235.7, 'cy': 197.0, 'rx': 12, 'ry': 15, 'rot': 15, 'shape': 'arc', 'green': True},
    {'name': 'Canadian Shield Ontario', 'cx': 308.1, 'cy': 174.0, 'rx': 20, 'ry': 15, 'rot': 10, 'green': True},
    {'name': 'Quebec and Labrador', 'cx': 361.2, 'cy': 164.0, 'rx': 21, 'ry': 17, 'rot': 15, 'green': True},
    {'name': 'Newfoundland and Maritimes', 'cx': 404.0, 'cy': 178.0, 'rx': 14, 'ry': 12, 'rot': 25, 'green': True},
    {'name': 'US Pacific Northwest', 'cx': 244.1, 'cy': 230.5, 'rx': 13, 'ry': 15, 'rot': 15, 'shape': 'arc'},
    {'name': 'California Coast', 'cx': 248.0, 'cy': 266.0, 'rx': 11, 'ry': 16, 'rot': 20, 'shape': 'arc'},
    {'name': 'US Rocky Mountains and Plains', 'cx': 286.0, 'cy': 224.0, 'rx': 19, 'ry': 15, 'rot': 0},
    {'name': 'US Midwest and Great Lakes', 'cx': 331.1, 'cy': 213.7, 'rx': 19, 'ry': 15, 'rot': 5, 'green': True, 'hub': 'na'},
    {'name': 'US East Coast and New England', 'cx': 374.0, 'cy': 212.0, 'rx': 17, 'ry': 16, 'rot': -25, 'green': True},
    {'name': 'US South and Gulf Coast', 'cx': 342.0, 'cy': 256.0, 'rx': 21, 'ry': 14, 'rot': -5},
    {'name': 'Texas and Southern Great Plains', 'cx': 298.0, 'cy': 260.0, 'rx': 16, 'ry': 14, 'rot': 0, 'shape': 'taper'},
    {'name': 'Florida Peninsula', 'cx': 382.0, 'cy': 268.0, 'rx': 10, 'ry': 16, 'rot': -30},
    {'name': 'Baja California', 'cx': 246.0, 'cy': 304.0, 'rx': 6, 'ry': 16, 'rot': 25, 'shape': 'arc'},
    {'name': 'Northern Mexico', 'cx': 278.0, 'cy': 296.0, 'rx': 16, 'ry': 14, 'rot': 15},
    {'name': 'Southern Mexico', 'cx': 298.0, 'cy': 328.0, 'rx': 14, 'ry': 13, 'rot': 25, 'shape': 'taper'},
    {'name': 'Yucatan Peninsula', 'cx': 338.0, 'cy': 318.0, 'rx': 13, 'ry': 11, 'rot': 20, 'shape': 'taper', 'green': True},
    {'name': 'Central America Isthmus', 'cx': 328.0, 'cy': 352.0, 'rx': 11, 'ry': 8, 'rot': 35, 'shape': 'arc'},
    {'name': 'Cuba and Greater Antilles', 'cx': 398.0, 'cy': 304.0, 'rx': 17, 'ry': 7, 'rot': -15},
    {'name': 'Bahamas and Caribbean Chain', 'cx': 424.0, 'cy': 322.0, 'rx': 9, 'ry': 6, 'rot': 25},
    {'name': 'Hawaii Pacific Outpost', 'cx': 155.0, 'cy': 255.0, 'rx': 10, 'ry': 7, 'rot': 20},

    # === SOUTH AMERICA (16 Islands: Colombia, Venezuela, Guyana, Amazon, Brazil, Andes, Argentina, Patagonia) ===
    {'name': 'Colombia and Northern Andes', 'cx': 354.0, 'cy': 382.0, 'rx': 15, 'ry': 13, 'rot': -20},
    {'name': 'Venezuela and Orinoco', 'cx': 390.0, 'cy': 370.0, 'rx': 17, 'ry': 11, 'rot': 10, 'green': True},
    {'name': 'Guyana Coast', 'cx': 424.0, 'cy': 378.0, 'rx': 13, 'ry': 9, 'rot': 20, 'green': True},
    {'name': 'Peru and Central Andes', 'cx': 342.0, 'cy': 420.0, 'rx': 13, 'ry': 19, 'rot': -15},
    {'name': 'Amazon Basin Heart', 'cx': 385.5, 'cy': 409.0, 'rx': 22, 'ry': 20, 'rot': 0, 'green': True},
    {'name': 'Brazil Northeast Bulge', 'cx': 446.8, 'cy': 415.4, 'rx': 20, 'ry': 16, 'rot': 20, 'green': True},
    {'name': 'Central Brazil and Cerrado Plateau', 'cx': 415.1, 'cy': 438.5, 'rx': 16, 'ry': 15, 'rot': 10, 'green': True},
    {'name': 'Bolivia and Pantanal', 'cx': 379.8, 'cy': 448.5, 'rx': 16, 'ry': 15, 'rot': 5},
    {'name': 'Paraguay and Gran Chaco Basin', 'cx': 366.3, 'cy': 479.4, 'rx': 13, 'ry': 14, 'rot': 5},
    {'name': 'Brazil Southeast Coast', 'cx': 436.4, 'cy': 469.3, 'rx': 18, 'ry': 17, 'rot': 25, 'green': True},
    {'name': 'Chile Andes Strip', 'cx': 338.2, 'cy': 489.1, 'rx': 9, 'ry': 25, 'rot': 8, 'shape': 'arc'},
    {'name': 'Argentina Pampas Core', 'cx': 384.6, 'cy': 511.7, 'rx': 17, 'ry': 19, 'rot': 5, 'shape': 'taper'},
    {'name': 'Uruguay and Rio de la Plata', 'cx': 417.8, 'cy': 505.1, 'rx': 12, 'ry': 12, 'rot': 15, 'green': True},
    {'name': 'Patagonia Southern Wedge', 'cx': 369.4, 'cy': 546.7, 'rx': 13, 'ry': 15, 'rot': 8, 'shape': 'taper'},
    {'name': 'Tierra del Fuego', 'cx': 379.3, 'cy': 572.1, 'rx': 11, 'ry': 7, 'rot': 10},
    {'name': 'Falkland Islands', 'cx': 402.0, 'cy': 565.0, 'rx': 7, 'ry': 5, 'rot': 0},

    # === ATLANTIC AND EUROPE (16 Islands: Iceland, Ireland, Great Britain, Scandinavia, Western Europe, Central Europe, Iberia, Italy, Greece, East Europe) ===
    {'name': 'Iceland', 'cx': 494.0, 'cy': 128.0, 'rx': 13, 'ry': 9, 'rot': -10, 'sand_light': True},
    {'name': 'Ireland', 'cx': 498.0, 'cy': 176.0, 'rx': 9, 'ry': 12, 'rot': 15},
    {'name': 'Great Britain', 'cx': 524.0, 'cy': 166.0, 'rx': 12, 'ry': 20, 'rot': -20, 'shape': 'arc'},
    {'name': 'Norway Fjord Coast', 'cx': 558.0, 'cy': 130.0, 'rx': 11, 'ry': 20, 'rot': 20, 'shape': 'arc', 'green': True},
    {'name': 'Denmark and Jutland Peninsula', 'cx': 564.0, 'cy': 168.0, 'rx': 9, 'ry': 13, 'rot': 10, 'shape': 'arc', 'green': True},
    {'name': 'Sweden and Finland', 'cx': 592.0, 'cy': 134.0, 'rx': 15, 'ry': 20, 'rot': 15, 'green': True},
    {'name': 'Western Europe Mainland Core', 'cx': 544.0, 'cy': 214.0, 'rx': 18, 'ry': 14, 'rot': 5, 'green': True, 'hub': 'eu'},
    {'name': 'France and Biscay Bay', 'cx': 512.6, 'cy': 229.7, 'rx': 13, 'ry': 13, 'rot': -10, 'green': True},
    {'name': 'Central Europe Germany and Alps', 'cx': 582.0, 'cy': 204.0, 'rx': 15, 'ry': 13, 'rot': 0, 'green': True},
    {'name': 'Iberian Peninsula', 'cx': 500.0, 'cy': 260.1, 'rx': 16, 'ry': 15, 'rot': -10},
    {'name': 'Italy Boot Peninsula', 'cx': 564.0, 'cy': 260.0, 'rx': 8, 'ry': 15, 'rot': 35},
    {'name': 'Sicily and Malta', 'cx': 562.0, 'cy': 288.0, 'rx': 6, 'ry': 4, 'rot': -15},
    {'name': 'Balkans and Greece', 'cx': 602.0, 'cy': 256.0, 'rx': 14, 'ry': 13, 'rot': 15},
    {'name': 'Danube Basin and Romania', 'cx': 614.8, 'cy': 224.6, 'rx': 14, 'ry': 12, 'rot': 15, 'green': True},
    {'name': 'Poland and Baltic States', 'cx': 618.0, 'cy': 178.0, 'rx': 16, 'ry': 13, 'rot': 10, 'green': True},
    {'name': 'Eastern Europe Ukraine Plains', 'cx': 646.6, 'cy': 209.7, 'rx': 17, 'ry': 15, 'rot': 5},

    # === AFRICA (18 Islands: Morocco, Sahara, Libya, Egypt, Senegal, Guinea Coast, Nigeria, Sudan, Horn, Congo, Rift, Angola, Cape, Madagascar) ===
    {'name': 'Morocco and Atlas', 'cx': 503.2, 'cy': 319.7, 'rx': 14, 'ry': 10, 'rot': -15},
    {'name': 'Sahara Core Northwest', 'cx': 540.2, 'cy': 326.2, 'rx': 19, 'ry': 14, 'rot': 0},
    {'name': 'Libya and Central Sahara', 'cx': 581.0, 'cy': 326.0, 'rx': 17, 'ry': 13, 'rot': 0},
    {'name': 'Egypt and Nile Delta', 'cx': 622.0, 'cy': 318.0, 'rx': 17, 'ry': 13, 'rot': 15},
    {'name': 'West Africa Senegal Bulge', 'cx': 476.0, 'cy': 362.0, 'rx': 15, 'ry': 13, 'rot': -25},
    {'name': 'Gulf of Guinea Ivory Coast', 'cx': 514.0, 'cy': 368.0, 'rx': 17, 'ry': 11, 'rot': -5, 'green': True},
    {'name': 'Nigeria and Sahel', 'cx': 558.0, 'cy': 364.0, 'rx': 18, 'ry': 13, 'rot': 0},
    {'name': 'Sudan and Nubia Basin', 'cx': 616.0, 'cy': 362.0, 'rx': 16, 'ry': 13, 'rot': 15},
    {'name': 'Horn of Africa Somalia', 'cx': 658.0, 'cy': 366.0, 'rx': 17, 'ry': 13, 'rot': 35, 'shape': 'taper'},
    {'name': 'Central African Savannah', 'cx': 539.5, 'cy': 397.3, 'rx': 13, 'ry': 12, 'rot': 0, 'green': True},
    {'name': 'Congo Basin Rainforest', 'cx': 576.3, 'cy': 408.3, 'rx': 21, 'ry': 17, 'rot': 5, 'green': True},
    {'name': 'East Africa Rift and Lakes', 'cx': 619.1, 'cy': 410.0, 'rx': 17, 'ry': 19, 'rot': 10, 'green': True},
    {'name': 'Angola Atlantic Coast', 'cx': 540.0, 'cy': 450.0, 'rx': 13, 'ry': 18, 'rot': -15, 'shape': 'arc'},
    {'name': 'Zambia and Zimbabwe Plateau', 'cx': 582.0, 'cy': 456.0, 'rx': 17, 'ry': 15, 'rot': 5},
    {'name': 'Mozambique Channel Coast', 'cx': 622.0, 'cy': 460.0, 'rx': 12, 'ry': 18, 'rot': -15, 'shape': 'arc', 'green': True},
    {'name': 'Namibia and Kalahari', 'cx': 556.0, 'cy': 496.0, 'rx': 14, 'ry': 16, 'rot': -5},
    {'name': 'South Africa Cape', 'cx': 594.0, 'cy': 512.0, 'rx': 19, 'ry': 15, 'rot': 5, 'shape': 'taper'},
    {'name': 'Madagascar Island', 'cx': 664.0, 'cy': 472.0, 'rx': 11, 'ry': 22, 'rot': -20, 'green': True},

    # === ASIA AND MIDDLE EAST (35 Islands: Russia, Urals, Siberia, Baikal, Kamchatka, Levant, Arabia, Central Asia, Kazakhstan, Pamir, Iran, India, Tibet, China, Korea, Japan, Indochina, Indonesia) ===
    {'name': 'European Russia Core', 'cx': 671.1, 'cy': 156.2, 'rx': 20, 'ry': 16, 'rot': 5, 'green': True},
    {'name': 'Ural Mountains and West Siberia', 'cx': 718.5, 'cy': 142.1, 'rx': 25, 'ry': 16, 'rot': 0},
    {'name': 'Central Siberia Plateau', 'cx': 776.8, 'cy': 130.8, 'rx': 30, 'ry': 16, 'rot': 0},
    {'name': 'Lake Baikal and Sayan Range', 'cx': 825.0, 'cy': 142.0, 'rx': 16, 'ry': 12, 'rot': -5, 'green': True},
    {'name': 'East Siberia and Yakutia', 'cx': 868.0, 'cy': 130.0, 'rx': 27, 'ry': 16, 'rot': -5},
    {'name': 'Kamchatka and Bering Shore', 'cx': 926.4, 'cy': 141.4, 'rx': 13, 'ry': 16, 'rot': 25, 'shape': 'arc'},
    {'name': 'Sakhalin Island Arc', 'cx': 947.9, 'cy': 162.8, 'rx': 7, 'ry': 13, 'rot': 10, 'shape': 'arc'},
    {'name': 'Levant and Mesopotamia', 'cx': 662.0, 'cy': 270.0, 'rx': 15, 'ry': 12, 'rot': 15},
    {'name': 'Arabian Peninsula', 'cx': 670.0, 'cy': 312.0, 'rx': 20, 'ry': 16, 'rot': -25},
    {'name': 'Central Asian Steppes', 'cx': 724.0, 'cy': 198.0, 'rx': 20, 'ry': 14, 'rot': 5},
    {'name': 'Kazakhstan and Altai Steppes', 'cx': 766.0, 'cy': 185.0, 'rx': 18, 'ry': 13, 'rot': 10},
    {'name': 'Pamir and Hindu Kush Plateau', 'cx': 752.0, 'cy': 234.0, 'rx': 16, 'ry': 13, 'rot': 25},
    {'name': 'Persian Plateau', 'cx': 712.0, 'cy': 256.0, 'rx': 17, 'ry': 14, 'rot': 20},
    {'name': 'Pakistan and Indus Basin', 'cx': 745.0, 'cy': 278.0, 'rx': 14, 'ry': 15, 'rot': 20},
    {'name': 'Northern India and Himalayas', 'cx': 782.0, 'cy': 264.0, 'rx': 19, 'ry': 13, 'rot': 15},
    {'name': 'Bengal and Ganges Delta', 'cx': 816.0, 'cy': 288.0, 'rx': 14, 'ry': 14, 'rot': 15, 'green': True},
    {'name': 'Indian Peninsula Triangle', 'cx': 776.0, 'cy': 318.0, 'rx': 20, 'ry': 24, 'rot': 15, 'green': True, 'shape': 'taper'},
    {'name': 'Sri Lanka Pearl', 'cx': 792.0, 'cy': 366.0, 'rx': 7, 'ry': 9, 'rot': 10},
    {'name': 'Mongolia Steppes', 'cx': 807.4, 'cy': 179.3, 'rx': 23, 'ry': 13, 'rot': 0},
    {'name': 'Tibetan High Plateau', 'cx': 816.2, 'cy': 225.8, 'rx': 20, 'ry': 12, 'rot': 10},
    {'name': 'Manchuria and Amur River Basin', 'cx': 886.0, 'cy': 174.0, 'rx': 17, 'ry': 13, 'rot': 10, 'green': True},
    {'name': 'North China Core', 'cx': 855.2, 'cy': 200.7, 'rx': 21, 'ry': 16, 'rot': 5, 'green': True, 'hub': 'asia'},
    {'name': 'East China Coast and Shanghai', 'cx': 895.3, 'cy': 240.0, 'rx': 13, 'ry': 14, 'rot': 15, 'green': True},
    {'name': 'South China and Yangtze', 'cx': 859.6, 'cy': 251.6, 'rx': 20, 'ry': 16, 'rot': 0, 'green': True},
    {'name': 'Korean Peninsula', 'cx': 908.0, 'cy': 209.6, 'rx': 9, 'ry': 15, 'rot': 20},
    {'name': 'Japan Hokkaido', 'cx': 948.1, 'cy': 191.6, 'rx': 11, 'ry': 11, 'rot': -20},
    {'name': 'Japan Honshu Arc', 'cx': 954.1, 'cy': 228.7, 'rx': 10, 'ry': 22, 'rot': 35, 'shape': 'arc'},
    {'name': 'Taiwan Island', 'cx': 908.0, 'cy': 272.0, 'rx': 7, 'ry': 12, 'rot': 25, 'shape': 'arc'},
    {'name': 'Indochina Peninsula Vietnam/Thailand', 'cx': 854.0, 'cy': 298.0, 'rx': 16, 'ry': 16, 'rot': 15},
    {'name': 'Malay Peninsula', 'cx': 846.0, 'cy': 336.0, 'rx': 8, 'ry': 13, 'rot': 15, 'shape': 'arc'},
    {'name': 'Sumatra Island', 'cx': 836.0, 'cy': 372.0, 'rx': 11, 'ry': 18, 'rot': -35, 'green': True, 'shape': 'arc'},
    {'name': 'Java Island', 'cx': 878.0, 'cy': 392.0, 'rx': 18, 'ry': 7, 'rot': 5, 'green': True},
    {'name': 'Borneo Heart', 'cx': 892.0, 'cy': 346.0, 'rx': 16, 'ry': 15, 'rot': 10, 'green': True},
    {'name': 'Sulawesi and Moluccas', 'cx': 924.0, 'cy': 358.0, 'rx': 11, 'ry': 14, 'rot': 25, 'shape': 'arc', 'green': True},
    {'name': 'Philippines Archipelago', 'cx': 932.0, 'cy': 310.0, 'rx': 10, 'ry': 16, 'rot': 20},

    # === OCEANIA (12 Islands: Papua New Guinea, Australia Outback, Queensland Reef, Central Australia, New South Wales, Tasmania, New Zealand) ===
    {'name': 'Papua New Guinea', 'cx': 948.0, 'cy': 386.0, 'rx': 20, 'ry': 10, 'rot': -10},
    {'name': 'Solomon Islands and Coral Archipelago', 'cx': 996.0, 'cy': 396.0, 'rx': 14, 'ry': 8, 'rot': -20},
    {'name': 'Western Australia Outback', 'cx': 884.0, 'cy': 456.0, 'rx': 18, 'ry': 20, 'rot': 10},
    {'name': 'Northern Territory Australia', 'cx': 924.0, 'cy': 432.0, 'rx': 16, 'ry': 14, 'rot': -5},
    {'name': 'Queensland and Barrier Reef', 'cx': 966.0, 'cy': 442.0, 'rx': 14, 'ry': 18, 'rot': -25, 'shape': 'arc', 'green': True},
    {'name': 'Central and South Australia', 'cx': 924.0, 'cy': 478.0, 'rx': 20, 'ry': 16, 'rot': 0, 'green': True, 'hub': 'oc'},
    {'name': 'Great Australian Bight and Adelaide', 'cx': 892.0, 'cy': 497.2, 'rx': 14, 'ry': 12, 'rot': 15, 'green': True},
    {'name': 'New South Wales and Victoria', 'cx': 964.0, 'cy': 488.0, 'rx': 16, 'ry': 16, 'rot': 20, 'green': True},
    {'name': 'Tasmania', 'cx': 959.6, 'cy': 529.6, 'rx': 9, 'ry': 7, 'rot': 0},
    {'name': 'New Zealand North Island', 'cx': 1018.0, 'cy': 482.0, 'rx': 9, 'ry': 13, 'rot': -35, 'shape': 'arc'},
    {'name': 'New Zealand South Island', 'cx': 992.2, 'cy': 507.2, 'rx': 9, 'ry': 15, 'rot': -30, 'shape': 'arc'},
    {'name': 'South Pacific Coral Isles', 'cx': 1038.0, 'cy': 428.0, 'rx': 9, 'ry': 7, 'rot': 20},

    # === ANTARCTICA (9 Islands: Antarctic Peninsula, Weddell Sea, Polar Dome Hub, Wilkes, Ross Shelves, Marie Byrd Land) ===
    {'name': 'Ellsworth Land Ice Shelf', 'cx': 348.9, 'cy': 581.7, 'rx': 17, 'ry': 9, 'rot': 10, 'sand_light': True},
    {'name': 'Antarctic Peninsula Graham Land', 'cx': 396.5, 'cy': 592.3, 'rx': 9, 'ry': 15, 'rot': -35, 'shape': 'arc', 'sand_light': True},
    {'name': 'Weddell Sea Ice Shelf', 'cx': 446.0, 'cy': 602.0, 'rx': 22, 'ry': 11, 'sand_light': True},
    {'name': 'Queen Maud Land Shelf', 'cx': 516.0, 'cy': 602.0, 'rx': 24, 'ry': 12, 'sand_light': True},
    {'name': 'Antarctic Polar Dome Hub', 'cx': 595.0, 'cy': 595.0, 'rx': 25, 'ry': 13, 'sand_light': True, 'hub': 'an'},
    {'name': 'Wilkes Land Ice Shelf', 'cx': 674.0, 'cy': 602.0, 'rx': 24, 'ry': 12, 'sand_light': True},
    {'name': 'Ross Ice Shelf East', 'cx': 748.0, 'cy': 602.0, 'rx': 24, 'ry': 11, 'sand_light': True},
    {'name': 'Ross Sea Ice Shelf West', 'cx': 812.1, 'cy': 592.0, 'rx': 20, 'ry': 11, 'sand_light': True},
    {'name': 'Marie Byrd Land Shelf', 'cx': 863.7, 'cy': 575.6, 'rx': 18, 'ry': 11, 'rot': -10, 'sand_light': True},
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
    o.append("<!-- RECOGNIZABLE WORLD CONTINENTS (VARIED SHAPES, ZERO OVERLAPS) -->")
    o.append('<g id="world-islands-group">')
    for i, isle in enumerate(WORLD_ISLES):
        cls = "map-sand-light" if isle.get("sand_light") else "map-sand"
        shape = isle.get("shape", "organic")
        d = smooth_island(isle["cx"], isle["cy"], isle["rx"], isle["ry"], rot=isle.get("rot", 0), seed=i + 1, shape=shape)
        o.append(f'<!-- {isle["name"]} -->')
        o.append(f'<path class="{cls}" d="{d}" />')
        if isle.get("green"):
            d_grn = smooth_island(isle["cx"], isle["cy"], isle["rx"] * 0.65, isle["ry"] * 0.65, rot=isle.get("rot", 0), seed=i + 10, shape=shape)
            o.append(f'<path class="map-greenery" d="{d_grn}" />')
    o.append("</g>")

    # Hub architectures on main continental islands
    us_hub = (331.1, 213.7)
    eu_hub = (544.0, 214.0)
    asia_hub = (855.2, 200.7)
    oc_hub = (924.0, 478.0)
    an_hub = (595.0, 595.0)

    o += [
        "<!-- Continental Hub Pavilions and Features -->",
        f'<rect x="{us_hub[0] - 16}" y="{us_hub[1] - 9}" width="32" height="18" rx="3" class="map-urban" />',
        f'<rect x="{eu_hub[0] - 14}" y="{eu_hub[1] - 8}" width="28" height="16" rx="3" class="map-urban" />',
        f'<rect x="{asia_hub[0] - 18}" y="{asia_hub[1] - 9}" width="36" height="18" rx="3" class="map-urban" />',
        f'<ellipse cx="{an_hub[0]}" cy="{an_hub[1]}" rx="24" ry="9" fill="#38bdf8" stroke="#ffffff" stroke-width="1.6" opacity="0.85" />',
    ]

    # Inter-island footbridges connecting close satellite pairs and inter-continental spans
    bridges = [
        # --- North America ---
        ((308.1, 174.0), (331.1, 213.7)),  # Canadian Shield Ontario to US Midwest and Great Lakes
        ((331.1, 213.7), (374.0, 212.0)),  # US Midwest and Great Lakes to US East Coast and New England
        ((331.1, 213.7), (342.0, 256.0)),  # US Midwest and Great Lakes to US South and Gulf Coast
        ((342.0, 256.0), (382.0, 268.0)),  # US South and Gulf Coast to Florida Peninsula
        ((286.0, 224.0), (298.0, 260.0)),  # US Rocky Mountains and Plains to Texas and Southern Great Plains
        ((298.0, 260.0), (278.0, 296.0)),  # Texas and Southern Great Plains to Northern Mexico
        ((278.0, 296.0), (298.0, 328.0)),  # Northern Mexico to Southern Mexico
        ((298.0, 328.0), (338.0, 318.0)),  # Southern Mexico to Yucatan Peninsula
        ((298.0, 328.0), (328.0, 352.0)),  # Southern Mexico to Central America Isthmus
        ((361.2, 164.0), (404.0, 178.0)),  # Quebec and Labrador to Newfoundland and Maritimes

        # --- South America ---
        ((354.0, 382.0), (390.0, 370.0)),  # Colombia and Northern Andes to Venezuela and Orinoco
        ((354.0, 382.0), (385.5, 409.0)),  # Colombia and Northern Andes to Amazon Basin Heart
        ((390.0, 370.0), (424.0, 378.0)),  # Venezuela and Orinoco to Guyana Coast
        ((385.5, 409.0), (379.8, 448.5)),  # Amazon Basin Heart to Bolivia and Pantanal
        ((385.5, 409.0), (446.8, 415.4)),  # Amazon Basin Heart to Brazil Northeast Bulge
        ((385.5, 409.0), (415.1, 438.5)),  # Amazon Basin Heart to Central Brazil and Cerrado Plateau
        ((415.1, 438.5), (436.4, 469.3)),  # Central Brazil and Cerrado Plateau to Brazil Southeast Coast
        ((379.8, 448.5), (366.3, 479.4)),  # Bolivia and Pantanal to Paraguay and Gran Chaco Basin
        ((366.3, 479.4), (384.6, 511.7)),  # Paraguay and Gran Chaco Basin to Argentina Pampas Core
        ((384.6, 511.7), (417.8, 505.1)),  # Argentina Pampas Core to Uruguay and Rio de la Plata
        ((384.6, 511.7), (369.4, 546.7)),  # Argentina Pampas Core to Patagonia Southern Wedge
        ((369.4, 546.7), (379.3, 572.1)),  # Patagonia Southern Wedge to Tierra del Fuego
        ((379.3, 572.1), (402.0, 565.0)),  # Tierra del Fuego to Falkland Islands

        # --- Europe ---
        ((498.0, 176.0), (524.0, 166.0)),  # Ireland to Great Britain
        ((524.0, 166.0), (544.0, 214.0)),  # Great Britain to Western Europe Mainland Core
        ((544.0, 214.0), (512.6, 229.7)),  # Western Europe Mainland Core to France and Biscay Bay
        ((512.6, 229.7), (500.0, 260.1)),  # France and Biscay Bay to Iberian Peninsula
        ((544.0, 214.0), (582.0, 204.0)),  # Western Europe Mainland Core to Central Europe Germany and Alps
        ((582.0, 204.0), (564.0, 168.0)),  # Central Europe Germany and Alps to Denmark and Jutland Peninsula
        ((582.0, 204.0), (614.8, 224.6)),  # Central Europe Germany and Alps to Danube Basin and Romania
        ((582.0, 204.0), (618.0, 178.0)),  # Central Europe Germany and Alps to Poland and Baltic States
        ((614.8, 224.6), (646.6, 209.7)),  # Danube Basin and Romania to Eastern Europe Ukraine Plains
        ((618.0, 178.0), (646.6, 209.7)),  # Poland and Baltic States to Eastern Europe Ukraine Plains

        # --- Africa ---
        ((503.2, 319.7), (540.2, 326.2)),  # Morocco and Atlas to Sahara Core Northwest
        ((540.2, 326.2), (581.0, 326.0)),  # Sahara Core Northwest to Libya and Central Sahara
        ((581.0, 326.0), (622.0, 318.0)),  # Libya and Central Sahara to Egypt and Nile Delta
        ((514.0, 368.0), (558.0, 364.0)),  # Gulf of Guinea Ivory Coast to Nigeria and Sahel
        ((558.0, 364.0), (581.0, 326.0)),  # Nigeria and Sahel to Libya and Central Sahara
        ((558.0, 364.0), (616.0, 362.0)),  # Nigeria and Sahel to Sudan and Nubia Basin
        ((558.0, 364.0), (576.3, 408.3)),  # Nigeria and Sahel to Congo Basin Rainforest
        ((576.3, 408.3), (619.1, 410.0)),  # Congo Basin Rainforest to East Africa Rift and Lakes
        ((576.3, 408.3), (582.0, 456.0)),  # Congo Basin Rainforest to Zambia and Zimbabwe Plateau
        ((582.0, 456.0), (622.0, 460.0)),  # Zambia and Zimbabwe Plateau to Mozambique Channel Coast
        ((582.0, 456.0), (594.0, 512.0)),  # Zambia and Zimbabwe Plateau to South Africa Cape

        # --- Asia ---
        ((671.1, 156.2), (718.5, 142.1)),  # European Russia Core to Ural Mountains and West Siberia
        ((718.5, 142.1), (776.8, 130.8)),  # Ural Mountains and West Siberia to Central Siberia Plateau
        ((776.8, 130.8), (825.0, 142.0)),  # Central Siberia Plateau to Lake Baikal and Sayan Range
        ((825.0, 142.0), (868.0, 130.0)),  # Lake Baikal and Sayan Range to East Siberia and Yakutia
        ((825.0, 142.0), (807.4, 179.3)),  # Lake Baikal and Sayan Range to Mongolia Steppes
        ((718.5, 142.1), (724.0, 198.0)),  # Ural Mountains to Central Asian Steppes
        ((724.0, 198.0), (766.0, 185.0)),  # Central Asian Steppes to Kazakhstan and Altai Steppes
        ((766.0, 185.0), (807.4, 179.3)),  # Kazakhstan and Altai Steppes to Mongolia Steppes
        ((766.0, 185.0), (776.8, 130.8)),  # Kazakhstan and Altai Steppes to Central Siberia Plateau
        ((724.0, 198.0), (752.0, 234.0)),  # Central Asian Steppes to Pamir and Hindu Kush Plateau
        ((752.0, 234.0), (782.0, 264.0)),  # Pamir and Hindu Kush Plateau to Northern India and Himalayas
        ((752.0, 234.0), (745.0, 278.0)),  # Pamir and Hindu Kush Plateau to Pakistan and Indus Basin
        ((712.0, 256.0), (752.0, 234.0)),  # Persian Plateau to Pamir and Hindu Kush Plateau
        ((752.0, 234.0), (816.2, 225.8)),  # Pamir and Hindu Kush Plateau to Tibetan High Plateau
        ((807.4, 179.3), (855.2, 200.7)),  # Mongolia Steppes to North China Core
        ((816.2, 225.8), (855.2, 200.7)),  # Tibetan High Plateau to North China Core
        ((855.2, 200.7), (886.0, 174.0)),  # North China Core to Manchuria and Amur River Basin
        ((855.2, 200.7), (908.0, 209.6)),  # North China Core to Korean Peninsula
        ((855.2, 200.7), (895.3, 240.0)),  # North China Core to East China Coast and Shanghai
        ((855.2, 200.7), (859.6, 251.6)),  # North China Core to South China and Yangtze
        ((859.6, 251.6), (854.0, 298.0)),  # South China and Yangtze to Indochina Peninsula Vietnam/Thailand
        ((782.0, 264.0), (816.0, 288.0)),  # Northern India and Himalayas to Bengal and Ganges Delta
        ((816.0, 288.0), (854.0, 298.0)),  # Bengal and Ganges Delta to Indochina Peninsula Vietnam/Thailand
        ((854.0, 298.0), (846.0, 336.0)),  # Indochina Peninsula Vietnam/Thailand to Malay Peninsula
        ((892.0, 346.0), (924.0, 358.0)),  # Borneo Heart to Sulawesi and Moluccas

        # --- Oceania ---
        ((884.0, 456.0), (924.0, 478.0)),  # Western Australia Outback to Central and South Australia
        ((924.0, 432.0), (924.0, 478.0)),  # Northern Territory Australia to Central and South Australia
        ((924.0, 478.0), (966.0, 442.0)),  # Central and South Australia to Queensland and Barrier Reef
        ((924.0, 478.0), (892.0, 497.2)),  # Central and South Australia to Great Australian Bight and Adelaide
        ((924.0, 478.0), (964.0, 488.0)),  # Central and South Australia to New South Wales and Victoria
        ((964.0, 488.0), (959.6, 529.6)),  # New South Wales and Victoria to Tasmania (Bass Strait Bridge)
        ((1018.0, 482.0), (992.2, 507.2)),  # New Zealand North Island to New Zealand South Island

        # --- Antarctica Chain ---
        ((348.9, 581.7), (396.5, 592.3)),  # Ellsworth Land to Antarctic Peninsula Graham Land
        ((396.5, 592.3), (446.0, 602.0)),  # Antarctic Peninsula Graham Land to Weddell Sea Ice Shelf
        ((446.0, 602.0), (516.0, 602.0)),  # Weddell Sea Ice Shelf to Queen Maud Land Shelf
        ((516.0, 602.0), (595.0, 595.0)),  # Queen Maud Land Shelf to Antarctic Polar Dome Hub

        # ==================== INTER-CONTINENTAL BRIDGES ====================
        # 1. North America <-> South America & Caribbean
        ((328.0, 352.0), (354.0, 382.0)),  # Central America Isthmus to Colombia and Northern Andes (Panama Bridge)
        ((382.0, 268.0), (398.0, 304.0)),  # Florida Peninsula to Cuba and Greater Antilles
        ((398.0, 304.0), (424.0, 322.0)),  # Cuba and Greater Antilles to Bahamas and Caribbean Chain

        # 2. Europe <-> Africa
        ((564.0, 260.0), (562.0, 288.0)),  # Italy Boot Peninsula to Sicily and Malta
        ((562.0, 288.0), (581.0, 326.0)),  # Sicily and Malta to Libya and Central Sahara

        # 3. Africa <-> Asia & Middle East
        ((622.0, 318.0), (670.0, 312.0)),  # Egypt and Nile Delta to Arabian Peninsula (Sinai/Red Sea Bridge)
        ((622.0, 318.0), (662.0, 270.0)),  # Egypt and Nile Delta to Levant and Mesopotamia (Suez Bridge)
        ((658.0, 366.0), (670.0, 312.0)),  # Horn of Africa Somalia to Arabian Peninsula (Bab-el-Mandeb Strait Bridge)

        # 4. Europe <-> Asia
        ((602.0, 256.0), (662.0, 270.0)),  # Balkans and Greece to Levant and Mesopotamia (Bosphorus Bridge)
        ((646.6, 209.7), (662.0, 270.0)),  # Eastern Europe Ukraine Plains to Levant and Mesopotamia (Caucasus Bridge)
        ((646.6, 209.7), (671.1, 156.2)),  # Eastern Europe Ukraine Plains to European Russia Core
        ((618.0, 178.0), (671.1, 156.2)),  # Poland and Baltic States to European Russia Core
        ((662.0, 270.0), (712.0, 256.0)),  # Levant and Mesopotamia to Persian Plateau
        ((712.0, 256.0), (745.0, 278.0)),  # Persian Plateau to Pakistan and Indus Basin
        ((745.0, 278.0), (782.0, 264.0)),  # Pakistan and Indus Basin to Northern India and Himalayas

        # 5. Asia <-> Oceania & Australia
        ((846.0, 336.0), (836.0, 372.0)),  # Malay Peninsula to Sumatra Island (Malacca Strait Bridge)
        ((836.0, 372.0), (878.0, 392.0)),  # Sumatra Island to Java Island (Sunda Strait Bridge)
        ((878.0, 392.0), (892.0, 346.0)),  # Java Island to Borneo Heart
        ((924.0, 358.0), (948.0, 386.0)),  # Sulawesi and Moluccas to Papua New Guinea
        ((948.0, 386.0), (924.0, 432.0)),  # Papua New Guinea to Northern Territory Australia (Arafura Sea Bridge)
        ((948.0, 386.0), (996.0, 396.0)),  # Papua New Guinea to Solomon Islands

        # 6. South America <-> Antarctica
        ((379.3, 572.1), (396.5, 592.3)),  # Tierra del Fuego to Antarctic Peninsula Graham Land (Drake Passage Bridge)

        # 7. North America <-> Europe (Stepping Stones)
        ((358.8, 122.9), (424.0, 112.0)),  # Baffin Island to Greenland Isle
        ((494.0, 128.0), (524.0, 166.0)),  # Iceland to Great Britain
    ]
    o.append("<!-- Inter-Island Arched Footbridges -->")
    o.append('<g stroke="#ffffff" stroke-width="2.2" stroke-linecap="round">')
    for b1, b2 in bridges:
        o.append(f'<line x1="{b1[0]}" y1="{b1[1]}" x2="{b2[0]}" y2="{b2[1]}" />')
    o.append("</g>")

    # Continental Teleferic (Sky-Way Aerial Cable Car) connecting major continental hubs
    tele_path = [us_hub, eu_hub]
    o += [
        "<!-- Continental Teleferic (Sky-Way Aerial Cable Car) -->",
        f'<path class="map-cableway" d="{poly_path(tele_path, close=False)}" />',
    ]
    for p in tele_path:
        o.append(f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="5" fill="#f43f5e" stroke="#ffffff" stroke-width="1.8" />')

    # Submerged suites in coral lagoon (Indian Ocean)
    sub_suites = (695, 405)
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
# 3. CHAMELEON ISLANDS (CHAMELEON ON A BRANCH: TIGHTLY GROUPED ARCHIPELAGO)
# ==========================================================================
# The chameleon silhouette is modelled as a continuous "tube" (snout -> body -> spiral tail)
# with a per-point dorsal / ventral half-width. The tube is then cut into many separate
# islands by narrow dredged channels (transverse cuts + a lateral belly channel), so the
# islands sit tightly together like the World continents and read as one animal.
CH_GAP = 7  # width of the dredged channels between neighbouring islands


def _catmull_dense(knots, step=3.0):
    """Densely sample a Catmull-Rom spline through knots (x, y, wt, wb); widths interpolate linearly."""
    pad = [knots[0]] + list(knots) + [knots[-1]]
    out = []
    for i in range(1, len(pad) - 2):
        p0, p1, p2, p3 = pad[i - 1], pad[i], pad[i + 1], pad[i + 2]
        m = max(2, int(math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / step))
        for j in range(m):
            u = j / m

            def cr(a, b, c, d):
                return 0.5 * (2 * b + (c - a) * u + (2 * a - 5 * b + 4 * c - d) * u * u + (3 * b - a - 3 * c + d) * u ** 3)

            out.append((
                cr(p0[0], p1[0], p2[0], p3[0]),
                cr(p0[1], p1[1], p2[1], p3[1]),
                p1[2] + (p2[2] - p1[2]) * u,
                p1[3] + (p2[3] - p1[3]) * u,
            ))
    out.append(tuple(knots[-1]))
    return out


class Tube:
    """A centre-line with dorsal (wt) and ventral (wb) half-widths, addressable by arc length."""

    def __init__(self, knots):
        self.p = _catmull_dense(knots)
        self.s = [0.0]
        for a, b in zip(self.p, self.p[1:]):
            self.s.append(self.s[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
        self.L = self.s[-1]
        k = len(self.p)
        self.nrm = []
        for i in range(k):
            a, b = self.p[max(0, i - 1)], self.p[min(k - 1, i + 1)]
            tx, ty = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(tx, ty) or 1.0
            self.nrm.append((-ty / ln, tx / ln))  # points to the dorsal side

    def at(self, s):
        s = min(max(s, 0.0), self.L)
        lo, hi = 0, len(self.s) - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if self.s[mid] <= s:
                lo = mid
            else:
                hi = mid
        seg = (self.s[hi] - self.s[lo]) or 1.0
        u = (s - self.s[lo]) / seg
        a, b = self.p[lo], self.p[hi]
        na, nb = self.nrm[lo], self.nrm[hi]
        nx, ny = na[0] + (nb[0] - na[0]) * u, na[1] + (nb[1] - na[1]) * u
        ln = math.hypot(nx, ny) or 1.0
        return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u,
                a[2] + (b[2] - a[2]) * u, a[3] + (b[3] - a[3]) * u, nx / ln, ny / ln)

    def off(self, s, f):
        x, y, wt, wb, nx, ny = self.at(s)
        d = f(wt, wb) if callable(f) else f
        return (x + nx * d, y + ny * d)

    def s_at_x(self, x_target):
        """First arc length where the (westward running) centre-line crosses x_target."""
        for i in range(1, len(self.p)):
            x0, x1 = self.p[i - 1][0], self.p[i][0]
            if (x0 - x_target) * (x1 - x_target) <= 0 and x0 != x1:
                return self.s[i - 1] + (self.s[i] - self.s[i - 1]) * (x0 - x_target) / (x0 - x1)
        return self.L

    def piece(self, s0, s1, lo=None, hi=None, inset=0.0, step=8.0):
        """Closed outline of the tube between s0..s1 and lateral offsets lo..hi (functions of wt, wb)."""
        lo = lo or (lambda wt, wb: -wb)
        hi = hi or (lambda wt, wb: wt)
        s0, s1 = s0 + inset, s1 - inset
        if s1 - s0 < 2:
            return None
        flo = (lambda wt, wb: lo(wt, wb) + inset)
        fhi = (lambda wt, wb: hi(wt, wb) - inset)
        _, _, wt, wb, _, _ = self.at((s0 + s1) / 2)
        if fhi(wt, wb) - flo(wt, wb) < 3:
            return None
        n_s = max(2, int((s1 - s0) / step))
        ss = [s0 + (s1 - s0) * i / n_s for i in range(n_s + 1)]
        top = [self.off(s, fhi) for s in ss]
        bot = [self.off(s, flo) for s in reversed(ss)]

        def cap(s, f_from, f_to):
            x, y, wt, wb, nx, ny = self.at(s)
            a, b = f_from(wt, wb), f_to(wt, wb)
            k = max(1, int(abs(b - a) / step))
            return [(x + nx * (a + (b - a) * j / k), y + ny * (a + (b - a) * j / k)) for j in range(1, k)]

        return top + cap(s1, fhi, flo) + bot + cap(s0, flo, fhi)


def _chaikin(pts, it=1):
    for _ in range(it):
        q = []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            q.append((0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]))
            q.append((0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1]))
        pts = q
    return pts


def smooth_closed(pts, rounds=1):
    """Round the corners (Chaikin) and emit a smooth closed cubic Bezier path."""
    pts = _chaikin(pts, rounds)
    k = len(pts)
    d = [f"M{pt(pts[0])}"]
    for i in range(k):
        p0, p1, p2, p3 = pts[(i - 1) % k], pts[i], pts[(i + 1) % k], pts[(i + 2) % k]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d.append(f"C{pt(c1)} {pt(c2)} {pt(p2)}")
    return " ".join(d) + " Z"


def circle_d(cx, cy, r):
    return f"M{n(cx - r)},{n(cy)} a{n(r)},{n(r)} 0 1 0 {n(2 * r)},0 a{n(r)},{n(r)} 0 1 0 {n(-2 * r)},0 Z"


def _spiral_knots(cx, cy, r0, r1, w0, w1, turns_rad, step=0.26):
    """Logarithmic spiral starting due north of (cx, cy), heading west and curling inward (ventrally)."""
    k_r = math.log(r0 / r1) / turns_rad
    k_w = math.log(w0 / w1) / turns_rad
    out = []
    phi = 0.0
    while phi <= turns_rad + 1e-6:
        th = 1.5 * math.pi - phi
        r = r0 * math.exp(-k_r * phi)
        w = w0 * math.exp(-k_w * phi)
        out.append((cx + r * math.cos(th), cy + r * math.sin(th), w, w))
        phi += step
    return out


# Head -> body -> tail centre-line knots (x, y, dorsal half-width, ventral half-width)
CH_SPIRAL = (368, 418)
CH_BODY_KNOTS = [
    (962, 269, 7, 8),      # blunt snout tip
    (946, 264, 17, 20),
    (908, 255, 30, 35),
    (868, 252, 36, 44),    # head (turret eye)
    (826, 257, 36, 44),    # back of the head
    (786, 267, 31, 38),    # neck
    (742, 262, 44, 51),    # shoulder
    (682, 248, 54, 58),
    (612, 242, 58, 60),    # crest of the arched back
    (542, 250, 55, 57),
    (476, 270, 45, 48),    # hip
    (428, 288, 30, 31),    # tail base
] + _spiral_knots(CH_SPIRAL[0], CH_SPIRAL[1], 124, 24, 28, 6, 7.2)

# Limbs (shoulder / hip -> elbow / knee -> wrist / ankle): thigh and shin are separate islands
CH_LIMBS = {
    "hind": [(520, 320, 16, 16), (566, 394, 13, 13), (536, 476, 10, 10)],
    "fore": [(744, 326, 16, 16), (704, 400, 13, 13), (746, 476, 10, 10)],
}


def branch_y(x):
    """Gently arched branch breakwater running beneath the chameleon."""
    return 545 - 35 * math.sin(math.pi * (x - 110) / 1000)


def chameleon_svg(t):
    g = CH_GAP
    body = Tube(CH_BODY_KNOTS)
    sx = body.s_at_x

    sand, green = [], []

    def add(poly, name, kind="sand", green_poly=None, hole=None):
        if not poly:
            return
        d = smooth_closed(poly)
        if hole:
            d += " " + circle_d(*hole)
        sand.append((name, d, kind, hole is not None))
        if green_poly:
            dg = smooth_closed(green_poly)
            if hole:
                dg += " " + circle_d(hole[0], hole[1], hole[2] + 6)
            green.append((name, dg, hole is not None))

    # ---- Transverse cuts along the head, body and tail ----------------------------------
    cuts = [0.0, sx(886), sx(806), sx(754), sx(682), sx(546), sx(470)]
    s = sx(470) + 70
    seg_len = 66.0
    while s < body.L - 30:
        cuts.append(s)
        seg_len = max(32.0, seg_len * 0.9)
        s += seg_len
    cuts.append(body.L)

    lateral = lambda frac: (lambda wt, wb: wt - frac * (wt + wb))  # noqa: E731
    split_mouth = lateral(0.55)
    split_belly = lateral(0.62)
    hg = g / 2.0

    def above(f):
        return lambda wt, wb: f(wt, wb) + hg

    def below(f):
        return lambda wt, wb: f(wt, wb) - hg

    names_tail = iter(range(1, 40))
    eye = (858, 242, 12)
    hole = (eye[0], eye[1], eye[2] + 6)
    road_ranges = []
    bridge_lines = []

    for i in range(len(cuts) - 1):
        a = cuts[i] + (hg if i > 0 else 0)
        b = cuts[i + 1] - (hg if i + 1 < len(cuts) - 1 else 0)
        mid = (a + b) / 2
        if i == 0:  # jaws: upper and lower, divided by the mouth channel
            add(body.piece(a, b, lo=above(split_mouth)), "Upper Jaw Isle", green_poly=body.piece(a, b, lo=above(split_mouth), inset=7))
            add(body.piece(a, b, hi=below(split_mouth)), "Lower Jaw Isle")
        elif i == 1:  # back of the head, ringed lagoon around the turret eye
            add(body.piece(a, b), "Head Crown Isle", green_poly=body.piece(a, b, inset=9), hole=hole)
        elif i == 2:
            add(body.piece(a, b), "Neck Isle", green_poly=body.piece(a, b, inset=9))
        elif i in (3, 4, 5):  # shoulder, mid-back, rump: dorsal island + belly islands
            label = {3: "Shoulder", 4: "Grand Pavilion Back", 5: "Rump"}[i]
            add(body.piece(a, b, lo=above(split_belly)), f"{label} Dorsal Isle", green_poly=body.piece(a, b, lo=above(split_belly), inset=9))
            belly_cuts = [a, b] if i != 4 else [a, (a + b) / 2, b]
            for j in range(len(belly_cuts) - 1):
                ba = belly_cuts[j] + (hg if j > 0 else 0)
                bb = belly_cuts[j + 1] - (hg if j + 1 < len(belly_cuts) - 1 else 0)
                add(body.piece(ba, bb, hi=below(split_belly)), f"{label} Belly Isle {j + 1}")
                bm = (ba + bb) / 2
                bridge_lines.append((body.off(bm, lambda wt, wb: split_belly(wt, wb) + hg + 5),
                                     body.off(bm, lambda wt, wb: split_belly(wt, wb) - hg - 5)))
        else:
            k = next(names_tail)
            _, _, wt, wb, _, _ = body.at(mid)
            gp = body.piece(a, b, inset=8) if wt + wb > 26 else None
            add(body.piece(a, b), f"Spiral Tail Isle {k}", green_poly=gp)
        road_ranges.append((a, b))

    # ---- Casque helmet and dorsal crest islets ---------------------------------------------
    s_c0, s_c1 = sx(880), sx(796)
    casque = [body.off(s_c0 + (s_c1 - s_c0) * j / 10, lambda wt, wb: wt + g) for j in range(11)]
    casque_peak = (800, 172)
    casque_poly = casque + [(casque_peak[0] - 4, casque_peak[1] + 6), casque_peak, (casque_peak[0] + 10, casque_peak[1] + 2)]
    add(casque_poly, "Casque Helmet Isle")
    casque_core = [(828, 208), (810, 186), (850, 209)]
    green.append(("Casque Helmet Isle", smooth_closed(casque_core, 2), False))

    for k, xc in enumerate(range(764, 470, -30), 1):
        sc = sx(xc)
        base_l = body.off(sc - 8, lambda wt, wb: wt + g)
        base_r = body.off(sc + 8, lambda wt, wb: wt + g)
        tip = body.off(sc, lambda wt, wb: wt + g + 15)
        add([base_r, tip, base_l], f"Dorsal Crest Islet {k}", kind="crest")

    # ---- Limbs: thigh / upper arm, shin / forearm and gripping claws ------------------------
    limb_meta = {}
    for limb, knots in CH_LIMBS.items():
        tube = Tube(knots)
        knee = tube.s[min(range(len(tube.p)), key=lambda q: math.hypot(tube.p[q][0] - knots[1][0], tube.p[q][1] - knots[1][1]))]
        upper = "Hindlimb Thigh" if limb == "hind" else "Forelimb Upper Arm"
        lower = "Hindlimb Shin" if limb == "hind" else "Forelimb Forearm"
        add(tube.piece(0, knee - hg), f"{upper} Isle", green_poly=tube.piece(0, knee - hg, inset=7))
        add(tube.piece(knee + hg, tube.L), f"{lower} Isle")
        bridge_lines.append((tube.off(knee - hg - 5, 0), tube.off(knee + hg + 5, 0)))
        top = tube.off(0, 0)
        bridge_lines.append((top, (top[0], top[1] - 14)))
        ax, ay = knots[-1][0], knots[-1][1]
        for side in (-1, 1):  # zygodactyl foot: two claw bundles straddling the branch
            ck = [(ax + side * 6, ay + 6, 5, 5), (ax + side * 18, ay + 12, 4.5, 4.5), (ax + side * 27, ay + 19, 2.5, 2.5)]
            ct = Tube(ck)
            add(ct.piece(0, ct.L), f"{lower} Claw {'East' if side > 0 else 'West'}")
        limb_meta[limb] = {"upper_mid": tube.off(knee / 2, 0)}

    # ---- Branch breakwater (with navigation channels) and leaf islets ----------------------
    br_knots = [(x, branch_y(x), 9, 9) for x in range(110, 1111, 50)]
    br_knots[0] = (110, branch_y(110), 4, 4)
    br_knots[-1] = (1110, branch_y(1110), 4, 4)
    branch = Tube(br_knots)
    br_cut_x = [300, 640, 900]
    br_cut_s = []
    for xc in br_cut_x:
        for q in range(1, len(branch.p)):
            if branch.p[q - 1][0] <= xc <= branch.p[q][0]:
                br_cut_s.append(branch.s[q])
                break
    br_cuts = [0.0] + br_cut_s + [branch.L]
    gate_pts = []
    for i in range(len(br_cuts) - 1):
        a = br_cuts[i] + (5 if i > 0 else 0)
        b = br_cuts[i + 1] - (5 if i + 1 < len(br_cuts) - 1 else 0)
        add(branch.piece(a, b), f"Branch Breakwater {i + 1}", green_poly=branch.piece(a, b, inset=5.5))
        if i > 0:
            gate_pts.append((branch.off(a, 0), branch.off(br_cuts[i] - 5, 0)))

    twig_r = Tube([(1006, branch_y(1006) - 13, 5, 5), (1034, 500, 4.5, 4.5), (1060, 482, 4, 4)])
    add(twig_r.piece(0, twig_r.L), "East Twig Isle")
    leaf_r = (1092, 458)
    sand.append(("Marine Station Leaf Isle", smooth_island(leaf_r[0], leaf_r[1], 26, 13, rot=-38, seed=5), "sand", False))
    green.append(("Marine Station Leaf Isle", smooth_island(leaf_r[0], leaf_r[1], 15, 6, rot=-38, seed=9), False))
    twig_l = Tube([(176, branch_y(176) + 14, 5, 5), (160, 574, 4.5, 4.5), (146, 586, 4, 4)])
    add(twig_l.piece(0, twig_l.L), "West Twig Isle")
    leaf_l = (122, 604)
    sand.append(("Power Hub Leaf Isle", smooth_island(leaf_l[0], leaf_l[1], 24, 12, rot=35, seed=7), "sand", False))
    green.append(("Power Hub Leaf Isle", smooth_island(leaf_l[0], leaf_l[1], 14, 6, rot=35, seed=11), False))

    # ---- Projecting tongue: stepping-stone islets to the Paradise atoll --------------------
    tongue = [(990, 275, 11, 5, 8), (1018, 280, 11, 5, 10), (1046, 285, 11, 5.5, 10), (1074, 289, 11, 6, 8)]
    for k, (x, y, rx, ry, rot) in enumerate(tongue):
        sand.append((f"Tongue Stepping Islet {k + 1}", smooth_island(x, y, rx, ry, rot=rot, seed=k + 2), "sand", False))
    villas = (1122, 294)
    sand.append(("Paradise Atoll", smooth_island(villas[0], villas[1], 27, 25, rot=10, seed=4) + " " + circle_d(villas[0], villas[1], 13), "sand", True))

    # ---------------------------------------------------------------------------------------
    # SVG OUTPUT
    # ---------------------------------------------------------------------------------------
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
        '<stop offset="0%" stop-color="#4ade80" stop-opacity="0.3" />',
        '<stop offset="60%" stop-color="#38bdf8" stop-opacity="0.18" />',
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
        '<ellipse cx="620" cy="370" rx="540" ry="290" fill="url(#cham-glow)" />',
        "<!-- Outer Protective Bio-Dyke Reef Buffer -->",
        '<ellipse cx="620" cy="372" rx="560" ry="290" class="map-reef" opacity="0.45" stroke-dasharray="10 8" stroke-width="2.5" fill="none" />',
        "<!-- Shallow Reef Halo hugging the Archipelago -->",
        '<g fill="none" stroke="#2ba29e" stroke-linecap="round" stroke-linejoin="round" opacity="0.35">',
        f'<path d="{poly_path([body.off(s, lambda wt, wb: wt + 4) for s in [body.L * q / 120 for q in range(121)]], close=False)}" stroke-width="16" />',
        "</g>",
        "<!-- Mainland Nova Aurelia Coastline (Bottom) -->",
        '<path class="map-sand" d="M0,656 Q300,642 600,646 Q900,642 1200,656 L1200,700 L0,700 Z" />',
        '<rect x="0" y="670" width="1200" height="30" class="map-urban" />',
        '<line x1="0" y1="670" x2="1200" y2="670" stroke="#ffffff" stroke-width="2.5" />',
    ]

    o.append(f"<!-- {len(sand)} DISTINCT ISLANDS FORMING A CHAMELEON ON A BRANCH (ZERO OVERLAPS) -->")
    o.append('<g id="chameleon-islands-group">')
    for name, d, kind, has_hole in sand:
        cls = "map-reef" if kind == "crest" else "map-sand"
        rule = ' fill-rule="evenodd"' if has_hole else ""
        o.append(f"<!-- {name} -->")
        o.append(f'<path class="{cls}" d="{d}"{rule} />')
    o.append("</g>")
    o.append("<!-- Island Greenery Cores -->")
    o.append('<g id="chameleon-greenery-group">')
    for name, d, has_hole in green:
        rule = ' fill-rule="evenodd"' if has_hole else ""
        o.append(f'<path class="map-greenery" d="{d}"{rule} />')
    o.append("</g>")

    # Waterfront villas dotted along the outer coast of the spiral tail
    villa_paths = []
    for a, b in road_ranges[6:]:
        _, _, wt, wb, _, _ = body.at((a + b) / 2)
        if wt < 9:
            continue
        pts = [body.off(a + (b - a) * q / 8, lambda wt, wb: wt - 4) for q in range(1, 8)]
        villa_paths.append(poly_path(pts, close=False))
    o += [
        "<!-- Spiral Tail Waterfront Villas -->",
        f'<path class="map-frond-villas" d="{" ".join(villa_paths)}" stroke-width="2.6" stroke-dasharray="0.1 7" />',
    ]

    # Chameleon Boulevard: continuous road from snout to tail tip, bridging every channel
    s_road_end = body.L - 26
    road_pts = [body.off(sx(930) + (s_road_end - sx(930)) * q / 160, lambda wt, wb: 0.28 * wt) for q in range(161)]
    o += [
        "<!-- Chameleon Boulevard (bridges every channel from the snout to the spiral tail) -->",
        f'<path class="map-road" d="{poly_path(road_pts, close=False)}" />',
        "<!-- Inter-Island Footbridges (belly channel, knees and limb causeways) -->",
        '<g stroke="#ffffff" stroke-width="2.2" stroke-linecap="round">',
    ]
    for p1, p2 in bridge_lines:
        o.append(f'<line x1="{n(p1[0])}" y1="{n(p1[1])}" x2="{n(p2[0])}" y2="{n(p2[1])}" />')
    cq = body.off(sx(838), lambda wt, wb: wt - 3)
    o.append(f'<line x1="{n(cq[0])}" y1="{n(cq[1])}" x2="{n(cq[0] - 4)}" y2="{n(cq[1] - 18)}" />')
    o.append("</g>")

    # Branch navigation gates
    o.append('<g class="twinkle">')
    for p1, p2 in gate_pts:
        o.append(f'<circle cx="{n(p1[0])}" cy="{n(p1[1])}" r="3.5" fill="#22c55e" />')
        o.append(f'<circle cx="{n(p2[0])}" cy="{n(p2[1])}" r="3.5" fill="#ef4444" />')
    o.append("</g>")

    # Casque spire beacon
    o += [
        "<!-- Golden Casque Crest Beacon -->",
        f'<circle cx="{casque_peak[0]}" cy="{casque_peak[1]}" r="3.5" fill="#c29a57" class="twinkle" />',
    ]

    # Spiral Tail Marina inside the coil
    mar = (CH_SPIRAL[0] + 4, CH_SPIRAL[1] + 2)
    o += [
        "<!-- Spiral Tail Deepwater Harbor Pontoons -->",
        '<g stroke="#ffffff" stroke-width="1.8" stroke-linecap="round">',
        f'<line x1="{mar[0] - 22}" y1="{mar[1] + 30}" x2="{mar[0] - 22}" y2="{mar[1] + 14}" />',
        f'<line x1="{mar[0] + 22}" y1="{mar[1] - 34}" x2="{mar[0] + 22}" y2="{mar[1] - 18}" />',
        "</g>",
    ]

    # Glass-Domed Grand Pavilion on the mid-back island
    pav_s = (sx(682) + sx(546)) / 2
    pav = body.off(pav_s, lambda wt, wb: 0.3 * wt)
    pav = (round(pav[0], 1), round(pav[1], 1))
    o += [
        "<!-- Glass-Domed Central Grand Pavilion -->",
        f'<g transform="translate({n(pav[0])}, {n(pav[1])})">',
        '<ellipse cx="0" cy="0" rx="36" ry="20" fill="#002244" opacity="0.8" />',
        '<ellipse cx="0" cy="0" rx="30" ry="16" fill="#38bdf8" filter="url(#glass-glow)" opacity="0.85" />',
        '<ellipse cx="0" cy="0" rx="20" ry="11" fill="none" stroke="#ffffff" stroke-width="1.4" />',
        '<line x1="-30" y1="0" x2="30" y2="0" stroke="#ffffff" stroke-width="1.6" />',
        '<line x1="0" y1="-16" x2="0" y2="16" stroke="#ffffff" stroke-width="1.6" />',
        '<circle cx="0" cy="0" r="4.5" fill="#f5c46e" class="twinkle" />',
        "</g>",
    ]

    # Revolving 360 Degree Observation Eye Dome inside its ringed lagoon
    o += [
        "<!-- Revolving 360 Degree Observation Eye Dome (Turret Eye Islet) -->",
        f'<circle cx="{eye[0]}" cy="{eye[1]}" r="{eye[2]}" class="map-sand" />',
        f'<g transform="translate({eye[0]}, {eye[1]})">',
        '<circle cx="0" cy="0" r="9" fill="#0f172a" stroke="#ffffff" stroke-width="1.5" />',
        '<circle cx="0" cy="0" r="6" fill="#38bdf8" opacity="0.9" />',
        '<circle cx="2" cy="-2" r="2.2" fill="#ffffff" />',
        "</g>",
    ]

    # International Youth Innovation Center on the forelimb
    youth = limb_meta["fore"]["upper_mid"]
    youth = (round(youth[0], 1), round(youth[1], 1))
    o += [
        "<!-- International Youth Innovation Center Campus -->",
        f'<rect x="{n(youth[0] - 9)}" y="{n(youth[1] - 12)}" width="18" height="24" rx="3" class="map-urban" />',
    ]

    # Marine Biology and Dolphin Station on the east leaf islet
    bio = leaf_r
    o += [
        "<!-- Marine Biology and Dolphin Station -->",
        f'<circle cx="{bio[0]}" cy="{bio[1]}" r="9" class="map-sea-lagoon" stroke="#ffffff" stroke-width="1.6" />',
        f'<path d="M{bio[0] - 3},{bio[1] - 2} C{bio[0] + 3},{bio[1] - 5} {bio[0] + 5},{bio[1] + 3} {bio[0]},{bio[1] + 4}" stroke="#0284c7" stroke-width="2" fill="none" />',
    ]

    # Floating Eco-District moored in the sheltered lagoon between the legs
    eco = (632, 420)
    o += ["<!-- Experimental Floating Eco-Communities (Sheltered Belly Lagoon) -->", '<g fill="#2dd4bf" stroke="#ffffff" stroke-width="1">']
    for dx, dy in ((-30, -22), (-12, -30), (8, -24), (26, -12), (-24, 2), (22, 10), (-8, 24), (12, 30)):
        o.append(f'<rect x="{eco[0] + dx - 5}" y="{eco[1] + dy - 5}" width="10" height="10" rx="2" />')
    o.append("</g>")

    # Tidal Power Hub on the west leaf islet
    o += [
        "<!-- Renewable Marine Power Hub -->",
        f'<g transform="translate({leaf_l[0]}, {leaf_l[1]})">',
        '<circle cx="0" cy="0" r="8" fill="#0284c7" stroke="#ffffff" stroke-width="1.4" />',
        '<path d="M0,-6 L0,6 M-6,0 L6,0" stroke="#ffffff" stroke-width="1.8" class="spin" />',
        "</g>",
    ]

    # Paradise Islands Overwater Villas on the tongue-tip atoll
    o += [
        "<!-- Paradise Islands Overwater Bungalows and Coral Nursery -->",
        f'<circle cx="{villas[0]}" cy="{villas[1]}" r="19" fill="none" stroke="#c29a57" stroke-width="2.5" stroke-dasharray="3 4" />',
        f'<circle cx="{villas[0]}" cy="{villas[1]}" r="13" class="map-sea-lagoon" stroke="#2dd4bf" stroke-width="1.6" />',
        f'<circle cx="{villas[0]}" cy="{villas[1]}" r="3.5" fill="#38bdf8" class="bob" />',
    ]
    tongue_pts = [body.off(sx(962) + 1, 0)] + [(x, y) for x, y, *_ in tongue] + [(villas[0] - 27, villas[1])]
    o += [
        "<!-- Overwater Boardwalk linking the Tongue Islets -->",
        f'<path d="{poly_path(tongue_pts, close=False)}" fill="none" stroke="#c29a57" stroke-width="2" stroke-linecap="round" />',
    ]

    # Sub-Sea Metro Tunnel
    metro = body.off((sx(682) + sx(546)) / 2 + 30, lambda wt, wb: split_belly(wt, wb) - 0.5 * (split_belly(wt, wb) + wb))
    metro = (round(metro[0], 1), round(metro[1], 1))
    o += [
        "<!-- Sub-Sea Metro Tunnel (Nova Aurelia to Portal, Pavilion, Eye Dome and Spiral Marina) -->",
        '<g fill="none" stroke="#f5c46e" stroke-dasharray="8 4">',
        f'<path d="M{n(metro[0])},670 L{n(metro[0])},{n(metro[1])} L{n(pav[0])},{n(pav[1])}" stroke-width="3" />',
        f'<path d="M{n(pav[0])},{n(pav[1])} C700,200 790,200 {eye[0]},{eye[1]}" stroke-width="2.5" />',
        f'<path d="M{n(metro[0])},{n(metro[1])} C520,330 430,360 {mar[0]},{mar[1]}" stroke-width="2.5" />',
        "</g>",
    ]
    for x, y in (metro, pav, (eye[0], eye[1]), mar):
        o.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="5" fill="#f5c46e" stroke="#ffffff" stroke-width="2" />')

    # Water taxis and labels
    o += [
        "<!-- Autonomous Electric Water Taxi Marine Paths -->",
        '<g class="map-ferry">',
        f'<path d="M{mar[0] - 60},{mar[1] + 40} C200,560 170,620 300,640" />',
        f'<path d="M{eco[0]},{eco[1] + 40} C640,560 700,610 760,640" />',
        f'<path d="M{villas[0]},{villas[1] + 28} C1130,380 1120,520 1060,640" />',
        "</g>",
        "<!-- Geographic Labels -->",
        '<g class="map-label-group">',
        f'<text class="map-label-text" x="{n(pav[0])}" y="148">{t["pavilion"]}</text>',
        f'<text class="map-label-text" x="{mar[0]}" y="502">{t["marina"]}</text>',
        f'<text class="map-label-text" x="{villas[0] - 20}" y="250">{t["villas"]}</text>',
        f'<text class="map-label-text" x="300" y="566">{t["branch"]}</text>',
        "</g>",
    ]

    # 8 Interactive Hotspots
    spots = [
        (1, pav[0], pav[1], "#38bdf8", "Glass-Domed Central Grand Pavilion", 12),
        (2, eye[0], eye[1], "#f5c46e", "Revolving 360 Degree Eye Dome", 11),
        (3, youth[0], youth[1], "#38bdf8", "Youth Innovation Center", 11),
        (4, mar[0], mar[1], "#0284c7", "Spiral Tail Marina", 11),
        (5, villas[0], villas[1], "#c29a57", "Paradise Islands Overwater Villas", 11),
        (6, bio[0], bio[1], "#22c55e", "Marine Biology and Dolphin Station", 11),
        (7, eco[0], eco[1], "#2dd4bf", "Floating Eco-District", 11),
        (8, metro[0], metro[1], "#f5c46e", "Sub-Sea Metro Tunnel Portal", 11),
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
