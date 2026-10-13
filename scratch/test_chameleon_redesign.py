#!/usr/bin/env python3
import sys, os, re, math
sys.path.insert(0, '/Volumes/Samsung X5 SSD/Projektek/Site/scripts')
import gen_island_maps as g
from gen_island_maps import Tube, CH_BODY_KNOTS, CH_LIMBS, CH_GAP, CH_SPIRAL, poly_path, pt, n, smooth_island, circle_d, _chaikin, smooth_closed, catmull_rom_open

def build_redesigned_chameleon(rounds=2, wave_amp=1.5):
    g_gap = CH_GAP
    body = Tube(CH_BODY_KNOTS)
    sx = body.s_at_x

    sand, green = [], []
    seed_counter = 1

    def add(poly, name, kind="sand", green_poly=None, hole=None, r_smooth=rounds):
        if not poly:
            return
        d = smooth_closed(poly, rounds=r_smooth)
        if hole:
            d += " " + circle_d(*hole)
        sand.append((name, d, kind, hole is not None))
        if green_poly:
            dg = smooth_closed(green_poly, rounds=r_smooth)
            if hole:
                dg += " " + circle_d(hole[0], hole[1], hole[2] + 6)
            green.append((name, dg, hole is not None))

    def organic_piece(tube, s0, s1, lo=None, hi=None, inset=0.0, step=6.0, seed=None):
        nonlocal seed_counter
        if seed is None:
            seed = seed_counter
            seed_counter += 1
        lo = lo or (lambda wt, wb: -wb)
        hi = hi or (lambda wt, wb: wt)
        s0, s1 = s0 + inset, s1 - inset
        if s1 - s0 < 2:
            return None
        flo = (lambda wt, wb: lo(wt, wb) + inset)
        fhi = (lambda wt, wb: hi(wt, wb) - inset)
        _, _, wt, wb, _, _ = tube.at((s0 + s1) / 2)
        if fhi(wt, wb) - flo(wt, wb) < 2.5:
            return None
        n_s = max(3, int((s1 - s0) / step))
        ss = [s0 + (s1 - s0) * i / n_s for i in range(n_s + 1)]
        
        top = []
        for idx, s in enumerate(ss):
            rel = (s - s0) / (s1 - s0)
            # subtle organic ripple (0 at ends to preserve channel gaps)
            w = wave_amp * math.sin(math.pi * rel) * (0.6 * math.sin(2.5 * math.pi * rel + seed) + 0.4 * math.cos(4 * math.pi * rel))
            top.append(tube.off(s, lambda wt, wb: fhi(wt, wb) + w))
            
        bot = []
        for idx, s in enumerate(reversed(ss)):
            rel = (s - s0) / (s1 - s0)
            w = wave_amp * math.sin(math.pi * rel) * (0.6 * math.cos(2.5 * math.pi * rel + seed * 2) - 0.4 * math.sin(3.5 * math.pi * rel))
            bot.append(tube.off(s, lambda wt, wb: flo(wt, wb) - w))

        def cap(s, f_from, f_to, is_end=False):
            x, y, wt, wb, nx, ny = tube.at(s)
            a, b = f_from(wt, wb), f_to(wt, wb)
            k = max(2, int(abs(b - a) / step))
            pts = []
            for j in range(1, k):
                u = j / float(k)
                # gentle natural curvature across channel cuts
                bow = 1.2 * math.sin(math.pi * u) * (-1 if is_end else 1)
                d = a + (b - a) * u
                pts.append((x + nx * d + (-ny) * bow, y + ny * d + nx * bow))
            return pts

        return top + cap(s1, fhi, flo, is_end=True) + bot + cap(s0, flo, fhi, is_end=False)

    # Lateral splits
    lateral = lambda frac: (lambda wt, wb: wt - frac * (wt + wb))
    split_mouth = lateral(0.55)
    split_belly = lateral(0.60)
    hg = g_gap / 2.0

    def above(f):
        return lambda wt, wb: f(wt, wb) + hg

    def below(f):
        return lambda wt, wb: f(wt, wb) - hg

    eye = (858, 242, 12)
    hole = (eye[0], eye[1], eye[2] + 6)
    road_ranges = []
    bridge_lines = []

    # 1. Jaws: split into 2 segments (Snout & Mid-Jaw) -> 4 islands
    s_j0 = 0.0
    s_j1 = 36.0
    s_j2 = sx(886)
    for a, b, tag in [(s_j0, s_j1 - hg, "Snout"), (s_j1 + hg, s_j2 - hg, "Mid-Jaw")]:
        add(organic_piece(body, a, b, lo=above(split_mouth)), f"Upper {tag} Isle", green_poly=organic_piece(body, a, b, lo=above(split_mouth), inset=6))
        add(organic_piece(body, a, b, hi=below(split_mouth)), f"Lower {tag} Isle")
        road_ranges.append((a, b))

    # 2. Head Crown around eye: split into 2 segments -> 2 crown islands
    s_c0 = sx(886)
    s_c1 = (sx(886) + sx(806)) / 2
    s_c2 = sx(806)
    add(organic_piece(body, s_c0 + hg, s_c1 - hg), "Head Crown Isle East", green_poly=organic_piece(body, s_c0 + hg, s_c1 - hg, inset=8), hole=hole)
    add(organic_piece(body, s_c1 + hg, s_c2 - hg), "Head Crown Isle West", green_poly=organic_piece(body, s_c1 + hg, s_c2 - hg, inset=8))
    road_ranges.extend([(s_c0 + hg, s_c1 - hg), (s_c1 + hg, s_c2 - hg)])

    # 3. Neck: split into 2 segments -> 2 neck islands
    s_n0 = sx(806)
    s_n1 = (sx(806) + sx(754)) / 2
    s_n2 = sx(754)
    add(organic_piece(body, s_n0 + hg, s_n1 - hg), "Neck Isle 1", green_poly=organic_piece(body, s_n0 + hg, s_n1 - hg, inset=7))
    add(organic_piece(body, s_n1 + hg, s_n2 - hg), "Neck Isle 2", green_poly=organic_piece(body, s_n1 + hg, s_n2 - hg, inset=7))
    road_ranges.extend([(s_n0 + hg, s_n1 - hg), (s_n1 + hg, s_n2 - hg)])

    # 4. Shoulder (sx 754 to 682): split into 2 cuts -> 2 dorsal + 2 belly = 4 islands
    s_sh0 = sx(754)
    s_sh1 = (sx(754) + sx(682)) / 2
    s_sh2 = sx(682)
    for idx, (a, b) in enumerate([(s_sh0 + hg, s_sh1 - hg), (s_sh1 + hg, s_sh2 - hg)], 1):
        add(organic_piece(body, a, b, lo=above(split_belly)), f"Shoulder Dorsal Isle {idx}", green_poly=organic_piece(body, a, b, lo=above(split_belly), inset=8))
        add(organic_piece(body, a, b, hi=below(split_belly)), f"Shoulder Belly Isle {idx}")
        bm = (a + b) / 2
        bridge_lines.append((body.off(bm, lambda wt, wb: split_belly(wt, wb) + hg + 4),
                             body.off(bm, lambda wt, wb: split_belly(wt, wb) - hg - 4)))
        road_ranges.append((a, b))

    # 5. Mid-Back (Pavilion, sx 682 to 546): split into 3 cuts -> 3 dorsal + 5 belly = 8 islands
    s_mb0 = sx(682)
    s_mb1 = s_mb0 + (sx(546) - s_mb0) / 3.0
    s_mb2 = s_mb0 + (sx(546) - s_mb0) * 2.0 / 3.0
    s_mb3 = sx(546)
    mb_cuts = [(s_mb0 + hg, s_mb1 - hg), (s_mb1 + hg, s_mb2 - hg), (s_mb2 + hg, s_mb3 - hg)]
    for idx, (a, b) in enumerate(mb_cuts, 1):
        add(organic_piece(body, a, b, lo=above(split_belly)), f"Pavilion Dorsal Isle {idx}", green_poly=organic_piece(body, a, b, lo=above(split_belly), inset=8))
        # Split belly of mid-back into 2 small isles each for cuts 1 and 2
        if idx in (1, 2):
            m_mid = (a + b) / 2
            add(organic_piece(body, a, m_mid - hg, hi=below(split_belly)), f"Pavilion Belly Isle {idx}a")
            add(organic_piece(body, m_mid + hg, b, hi=below(split_belly)), f"Pavilion Belly Isle {idx}b")
        else:
            add(organic_piece(body, a, b, hi=below(split_belly)), f"Pavilion Belly Isle {idx}")
        bm = (a + b) / 2
        bridge_lines.append((body.off(bm, lambda wt, wb: split_belly(wt, wb) + hg + 4),
                             body.off(bm, lambda wt, wb: split_belly(wt, wb) - hg - 4)))
        road_ranges.append((a, b))

    # 6. Rump (sx 546 to 470): split into 2 cuts -> 2 dorsal + 2 belly = 4 islands
    s_r0 = sx(546)
    s_r1 = (sx(546) + sx(470)) / 2
    s_r2 = sx(470)
    for idx, (a, b) in enumerate([(s_r0 + hg, s_r1 - hg), (s_r1 + hg, s_r2 - hg)], 1):
        add(organic_piece(body, a, b, lo=above(split_belly)), f"Rump Dorsal Isle {idx}", green_poly=organic_piece(body, a, b, lo=above(split_belly), inset=8))
        add(organic_piece(body, a, b, hi=below(split_belly)), f"Rump Belly Isle {idx}")
        bm = (a + b) / 2
        bridge_lines.append((body.off(bm, lambda wt, wb: split_belly(wt, wb) + hg + 4),
                             body.off(bm, lambda wt, wb: split_belly(wt, wb) - hg - 4)))
        road_ranges.append((a, b))

    # 7. Spiral Tail: finely segmented into smaller organic pebble islands (~24-26 islands)
    s = sx(470) + hg
    t_idx = 1
    t_seg_len = 38.0
    while s < body.L - 20:
        a = s
        b = min(body.L, s + t_seg_len - g_gap)
        mid = (a + b) / 2
        _, _, wt, wb, _, _ = body.at(mid)
        gp = organic_piece(body, a, b, inset=7) if wt + wb > 24 else None
        add(organic_piece(body, a, b), f"Spiral Tail Isle {t_idx}", green_poly=gp)
        road_ranges.append((a, b))
        s += t_seg_len
        t_seg_len = max(22.0, t_seg_len * 0.94)
        t_idx += 1

    # 8. Casque Helmet: 3 organic sweeping crest islands instead of 1 giant triangle
    s_c0, s_c1 = sx(880), sx(796)
    for k in range(3):
        t0 = k / 3.0
        t1 = (k + 1) / 3.0
        sc_a = s_c0 + (s_c1 - s_c0) * t0
        sc_b = s_c0 + (s_c1 - s_c0) * t1
        casque_arc = [body.off(sc_a + (sc_b - sc_a) * j / 6, lambda wt, wb: wt + g_gap) for j in range(7)]
        peak_x = 840 - k * 22
        peak_y = 195 - (2 - k) * 10
        casque_isl = casque_arc + [(peak_x + 6, peak_y + 4), (peak_x, peak_y), (peak_x - 6, peak_y + 8)]
        add(casque_isl, f"Casque Helmet Crest Isle {k + 1}")

    # 9. Dorsal Crest Islets: 16 rounded tooth/pebble islets
    for k, xc in enumerate(range(768, 465, -19), 1):
        sc = sx(xc)
        base_l = body.off(sc - 6, lambda wt, wb: wt + g_gap)
        base_r = body.off(sc + 6, lambda wt, wb: wt + g_gap)
        tip = body.off(sc, lambda wt, wb: wt + g_gap + 13 + 3 * math.sin(k * 1.2))
        # Rounded crest pebble
        tip_l = ((base_l[0] + tip[0]) / 2 - 1, (base_l[1] + tip[1]) / 2)
        tip_r = ((base_r[0] + tip[0]) / 2 + 1, (base_r[1] + tip[1]) / 2)
        add([base_r, tip_r, tip, tip_l, base_l], f"Dorsal Crest Islet {k}", kind="crest")

    # 10. Limbs: Upper limb and Lower limb each split into 2 smaller articulated islands
    limb_meta = {}
    for limb, knots in CH_LIMBS.items():
        tube = Tube(knots)
        knee = tube.s[min(range(len(tube.p)), key=lambda q: math.hypot(tube.p[q][0] - knots[1][0], tube.p[q][1] - knots[1][1]))]
        upper_name = "Hindlimb Thigh" if limb == "hind" else "Forelimb Upper Arm"
        lower_name = "Hindlimb Shin" if limb == "hind" else "Forelimb Forearm"
        
        # Upper split into 2
        u_mid = knee / 2.0
        add(organic_piece(tube, 0, u_mid - hg), f"{upper_name} Isle 1", green_poly=organic_piece(tube, 0, u_mid - hg, inset=6))
        add(organic_piece(tube, u_mid + hg, knee - hg), f"{upper_name} Isle 2", green_poly=organic_piece(tube, u_mid + hg, knee - hg, inset=6))
        bridge_lines.append((tube.off(u_mid - hg - 3, 0), tube.off(u_mid + hg + 3, 0)))

        # Lower split into 2
        l_mid = (knee + tube.L) / 2.0
        add(organic_piece(tube, knee + hg, l_mid - hg), f"{lower_name} Isle 1")
        add(organic_piece(tube, l_mid + hg, tube.L), f"{lower_name} Isle 2")
        bridge_lines.append((tube.off(knee - hg - 4, 0), tube.off(knee + hg + 4, 0)))
        bridge_lines.append((tube.off(l_mid - hg - 3, 0), tube.off(l_mid + hg + 3, 0)))

        p_limb = tube.off(12, 0)
        p_belly = body.off(sx(p_limb[0]), lambda wt, wb: -wb + 6)
        bridge_lines.append((p_limb, p_belly))
        ax, ay = knots[-1][0], knots[-1][1]
        for side in (-1, 1):
            ck = [(ax + side * 6, ay + 6, 5, 5), (ax + side * 18, ay + 12, 4.5, 4.5), (ax + side * 27, ay + 19, 2.5, 2.5)]
            ct = Tube(ck)
            add(organic_piece(ct, 0, ct.L), f"{lower_name} Claw {'East' if side > 0 else 'West'}")
        limb_meta[limb] = {"upper_mid": tube.off(knee / 2, 0)}

    # 11. Curved tongue: 5 stepping-stone islets to Paradise Atoll
    tongue = [
        (965, 292, 10, 5, 30),
        (968, 318, 10, 5, 55),
        (964, 344, 9.5, 5, 75),
        (952, 368, 9.5, 5.2, 95),
        (936, 386, 9.5, 5.5, 115),
    ]
    for k, (x, y, rx, ry, rot) in enumerate(tongue):
        sand.append((f"Tongue Stepping Islet {k + 1}", smooth_island(x, y, rx, ry, rot=rot, seed=k + 2), "sand", False))
    villas = (920, 410)
    sand.append(("Paradise Atoll", smooth_island(villas[0], villas[1], 25, 23, rot=10, seed=4) + " " + circle_d(villas[0], villas[1], 12), "sand", True))

    # 12. Satellites
    leaf_r = (912, 492)
    sand.append(("Marine Station Leaf Isle", smooth_island(leaf_r[0], leaf_r[1], 22, 11, rot=-30, seed=5), "sand", False))
    green.append(("Marine Station Leaf Isle", smooth_island(leaf_r[0], leaf_r[1], 13, 5, rot=-30, seed=9), False))
    leaf_l = (268, 486)
    sand.append(("Power Hub Leaf Isle", smooth_island(leaf_l[0], leaf_l[1], 22, 11, rot=40, seed=7), "sand", False))
    green.append(("Power Hub Leaf Isle", smooth_island(leaf_l[0], leaf_l[1], 13, 5, rot=40, seed=11), False))

    print(f"Total islands: {len(sand)} (was 50)")

    # Construct complete SVG
    t = g.L['en']
    o = g.map_header(t["cham_aria"])
    o += [
        "<!-- Shallow Lagoon -->",
        '<ellipse cx="600" cy="345" rx="540" ry="290" fill="url(#lagoon-glow)" />',
        "<!-- Chameleon Archipelago Group -->",
        '<g id="chameleon-group" transform="translate(585, 350) scale(1.45) translate(-585, -350)">',
        "<!-- Shallow Reef Halo hugging the Archipelago -->",
        '<g fill="none" stroke="#2ba29e" stroke-linecap="round" stroke-linejoin="round" opacity="0.35">',
        f'<path d="{poly_path([body.off(s, lambda wt, wb: wt + 4) for s in [body.L * q / 120 for q in range(121)]], close=False)}" stroke-width="16" />',
        "</g>",
        f"<!-- {len(sand)} DISTINCT ISLANDS FORMING A CHAMELEON (ZERO OVERLAPS) -->",
        '<g id="chameleon-islands-group">',
    ]
    for name, d, kind, has_hole in sand:
        cls = "map-reef" if kind == "crest" else "map-sand"
        rule = ' fill-rule="evenodd"' if has_hole else ""
        o.append(f'<!-- {name} -->\n<path class="{cls}" d="{d}"{rule} />')
    o.append("</g>")

    o += ["<!-- Island Greenery Cores -->", '<g id="chameleon-greenery-group">']
    for name, d, has_hole in green:
        rule = ' fill-rule="evenodd"' if has_hole else ""
        o.append(f'<path class="map-greenery" d="{d}"{rule} />')
    o.append("</g>")

    # Waterfront villas along tail
    villa_paths = []
    for a, b in road_ranges[12:]:
        _, _, wt, wb, _, _ = body.at((a + b) / 2)
        if wt < 9:
            continue
        pts = [body.off(a + (b - a) * q / 8, lambda wt, wb: wt - 4) for q in range(1, 8)]
        villa_paths.append(poly_path(pts, close=False))
    if villa_paths:
        o += [
            "<!-- Spiral Tail Waterfront Villas -->",
            f'<path class="map-frond-villas" d="{" ".join(villa_paths)}" stroke-width="2.6" stroke-dasharray="0.1 7" />',
        ]

    # Continuous road from Paradise Atoll to tail tip
    s_road_end = body.L - 26
    spine_road = [body.off(s_road_end * q / 180, lambda wt, wb: 0.28 * wt * (q / 180)**0.5 if q > 0 else 0) for q in range(181)]
    atoll_pier = (villas[0], villas[1] - 20)
    tongue_knots = [
        (910, 393),
        atoll_pier,
        (936, 386),
        (952, 368),
        (964, 344),
        (968, 318),
        (965, 292),
        (962, 269),
        spine_road[2],
        spine_road[5],
        spine_road[9],
    ]
    tongue_spline = catmull_rom_open(tongue_knots, n_per_seg=25, alpha=0.5)
    idx_junc = min(range(len(tongue_spline)), key=lambda k: math.hypot(tongue_spline[k][0] - spine_road[5][0], tongue_spline[k][1] - spine_road[5][1]))
    road_pts = tongue_spline[:idx_junc] + spine_road[5:]
    o += [
        "<!-- Chameleon Boulevard and Overwater Tongue Road (bridges every channel from Paradise Atoll to the spiral tail) -->",
        f'<path class="map-road" d="{poly_path(road_pts, close=False)}" />',
        "<!-- Inter-Island Footbridges -->",
        '<g stroke="#ffffff" stroke-width="2.2" stroke-linecap="round">',
    ]
    for p1, p2 in bridge_lines:
        o.append(f'<line x1="{n(p1[0])}" y1="{n(p1[1])}" x2="{n(p2[0])}" y2="{n(p2[1])}" />')
    p_head = body.off(sx(835), lambda wt, wb: wt - 4)
    p_casque = body.off(sx(835), lambda wt, wb: wt + g_gap + 6)
    o.append(f'<line x1="{n(p_head[0])}" y1="{n(p_head[1])}" x2="{n(p_casque[0])}" y2="{n(p_casque[1])}" />')
    o.append("</g>")

    mar = (CH_SPIRAL[0] + 4, CH_SPIRAL[1] + 2)
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
        "<!-- Revolving 360 Degree Observation Eye Dome (Turret Eye Islet) -->",
        f'<circle cx="{eye[0]}" cy="{eye[1]}" r="{eye[2]}" class="map-sand" />',
        f'<g transform="translate({eye[0]}, {eye[1]})">',
        '<circle cx="0" cy="0" r="9" fill="#0f172a" stroke="#ffffff" stroke-width="1.5" />',
        '<circle cx="0" cy="0" r="6" fill="#38bdf8" opacity="0.9" />',
        '<circle cx="2" cy="-2" r="2.2" fill="#ffffff" />',
        "</g>",
    ]

    bio = leaf_r
    youth = limb_meta["fore"]["upper_mid"]
    youth = (round(youth[0], 1), round(youth[1], 1))
    o += [
        "<!-- International Youth Innovation Center Campus -->",
        f'<rect x="{n(youth[0] - 9)}" y="{n(youth[1] - 12)}" width="18" height="24" rx="3" class="map-urban" />',
        "<!-- Marine Biology and Dolphin Station -->",
        f'<circle cx="{bio[0]}" cy="{bio[1]}" r="9" class="map-sea-lagoon" stroke="#ffffff" stroke-width="1.6" />',
        f'<path d="M{bio[0] - 3},{bio[1] - 2} C{bio[0] + 3},{bio[1] - 5} {bio[0] + 5},{bio[1] + 3} {bio[0]},{bio[1] + 4}" stroke="#0284c7" stroke-width="2" fill="none" />',
        "<!-- Experimental Floating Eco-Communities -->",
        '<g fill="#2dd4bf" stroke="#ffffff" stroke-width="1">',
    ]
    eco = (632, 420)
    for dx, dy in ((-30, -22), (-12, -30), (8, -24), (26, -12), (-24, 2), (22, 10), (-8, 24), (12, 30)):
        o.append(f'<rect x="{eco[0] + dx - 5}" y="{eco[1] + dy - 5}" width="10" height="10" rx="2" />')
    o += [
        "</g>",
        "<!-- Renewable Marine Power Hub -->",
        f'<g transform="translate({leaf_l[0]}, {leaf_l[1]})">',
        '<circle cx="0" cy="0" r="8" fill="#0284c7" stroke="#ffffff" stroke-width="1.4" />',
        '<path d="M0,-6 L0,6 M-6,0 L6,0" stroke="#ffffff" stroke-width="1.8" class="spin" />',
        "</g>",
        "<!-- Paradise Islands Overwater Bungalows and Coral Nursery -->",
        f'<circle cx="{villas[0]}" cy="{villas[1]}" r="18" fill="none" stroke="#c29a57" stroke-width="2.5" stroke-dasharray="3 4" />',
        f'<circle cx="{villas[0]}" cy="{villas[1]}" r="12" class="map-sea-lagoon" stroke="#2dd4bf" stroke-width="1.6" />',
        f'<circle cx="{villas[0]}" cy="{villas[1]}" r="3.5" fill="#38bdf8" class="bob" />',
    ]

    metro = body.off((sx(682) + sx(546)) / 2 + 30, lambda wt, wb: split_belly(wt, wb) - 0.5 * (split_belly(wt, wb) + wb))
    metro = (round(metro[0], 1), round(metro[1], 1))
    o += [
        "<!-- Sub-Sea Metro Tunnel -->",
        '<g fill="none" stroke="#f5c46e" stroke-dasharray="8 4">',
        f'<path d="M{n(metro[0])},670 L{n(metro[0])},{n(metro[1])} L{n(pav[0])},{n(pav[1])}" stroke-width="3" />',
        "</g>",
    ]
    for x, y in (metro, pav, (eye[0], eye[1]), mar):
        o.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="5" fill="#f5c46e" stroke="#ffffff" stroke-width="2" />')

    o += [
        "<!-- Geographic Labels -->",
        '<g class="map-label-group">',
        f'<text class="map-label-text" x="{n(pav[0])}" y="148">{t["pavilion"]}</text>',
        f'<text class="map-label-text" x="{mar[0]}" y="502">{t["marina"]}</text>',
        f'<text class="map-label-text" x="{villas[0]}" y="{villas[1] + 34}">{t["villas"]}</text>',
        "</g>",
        "<!-- 8 INTERACTIVE HOTSPOT PINS -->",
    ]
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
    for i, x, y, col, name, r in spots:
        o.append(f"<!-- Hotspot {i}: {name} -->")
        o += g.hotspot(i, x, y, col, r)
    o.append("</g>")
    o.append("</svg>")
    return o

