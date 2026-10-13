#!/usr/bin/env python3
import sys, os, re, math
sys.path.insert(0, '/Volumes/Samsung X5 SSD/Projektek/Site/scripts')
import gen_island_maps as g
from gen_island_maps import Tube, CH_BODY_KNOTS, poly_path, pt, n

body = Tube(CH_BODY_KNOTS)
s_road_end = body.L - 26
spine_road = [body.off(s_road_end * q / 180, lambda wt, wb: 0.28 * wt * (q / 180)**0.5 if q > 0 else 0) for q in range(181)]

snout = spine_road[0] # (962.0, 269.0)
villas = (920, 410)
atoll = (villas[0], villas[1] - 20) # (920, 390)

# Full sequence of knots from Atoll through Tongue, around Snout, into Head spine:
# Let's see:
# Atoll -> Islet 4 -> Islet 3 -> Islet 2 -> Islet 1 -> Snout -> spine points
# If we treat the whole road from atoll into spine as a continuous spline:
# Spine points: spine_road[1], spine_road[2], spine_road[3], spine_road[4], spine_road[6]...

# What if we build a smooth spline from atoll all the way into the head,
# say up to spine_road[10] (which is well inside the head),
# and from spine_road[10] onwards use spine_road[10:]?

tongue_and_head_knots = [
    (910, 393),   # lead into atoll
    atoll,        # (920, 390)
    (944, 375),   # Islet 4
    (960, 346),   # Islet 3
    (968, 318),   # Islet 2
    (965, 292),   # Islet 1
    (963, 271),   # soft snout tip fillet
    spine_road[2],# (951.3, 265.0)
    spine_road[5],# (935.0, 260.0)
    spine_road[9] # inside head
]

def catmull_rom(knots, n_per_seg=25, alpha=0.5):
    pts = []
    k = knots
    for i in range(1, len(k) - 2):
        p0, p1, p2, p3 = k[i-1], k[i], k[i+1], k[i+2]
        def d(pa, pb):
            return max(1e-4, math.hypot(pb[0]-pa[0], pb[1]-pa[1]) ** alpha)
        t0 = 0.0
        t1 = t0 + d(p0, p1)
        t2 = t1 + d(p1, p2)
        t3 = t2 + d(p2, p3)
        for s in range(n_per_seg):
            t = t1 + (t2 - t1) * (s / float(n_per_seg))
            a1_x = (t1-t)/(t1-t0)*p0[0] + (t-t0)/(t1-t0)*p1[0]
            a1_y = (t1-t)/(t1-t0)*p0[1] + (t-t0)/(t1-t0)*p1[1]
            a2_x = (t2-t)/(t2-t1)*p1[0] + (t-t1)/(t2-t1)*p2[0]
            a2_y = (t2-t)/(t2-t1)*p1[1] + (t-t1)/(t2-t1)*p2[1]
            a3_x = (t3-t)/(t3-t2)*p2[0] + (t-t2)/(t3-t2)*p3[0]
            a3_y = (t3-t)/(t3-t2)*p2[1] + (t-t2)/(t3-t2)*p3[1]
            b1_x = (t2-t)/(t2-t0)*a1_x + (t-t0)/(t2-t0)*a2_x
            b1_y = (t2-t)/(t2-t0)*a1_y + (t-t0)/(t2-t0)*a2_y
            b2_x = (t3-t)/(t3-t1)*a2_x + (t-t1)/(t3-t1)*a3_x
            b2_y = (t3-t)/(t3-t1)*a2_y + (t-t1)/(t3-t1)*a3_y
            cx = (t2-t)/(t2-t1)*b1_x + (t-t1)/(t2-t1)*b2_x
            cy = (t2-t)/(t2-t1)*b1_y + (t-t1)/(t2-t1)*b2_y
            pts.append((round(cx, 2), round(cy, 2)))
    pts.append(k[-2])
    return pts

