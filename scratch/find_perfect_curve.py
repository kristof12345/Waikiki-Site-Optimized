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

# Knots from Atoll to Snout
# Let's inspect options:
# 1) Natural cubic spline / Bezier through (920, 390), (944, 375), (960, 346), (968, 318), (965, 292), snout
# 2) Catmull-Rom with centripetal parameterization
# 3) Cubic Bezier path directly

# Catmull-Rom sampling:
def cr_sample(knots, n_per_seg=20, alpha=0.5):
    # knots: list of (x, y)
    pts = []
    # pad ends
    p_start = (2*knots[0][0] - knots[1][0], 2*knots[0][1] - knots[1][1])
    p_end = (2*knots[-1][0] - knots[-2][0], 2*knots[-1][1] - knots[-2][1])
    k = [p_start] + knots + [p_end]
    
    for i in range(1, len(knots)):
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
    pts.append(knots[-1])
    return pts

# Option 1: Standard Catmull-Rom through the 5 islets and snout
knots_std = [atoll, (944, 375), (960, 346), (968, 318), (965, 292), snout]

# Option 2: Smooth approach into atoll (horizontal tangent) and snout
knots_tangent = [(912, 393), atoll, (944, 375), (960, 346), (968, 318), (965, 292), snout, (951, 265)]

def render_opt(name, curve):
    full_road = curve[:-1] + spine_road
    d = poly_path(full_road, close=False)
    
    svg_lines = g.chameleon_svg(g.L['en'])
    svg_text = "\n".join(svg_lines)
    # Remove old separate overwater road
    svg_text = re.sub(r'<!-- Overwater Road linking the Tongue Islets.*?/>\n?', '', svg_text, flags=re.DOTALL)
    # Update Chameleon Boulevard with the complete continuous path
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
    with open(f'{base_path}_full.html', 'w', encoding='utf-8') as f:
        f.write(html)
        
    cmd = f'"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --window-size=960,1080 --screenshot={base_path}_zoom.png file://{base_path}_zoom.html'
    os.system(cmd)
    print(f"Rendered {name}")

c1 = cr_sample(knots_std, n_per_seg=20, alpha=0.5)
render_opt("opt1_cr_std", c1)

# For knots_tangent, we slice from atoll to snout
c2_full = cr_sample(knots_tangent, n_per_seg=20, alpha=0.5)
# Find index of atoll and snout
idx_atoll = min(range(len(c2_full)), key=lambda k: math.hypot(c2_full[k][0]-atoll[0], c2_full[k][1]-atoll[1]))
idx_snout = min(range(len(c2_full)), key=lambda k: math.hypot(c2_full[k][0]-snout[0], c2_full[k][1]-snout[1]))
c2 = c2_full[idx_atoll:idx_snout+1]
render_opt("opt2_cr_tangent", c2)

# Option 3: Chaikin smoothing
def chaikin_smooth(pts, rounds=3):
    for _ in range(rounds):
        q = [pts[0]]
        for i in range(len(pts) - 1):
            p0, p1 = pts[i], pts[i+1]
            q.append((0.75 * p0[0] + 0.25 * p1[0], 0.75 * p0[1] + 0.25 * p1[1]))
            q.append((0.25 * p0[0] + 0.75 * p1[0], 0.25 * p0[1] + 0.75 * p1[1]))
        q.append(pts[-1])
        pts = q
    return pts

# Dense points along polyline then Chaikin
c3 = chaikin_smooth(knots_std, 4)
render_opt("opt3_chaikin", c3)
