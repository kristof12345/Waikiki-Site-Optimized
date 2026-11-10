import re
import xml.etree.ElementTree as ET
import sys
import os
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

# ==============================================================================
# CONST ARRAY OF CITIES
# Position (x, y px), Name, Type ('Capital', 'Large', 'Small')
# ==============================================================================
CITIES = [
    {
        "name": "Nova Aurelia",
        "pos": (412, 330),
        "type": "Capital",
        "label": {"anchor": "middle", "offset": (0, 30), "size": 14, "weight": 700}
    },
    {
        "name": "Miami",
        "pos": (451, 105),
        "type": "Large",
        "label": {"anchor": "start", "offset": (15, 0), "size": 12, "weight": 600}
    },
    {
        "name": "Key West",
        "pos": (412, 160),
        "type": "Small",
        "label": {"anchor": "end", "offset": (-10, 5), "size": 10, "weight": 400}
    },
    {
        "name": "Havana",
        "pos": (396, 260),
        "type": "Large",
        "label": {"anchor": "end", "offset": (-10, -10), "size": 12, "weight": 600}
    },
    {
        "name": "Mega Pyramid City",
        "pos": (446, 294),
        "type": "Small",
        "has_pyramid": True,
        "label": {"anchor": "start", "offset": (15, -5), "size": 10, "weight": 400}
    },
    {
        "name": "Morón",
        "pos": (658, 348),
        "type": "Large",
        "label": {"anchor": "middle", "offset": (0, -15), "size": 12, "weight": 600}
    },
    {
        "name": "Port Royal",
        "pos": (742, 397),
        "type": "Small",
        "label": {"anchor": "start", "offset": (15, -5), "size": 10, "weight": 400}
    },
    {
        "name": "Santiago",
        "pos": (824, 508),
        "type": "Large",
        "label": {"anchor": "end", "offset": (-15, 15), "size": 12, "weight": 600}
    },
    {
        "name": "Carib City",
        "pos": (980, 510),
        "type": "Small",
        "label": {"anchor": "middle", "offset": (0, -20), "size": 10, "weight": 400}
    },
    {
        "name": "Blue Bay",
        "pos": (1000, 540),
        "type": "Small",
        "label": {"anchor": "middle", "offset": (0, 20), "size": 10, "weight": 400}
    },
    {
        "name": "Cap-Haïtien",
        "pos": (1123, 448),
        "type": "Large",
        "label": {"anchor": "middle", "offset": (0, -15), "size": 12, "weight": 600}
    },
    {
        "name": "Port-au-Prince",
        "pos": (1115, 540),
        "type": "Large",
        "label": {"anchor": "middle", "offset": (0, 25), "size": 12, "weight": 600}
    },
    {
        "name": "Kingston",
        "pos": (860, 605),
        "type": "Large",
        "label": {"anchor": "start", "offset": (15, 15), "size": 12, "weight": 600}
    },
    {
        "name": "Montego Bay",
        "pos": (786, 578),
        "type": "Small",
        "label": {"anchor": "end", "offset": (-10, -5), "size": 10, "weight": 400}
    },
    {
        "name": "Pinar del Río",
        "pos": (220, 310),
        "type": "Small",
        "label": {"anchor": "end", "offset": (-10, 0), "size": 10, "weight": 400}
    },
    {
        "name": "Santo Domingo",
        "pos": (1304, 540),
        "type": "Large",
        "label": {"anchor": "middle", "offset": (0, 25), "size": 12, "weight": 600}
    },
    {
        "name": "Punta Cana",
        "pos": (1410, 532),
        "type": "Small",
        "label": {"anchor": "middle", "offset": (0, -14), "size": 10, "weight": 400}
    },
    {
        "name": "Santa Cruz del Sur",
        "pos": (634, 448),
        "type": "Small",
        "label": {"anchor": "middle", "offset": (0, 20), "size": 10, "weight": 400}
    }
]

# ==============================================================================
# CONST ARRAY OF CONNECTIONS
# From, To, Type ('Maglev', 'Hyperloop', 'Tunnel', 'Main Line', 'Maritime', 'Elevated')
# ==============================================================================
CONNECTIONS = [
    {
        "from": "Morón",
        "to": "Santa Cruz del Sur",
        "type": "Main Line",
        "bend": 0.05,
        "dur": "3.0s"
    },
    {
        "from": "Havana",
        "to": "Pinar del Río",
        "type": "Main Line",
        "bend": -0.1,
        "dur": "3.5s"
    },
    {
        "from": "Port-au-Prince",
        "to": "Santo Domingo",
        "type": "Main Line",
        "bend": 0.05,
        "dur": "3.5s"
    },
    {
        "from": "Santo Domingo",
        "to": "Punta Cana",
        "type": "Main Line",
        "bend": 0.05,
        "dur": "2.2s"
    },
    {
        "from": "Miami",
        "to": "Key West",
        "type": "Tunnel",
        "bend": 0.15,
        "dur": "2.5s"
    },
    {
        "from": "Key West",
        "to": "Havana",
        "type": "Tunnel",
        "bend": 0.1,
        "dur": "4.0s"
    },
    {
        "from": "Havana",
        "to": "Nova Aurelia",
        "type": "Main Line",
        "bend": -0.1,
        "dur": "2.5s"
    },
    {
        "from": "Nova Aurelia",
        "to": "Morón",
        "type": "Maglev",
        "bend": 0.08,
        "dur": "4.5s"
    },
    {
        "from": "Nova Aurelia",
        "to": "Mega Pyramid City",
        "type": "Hyperloop",
        "bend": 0.0,
        "dur": "1.8s"
    },
    {
        "from": "Morón",
        "to": "Port Royal",
        "type": "Maglev",
        "bend": -0.1,
        "dur": "2.2s"
    },
    {
        "from": "Port Royal",
        "to": "Santiago",
        "type": "Maglev",
        "bend": 0.04,
        "dur": "2.0s"
    },
    {
        "from": "Santiago",
        "to": "Carib City",
        "type": "Maglev",
        "bend": -0.08,
        "dur": "5.5s"
    },
    {
        "from": "Carib City",
        "to": "Blue Bay",
        "type": "Tunnel",
        "bend": -0.08,
        "dur": "0.5s"
    },
    {
        "from": "Blue Bay",
        "to": "Port-au-Prince",
        "type": "Maglev",
        "bend": -0.08,
        "dur": "5.5s"
    },
    {
        "from": "Port-au-Prince",
        "to": "Cap-Haïtien",
        "type": "Main Line",
        "bend": -0.8,
        "dur": "3.6s"
    },
    {
        "from": "Santiago",
        "to": "Kingston",
        "type": "Maritime",
        "bend": -0.06,
        "animated": False
    },
    {
        "from": "Kingston",
        "to": "Blue Bay",
        "type": "Maritime",
        "bend": -0.2,
        "animated": False
    },
    {
        "from": "Nova Aurelia",
        "to": "Montego Bay",
        "type": "Maritime",
        "bend": -0.15,
        "animated": False
    }
]

CITY_BY_NAME = {c["name"].upper(): c for c in CITIES}

def get_city_pos(name_or_point):
    """Returns (x, y) coordinates for a city name or a direct (x, y) tuple."""
    if isinstance(name_or_point, (tuple, list)):
        return name_or_point
    key = str(name_or_point).upper()
    if key in CITY_BY_NAME:
        return CITY_BY_NAME[key]["pos"]
    raise KeyError(f"City '{name_or_point}' not found in CITIES")