svg_lines = build_redesigned_chameleon(rounds=2, wave_amp=1.5)
svg_text = "\n".join(svg_lines)

css = open('/Volumes/Samsung X5 SSD/Projektek/Site/css/infrastructure.css', encoding='utf-8').read()
m = re.search(r'/\* SVG Map Artwork Classes \*/(.*?)/\* Interactive Map Hotspot Pins', css, re.S)
hs = re.search(r'(\.map-hotspot \{.*?)\n\.map-tooltip \{', css, re.S)

html = f"""<!doctype html><html><head><style>
body{{margin:0;background:#051329}} :root{{--font-sans:Helvetica,Arial,sans-serif}}
.island-map-canvas svg{{width:1200px;height:700px;display:block}}
{m.group(1)}
{hs.group(1) if hs else ''}
</style></head><body><div class="island-map-canvas">{svg_text}</div></body></html>"""

base_path = '/Users/kristof/.gemini/antigravity-ide/brain/4ffed735-ad3b-4b01-8196-232b554fd79d/scratch/chameleon_redesign_preview'
with open(f'{base_path}.html', 'w', encoding='utf-8') as f:
    f.write(html)

cmd = f'"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --window-size=1200,700 --screenshot={base_path}.png file://{base_path}.html'
os.system(cmd)
print("Preview rendered successfully")
