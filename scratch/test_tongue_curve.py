#!/usr/bin/env python3
import sys, os, math, re
sys.path.insert(0, '/Volumes/Samsung X5 SSD/Projektek/Site/scripts')
import gen_island_maps as g
from gen_island_maps import Tube, CH_BODY_KNOTS, CH_LIMBS, CH_GAP, CH_SPIRAL, smooth_closed, smooth_island, circle_d, poly_path, pt, n, hotspot, map_header

def get_tongue_spline(pts, end_tangent_snout=None, num_samples=25):
    # pts: [(920, 390), (944, 375), (960, 346), (968, 318), (965, 292), (962, 269)]
    # end_tangent_snout: vector entering snout body (dx, dy)
    p0_phantom = (2 * pts[0][0] - pts[1][0], 2 * pts[0][1] - pts[1][1])
    if end_tangent_snout:
        p_last_phantom = (pts[-1][0] + end_tangent_snout[0], pts[-1][1] + end_tangent_snout[1])
    else:
        p_last_phantom = (2 * pts[-1][0] - pts[-2][0], 2 * pts[-1][1] - pts[-2][1])
        
    p = [p0_phantom] + pts + [p_last_phantom]
    curve = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i-1], p[i], p[i+1], p[i+2]
        for t_step in range(num_samples):
            t = t_step / float(num_samples)
            t2 = t * t
            t3 = t2 * t
            x = 0.5 * ((2 * p1[0]) +
                       (-p0[0] + p2[0]) * t +
                       (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) +
                       (-p0[1] + p2[1]) * t +
                       (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1]) * t3)
            curve.append((round(x, 2), round(y, 2)))
    curve.append(pts[-1])
    return curve

def get_tongue_bezier(pts, end_tangent_snout=None):
    # Emit cubic Bezier path string
    p0_phantom = (2 * pts[0][0] - pts[1][0], 2 * pts[0][1] - pts[1][1])
    if end_tangent_snout:
        p_last_phantom = (pts[-1][0] + end_tangent_snout[0], pts[-1][1] + end_tangent_snout[1])
    else:
        p_last_phantom = (2 * pts[-1][0] - pts[-2][0], 2 * pts[-1][1] - pts[-2][1])
    p = [p0_phantom] + pts + [p_last_phantom]
    
    d = [f"M{pt(pts[0])}"]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i-1], p[i], p[i+1], p[i+2]
        # Catmull-Rom to Bezier control points:
        # cp1 = p1 + (p2 - p0) / 6
        # cp2 = p2 - (p3 - p1) / 6
        cp1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        cp2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d.append(f"C{pt(cp1)} {pt(cp2)} {pt(p2)}")
    return " ".join(d)

print("Spline functions ready")