def get_connection_style(conn_type):
    """Returns the SVG styling attributes and animation parameters for each connection type."""
    t = conn_type.strip().lower()
    if "maglev" in t:
        return {
            "attrs": 'class="k-coral" stroke-width="5.5" stroke-linecap="round"',
            "dot_r": 5.0,
            "default_dur": "4.5s"
        }
    elif "hyperloop" in t:
        return {
            "attrs": 'class="k-gold" stroke-width="5.5" stroke-linecap="round"',
            "dot_r": 4.0,
            "default_dur": "1.8s"
        }
    elif "tunnel" in t:
        return {
            "attrs": 'class="k-ink" stroke-width="4.5" stroke-dasharray="2 7" stroke-linecap="round"',
            "dot_r": 4.5,
            "default_dur": "2.5s"
        }
    elif "main" in t:
        return {
            "attrs": 'class="k-ink2" stroke-width="4.5" stroke-linecap="round"',
            "dot_r": 5.0,
            "default_dur": "4.0s"
        }
    elif "maritime" in t or "sea" in t:
        return {
            "attrs": 'class="k-sea" stroke-width="3.5" stroke-dasharray="6 4" stroke-linecap="round"',
            "dot_r": 4.0,
            "default_dur": "6.0s"
        }
    elif "elevated" in t:
        return {
            "attrs": 'class="k-ink2" stroke-width="2.8" stroke-dasharray="4 4" stroke-linecap="round"',
            "dot_r": 0,
            "default_dur": "4.0s"
        }
    else:
        return {
            "attrs": 'class="k-ink" stroke-width="3.5" stroke-linecap="round"',
            "dot_r": 4.0,
            "default_dur": "4.0s"
        }

def make_curved_path(p1, p2, bend=0.0):
    """
    Dynamically generates an SVG path (straight or cubic Bezier) between two positions.
    bend: relative deflection perpendicular to travel direction.
    Positive deflects to the right, negative deflects to the left.
    """
    x1, y1 = get_city_pos(p1)
    x2, y2 = get_city_pos(p2)
    dx = x2 - x1
    dy = y2 - y1
    dist = math.hypot(dx, dy)

    if dist < 1e-4 or abs(bend) < 1e-4:
        return f"M{x1:.0f} {y1:.0f} L{x2:.0f} {y2:.0f}"

    # Right-hand normal (dy/dist, -dx/dist)
    nx = dy / dist
    ny = -dx / dist
    offset = bend * dist

    cx1 = x1 + dx * 0.35 + nx * offset
    cy1 = y1 + dy * 0.35 + ny * offset
    cx2 = x1 + dx * 0.65 + nx * offset
    cy2 = y1 + dy * 0.65 + ny * offset

    return f"M{x1:.0f} {y1:.0f} C{cx1:.0f} {cy1:.0f}, {cx2:.0f} {cy2:.0f}, {x2:.0f} {y2:.0f}"

def merge_path_d(d_list):
    """Normalizes and combines multiple SVG path d strings into one compound path."""
    res = []
    for d in d_list:
        d = d.strip()
        if not d:
            continue
        # Convert initial relative moveto 'm X,Y' to absolute 'M X,Y l '
        # so multiple subpaths can be cleanly concatenated without offsetting each other
        d_norm = re.sub(r'^[mM]\s*([-\d.]+)[,\s]+([-\d.]+)\s*', r'M \1,\2 l ', d)
        res.append(d_norm)
    return ' '.join(res)

def get_cuba_group():
    tree = ET.parse('content/Maps/cuba.svg')
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    paths = tree.findall('.//svg:path', ns) or tree.findall('.//path')
    d_list = [p.attrib.get('d', '') for p in paths]
    merged_d = merge_path_d(d_list)
    return (
        '                        <!-- ==================== CUBA ARCHIPELAGO ==================== -->\n'
        '                        <g class="cuba-archipelago" transform="translate(90, 240) scale(1.15)">\n'
        f'                            <path class="f-sand province-path" vector-effect="non-scaling-stroke" d="{merged_d}" />\n'
        '                        </g>'
    )

def is_florida_county_visible(d, tx=88, ty=-157.4, scale=4.0, vw=1800, vh=650):
    tokens = re.findall(r'([a-zA-Z])|([-+]?(?:\d*\.\d+|\d+))', d)
    cmd = None
    cur_x, cur_y = 0.0, 0.0
    start_x, start_y = 0.0, 0.0
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t[0]:
            cmd = t[0]; i += 1; continue
        if not cmd:
            i += 1; continue
        if cmd in ['m', 'M']:
            if cmd == 'm':
                cur_x += float(t[1]); i += 1
                cur_y += float(tokens[i][1]); i += 1
            else:
                cur_x = float(t[1]); i += 1
                cur_y += float(tokens[i][1]); i += 1
            start_x, start_y = cur_x, cur_y
            cmd = 'l' if cmd == 'm' else 'L'
        elif cmd == 'l':
            cur_x += float(t[1]); i += 1
            cur_y += float(tokens[i][1]); i += 1
        elif cmd == 'L':
            cur_x = float(t[1]); i += 1
            cur_y += float(tokens[i][1]); i += 1
        elif cmd == 'c':
            coords = [float(tokens[i+k][1]) for k in range(6)]
            i += 6
            cur_x += coords[4]
            cur_y += coords[5]
        elif cmd in ['z', 'Z']:
            cur_x, cur_y = start_x, start_y
        else:
            i += 1
        gx = tx + cur_x * scale
        gy = ty + cur_y * scale
        if gx < min_x: min_x = gx
        if gx > max_x: max_x = gx
        if gy < min_y: min_y = gy
        if gy > max_y: max_y = gy
    return max_x >= 0 and min_x <= vw and max_y >= 0 and min_y <= vh

def get_florida_group():
    tree = ET.parse('content/Maps/usa-fl.svg')
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    paths = tree.findall('.//svg:path', ns) or tree.findall('.//path')
    d_list = [
        p.attrib.get('d', '')
        for p in paths
        if is_florida_county_visible(p.attrib.get('d', ''))
    ]
    merged_d = merge_path_d(d_list)
    return (
        '                        <!-- ==================== FLORIDA ==================== -->\n'
        '                        <g transform="translate(88, -157.4) scale(4.0)">\n'
        f'                            <path class="f-sand florida-path" d="{merged_d}" />\n'
        '                        </g>'
    )

def get_jamaica_group():
    tree = ET.parse('content/Maps/jamaica.svg')
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    paths = tree.findall('.//svg:path', ns) or tree.findall('.//path')
    d_list = [p.attrib.get('d', '') for p in paths]
    merged_d = merge_path_d(d_list)
    return (
        '                        <!-- ==================== JAMAICA ==================== -->\n'
        '                        <g transform="translate(752.5, 566.3) scale(0.1915)">\n'
        f'                            <path class="f-sand province-path" vector-effect="non-scaling-stroke" d="{merged_d}" />\n'
        '                        </g>'
    )

def transform_path_d(d, tx=0.0, ty=0.0, sx=1.0, sy=1.0):
    """Transforms coordinates in an SVG path d string by translation and scaling."""
    tokens = re.findall(r'([a-zA-Z])|([-+]?(?:\d*\.\d+|\d+))', d)
    out = []
    cmd = None
    is_relative = False
    coord_idx = 0
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t[0]:
            cmd = t[0]
            out.append(cmd)
            is_relative = cmd.islower()
            coord_idx = 0
            i += 1
            continue
        num = float(t[1])
        if cmd in ['H', 'h']:
            new_num = (num * sx) if is_relative else (tx + num * sx)
        elif cmd in ['V', 'v']:
            new_num = (num * sy) if is_relative else (ty + num * sy)
        else:
            if coord_idx == 0:
                new_num = (num * sx) if is_relative else (tx + num * sx)
                coord_idx = 1
            else:
                new_num = (num * sy) if is_relative else (ty + num * sy)
                coord_idx = 0
        s = f'{new_num:.2f}'.rstrip('0').rstrip('.')
        if s == '-0' or s == '':
            s = '0'
        out.append(s)
        i += 1
    return ' '.join(out)

def get_hispaniola_group():
    tree_ht = ET.parse('content/Maps/haiti.svg')
    tree_do = ET.parse('content/Maps/dominican-republic.svg')
    ns = {'svg': 'http://www.w3.org/2000/svg'}

    ht_paths = tree_ht.findall('.//svg:path', ns) or tree_ht.findall('.//path')
    ht_d = merge_path_d([p.attrib.get('d', '') for p in ht_paths])

    do_paths = tree_do.findall('.//svg:path', ns) or tree_do.findall('.//path')
    do_d = merge_path_d([p.attrib.get('d', '') for p in do_paths])
    do_d_transformed = transform_path_d(do_d, tx=670.97, ty=45.06, sx=1.25826, sy=1.26938)
    hispaniola_d = f"{ht_d} {do_d_transformed}"

    return (
        '                        <!-- ==================== HISPANIOLA ==================== -->\n'
        '                        <g transform="translate(1000, 425) scale(0.247)">\n'
        f'                            <path class="f-sand province-path" vector-effect="non-scaling-stroke" d="{hispaniola_d}" />\n'
        '                        </g>'
    )

