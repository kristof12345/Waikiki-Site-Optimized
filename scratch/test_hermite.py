#!/usr/bin/env python3
import sys, os, re, math
sys.path.insert(0, '/Volumes/Samsung X5 SSD/Projektek/Site/scripts')
import gen_island_maps as g
from gen_island_maps import Tube, CH_BODY_KNOTS, poly_path, pt, n

body = Tube(CH_BODY_KNOTS)
s_road_end = body.L - 26
spine_road = [body.off(s_road_end * q / 180, lambda wt, wb: 0.28 * wt * (q / 180)**0.5 if q > 0 else 0) for q in range(181)]

snout = spine_road[0] # (962.0, 269.0)
# Vector leaving snout into spine road:
v_spine = (spine_road[1][0] - snout[0], spine_road[1][1] - snout[1])
l_spine = math.hypot(v_spine[0], v_spine[1])
# Unit tangent entering body from snout:
T_snout = (v_spine[0] / l_spine, v_spine[1] / l_spine)

knots = [
    (920, 392), # 0: Atoll
    (944, 375), # 1: Islet 4
    (960, 346), # 2: Islet 3
    (968, 318), # 3: Islet 2
    (965, 292), # 4: Islet 1
    snout       # 5: Snout
]

def hermite_spline(pts, t_start=None, t_end=None, num_samples_per_seg=30):
    # Compute tangents at each point
    tangents = []
    n_pts = len(pts)
    for i in range(n_pts):
        if i == 0:
            if t_start:
                tangents.append(t_start)
            else:
                tangents.append(((pts[1][0] - pts[0][0]), (pts[1][1] - pts[0][1])))
        elif i == n_pts - 1:
            if t_end:
                tangents.append(t_end)
            else:
                tangents.append(((pts[-1][0] - pts[-2][0]), (pts[-1][1] - pts[-2][1])))
        else:
            # Average tangent
            dx = (pts[i+1][0] - pts[i-1][0]) * 0.5
            dy = (pts[i+1][1] - pts[i-1][1]) * 0.5
            tangents.append((dx, dy))
            
    curve = []
    for i in range(n_pts - 1):
        p0, p1 = pts[i], pts[i+1]
        m0, m1 = tangents[i], tangents[i+1]
        for step in range(num_samples_per_seg):
            t = step / float(num_samples_per_seg)
            t2 = t * t
            t3 = t2 * t
            # Hermite basis
            h00 = 2*t3 - 3*t2 + 1
            h10 = t3 - 2*t2 + t
            h01 = -2*t3 + 3*t2
            h11 = t3 - t2
            x = h00 * p0[0] + h10 * m0[0] + h01 * p1[0] + h11 * m1[0]
            y = h00 * p0[1] + h10 * m0[1] + h01 * p1[1] + h11 * m1[1]
            curve.append((round(x, 2), round(y, 2)))
    curve.append(pts[-1])
    return curve

def render_test(name, t_snout_scale=20.0, t_atoll=(-20.0, 10.0)):
    # t_end at snout: we want the curve (which arrives at snout) to have tangent T_snout * scale
    t_snout = (T_snout[0] * t_snout_scale, T_snout[1] * t_snout_scale)
    c = hermite_spline(knots, t_start=t_atoll, t_end=t_snout, num_samples_per_seg=30)
    
    full = c[:-1] + spine_road
    d = poly_path(full, close=False)
    
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

for scale in [15.0, 25.0, 35.0, 50.0]:
    render_test(f"hermite_scale{int(scale)}", t_snout_scale=scale)

