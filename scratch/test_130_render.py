import sys
sys.path.insert(0, 'scripts')
import gen_island_maps
import scratch.relaxed_130_isles as r130

# Override WORLD_ISLES
gen_island_maps.WORLD_ISLES = r130.WORLD_ISLES_130

# Also test rendering
svg_lines = gen_island_maps.world_svg(gen_island_maps.L['en'])
svg_content = "\n".join(svg_lines)

with open('scratch/test_world_130.svg', 'w') as f:
    f.write(svg_content)

print("Wrote scratch/test_world_130.svg successfully!")
