#!/usr/bin/env python3
import sys, os, re, math
sys.path.insert(0, '/Volumes/Samsung X5 SSD/Projektek/Site/scripts')
import gen_island_maps as g
from gen_island_maps import Tube, CH_BODY_KNOTS, poly_path, pt, n

body = Tube(CH_BODY_KNOTS)
s_road_end = body.L - 26
spine_road = [body.off(s_road_end * q / 180, lambda wt, wb: 0.28 * wt * (q / 180)**0.5 if q > 0 else 0) for q in range(181)]

# Snout is spine_road[0] = (962.0, 269.0)
snout = spine_road[0]
# Tangent exiting snout towards tongue:
p_in = spine_road[2] # inside the head
v_exit = (snout[0] - p_in[0], snout[1] - p_in[1]) # direction leaving snout
v_len = math.hypot(v_exit[0], v_exit[1])
u_exit = (v_exit[0] / v_len, v_exit[1] / v_len)

tongue_islets = [
    (965, 292), # Islet 1
    (968, 318), # Islet 2
    (960, 346), # Islet 3
    (944, 375), # Islet 4
    (920, 392), # Paradise Atoll entrance
]

def render_variant(name, tongue_pts):
    # tongue_pts goes from Atoll (tongue_pts[0]) to Snout (tongue_pts[-1] = snout)
    # Then joins spine_road[1:]
    full_road = tongue_pts[:-1] + spine_road
    road_d = poly_path(full_road, close=False)
    
    svg_lines = g.chameleon_svg(g.L['en'])
    svg_text = "\n".join(svg_lines)
    svg_text = re.sub(r'<!-- Overwater Road linking the Tongue Islets.*?/>\n?', '', svg_text, flags=re.DOTALL)
    new_road_svg = f'<!-- Chameleon Boulevard and Overwater Tongue Road (continuous spine road) -->\n<path class="map-road" d="{road_d}" />'
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
    
    html_zoom = html.replace('viewBox="0 0 1200 700"', 'viewBox="1030 180 180 320"')
    
    base_path = f'/Users/kristof/.gemini/antigravity-ide/brain/4ffed735-ad3b-4b01-8196-232b554fd79d/scratch/{name}'
    with open(f'{base_path}.html', 'w', encoding='utf-8') as f:
        f.write(html)
    with open(f'{base_path}_zoom.html', 'w', encoding='utf-8') as f:
        f.write(html_zoom)
        
    os.system(f'"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --window-size=1200,700 --screenshot={base_path}.png file://{base_path}.html >/dev/null 2>&1')
    os.system(f'"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --window-size=600,900 --screenshot={base_path}_zoom.png file://{base_path}_zoom.html >/dev/null 2>&1')
    print(f"Rendered {name}")

# Test 1: Cubic Bezier spline through:
# Snout -> Islet 1 -> Islet 2 -> Islet 3 -> Islet 4 -> Atoll
# Snout tangent = u_exit * factor
def make_bezier_samples(lead_dist=12):
    # From snout to atoll
    p_snout = snout
    # Forward guide point exiting snout along spine direction:
    p_lead = (p_snout[0] + u_exit[0] * lead_dist, p_snout[1] + u_exit[1] * lead_dist)
    
    # Points in order from snout to atoll:
    chain = [p_snout, p_lead, tongue_islets[0], tongue_islets[1], tongue_islets[2], tongue_islets[3], tongue_islets[4]]
    
    # Dense Chaikin or Catmull-Rom through chain:
    # Catmull-Rom
    curve = []
    p = [p_snout] + chain + [tongue_islets[4]]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i-1], p[i], p[i+1], p[i+2]
        for step in range(20):
            t = step / 20.0
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
    curve.append(tongue_islets[4])
    
    # Reverse so it goes from Atoll to Snout
    return curve[::-1]

render_variant("smooth_lead8", make_bezier_samples(8))
render_variant("smooth_lead14", make_bezier_samples(14))
render_variant("smooth_lead20", make_bezier_samples(20))
