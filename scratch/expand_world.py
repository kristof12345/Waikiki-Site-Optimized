import math
import sys
sys.path.insert(0, 'scripts')
import gen_island_maps

# Base islands
isles = list(gen_island_maps.WORLD_ISLES)

# 23 new gap-filling islands to test
new_isles = [
    # NORTH AMERICA GAPS
    {'name': 'Canadian Rockies and British Columbia', 'cx': 242, 'cy': 198, 'rx': 12, 'ry': 15, 'rot': 15, 'shape': 'arc', 'green': True},
    {'name': 'Newfoundland and Maritimes', 'cx': 396, 'cy': 184, 'rx': 14, 'ry': 12, 'rot': 25, 'green': True},
    {'name': 'Texas and Southern Great Plains', 'cx': 300, 'cy': 260, 'rx': 16, 'ry': 15, 'rot': 0, 'shape': 'taper'},
    {'name': 'Yucatan Peninsula', 'cx': 346, 'cy': 316, 'rx': 13, 'ry': 11, 'rot': 20, 'shape': 'taper', 'green': True},

    # SOUTH AMERICA GAPS
    {'name': 'Central Brazil and Cerrado Plateau', 'cx': 416, 'cy': 438, 'rx': 16, 'ry': 15, 'rot': 10, 'green': True},
    {'name': 'Paraguay and Gran Chaco Basin', 'cx': 366, 'cy': 466, 'rx': 13, 'ry': 14, 'rot': 5},
    {'name': 'Uruguay and Rio de la Plata', 'cx': 412, 'cy': 502, 'rx': 12, 'ry': 12, 'rot': 15, 'green': True},

    # EUROPE GAPS
    {'name': 'Denmark and Jutland Peninsula', 'cx': 566, 'cy': 168, 'rx': 9, 'ry': 13, 'rot': 10, 'shape': 'arc', 'green': True},
    {'name': 'France and Biscay Bay', 'cx': 524, 'cy': 232, 'rx': 14, 'ry': 13, 'rot': -10, 'green': True},
    {'name': 'Danube Basin and Romania', 'cx': 618, 'cy': 226, 'rx': 14, 'ry': 12, 'rot': 15, 'green': True},

    # AFRICA GAPS
    {'name': 'Libya and Central Sahara', 'cx': 580, 'cy': 326, 'rx': 18, 'ry': 13, 'rot': 0},
    {'name': 'Sudan and Nubia Basin', 'cx': 618, 'cy': 364, 'rx': 17, 'ry': 13, 'rot': 15},
    {'name': 'Central African Savannah', 'cx': 546, 'cy': 394, 'rx': 13, 'ry': 11, 'rot': 0, 'green': True},
    {'name': 'Mozambique Channel Coast', 'cx': 624, 'cy': 462, 'rx': 12, 'ry': 18, 'rot': -15, 'shape': 'arc', 'green': True},

    # ASIA GAPS
    {'name': 'Manchuria and Amur River Basin', 'cx': 888, 'cy': 174, 'rx': 18, 'ry': 13, 'rot': 10, 'green': True},
    {'name': 'East China Coast and Shanghai', 'cx': 890, 'cy': 236, 'rx': 13, 'ry': 14, 'rot': 15, 'green': True},
    {'name': 'Bengal and Ganges Delta', 'cx': 818, 'cy': 290, 'rx': 14, 'ry': 14, 'rot': 15, 'green': True},
    {'name': 'Sulawesi and Moluccas', 'cx': 924, 'cy': 358, 'rx': 12, 'ry': 14, 'rot': 25, 'shape': 'arc', 'green': True},
    {'name': 'Sakhalin Island Arc', 'cx': 946, 'cy': 158, 'rx': 7, 'ry': 14, 'rot': 10, 'shape': 'arc'},

    # OCEANIA GAPS
    {'name': 'Great Australian Bight and Adelaide', 'cx': 898, 'cy': 494, 'rx': 14, 'ry': 12, 'rot': 15, 'green': True},
    {'name': 'Solomon Islands and Coral Archipelago', 'cx': 996, 'cy': 396, 'rx': 14, 'ry': 8, 'rot': -20},

    # ANTARCTICA GAPS
    {'name': 'Marie Byrd Land Shelf', 'cx': 864, 'cy': 578, 'rx': 18, 'ry': 11, 'rot': -10, 'sand_light': True},
    {'name': 'Ellsworth Land Ice Shelf', 'cx': 358, 'cy': 598, 'rx': 18, 'ry': 10, 'rot': 10, 'sand_light': True},
]

all_isles = [dict(x) for x in isles] + [dict(x) for x in new_isles]
print(f"Total isles to test: {len(all_isles)}")

# Check ellipse bounds
ecx, ecy, erx, ery = 600, 345, 540, 305

def check_all(islands, min_gap=4.0):
    overlaps = []
    out_of_bounds = []
    n = len(islands)
    for i in range(n):
        a = islands[i]
        # check boundary
        d_norm = math.sqrt(((a['cx'] - ecx) / (erx - a['rx']))**2 + ((a['cy'] - ecy) / (ery - a['ry']))**2)
        if d_norm > 1.0:
            out_of_bounds.append((a['name'], d_norm))
        for j in range(i + 1, n):
            b = islands[j]
            dx = a['cx'] - b['cx']
            dy = a['cy'] - b['cy']
            dist = math.hypot(dx, dy)
            req_dist = max(a['rx'], a['ry']) + max(b['rx'], b['ry']) + min_gap
            if dist < req_dist:
                overlaps.append((a['name'], b['name'], dist, req_dist, req_dist - dist))
    return overlaps, out_of_bounds

ov, oob = check_all(all_isles, min_gap=3.0)
print(f"Initial overlaps: {len(ov)}, out of bounds: {len(oob)}")
for a, b, dist, req, pen in ov[:15]:
    print(f"  Overlap: {a} <-> {b}: dist={dist:.1f}, req={req:.1f}, pen={pen:.1f}")
