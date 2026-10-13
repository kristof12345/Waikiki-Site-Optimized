#!/usr/bin/env python3
import sys, os, re, math
sys.path.insert(0, '/Volumes/Samsung X5 SSD/Projektek/Site/scripts')
import gen_island_maps as g
from gen_island_maps import Tube, CH_BODY_KNOTS, poly_path, pt, n

body = Tube(CH_BODY_KNOTS)
s_road_end = body.L - 26
spine_road = [body.off(s_road_end * q / 180, lambda wt, wb: 0.28 * wt * (q / 180)**0.5 if q > 0 else 0) for q in range(181)]

# spine_road[0] is snout (962, 269)
# spine_road[180] is spiral tail

villas = (920, 410)
atoll = (villas[0], villas[1] - 20) # (920, 390)

# Tongue knots from atoll to snout:
# (920, 390), (944, 375), (960, 346), (968, 318), (965, 292), (962, 269)

# If we build a spline from atoll -> Islet 4 -> Islet 3 -> Islet 2 -> Islet 1 -> Snout -> spine_road[1] -> spine_road[3]...
def catmull_rom_spline(pts, alpha=0.5, n_steps=20):
    def dist(pA, pB):
        return max(1e-4, math.hypot(pB[0] - pA[0], pB[1] - pA[1]) ** alpha)

    curve = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i-1], pts[i], pts[i+1], pts[i+2]
        t0 = 0.0
        t1 = t0 + dist(p0, p1)
        t2 = t1 + dist(p1, p2)
        t3 = t2 + dist(p2, p3)
        for s in range(n_steps):
            t = t1 + (t2 - t1) * (s / float(n_steps))
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
            curve.append((round(cx, 2), round(cy, 2)))
    curve.append(pts[-2])
    return curve

def test_variant(name, tongue_pts):
    # tongue_pts starts at atoll and ends at snout = spine_road[0]
    # combined single path: tongue_pts[:-1] + spine_road
    full_road = tongue_pts[:-1] + spine_road
    d = poly_path(full_road, close=False)
    
    svg_lines = g.chameleon_svg(g.L['en'])
    svg_text = "\n".join(svg_lines)
    svg_text = re.sub(r'<!-- Overwater Road linking the Tongue Islets.*?/>\n?', '', svg_text, flags=re.DOTALL)
    new_road_svg = f'<!-- Chameleon Boulevard and Overwater Tongue Road (continuous spine road) -->\n<path class="map-road" d="{d}" />'
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
    
    html_zoom = html.replace('viewBox="0 0 1200 700"', 'viewBox="900 150 300 400"')
    base_path = f'/Users/kristof/.gemini/antigravity-ide/brain/4ffed735-ad3b-4b01-8196-232b554fd79d/scratch/{name}'
    with open(f'{base_path}_zoom.html', 'w', encoding='utf-8') as f:
        f.write(html_zoom)
    os.system(f'"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --window-size=900,1200 --screenshot={base_path}_zoom.png file://{base_path}_zoom.html >/dev/null 2>&1')
    print(f"Rendered {name}")

# Variant 1: Catmull-Rom with spine continuity
# Knots from atoll to snout, then points along spine
knots1 = [
    (904, 396), # tangent guide entering atoll
    atoll,      # (920, 390)
    (944, 375),
    (960, 346),
    (968, 318),
    (965, 292),
    spine_road[0], # (962, 269) Snout
    spine_road[2],
    spine_road[5]
]
# Segment from atoll (idx 1) to snout (idx 6)
c1 = catmull_rom_spline(knots1[:8], alpha=0.5, n_steps=25)
test_variant("spline_cr_centripetal", c1)

# Variant 2: Uniform Catmull-Rom (alpha=0.0)
c2 = catmull_rom_spline(knots1[:8], alpha=0.0, n_steps=25)
test_variant("spline_cr_uniform", c2)

# Variant 3: Chaikin with 3 rounds, then smooth connection
# Let's test knots with Chaikin
def chaikin_subdiv(pts, rounds=3):
    for _ in range(rounds):
        q = [pts[0]]
        for i in range(len(pts) - 1):
            p0, p1 = pts[i], pts[i+1]
            q.append((0.75 * p0[0] + 0.25 * p1[0], 0.75 * p0[1] + 0.25 * p1[1]))
            q.append((0.25 * p0[0] + 0.75 * p1[0], 0.25 * p0[1] + 0.75 * p1[1]))
        q.append(pts[-1])
        pts = q
    return pts

c3_knots = [
    (910, 393),
    atoll,
    (944, 375),
    (960, 346),
    (968, 318),
    (965, 292),
    spine_road[0],
    spine_road[1],
    spine_road[2]
]
c3_full = chaikin_subdiv(c3_knots, 3)
# Find snout index
snout_idx = min(range(len(c3_full)), key=lambda k: math.hypot(c3_full[k][0]-spine_road[0][0], c3_full[k][1]-spine_road[0][1]))
c3 = c3_full[1:snout_idx+1]
test_variant("spline_chaikin_flow", c3)