# Test different snout knots:
# Variant A: passes through exact snout (962, 269)
knots_A = [
    (910, 393), atoll, (944, 375), (960, 346), (968, 318), (965, 292),
    (962, 269), spine_road[2], spine_road[5], spine_road[9]
]
spline_A = catmull_rom(knots_A, 25, 0.5)
# Find closest point to spine_road[5]
idx_A = min(range(len(spline_A)), key=lambda k: math.hypot(spline_A[k][0]-spine_road[5][0], spline_A[k][1]-spine_road[5][1]))
road_A = spline_A[:idx_A] + spine_road[5:]

# Variant B: rounded snout apex at (963.5, 271)
knots_B = [
    (910, 393), atoll, (944, 375), (960, 346), (968, 318), (965, 292),
    (963.5, 271.5), spine_road[2], spine_road[5], spine_road[9]
]
spline_B = catmull_rom(knots_B, 25, 0.5)
idx_B = min(range(len(spline_B)), key=lambda k: math.hypot(spline_B[k][0]-spine_road[5][0], spline_B[k][1]-spine_road[5][1]))
road_B = spline_B[:idx_B] + spine_road[5:]

# Variant C: Chaikin rounding of the whole head-snout-tongue polyline
knots_C = [atoll, (944, 375), (960, 346), (968, 318), (965, 292), (962, 269)] + spine_road[:8]
pts_C = list(knots_C)
for _ in range(3):
    q = [pts_C[0]]
    for i in range(len(pts_C) - 1):
        p0, p1 = pts_C[i], pts_C[i+1]
        q.append((0.75 * p0[0] + 0.25 * p1[0], 0.75 * p0[1] + 0.25 * p1[1]))
        q.append((0.25 * p0[0] + 0.75 * p1[0], 0.25 * p0[1] + 0.75 * p1[1]))
    q.append(pts_C[-1])
    pts_C = q
idx_C = min(range(len(pts_C)), key=lambda k: math.hypot(pts_C[k][0]-spine_road[5][0], pts_C[k][1]-spine_road[5][1]))
road_C = pts_C[:idx_C] + spine_road[5:]

def render(name, full_road):
    d = poly_path(full_road, close=False)
    svg_lines = g.chameleon_svg(g.L['en'])
    svg_text = "\n".join(svg_lines)
    svg_text = re.sub(r'<!-- Overwater Road linking the Tongue Islets.*?/>\n?', '', svg_text, flags=re.DOTALL)
    new_road_svg = f'<!-- Chameleon Boulevard and Overwater Tongue Road (continuous spine road from Paradise Atoll to Spiral Tail) -->\n<path class="map-road" d="{d}" />'
    svg_text = re.sub(r'<!-- Chameleon Boulevard.*?/>', new_road_svg, svg_text, flags=re.DOTALL)
    
    css = open('/Volumes/Samsung X5 SSD/Projektek/Site/css/infrastructure.css', encoding='utf-8').read()
    m = re.search(r'/\* SVG Map Artwork Classes \*/(.*?)/\* Interactive Map Hotspot Pins', css, re.S)
    hs = re.search(r'(\.map-hotspot \{.*?)\n\.map-tooltip \{', css, re.S)
    
    html = f"""<!doctype html><html><head><style>
body{{margin:0;background:#051329}} :root{{--font-sans:Helvetica,Arial,sans-serif}}
.island-map-canvas svg{{width:1200px;height:700px;display:block}}
{m.group(1)}
{hs.group(1) if hs else ''}
</style></head><body><div class="island-map-canvas">{svg_text}</div></body></html>"""
    
    html_zoom = html.replace('viewBox="0 0 1200 700"', 'viewBox="880 180 320 360"')
    base_path = f'/Users/kristof/.gemini/antigravity-ide/brain/4ffed735-ad3b-4b01-8196-232b554fd79d/scratch/{name}'
    with open(f'{base_path}_zoom.html', 'w', encoding='utf-8') as f:
        f.write(html_zoom)
        
    cmd = f'"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --window-size=960,1080 --screenshot={base_path}_zoom.png file://{base_path}_zoom.html'
    os.system(cmd)
    print(f"Rendered {name}")

render("blend_A_exact_snout", road_A)
render("blend_B_rounded_snout", road_B)
render("blend_C_chaikin_snout", road_C)
