import sys
sys.path.insert(0, "/Volumes/Samsung X5 SSD/Projektek/Site/scripts")
from gen_island_maps import world_svg, chameleon_svg, L

t = L["en"]
w_svg = "\n".join(world_svg(t))
c_svg = "\n".join(chameleon_svg(t))

with open("/Volumes/Samsung X5 SSD/Projektek/Site/scratch/test_world.svg", "w") as f:
    f.write(w_svg)
with open("/Volumes/Samsung X5 SSD/Projektek/Site/scratch/test_cham.svg", "w") as f:
    f.write(c_svg)
print("Saved test_world.svg and test_cham.svg")