def generate_transport_corridors():
    """Generates all transport corridor lines and animated traffic dots solely based on CONNECTIONS."""
    line_paths = []
    anim_dots = []

    for conn in CONNECTIONS:
        if isinstance(conn, (tuple, list)):
            c_from = conn[0]
            c_to = conn[1]
            c_type = conn[2]
            bend = conn[3] if len(conn) > 3 else 0.0
            anim = True
            dur = None
        else:
            c_from = conn["from"]
            c_to = conn["to"]
            c_type = conn["type"]
            bend = conn.get("bend", 0.0)
            anim = conn.get("animated", True)
            dur = conn.get("dur")

        path_d = make_curved_path(c_from, c_to, bend=bend)
        style = get_connection_style(c_type)

        line_paths.append(f'                        <!-- {c_type}: {c_from} to {c_to} -->\n                        <path d="{path_d}" {style["attrs"]} />')

        if anim and style.get("dot_r", 0) > 0:
            anim_dur = dur or style.get("default_dur", "4.0s")
            dot_r = style["dot_r"]
            anim_dots.append(f'''                        <circle r="{dot_r}" class="f-white">
                            <animateMotion dur="{anim_dur}" repeatCount="indefinite" path="{path_d}" />
                        </circle>''')

    return (
        "                        <!-- ==================== TRANSPORT CORRIDORS ==================== -->\n"
        + "\n".join(line_paths)
        + "\n                        <!-- Animated Traffic Dots -->\n"
        + "\n".join(anim_dots)
    )

def generate_cities_xml(g_florida, g_bahamas, g_jamaica):
    """Generates capital markers, station nodes, white inner dots and labels dynamically from CITIES."""
    capital_xml = []
    ink_nodes = []
    white_dots = []
    pyramid_xml = []
    labels = []
    
    for c in CITIES:
        if c.get("hide_marker") and c.get("hide_label"):
            continue
            
        x, y = c["pos"]
        ctype = c["type"]
        name = c["name"].upper()
        lbl = c.get("label", {})
        dx, dy = lbl.get("offset", (0, 0))
        anchor = lbl.get("anchor", "start")
        size = lbl.get("size", 11)
        weight = lbl.get("weight", 400)
        
        if not c.get("hide_label"):
            anchor_attr = f' text-anchor="{anchor}"' if anchor != "start" else ""
            labels.append(f'                            <text x="{x + dx}" y="{y + dy}" font-size="{size}" font-weight="{weight}"{anchor_attr}>{name}</text>')
        
        if not c.get("hide_marker"):
            if ctype == "Capital":
                capital_xml.append(f'''                        <!-- Capital City Marker: {c['name']} -->
                        <g>
                            <circle cx="{x}" cy="{y}" r="16" class="f-coral pulse" />
                            <circle cx="{x}" cy="{y}" r="11" class="f-coral" />
                            <path d="M{x} {y-7} l2 4.2 4.6.6 -3.4 3.2 .9 4.5 -4.1 -2.2 -4.1 2.2 .9 -4.5 -3.4 -3.2 4.6 -.6 z" class="f-white" />
                        </g>''')
            else:
                r_ink = 7 if ctype == "Large" else (6 if c.get("has_pyramid") else 5.5)
                r_white = 2.8 if ctype == "Large" else (2.4 if name == "KINGSTON" else 2.2)
                ink_nodes.append(f'                            <circle cx="{x}" cy="{y}" r="{r_ink}" />')
                white_dots.append(f'                            <circle cx="{x}" cy="{y}" r="{r_white}" />')
                if c.get("has_pyramid"):
                    pyramid_xml.append(f'''                        <!-- Mega Pyramid Mark -->
                        <path d="M{x} {y-9} l4 7 h-8 z" class="f-gold" />''')
                
    territory_labels = f'''                            <!-- Major Territories -->
                            <text x="380" y="45" font-size="13" font-weight="600" opacity=".6" letter-spacing=".15em">{g_florida}</text>
                            <text x="530" y="70" font-size="11" font-weight="600" opacity=".45" letter-spacing=".15em">{g_bahamas}</text>
                            <text x="825" y="600" font-size="11" opacity=".55" letter-spacing=".15em" text-anchor="middle">{g_jamaica}</text>'''

    return f'''                        <!-- ==================== CAPITAL AND STATIONS ==================== -->
{chr(10).join(capital_xml)}
                        <!-- Station Network Nodes -->
                        <g class="f-ink">
{chr(10).join(ink_nodes)}
                        </g>
{chr(10).join(pyramid_xml)}
                        <g class="f-white">
{chr(10).join(white_dots)}
                        </g>
                        <!-- ==================== TYPOGRAPHY AND LABELS ==================== -->
                        <g font-size="11.5">
{chr(10).join(labels)}
{territory_labels}
                        </g>'''

def build_svg(lang="en", cuba_xml=""):
    is_hu = (lang == "hu")
    
    fl_xml = get_florida_group()
    jm_xml = get_jamaica_group()
    hi_xml = get_hispaniola_group()
    cuba_xml = cuba_xml or get_cuba_group()
    
    # Legend labels
    lbl_maglev = "MAGLEV"
    lbl_hyperloop = "HYPERLOOP"
    lbl_tunnel = "ALAGÚT" if is_hu else "TUNNEL"
    lbl_mainline = "FŐVONAL" if is_hu else "MAIN LINE"
    lbl_maritime = "TENGERI ÚTVONAL" if is_hu else "MARITIME ROUTE"
    
    # Geographic labels
    g_florida = "FLORIDA"
    g_bahamas = "BAHAMA-SZIGETEK" if is_hu else "BAHAMAS"
    g_jamaica = "JAMAICA"

    # Corridors and nodes generated dynamically
    corridors_xml = generate_transport_corridors()
    cities_xml = generate_cities_xml(g_florida, g_bahamas, g_jamaica)

    # Artificial islands position dynamically aligned with Nova Aurelia
    na_x, na_y = get_city_pos("Nova Aurelia")
    art_tx = na_x - 255
    art_ty = na_y - 292

    # Assemble SVG text
    svg = f'''<svg class="ill" viewBox="0 0 1800 650">
                    <rect width="1800" height="650" class="f-sea3" />
                    <!-- Geographic Coordinate Grid -->
                    <g class="k-white" stroke-width="1" opacity=".3">
                        <path d="M0 130h1800M0 260h1800M0 390h1800M0 520h1800M300 0v650M600 0v650M900 0v650M1200 0v650M1500 0v650" />
                    </g>
{fl_xml}
                        <!-- ==================== BAHAMAS ARCHIPELAGO ==================== -->
                        <g class="f-sand" opacity=".88" transform="translate(200, -45) scale(1.15)">
                            <path d="M294 72 c16 -5 36 -6 49 -2 c4 2 2 6 -3 7 c-16 3 -36 2 -48 -2 c-4 -1 -2 -5 2 -5 z" />
                            <path d="M352 62 c8 2 13 10 11 18 c-2 9 -10 15 -14 12 c-3 -2 -1 -7 2 -12 c3 -5 3 -14 1 -18 z" />
                            <ellipse cx="292" cy="154" rx="4.5" ry="2.8" />
                            <circle cx="328" cy="118" r="3.2" />
                            <path d="M318 152 c9 -6 22 -4 26 5 c4 10 2 26 -4 37 c-6 11 -16 15 -21 9 c-5 -7 -3 -24 1 -35 c2 -8 1 -12 -2 -16 z" />
                            <circle cx="370" cy="176" r="3" />
                            <path d="M382 192 c12 -4 26 -2 32 4 c3 3 0 7 -4 7 c-12 1 -24 -2 -28 -6 z" />
                            <circle cx="430" cy="226" r="2.8" />
                        </g>
{cuba_xml}
{jm_xml}
{hi_xml}
{corridors_xml}
{cities_xml}
                        <!-- ==================== MAP LEGEND BOX ==================== -->
                        <g transform="translate(1460 550)" font-size="10">
                            <rect x="-14" y="-12" width="314" height="70" rx="12" class="f-white" opacity=".92" />
                            <path d="M0 2h26" class="k-coral" stroke-width="5" stroke-linecap="round" /><text x="34" y="5.5" font-weight="600">{lbl_maglev}</text>
                            <path d="M125 2h26" class="k-gold" stroke-width="5" stroke-linecap="round" /><text x="159" y="5.5" font-weight="600">{lbl_hyperloop}</text>
                            <path d="M0 26h26" class="k-ink" stroke-width="4" stroke-dasharray="2 7" stroke-linecap="round" /><text x="34" y="29.5" font-weight="600">{lbl_tunnel}</text>
                            <path d="M125 26h26" class="k-ink2" stroke-width="4" stroke-linecap="round" /><text x="159" y="29.5" font-weight="600">{lbl_mainline}</text>
                            <path d="M0 46h26" class="k-sea" stroke-width="3.5" stroke-dasharray="5 3" stroke-linecap="round" /><text x="34" y="49.5" font-weight="600">{lbl_maritime}</text>
                        </g>
                </svg>'''
    return svg

