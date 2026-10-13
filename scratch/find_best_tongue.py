#!/usr/bin/env python3
import sys, os, re, math
sys.path.insert(0, '/Volumes/Samsung X5 SSD/Projektek/Site/scripts')
import gen_island_maps as g
from gen_island_maps import Tube, CH_BODY_KNOTS, poly_path, pt, n

body = Tube(CH_BODY_KNOTS)
s_road_end = body.L - 26
spine_road = [body.off(s_road_end * q / 180, lambda wt, wb: 0.28 * wt * (q / 180)**0.5 if q > 0 else 0) for q in range(181)]

# Knots
snout = spine_road[0] # (962, 269)
tongue = [
    (965, 292), # Islet 1
    (968, 318), # Islet 2
    (960, 346), # Islet 3
    (944, 375), # Islet 4
]
villas = (920, 410)
atoll = (villas[0], villas[1] - 20) # (920, 390)

# Option A: Smooth cubic bezier using Catmull-Rom to Bezier conversion
def option_a(alpha=0.5): # alpha=0.5 centripetal, alpha=0 uniform
    # Sequence of points from Atoll to Snout, plus spine points for tangent continuity
    pts = [atoll, tongue[3], tongue[2], tongue[1], tongue[0], snout, spine_road[2], spine_road[6]]
    
    # We want to interpolate from pts[0] (Atoll) to pts[5] (Snout)
    # Centripetal Catmull-Rom
    curve = []
    # Add phantom start
    p_start_phantom = (2*pts[0][0] - pts[1][0], 2*pts[0][1] - pts[1][1])
    full_knots = [p_start_phantom] + pts
    
    for i in range(1, 6): # segments from 0 to 5
        p0, p1, p2, p3 = full_knots[i-1], full_knots[i], full_knots[i+1], full_knots[i+2]
        
        # Centripetal parameterization
        def dist(pa, pb):
            return max(1e-4, math.hypot(pb[0]-pa[0], pb[1]-pa[1]) ** alpha)
            
        t0 = 0.0
        t1 = t0 + dist(p0, p1)
        t2 = t1 + dist(p1, p2)
        t3 = t2 + dist(p2, p3)
        
        num_steps = 25
        for s in range(num_steps):
            t = t1 + (t2 - t1) * (s / float(num_steps))
            
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
            
            c_x = (t2-t)/(t2-t1)*b1_x + (t-t1)/(t2-t1)*b2_x
            c_y = (t2-t)/(t2-t1)*b1_y + (t-t1)/(t2-t1)*b2_y
            
            curve.append((round(c_x, 2), round(c_y, 2)))
            
    curve.append(snout)
    return curve

# Option B: Chaikin subdivision of knots
def option_b():
    knots = [atoll, tongue[3], tongue[2], tongue[1], tongue[0], snout, spine_road[2]]
    # Chaikin rounds
    pts = list(knots)
    for _ in range(4):
        q = [pts[0]]
        for i in range(len(pts) - 1):
            p0, p1 = pts[i], pts[i+1]
            q.append((0.75*p0[0] + 0.25*p1[0], 0.75*p0[1] + 0.25*p1[1]))
            q.append((0.25*p0[0] + 0.75*p1[0], 0.25*p0[1] + 0.75*p1[1]))
        q.append(pts[-1])
        pts = q
    # find where snout is and truncate
    # snout is near the end
    idx = min(range(len(pts)), key=lambda k: math.hypot(pts[k][0]-snout[0], pts[k][1]-snout[1]))
    return pts[:idx] + [snout]

# Option C: Natural cubic spline passing through the knots
def option_c():
    # Centripetal Catmull-Rom with alpha=0.5
    return option_a(alpha=0.5)

def render(name, curve_func):
    c = curve_func()
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

render("opt_a_centripetal", lambda: option_a(0.5))
render("opt_a_uniform", lambda: option_a(0.0))
render("opt_b_chaikin", option_b)
