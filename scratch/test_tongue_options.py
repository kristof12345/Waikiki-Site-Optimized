#!/usr/bin/env python3
import sys, os, re, math
sys.path.insert(0, '/Volumes/Samsung X5 SSD/Projektek/Site/scripts')
import gen_island_maps as g
from gen_island_maps import Tube, CH_BODY_KNOTS, CH_LIMBS, CH_GAP, CH_SPIRAL, smooth_closed, smooth_island, circle_d, poly_path, pt, n, hotspot, map_header

def catmull_rom_spline(pts, num_samples_per_seg=20, end_tangent=None, start_tangent=None):
    if start_tangent:
        p0_phantom = (pts[0][0] - start_tangent[0], pts[0][1] - start_tangent[1])
    else:
        p0_phantom = (2 * pts[0][0] - pts[1][0], 2 * pts[0][1] - pts[1][1])
        
    if end_tangent:
        p_last_phantom = (pts[-1][0] + end_tangent[0], pts[-1][1] + end_tangent[1])
    else:
        p_last_phantom = (2 * pts[-1][0] - pts[-2][0], 2 * pts[-1][1] - pts[-2][1])
        
    p = [p0_phantom] + pts + [p_last_phantom]
    curve = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i-1], p[i], p[i+1], p[i+2]
        for t_step in range(num_samples_per_seg):
            t = t_step / float(num_samples_per_seg)
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

def render_preview(variant_name, tongue_pts_func):
    body = Tube(CH_BODY_KNOTS)
    s_road_end = body.L - 26
    spine_road = [body.off(s_road_end * q / 180, lambda wt, wb: 0.28 * wt * (q / 180)**0.5 if q > 0 else 0) for q in range(181)]
    
    tongue_curve = tongue_pts_func(body, spine_road)
    # Join into one single path: from tongue tip (Paradise Atoll) to snout, then continuing along spine
    # tongue_curve ends at snout (spine_road[0])
    combined_road = tongue_curve + spine_road[1:]
    
    # Generate SVG using modified chameleon_svg
    svg_lines = g.chameleon_svg(g.L['en'])
    # Replace the road paths with our combined path
    svg_text = "\n".join(svg_lines)
    
    # Remove old overwater road
    svg_text = re.sub(r'<!-- Overwater Road linking the Tongue Islets.*?/>\n?', '', svg_text, flags=re.DOTALL)
    # Replace Chameleon Boulevard path with combined road
    new_road_svg = f'<!-- Chameleon Boulevard and Overwater Tongue Road (continuous spine road) -->\n<path class="map-road" d="{poly_path(combined_road, close=False)}" />'
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
    
    out_html = f'/Users/kristof/.gemini/antigravity-ide/brain/4ffed735-ad3b-4b01-8196-232b554fd79d/scratch/{variant_name}.html'
    out_png = f'/Users/kristof/.gemini/antigravity-ide/brain/4ffed735-ad3b-4b01-8196-232b554fd79d/scratch/{variant_name}.png'
    with open(out_html, 'w', encoding='utf-8') as f:
        f.write(html)
        
    os.system(f'"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars --window-size=1200,700 --screenshot={out_png} file://{out_html} >/dev/null 2>&1')
    print(f"Rendered {variant_name}: {out_png}")

# Let's test Variant 1: Catmull-Rom through the 6 points
def var1_pts(body, spine_road):
    tongue = [(965, 292), (968, 318), (960, 346), (944, 375)]
    villas = (920, 410)
    # knots from Paradise Atoll to snout
    pts = [(villas[0], villas[1] - 20)] + tongue[::-1] + [body.off(0, 0)]
    # tangent entering body from snout
    p_snout = body.off(0, 0)
    p_next = spine_road[2]
    tan = (p_next[0] - p_snout[0], p_next[1] - p_snout[1])
    return catmull_rom_spline(pts, num_samples_per_seg=20, end_tangent=tan)

render_preview("road_variant1", var1_pts)