def get_brazil_states():
    """Extract state SVG path data from content/Maps/brazil.svg."""
    brazil_svg = ROOT / "content" / "Maps" / "brazil.svg"
    tree = ET.parse(brazil_svg)
    states = {}
    for elem in tree.getroot().iter():
        eid = elem.attrib.get("id", "")
        if eid.startswith("BR-") and "d" in elem.attrib:
            states[eid] = elem.attrib["d"]
    return states


AMAZONIA_STATE_IDS = [
    "BR-AC", "BR-AM", "BR-RR", "BR-RO", "BR-PA", "BR-AP",
    "BR-MT", "BR-MA", "BR-TO", "BR-PI", "BR-CE",
]

BRAZILIA_STATE_IDS = [
    "BR-MG", "BR-MS", "BR-PB", "BR-PE", "BR-RJ", "BR-RN",
    "BR-RS", "BR-SC", "BR-SE", "BR-SP", "BR-GO", "BR-BA",
    "BR-PR", "BR-ES", "BR-DF", "BR-AL",
]


def build_legend_xml(lang):
    is_hu = lang == "hu"
    lbl_maglev = "MAGLEV"
    lbl_hyperloop = "HYPERLOOP"
    lbl_tunnel = "ALAGÚT" if is_hu else "TUNNEL"
    lbl_mainline = "FŐVONAL" if is_hu else "MAIN LINE"
    lbl_maritime = "TENGERI ÚTVONAL" if is_hu else "MARITIME ROUTE"
    return f'''                        <!-- ==================== MAP LEGEND BOX ==================== -->
                        <g transform="translate(1460 550)" font-size="10">
                            <rect x="-14" y="-12" width="314" height="70" rx="12" class="f-white" opacity=".92" />
                            <path d="M0 2h26" class="k-coral" stroke-width="5" stroke-linecap="round" /><text x="34" y="5.5" font-weight="600">{lbl_maglev}</text>
                            <path d="M125 2h26" class="k-gold" stroke-width="5" stroke-linecap="round" /><text x="159" y="5.5" font-weight="600">{lbl_hyperloop}</text>
                            <path d="M0 26h26" class="k-ink" stroke-width="4" stroke-dasharray="2 7" stroke-linecap="round" /><text x="34" y="29.5" font-weight="600">{lbl_tunnel}</text>
                            <path d="M125 26h26" class="k-ink2" stroke-width="4" stroke-linecap="round" /><text x="159" y="29.5" font-weight="600">{lbl_mainline}</text>
                            <path d="M0 46h26" class="k-sea" stroke-width="3.5" stroke-dasharray="5 3" stroke-linecap="round" /><text x="34" y="49.5" font-weight="600">{lbl_maritime}</text>
                        </g>'''


