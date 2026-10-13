#!/usr/bin/env python3
import sys, os, re, math
sys.path.insert(0, '/Volumes/Samsung X5 SSD/Projektek/Site/scripts')
import gen_island_maps as g
from gen_island_maps import Tube, CH_BODY_KNOTS, poly_path, pt, n

body = Tube(CH_BODY_KNOTS)
s_road_end = body.L - 26
spine_road = [body.off(s_road_end * q / 180, lambda wt, wb: 0.28 * wt * (q / 180)**0.5 if q > 0 else 0) for q in range(181)]

tongue = [(965, 292), (968, 318), (960, 346), (944, 375)]
villas = (920, 410)
atoll_entry = (villas[0], villas[1] - 20) # (920, 390)

# The sequence of key knots from atoll to snout, and continuing into the head
# Knots: Atoll -> Islet 4 -> Islet 3 -> Islet 2 -> Islet 1 -> Snout -> Spine point 4 -> Spine point 8 ...
knots = [atoll_entry, tongue[3], tongue[2], tongue[1], tongue[0], spine_road[0]]

# Let's test Method 1: Centripetal Catmull-Rom with proper continuity
def test_method1():
    # We include points along the spine to ensure 100% C1 continuity at the snout!
    # spine_road[0] is snout.
    # spine_road[1], spine_road[2], spine_road[3] are inside the head.
    guide_pts = [atoll_entry, tongue[3], tongue[2], tongue[1], tongue[0], spine_road[0], spine_road[2], spine_road[5]]
    
    # Generate smooth Catmull-Rom spline from atoll_entry to spine_road[0]
    p = [ (2*guide_pts[0][0] - guide_pts[1][0], 2*guide_pts[0][1] - guide_pts[1][1]) ] + guide_pts
    
    # We only interpolate segments from guide_pts[0] up to guide_pts[5] (which is snout)
    curve = []
    num_samples = 25
    for i in range(1, 6): # up to guide_pts[5] (snout)
        p0, p1, p2, p3 = p[i-1], p[i], p[i+1], p[i+2]
        for step in range(num_samples):
            t = step / float(num_samples)
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
            
    # curve ends at snout!
    # Append the rest of spine_road (from index 1 onwards)
    return curve + spine_road[1:]

# Method 2: Cubic Bezier spline through the knots
def test_method2():
    # Natural Catmull-Rom converted to Bezier C commands:
    # Atoll -> Islet 4 -> Islet 3 -> Islet 2 -> Islet 1 -> Snout
    guide_pts = [atoll_entry, tongue[3], tongue[2], tongue[1], tongue[0], spine_road[0], spine_road[2]]
    p = [ (2*guide_pts[0][0] - guide_pts[1][0], 2*guide_pts[0][1] - guide_pts[1][1]) ] + guide_pts
    
    # Bezier commands from atoll to snout
    d_parts = [f"M{pt(guide_pts[0])}"]
    for i in range(1, 6):
        p0, p1, p2, p3 = p[i-1], p[i], p[i+1], p[i+2]
        cp1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        cp2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        d_parts.append(f"C{pt(cp1)} {pt(cp2)} {pt(p2)}")
        
    # Then L commands along spine_road[1:]
    for pt_spine in spine_road[1:]:
        d_parts.append(f"L{pt(pt_spine)}")
    return " ".join(d_parts)

# Method 3: Hand-tuned graceful Bezier curve matching the crescent arc of the tongue
def test_method3():
    # Let's inspect the arc from Snout (962, 269) to Atoll (920, 390)
    # Passing through Islet 1 (965, 292), Islet 2 (968, 318), Islet 3 (960, 346), Islet 4 (944, 375)
    # With a smooth cubic Bezier segment per islet
    return test_method1()

def render(name, road_d):
    svg_lines = g.chameleon_svg(g.L['en'])
    svg_text = "\n".join(svg_lines)
    # Remove old overwater road
    svg_text = re.sub(r'<!-- Overwater Road linking the Tongue Islets.*?/>\n?', '', svg_text, flags=re.DOTALL)
    # Replace Chameleon Boulevard path with combined road
    new_road_svg = f'<!-- Chameleon Boulevard (continuous road from Paradise Atoll across Tongue Islets and Snout to the Spiral Tail) -->\n<path class="map-road" d="{road_d}" />'
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

m1_pts = test_method1()
render("m1_dense_spline", poly_path(m1_pts, close=False))

m2_d = test_method2()
render("m2_bezier_spline", m2_d)
