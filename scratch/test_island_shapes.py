#!/usr/bin/env python3
import sys, os, re, math
sys.path.insert(0, '/Volumes/Samsung X5 SSD/Projektek/Site/scripts')
import gen_island_maps as g
from gen_island_maps import Tube, CH_BODY_KNOTS, CH_LIMBS, CH_GAP, CH_SPIRAL, poly_path, pt, n, smooth_island, circle_d, _chaikin, smooth_closed

body = Tube(CH_BODY_KNOTS)

# Let's inspect a single piece:
# e.g. shoulder dorsal: s0=212, s1=286, hi=top, lo=split_belly
split_belly = lambda wt, wb: wt - 0.62 * (wt + wb)
hg = 4.0

p_orig = body.piece(212 + hg, 286 - hg, lo=lambda wt, wb: split_belly(wt, wb) + hg)

def organic_piece(tube, s0, s1, lo=None, hi=None, inset=0.0, step=6.0, seed=1):
    lo = lo or (lambda wt, wb: -wb)
    hi = hi or (lambda wt, wb: wt)
    s0, s1 = s0 + inset, s1 - inset
    if s1 - s0 < 2:
        return None
    flo = (lambda wt, wb: lo(wt, wb) + inset)
    fhi = (lambda wt, wb: hi(wt, wb) - inset)
    _, _, wt, wb, _, _ = tube.at((s0 + s1) / 2)
    if fhi(wt, wb) - flo(wt, wb) < 3:
        return None
    n_s = max(3, int((s1 - s0) / step))
    ss = [s0 + (s1 - s0) * i / n_s for i in range(n_s + 1)]
    
    # Add subtle organic coastline variation along dorsal & ventral coast
    top = []
    for idx, s in enumerate(ss):
        rel = (s - s0) / (s1 - s0)
        # organic ripple, zero at ends
        wave = 1.8 * math.sin(math.pi * rel) * (0.6 * math.sin(3 * math.pi * rel + seed) + 0.4 * math.cos(5 * math.pi * rel))
        top.append(tube.off(s, lambda wt, wb: fhi(wt, wb) + wave))
        
    bot = []
    for idx, s in enumerate(reversed(ss)):
        rel = (s - s0) / (s1 - s0)
        wave = 1.6 * math.sin(math.pi * rel) * (0.6 * math.cos(3 * math.pi * rel + seed * 2) - 0.4 * math.sin(4 * math.pi * rel))
        bot.append(tube.off(s, lambda wt, wb: flo(wt, wb) - wave))

    def cap(s, f_from, f_to, is_end=False):
        x, y, wt, wb, nx, ny = tube.at(s)
        a, b = f_from(wt, wb), f_to(wt, wb)
        k = max(2, int(abs(b - a) / step))
        pts = []
        for j in range(1, k):
            u = j / float(k)
            # slight bowing inward or outward along the channel cut
            bow = 1.5 * math.sin(math.pi * u) * (-1 if is_end else 1)
            d = a + (b - a) * u
            pts.append((x + nx * d + (-ny) * bow, y + ny * d + nx * bow))
        return pts

    return top + cap(s1, fhi, flo, is_end=True) + bot + cap(s0, flo, fhi, is_end=False)

p_org = organic_piece(body, 212 + hg, 286 - hg, lo=lambda wt, wb: split_belly(wt, wb) + hg, seed=3)

print("Original piece points:", len(p_orig))
print("Organic piece points:", len(p_org))