def build_amazonia_svg(lang, brazil_states):
    is_hu = lang == "hu"
    lbl_atlantic = "ATLANTI-ÓCEÁN" if is_hu else "ATLANTIC OCEAN"
    lbl_basin = "AMAZONAS-MEDENCE" if is_hu else "AMAZON BASIN"
    lbl_guiana = "GUAYANAI-PAJZS" if is_hu else "GUIANA SHIELD"
    lbl_brazilia = "BRAZÍLIA TARTOMÁNY" if is_hu else "BRAZILIA PROVINCE"
    lbl_waikiki_route = "WAIKIKI ÉSZAKI ÚTVONAL" if is_hu else "WAIKIKI NORTH ROUTE"

    neighbor_ids = ["BR-GO", "BR-DF", "BR-MS", "BR-MG", "BR-BA", "BR-PE", "BR-PB", "BR-RN", "BR-AL", "BR-SE"]
    context_paths = "\n".join(
        f'                            <path class="f-sand florida-path" vector-effect="non-scaling-stroke" d="{brazil_states[sid]}" />'
        for sid in neighbor_ids
        if sid in brazil_states
    )
    province_paths = "\n".join(
        f'                            <path class="f-sand province-path" vector-effect="non-scaling-stroke" d="{brazil_states[sid]}" />'
        for sid in AMAZONIA_STATE_IDS
        if sid in brazil_states
    )

    legend_xml = build_legend_xml(lang)

    return f'''<svg class="ill" viewBox="0 0 1800 650">
                    <defs>
                        <clipPath id="amazonia-map-clip">
                            <rect width="1800" height="650" />
                        </clipPath>
                    </defs>
                    <g clip-path="url(#amazonia-map-clip)">
                    <rect width="1800" height="650" class="f-sea3" />
                    <!-- Geographic Coordinate Grid -->
                    <g class="k-white" stroke-width="1" opacity=".3">
                        <path d="M0 130h1800M0 260h1800M0 390h1800M0 520h1800M300 0v650M600 0v650M900 0v650M1200 0v650M1500 0v650" />
                    </g>
                    <!-- ==================== NEIGHBORING BRAZILIA CONTEXT ==================== -->
                    <g opacity=".45" transform="translate(210, 20) scale(1.75, 1.62)">
{context_paths}
                    </g>
                    <!-- ==================== AMAZONIA PROVINCE ==================== -->
                    <g class="amazonia-province" transform="translate(210, 20) scale(1.75, 1.62)">
{province_paths}
                    </g>
                    <!-- ==================== AMAZON RIVER HYDROGRAPHY ==================== -->
                    <g class="k-sea" fill="none" stroke-linecap="round" opacity=".38">
                        <path d="M 368 249 Q 465 240 569 227 Q 658 236 746 218 Q 815 186 882 138" stroke-width="4.5" />
                        <path d="M 465 146 Q 515 186 569 227" stroke-width="3" />
                        <path d="M 487 383 Q 532 304 596 231" stroke-width="3" />
                        <path d="M 704 438 Q 726 328 746 218" stroke-width="2.8" />
                        <path d="M 914 402 Q 890 342 868 282 Q 882 225 896 169" stroke-width="2.8" />
                    </g>
                    <!-- ==================== TRANSPORT CORRIDORS & LIVE DOTS ==================== -->
                    <!-- 1. MARITIME & RIVER ROUTES -->
                    <g class="k-sea" stroke-width="3.5" stroke-dasharray="5 3" fill="none" opacity=".85">
                        <!-- Amazon Deep-Water Navigation Spine to North Atlantic / Waikiki -->
                        <path d="M 569 227 Q 658 234 746 218 Q 812 184 862 142 Q 945 96 1085 42" />
                        <!-- Belém - Macapá - Equatorial Atlantic Shipping Lane -->
                        <path d="M 896 169 Q 856 146 814 127 Q 875 82 985 38" />
                        <!-- Equatorial Coastal Maritime Corridor (Belém - São Luís - Fortaleza - East Atlantic) -->
                        <path d="M 896 169 Q 946 162 994 201 Q 1082 178 1166 244 Q 1295 256 1430 295" />
                    </g>
                    <!-- Maritime Animated Dots -->
                    <circle r="4" class="f-white" opacity=".9">
                        <animateMotion dur="11s" repeatCount="indefinite" path="M 569 227 Q 658 234 746 218 Q 812 184 862 142 Q 945 96 1085 42" />
                    </circle>
                    <circle r="4" class="f-white" opacity=".9">
                        <animateMotion dur="7s" repeatCount="indefinite" path="M 896 169 Q 856 146 814 127 Q 875 82 985 38" />
                    </circle>
                    <circle r="4" class="f-white" opacity=".9">
                        <animateMotion dur="10s" repeatCount="indefinite" path="M 896 169 Q 946 162 994 201 Q 1082 178 1166 244 Q 1295 256 1430 295" />
                    </circle>
                    <!-- 2. SUB-RIVER & DELTA TUNNELS -->
                    <g class="k-ink" stroke-width="4" stroke-dasharray="2 7" stroke-linecap="round" fill="none">
                        <!-- Marajó Delta Undersea Tunnel (Belém - Macapá) -->
                        <path d="M 896 169 Q 854 150 814 127" />
                        <!-- Rio Negro - Solimões Sub-River Crossing (Manaus - Amazonia City Approach) -->
                        <path d="M 569 227 Q 618 252 669 273" />
                    </g>
                    <circle r="4" class="f-white">
                        <animateMotion dur="5s" repeatCount="indefinite" path="M 896 169 Q 854 150 814 127" />
                    </circle>
                    <circle r="4" class="f-white">
                        <animateMotion dur="4.5s" repeatCount="indefinite" path="M 569 227 Q 618 252 669 273" />
                    </circle>
                    <!-- 3. MAIN LINES (Regional Rail Corridors) -->
                    <g class="k-ink2" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round">
                        <!-- Northern Guiana Shield Trunk (Manaus - Boa Vista) -->
                        <path d="M 569 227 Q 554 158 546 91" />
                        <!-- Western Amazon Trunk (Manaus - Porto Velho - Rio Branco) -->
                        <path d="M 569 227 Q 524 306 487 383 Q 420 392 354 396" />
                        <!-- Madeira - Mato Grosso Rail Link (Porto Velho - Sinop - Cuiabá) -->
                        <path d="M 487 383 Q 596 412 704 438 Q 690 486 679 532" />
                        <!-- Tocantins - Carajás Freight & Passenger Line (Belém - Marabá - Imperatriz - Palmas) -->
                        <path d="M 896 169 Q 880 226 868 282 L 949 289 Q 930 346 914 402" />
                        <!-- Parnaíba - Eastern Interior Line (São Luís - Imperatriz - Teresina - Palmas) -->
                        <path d="M 994 201 Q 970 245 949 289 Q 1010 286 1071 282 Q 992 342 914 402" />
                    </g>
                    <!-- Main Line Animated Dots -->
                    <circle r="4" class="f-white">
                        <animateMotion dur="6s" repeatCount="indefinite" path="M 569 227 Q 554 158 546 91" />
                    </circle>
                    <circle r="4" class="f-white">
                        <animateMotion dur="8.5s" repeatCount="indefinite" path="M 569 227 Q 524 306 487 383 Q 420 392 354 396" />
                    </circle>
                    <circle r="4" class="f-white">
                        <animateMotion dur="8s" repeatCount="indefinite" path="M 487 383 Q 596 412 704 438 Q 690 486 679 532" />
                    </circle>
                    <circle r="4" class="f-white">
                        <animateMotion dur="7.5s" repeatCount="indefinite" path="M 896 169 Q 880 226 868 282 L 949 289 Q 930 346 914 402" />
                    </circle>
                    <circle r="4" class="f-white">
                        <animateMotion dur="8s" repeatCount="indefinite" path="M 994 201 Q 970 245 949 289 Q 1010 286 1071 282 Q 992 342 914 402" />
                    </circle>
                    <!-- 4. MAGLEV LINES (High-Speed Provincial Spines) -->
                    <g class="k-coral" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round">
                        <!-- Trans-Amazonian & Equatorial Coastal Maglev Spine (Manaus - Amazonia City - Santarém - Belém - São Luís - Teresina - Fortaleza) -->
                        <path d="M 569 227 Q 618 252 669 273 Q 708 246 746 218 Q 820 194 896 169 Q 945 184 994 201 Q 1032 242 1071 282 Q 1118 264 1166 244" />
                        <!-- North-South Central Maglev Spine (Amazonia City - Sinop - Cuiabá - Palmas - Marabá - Belém) -->
                        <path d="M 669 273 Q 688 355 704 438 Q 692 485 679 532 Q 796 468 914 402 Q 890 342 868 282 Q 882 225 896 169" />
                    </g>
                    <!-- Maglev Animated Dots -->
                    <circle r="5.5" class="f-white">
                        <animateMotion dur="6.5s" repeatCount="indefinite" path="M 569 227 Q 618 252 669 273 Q 708 246 746 218 Q 820 194 896 169 Q 945 184 994 201 Q 1032 242 1071 282 Q 1118 264 1166 244" />
                    </circle>
                    <circle r="5.5" class="f-white">
                        <animateMotion dur="6.5s" begin="3.2s" repeatCount="indefinite" path="M 1166 244 Q 1118 264 1071 282 Q 1032 242 994 201 Q 945 184 896 169 Q 820 194 746 218 Q 708 246 669 273 Q 618 252 569 227" />
                    </circle>
                    <circle r="5.5" class="f-white">
                        <animateMotion dur="6s" repeatCount="indefinite" path="M 669 273 Q 688 355 704 438 Q 692 485 679 532 Q 796 468 914 402 Q 890 342 868 282 Q 882 225 896 169" />
                    </circle>
                    <!-- 5. HYPERLOOP EXPRESS CORRIDOR -->
                    <g class="k-gold" stroke-width="5" fill="none" stroke-linecap="round">
                        <!-- Manaus - Amazonia City - Santarém - Belém Express Hyperloop -->
                        <path d="M 569 227 Q 620 258 669 273 Q 710 250 746 218 Q 822 184 896 169" />
                    </g>
                    <circle r="4.5" class="f-white">
                        <animateMotion dur="2.6s" repeatCount="indefinite" path="M 569 227 Q 620 258 669 273 Q 710 250 746 218 Q 822 184 896 169" />
                    </circle>
                    <!-- ==================== CITIES & STATION NODES ==================== -->
                    <!-- Provincial Hub: MANAUS -->
                    <g>
                        <circle cx="569" cy="227" r="22" class="f-coral" opacity=".18">
                            <animate attributeName="r" values="14;26;14" dur="3s" repeatCount="indefinite" />
                        </circle>
                        <circle cx="569" cy="227" r="10.5" class="f-coral k-white" stroke-width="2.5" />
                        <g transform="translate(569, 227)">
                            <polygon points="0,-5 1.5,-1.5 5,-1 2.5,1.5 3,5 0,3 -3,5 -2.5,1.5 -5,-1 -1.5,-1.5" class="f-white" />
                        </g>
                    </g>
                    <!-- Major Provincial Hubs: BELÉM, FORTALEZA, CUIABÁ -->
                    <g class="f-coral k-white" stroke-width="2.2">
                        <circle cx="896" cy="169" r="8.5" />
                        <circle cx="1166" cy="244" r="8.5" />
                        <circle cx="679" cy="532" r="8.5" />
                    </g>
                    <g class="f-white">
                        <circle cx="896" cy="169" r="3.2" />
                        <circle cx="1166" cy="244" r="3.2" />
                        <circle cx="679" cy="532" r="3.2" />
                    </g>
                    <!-- Special Eco-Metropolis Hub: AMAZONIA CITY -->
                    <g transform="translate(669, 273)">
                        <polygon points="-9,5 0,-11 9,5" class="f-gold k-ink" stroke-width="1.5" stroke-linejoin="round" />
                        <polygon points="0,-11 9,5 4,5" class="f-ink" opacity=".22" />
                    </g>
                    <!-- Large Cities -->
                    <g class="f-ink k-white" stroke-width="1.8">
                        <circle cx="746" cy="218" r="7" />
                        <circle cx="814" cy="127" r="7" />
                        <circle cx="994" cy="201" r="7" />
                        <circle cx="1071" cy="282" r="7" />
                        <circle cx="914" cy="402" r="7" />
                        <circle cx="487" cy="383" r="7" />
                        <circle cx="546" cy="91" r="7" />
                    </g>
                    <g class="f-gold">
                        <circle cx="746" cy="218" r="2.8" />
                        <circle cx="814" cy="127" r="2.8" />
                        <circle cx="994" cy="201" r="2.8" />
                        <circle cx="1071" cy="282" r="2.8" />
                        <circle cx="914" cy="402" r="2.8" />
                        <circle cx="487" cy="383" r="2.8" />
                        <circle cx="546" cy="91" r="2.8" />
                    </g>
                    <!-- Regional Cities -->
                    <g class="f-ink k-white" stroke-width="1.5">
                        <circle cx="354" cy="396" r="5.5" />
                        <circle cx="704" cy="438" r="5.5" />
                        <circle cx="868" cy="282" r="5.5" />
                        <circle cx="949" cy="289" r="5.5" />
                    </g>
                    <g class="f-gold">
                        <circle cx="354" cy="396" r="2.2" />
                        <circle cx="704" cy="438" r="2.2" />
                        <circle cx="868" cy="282" r="2.2" />
                        <circle cx="949" cy="289" r="2.2" />
                    </g>
                    <!-- ==================== LABELS ==================== -->
                    <g font-size="11" letter-spacing=".08em">
                        <!-- Primary Hub -->
                        <text x="569" y="206" font-size="14" font-weight="800" text-anchor="middle">MANAUS</text>
                        <!-- Major Hubs -->
                        <text x="896" y="150" font-size="12" font-weight="700" text-anchor="middle">BELÉM</text>
                        <text x="1182" y="248" font-size="12" font-weight="700">FORTALEZA</text>
                        <text x="679" y="556" font-size="12" font-weight="700" text-anchor="middle">CUIABÁ</text>
                        <!-- Special Hub -->
                        <text x="669" y="294" font-size="10.5" font-weight="700" text-anchor="middle">AMAZONIA CITY</text>
                        <!-- Large Cities -->
                        <text x="746" y="201" font-size="10.5" text-anchor="middle">SANTARÉM</text>
                        <text x="800" y="118" font-size="10.5" text-anchor="end">MACAPÁ</text>
                        <text x="1008" y="195" font-size="10.5">SÃO LUÍS</text>
                        <text x="1086" y="296" font-size="10.5">TERESINA</text>
                        <text x="930" y="407" font-size="10.5">PALMAS</text>
                        <text x="487" y="404" font-size="10.5" text-anchor="middle">PORTO VELHO</text>
                        <text x="546" y="74" font-size="10.5" text-anchor="middle">BOA VISTA</text>
                        <!-- Regional Cities -->
                        <text x="354" y="416" font-size="9" opacity=".88" text-anchor="middle">RIO BRANCO</text>
                        <text x="720" y="442" font-size="9" opacity=".88">SINOP</text>
                        <text x="854" y="286" font-size="9" opacity=".88" text-anchor="end">MARABÁ</text>
                        <text x="955" y="276" font-size="9" opacity=".88">IMPERATRIZ</text>
                        <!-- Major Territories & Oceans -->
                        <text x="1280" y="95" font-size="13" font-weight="600" opacity=".6" letter-spacing=".15em">{lbl_atlantic}</text>
                        <text x="1105" y="34" font-size="10" font-weight="600" opacity=".5" letter-spacing=".14em">{lbl_waikiki_route}</text>
                        <text x="415" y="195" font-size="11" font-weight="600" opacity=".45" letter-spacing=".15em" text-anchor="middle">{lbl_basin}</text>
                        <text x="695" y="58" font-size="11" font-weight="600" opacity=".45" letter-spacing=".15em" text-anchor="middle">{lbl_guiana}</text>
                        <text x="1085" y="495" font-size="11" font-weight="600" opacity=".5" letter-spacing=".15em" text-anchor="middle">{lbl_brazilia}</text>
                    </g>
{legend_xml}
                    </g>
                </svg>'''


