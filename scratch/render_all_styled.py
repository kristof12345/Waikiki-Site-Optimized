import sys
sys.path.insert(0, "/Volumes/Samsung X5 SSD/Projektek/Site/scripts")
from gen_island_maps import world_svg, chameleon_svg, palm_svg, L

with open("/Volumes/Samsung X5 SSD/Projektek/Site/css/infrastructure.css") as f:
    css = f.read()

# Extract the SVG map styles from infrastructure.css
style_block = f"<style>\n{css}\n</style>"

t = L["en"]
p_svg = "\n".join(palm_svg(t)).replace("<defs>", f"<defs>\n{style_block}")
w_svg = "\n".join(world_svg(t)).replace("<defs>", f"<defs>\n{style_block}")
c_svg = "\n".join(chameleon_svg(t)).replace("<defs>", f"<defs>\n{style_block}")

with open("/Volumes/Samsung X5 SSD/Projektek/Site/scratch/styled_palm.svg", "w") as f:
    f.write(p_svg)
with open("/Volumes/Samsung X5 SSD/Projektek/Site/scratch/styled_world.svg", "w") as f:
    f.write(w_svg)
with open("/Volumes/Samsung X5 SSD/Projektek/Site/scratch/styled_cham.svg", "w") as f:
    f.write(c_svg)

print("Generated styled_palm.svg, styled_world.svg, styled_cham.svg")