def build_brazilia_svg(lang, brazil_states):
    is_hu = lang == "hu"
    lbl_atlantic = "ATLANTI-ÓCEÁN" if is_hu else "ATLANTIC OCEAN"
    lbl_amazonia = "AMAZÓNIA TARTOMÁNY" if is_hu else "AMAZONIA PROVINCE"
    lbl_highlands = "BRAZIL-FELFÖLD" if is_hu else "BRAZILIAN HIGHLANDS"
    lbl_santos_basin = "SANTOS-MEDENCE" if is_hu else "SANTOS BASIN"
    lbl_waikiki_route = "WAIKIKI ÉSZAKI ÚTVONAL" if is_hu else "WAIKIKI NORTH ROUTE"

    neighbor_ids = ["BR-MT", "BR-TO", "BR-PI", "BR-CE", "BR-MA", "BR-PA", "BR-RO"]
    context_paths = "\n".join(
        f'                            <path class="f-sand florida-path" vector-effect="non-scaling-stroke" d="{brazil_states[sid]}" />'
        for sid in neighbor_ids
        if sid in brazil_states
    )
    province_paths = "\n".join(
        f'                            <path class="f-sand province-path" vector-effect="non-scaling-stroke" d="{brazil_states[sid]}" />'
        for sid in BRAZILIA_STATE_IDS
        if sid in brazil_states
    )

    legend_xml = build_legend_xml(lang)

    return f'''<svg class="ill" viewBox="0 0 1800 650">
                    <defs>
                        <clipPath id="brazilia-map-clip">
                            <rect width="1800" height="650" />
                        </clipPath>
                    </defs>
                    <g clip-path="url(#brazilia-map-clip)">
                    <rect width="1800" height="650" class="f-sea3" />
                    <!-- Geographic Coordinate Grid -->
                    <g class="k-white" stroke-width="1" opacity=".3">
                        <path d="M0 130h1800M0 260h1800M0 390h1800M0 520h1800M300 0v650M600 0v650M900 0v650M1200 0v650M1500 0v650" />
                    </g>
                    <!-- ==================== NEIGHBORING AMAZONIA CONTEXT ==================== -->
                    <g opacity=".45" transform="translate(180, -182) scale(1.55, 1.28)">
{context_paths}
                    </g>
                    <!-- ==================== BRAZILIA PROVINCE ==================== -->
                    <g class="brazilia-province" transform="translate(180, -182) scale(1.55, 1.28)">
{province_paths}
                    </g>
                    <!-- ==================== PARANÁ & SÃO FRANCISCO HYDROGRAPHY ==================== -->
                    <g class="k-sea" fill="none" stroke-linecap="round" opacity=".38">
                        <path d="M 885 305 Q 925 225 985 150 Q 1040 125 1104 107" stroke-width="3" />
                        <path d="M 797 302 Q 735 355 702 425" stroke-width="3" />
                    </g>
                    <!-- ==================== TRANSPORT CORRIDORS & LIVE DOTS ==================== -->
                    <!-- 1. MARITIME ROUTES -->
                    <g class="k-sea" stroke-width="3.5" stroke-dasharray="5 3" fill="none" opacity=".85">
                        <!-- South Atlantic Deep-Water Coastal Lane (Porto Alegre - Florianópolis - Santos - Rio - Vitória - Salvador - Recife - Natal) -->
                        <path d="M 723 553 Q 785 535 791 496 Q 825 462 825 427 Q 885 422 918 389 Q 985 365 992 320 Q 1035 255 1020 189 Q 1095 140 1122 77 Q 1125 55 1107 38" />
                        <!-- Recife Smart Port - Waikiki North Atlantic Trunk -->
                        <path d="M 1122 77 Q 1245 48 1390 22" />
                        <!-- Santos & Rio de Janeiro Trans-Atlantic Commercial Corridor -->
                        <path d="M 825 427 Q 995 442 1190 412 Q 1345 385 1490 340" />
                    </g>
                    <!-- Maritime Animated Dots -->
                    <circle r="4" class="f-white" opacity=".9">
                        <animateMotion dur="13s" repeatCount="indefinite" path="M 723 553 Q 785 535 791 496 Q 825 462 825 427 Q 885 422 918 389 Q 985 365 992 320 Q 1035 255 1020 189 Q 1095 140 1122 77 Q 1125 55 1107 38" />
                    </circle>
                    <circle r="4" class="f-white" opacity=".9">
                        <animateMotion dur="8s" repeatCount="indefinite" path="M 1122 77 Q 1245 48 1390 22" />
                    </circle>
                    <circle r="4" class="f-white" opacity=".9">
                        <animateMotion dur="10s" repeatCount="indefinite" path="M 825 427 Q 995 442 1190 412 Q 1345 385 1490 340" />
                    </circle>
                    <!-- 2. UNDERSEA & MOUNTAIN BASE TUNNELS -->
                    <g class="k-ink" stroke-width="4" stroke-dasharray="2 7" stroke-linecap="round" fill="none">
                        <!-- Guanabara Bay Undersea Tunnel (Rio de Janeiro - Miapolis) -->
                        <path d="M 918 389 L 949 374" />
                        <!-- Serra do Mar Base Tunnel (São Paulo - Santos) -->
                        <path d="M 803 402 L 825 427" />
                        <!-- All Saints' Bay Undersea Crossing (Salvador) -->
                        <path d="M 992 206 Q 1020 189 1044 170" />
                    </g>
                    <circle r="4" class="f-white">
                        <animateMotion dur="3.5s" repeatCount="indefinite" path="M 918 389 L 949 374" />
                    </circle>
                    <circle r="4" class="f-white">
                        <animateMotion dur="3.5s" repeatCount="indefinite" path="M 803 402 L 825 427" />
                    </circle>
                    <!-- 3. MAIN LINES (Interior Rail Corridors) -->
                    <g class="k-ink2" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round">
                        <!-- Western Pantanal & Paraná Trunk (São Paulo - Londrina - Campo Grande - Goiânia) -->
                        <path d="M 803 402 Q 758 406 713 409 Q 682 377 651 345 Q 710 307 769 269" />
                        <!-- Southern Interior Connector (Curitiba - Londrina) -->
                        <path d="M 760 448 L 713 409" />
                        <!-- Central Plateau - Bahia Trunk (Brasília - Salvador) -->
                        <path d="M 815 240 Q 918 214 1020 189" />
                        <!-- Minas - Espírito Santo Corridor (Uberlândia - Belo Horizonte - Vitória) -->
                        <path d="M 797 302 Q 848 308 899 315 Q 946 318 992 320" />
                    </g>
                    <!-- Main Line Animated Dots -->
                    <circle r="4" class="f-white">
                        <animateMotion dur="8s" repeatCount="indefinite" path="M 803 402 Q 758 406 713 409 Q 682 377 651 345 Q 710 307 769 269" />
                    </circle>
                    <circle r="4" class="f-white">
                        <animateMotion dur="7s" repeatCount="indefinite" path="M 815 240 Q 918 214 1020 189" />
                    </circle>
                    <circle r="4" class="f-white">
                        <animateMotion dur="7.5s" repeatCount="indefinite" path="M 797 302 Q 848 308 899 315 Q 946 318 992 320" />
                    </circle>
                    <!-- 4. MAGLEV LINES (High-Speed Provincial Spines) -->
                    <g class="k-coral" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round">
                        <!-- Atlantic Coastal Maglev Spine (Porto Alegre - Florianópolis - Curitiba - São Paulo - Rio - Vitória - Salvador - Aracaju - Maceió - Recife - Natal) -->
                        <path d="M 723 553 Q 757 525 791 496 Q 775 472 760 448 Q 782 425 803 402 Q 860 396 918 389 Q 955 355 992 320 Q 1006 255 1020 189 Q 1046 164 1073 138 L 1104 107 L 1122 77 L 1107 38" />
                        <!-- Central Plateau Maglev Spine (São Paulo - Uberlândia - Goiânia - Brasília - Belo Horizonte - Rio de Janeiro) -->
                        <path d="M 803 402 Q 800 352 797 302 L 769 269 L 815 240 Q 857 278 899 315 Q 908 352 918 389" />
                    </g>
                    <!-- Maglev Animated Dots -->
                    <circle r="5.5" class="f-white">
                        <animateMotion dur="7.5s" repeatCount="indefinite" path="M 723 553 Q 757 525 791 496 Q 775 472 760 448 Q 782 425 803 402 Q 860 396 918 389 Q 955 355 992 320 Q 1006 255 1020 189 Q 1046 164 1073 138 L 1104 107 L 1122 77 L 1107 38" />
                    </circle>
                    <circle r="5.5" class="f-white">
                        <animateMotion dur="7.5s" begin="3.7s" repeatCount="indefinite" path="M 1107 38 L 1122 77 L 1104 107 L 1073 138 Q 1046 164 1020 189 Q 1006 255 992 320 Q 955 355 918 389 Q 860 396 803 402 Q 782 425 760 448 Q 775 472 791 496 Q 757 525 723 553" />
                    </circle>
                    <circle r="5.5" class="f-white">
                        <animateMotion dur="5.5s" repeatCount="indefinite" path="M 803 402 Q 800 352 797 302 L 769 269 L 815 240 Q 857 278 899 315 Q 908 352 918 389" />
                    </circle>
                    <!-- 5. HYPERLOOP EXPRESS TRIANGLE -->
                    <g class="k-gold" stroke-width="5" fill="none" stroke-linecap="round">
                        <!-- Southeast Megacity Hyperloop Triangle (São Paulo - Rio de Janeiro - Miapolis - Belo Horizonte - Brasília - São Paulo) -->
                        <path d="M 803 402 Q 860 396 918 389 L 949 374 Q 924 344 899 315 Q 857 278 815 240 Q 809 321 803 402" />
                    </g>
                    <circle r="4.5" class="f-white">
                        <animateMotion dur="3.2s" repeatCount="indefinite" path="M 803 402 Q 860 396 918 389 L 949 374 Q 924 344 899 315 Q 857 278 815 240 Q 809 321 803 402" />
                    </circle>
                    <!-- ==================== CITIES & STATION NODES ==================== -->
                    <!-- Primary Provincial Megahub: SÃO PAULO -->
                    <g>
                        <circle cx="803" cy="402" r="22" class="f-coral" opacity=".18">
                            <animate attributeName="r" values="14;26;14" dur="3s" repeatCount="indefinite" />
                        </circle>
                        <circle cx="803" cy="402" r="10.5" class="f-coral k-white" stroke-width="2.5" />
                        <g transform="translate(803, 402)">
                            <polygon points="0,-5 1.5,-1.5 5,-1 2.5,1.5 3,5 0,3 -3,5 -2.5,1.5 -5,-1 -1.5,-1.5" class="f-white" />
                        </g>
                    </g>
                    <!-- Major Provincial Hubs: RIO DE JANEIRO, BRASÍLIA, PORTO ALEGRE, SALVADOR, RECIFE -->
                    <g class="f-coral k-white" stroke-width="2.2">
                        <circle cx="918" cy="389" r="8.5" />
                        <circle cx="815" cy="240" r="8.5" />
                        <circle cx="723" cy="553" r="8.5" />
                        <circle cx="1020" cy="189" r="8.5" />
                        <circle cx="1122" cy="77" r="8.5" />
                    </g>
                    <g class="f-white">
                        <circle cx="918" cy="389" r="3.2" />
                        <circle cx="815" cy="240" r="3.2" />
                        <circle cx="723" cy="553" r="3.2" />
                        <circle cx="1020" cy="189" r="3.2" />
                        <circle cx="1122" cy="77" r="3.2" />
                    </g>
                    <!-- Special Megaproject Landmark: MIAPOLIS -->
                    <g transform="translate(949, 374)">
                        <polygon points="-8,5 0,-11 8,5" class="f-gold k-ink" stroke-width="1.5" stroke-linejoin="round" />
                        <polygon points="0,-11 8,5 3.5,5" class="f-ink" opacity=".22" />
                    </g>
                    <!-- Large Cities -->
                    <g class="f-ink k-white" stroke-width="1.8">
                        <circle cx="899" cy="315" r="7" />
                        <circle cx="760" cy="448" r="7" />
                        <circle cx="769" cy="269" r="7" />
                        <circle cx="651" cy="345" r="7" />
                        <circle cx="992" cy="320" r="7" />
                        <circle cx="791" cy="496" r="7" />
                        <circle cx="1107" cy="38" r="7" />
                    </g>
                    <g class="f-gold">
                        <circle cx="899" cy="315" r="2.8" />
                        <circle cx="760" cy="448" r="2.8" />
                        <circle cx="769" cy="269" r="2.8" />
                        <circle cx="651" cy="345" r="2.8" />
                        <circle cx="992" cy="320" r="2.8" />
                        <circle cx="791" cy="496" r="2.8" />
                        <circle cx="1107" cy="38" r="2.8" />
                    </g>
                    <!-- Regional Cities -->
                    <g class="f-ink k-white" stroke-width="1.5">
                        <circle cx="825" cy="427" r="5.5" />
                        <circle cx="797" cy="302" r="5.5" />
                        <circle cx="713" cy="409" r="5.5" />
                        <circle cx="1073" cy="138" r="5.5" />
                        <circle cx="1104" cy="107" r="5.5" />
                    </g>
                    <g class="f-gold">
                        <circle cx="825" cy="427" r="2.2" />
                        <circle cx="797" cy="302" r="2.2" />
                        <circle cx="713" cy="409" r="2.2" />
                        <circle cx="1073" cy="138" r="2.2" />
                        <circle cx="1104" cy="107" r="2.2" />
                    </g>
                    <!-- ==================== LABELS ==================== -->
                    <g font-size="11" letter-spacing=".08em">
                        <!-- Primary Megahub -->
                        <text x="788" y="388" font-size="14" font-weight="800" text-anchor="end">SÃO PAULO</text>
                        <!-- Major Hubs -->
                        <text x="918" y="411" font-size="12" font-weight="700" text-anchor="middle">RIO DE JANEIRO</text>
                        <text x="815" y="222" font-size="12" font-weight="700" text-anchor="middle">BRASÍLIA</text>
                        <text x="723" y="576" font-size="12" font-weight="700" text-anchor="middle">PORTO ALEGRE</text>
                        <text x="1036" y="193" font-size="12" font-weight="700">SALVADOR</text>
                        <text x="1138" y="81" font-size="12" font-weight="700">RECIFE</text>
                        <!-- Special Megaproject -->
                        <text x="963" y="378" font-size="9.5" font-weight="700">MIAPOLIS</text>
                        <!-- Large Cities -->
                        <text x="904" y="305" font-size="9.5">BELO HORIZONTE</text>
                        <text x="746" y="452" font-size="10.5" text-anchor="end">CURITIBA</text>
                        <text x="755" y="272" font-size="10.5" text-anchor="end">GOIÂNIA</text>
                        <text x="637" y="349" font-size="10.5" text-anchor="end">CAMPO GRANDE</text>
                        <text x="1008" y="324" font-size="10.5">VITÓRIA</text>
                        <text x="807" y="500" font-size="10.5">FLORIANÓPOLIS</text>
                        <text x="1123" y="42" font-size="10.5">NATAL</text>
                        <!-- Regional Cities -->
                        <text x="838" y="434" font-size="9" opacity=".88">SANTOS</text>
                        <text x="785" y="310" font-size="9" opacity=".88" text-anchor="end">UBERLÂNDIA</text>
                        <text x="699" y="413" font-size="9" opacity=".88" text-anchor="end">LONDRINA</text>
                        <text x="1087" y="142" font-size="9" opacity=".88">ARACAJU</text>
                        <text x="1118" y="111" font-size="9" opacity=".88">MACEIÓ</text>
                        <!-- Major Territories & Oceans -->
                        <text x="1320" y="245" font-size="13" font-weight="600" opacity=".6" letter-spacing=".15em">{lbl_atlantic}</text>
                        <text x="1395" y="42" font-size="10" font-weight="600" opacity=".5" letter-spacing=".14em">{lbl_waikiki_route}</text>
                        <text x="625" y="105" font-size="11" font-weight="600" opacity=".5" letter-spacing=".15em" text-anchor="middle">{lbl_amazonia}</text>
                        <text x="655" y="195" font-size="11" font-weight="600" opacity=".45" letter-spacing=".15em" text-anchor="middle">{lbl_highlands}</text>
                        <text x="1055" y="485" font-size="11" font-weight="600" opacity=".45" letter-spacing=".15em" text-anchor="middle">{lbl_santos_basin}</text>
                    </g>
{legend_xml}
                    </g>
                </svg>'''


def build_mobility_block(lang, cuba_group, brazil_states):
    is_hu = lang == "hu"
    tab_waikiki = "Waikiki tartomány" if is_hu else "Waikiki Province"
    tab_amazonia = "Amazónia tartomány" if is_hu else "Amazonia Province"
    tab_brazilia = "Brazília tartomány" if is_hu else "Brazilia Province"
    caption = (
        "Sematikus ábra, nem méretarányos. A mozgó pontok az egyes folyosók forgalmát jelzik."
        if is_hu
        else "Schematic, not to scale. Animated dots show live service on each corridor."
    )

    waikiki_svg = build_svg(lang, cuba_group)
    amazonia_svg = build_amazonia_svg(lang, brazil_states)
    brazilia_svg = build_brazilia_svg(lang, brazil_states)

    for name, s in [("waikiki", waikiki_svg), ("amazonia", amazonia_svg), ("brazilia", brazilia_svg)]:
        ET.fromstring(s)
        print(f"[{lang}:{name}] SVG parsed successfully as valid XML!")

    return f'''<div class="island-tabs-bar" role="tablist">
                <button class="island-tab-btn is-active" id="tab-btn-waikiki" type="button" role="tab" aria-selected="true" aria-controls="tab-panel-waikiki" data-island-tab="waikiki"><img src="../icons/mdi/island.svg" />
                    <span>{tab_waikiki}</span>
                </button>
                <button class="island-tab-btn" id="tab-btn-amazonia" type="button" role="tab" aria-selected="false" aria-controls="tab-panel-amazonia" data-island-tab="amazonia"><img src="../icons/mdi/forest.svg" />
                    <span>{tab_amazonia}</span>
                </button>
                <button class="island-tab-btn" id="tab-btn-brazilia" type="button" role="tab" aria-selected="false" aria-controls="tab-panel-brazilia" data-island-tab="brazilia"><img src="../icons/mdi/city.svg" />
                    <span>{tab_brazilia}</span>
                </button>
            </div>
            <div class="island-panel is-active" id="tab-panel-waikiki" role="tabpanel" aria-labelledby="tab-btn-waikiki">
                <figure class="ill-panel" data-reveal="zoom">
                    {waikiki_svg}
                    <figcaption class="ill-caption">{caption}</figcaption>
                </figure>
            </div>
            <div class="island-panel" id="tab-panel-amazonia" role="tabpanel" aria-labelledby="tab-btn-amazonia">
                <figure class="ill-panel" data-reveal="zoom">
                    {amazonia_svg}
                    <figcaption class="ill-caption">{caption}</figcaption>
                </figure>
            </div>
            <div class="island-panel" id="tab-panel-brazilia" role="tabpanel" aria-labelledby="tab-btn-brazilia">
                <figure class="ill-panel" data-reveal="zoom">
                    {brazilia_svg}
                    <figcaption class="ill-caption">{caption}</figcaption>
                </figure>
            </div>'''


def main():
    cuba_group = get_cuba_group()
    brazil_states = get_brazil_states()
    print(f"Found Cuba group ({len(cuba_group)} chars) and {len(brazil_states)} Brazil states.")

    for lang, rel_path in [("en", "en/infrastructure.html"), ("hu", "hu/infrastructure.html")]:
        filepath = ROOT / rel_path
        mobility_block = build_mobility_block(lang, cuba_group, brazil_states)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        mob_idx = content.find('id="mobility"')
        intro_end = content.find('</p>', mob_idx)
        list_idx = content.find('<ol class="feature-list">', mob_idx)

        if mob_idx == -1 or intro_end == -1 or list_idx == -1:
            raise ValueError(f"Could not locate mobility boundaries in {filepath}")

        before = content[:intro_end + len('</p>')]
        after = content[list_idx:]

        new_content = before + "\n            " + mobility_block + "\n            " + after

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath} successfully!")

        subprocess.run(["python3", str(ROOT / "scripts" / "build_pages.py"), "--format", str(filepath)], check=False)

if __name__ == '__main__':
    main()
