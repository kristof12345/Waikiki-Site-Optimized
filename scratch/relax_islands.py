import math
import copy
from scratch.test_tight_continents import ISLES

ecx, ecy, erx, ery = 600, 345, 540, 305

# Specific initial manual nudges:
nudges = {
    'Alaska North Slope': {'cx': 238, 'cy': 148, 'rx': 18, 'ry': 12},
    'Alaska Peninsula & Aleutians': {'cx': 202, 'cy': 175, 'rx': 14, 'ry': 8},
    'Yukon & Northwest Territories': {'cx': 272, 'cy': 152, 'rx': 17, 'ry': 13},
    'Western Canada Alberta': {'cx': 258, 'cy': 188, 'rx': 16, 'ry': 14},
    'Canadian Shield Ontario': {'cx': 304, 'cy': 176, 'rx': 21, 'ry': 15},
    'Canadian Arctic Islands': {'cx': 312, 'cy': 128, 'rx': 22, 'ry': 12},
    'Baffin Island': {'cx': 365, 'cy': 124, 'rx': 17, 'ry': 13},
    'Greenland Isle': {'cx': 424, 'cy': 112, 'rx': 25, 'ry': 26},
    'US Pacific Northwest': {'cx': 244, 'cy': 222, 'rx': 13, 'ry': 16},
    'California Coast': {'cx': 248, 'cy': 262, 'rx': 11, 'ry': 17},
    'US Rocky Mountains & Plains': {'cx': 286, 'cy': 226, 'rx': 21, 'ry': 17},
    'US Midwest & Great Lakes': {'cx': 330, 'cy': 214, 'rx': 19, 'ry': 15},
    'US East Coast & New England': {'cx': 374, 'cy': 212, 'rx': 17, 'ry': 16},
    'US South & Gulf Coast': {'cx': 330, 'cy': 256, 'rx': 22, 'ry': 14},
    'Florida Peninsula': {'cx': 374, 'cy': 270, 'rx': 10, 'ry': 16},
    'Baja California': {'cx': 246, 'cy': 302, 'rx': 6, 'ry': 16},
    'Northern Mexico': {'cx': 280, 'cy': 292, 'rx': 17, 'ry': 15},
    'Southern Mexico': {'cx': 300, 'cy': 326, 'rx': 15, 'ry': 13},
    'Central America Isthmus': {'cx': 328, 'cy': 350, 'rx': 11, 'ry': 8},
    'Cuba & Greater Antilles': {'cx': 398, 'cy': 304, 'rx': 17, 'ry': 7},
    'Bahamas & Caribbean Chain': {'cx': 424, 'cy': 322, 'rx': 9, 'ry': 6},
    
    # South America
    'Colombia & Northern Andes': {'cx': 354, 'cy': 382, 'rx': 15, 'ry': 13},
    'Venezuela & Orinoco': {'cx': 390, 'cy': 370, 'rx': 17, 'ry': 11},
    'Guyana Coast': {'cx': 424, 'cy': 378, 'rx': 13, 'ry': 9},
    'Peru & Central Andes': {'cx': 344, 'cy': 418, 'rx': 13, 'ry': 20},
    'Amazon Basin Heart': {'cx': 390, 'cy': 412, 'rx': 24, 'ry': 22},
    'Brazil Northeast Bulge': {'cx': 444, 'cy': 416, 'rx': 20, 'ry': 16},
    'Bolivia & Pantanal': {'cx': 386, 'cy': 458, 'rx': 17, 'ry': 16},
    'Brazil Southeast Coast': {'cx': 428, 'cy': 462, 'rx': 19, 'ry': 18},
    'Chile Andes Strip': {'cx': 346, 'cy': 486, 'rx': 9, 'ry': 28},
    'Argentina Pampas Core': {'cx': 384, 'cy': 506, 'rx': 18, 'ry': 20},
    'Patagonia Southern Wedge': {'cx': 372, 'cy': 548, 'rx': 13, 'ry': 16},
    'Tierra del Fuego': {'cx': 368, 'cy': 580, 'rx': 11, 'ry': 7},
    'Falkland Islands': {'cx': 402, 'cy': 565, 'rx': 7, 'ry': 5},
    
    # Europe
    'Iceland': {'cx': 494, 'cy': 128, 'rx': 13, 'ry': 9},
    'Ireland': {'cx': 498, 'cy': 176, 'rx': 9, 'ry': 12},
    'Great Britain': {'cx': 524, 'cy': 166, 'rx': 12, 'ry': 20},
    'Norway Fjord Coast': {'cx': 558, 'cy': 130, 'rx': 11, 'ry': 20},
    'Sweden & Finland': {'cx': 592, 'cy': 134, 'rx': 15, 'ry': 20},
    'Western Europe Mainland Core': {'cx': 544, 'cy': 214, 'rx': 18, 'ry': 14},
    'Central Europe Germany & Alps': {'cx': 584, 'cy': 205, 'rx': 15, 'ry': 13},
    'Iberian Peninsula': {'cx': 504, 'cy': 256, 'rx': 17, 'ry': 15},
    'Italy Boot Peninsula': {'cx': 564, 'cy': 260, 'rx': 8, 'ry': 15},
    'Sicily & Malta': {'cx': 562, 'cy': 288, 'rx': 6, 'ry': 4},
    'Balkans & Greece': {'cx': 602, 'cy': 256, 'rx': 14, 'ry': 13},
    'Poland & Baltic States': {'cx': 618, 'cy': 178, 'rx': 16, 'ry': 13},
    'Eastern Europe Ukraine Plains': {'cx': 642, 'cy': 214, 'rx': 18, 'ry': 15},
    
    # Africa
    'Morocco & Atlas': {'cx': 510, 'cy': 320, 'rx': 14, 'ry': 10},
    'Sahara Core Northwest': {'cx': 548, 'cy': 328, 'rx': 20, 'ry': 14},
    'Egypt & Nile Delta': {'cx': 618, 'cy': 318, 'rx': 17, 'ry': 13},
    'West Africa Senegal Bulge': {'cx': 476, 'cy': 362, 'rx': 15, 'ry': 13},
    'Gulf of Guinea Ivory Coast': {'cx': 514, 'cy': 368, 'rx': 17, 'ry': 11},
    'Nigeria & Sahel': {'cx': 560, 'cy': 366, 'rx': 20, 'ry': 13},
    'Horn of Africa Somalia': {'cx': 655, 'cy': 366, 'rx': 17, 'ry': 13},
    'Congo Basin Rainforest': {'cx': 564, 'cy': 408, 'rx': 22, 'ry': 18},
    'East Africa Rift & Lakes': {'cx': 614, 'cy': 412, 'rx': 17, 'ry': 20},
    'Angola Atlantic Coast': {'cx': 542, 'cy': 452, 'rx': 13, 'ry': 18},
    'Zambia & Zimbabwe Plateau': {'cx': 585, 'cy': 458, 'rx': 17, 'ry': 15},
    'Namibia & Kalahari': {'cx': 558, 'cy': 496, 'rx': 14, 'ry': 16},
    'South Africa Cape': {'cx': 594, 'cy': 512, 'rx': 19, 'ry': 15},
    'Madagascar Island': {'cx': 662, 'cy': 472, 'rx': 11, 'ry': 22},
    
    # Asia
    'European Russia Core': {'cx': 680, 'cy': 156, 'rx': 20, 'ry': 16},
    'Ural Mountains & West Siberia': {'cx': 730, 'cy': 142, 'rx': 25, 'ry': 16},
    'Central Siberia Plateau': {'cx': 798, 'cy': 134, 'rx': 30, 'ry': 16},
    'East Siberia & Yakutia': {'cx': 872, 'cy': 132, 'rx': 28, 'ry': 16},
    'Kamchatka & Bering Shore': {'cx': 938, 'cy': 140, 'rx': 13, 'ry': 16},
    'Levant & Mesopotamia': {'cx': 662, 'cy': 270, 'rx': 15, 'ry': 12},
    'Arabian Peninsula': {'cx': 670, 'cy': 312, 'rx': 20, 'ry': 16},
    'Central Asian Steppes': {'cx': 724, 'cy': 198, 'rx': 20, 'ry': 14},
    'Persian Plateau': {'cx': 712, 'cy': 256, 'rx': 17, 'ry': 14},
    'Pakistan & Indus Basin': {'cx': 745, 'cy': 278, 'rx': 14, 'ry': 15},
    'Northern India & Himalayas': {'cx': 782, 'cy': 264, 'rx': 20, 'ry': 13},
    'Indian Peninsula Triangle': {'cx': 776, 'cy': 318, 'rx': 20, 'ry': 24},
    'Sri Lanka Pearl': {'cx': 792, 'cy': 366, 'rx': 7, 'ry': 9},
    'Mongolia Steppes': {'cx': 792, 'cy': 178, 'rx': 23, 'ry': 13},
    'Tibetan High Plateau': {'cx': 808, 'cy': 224, 'rx': 20, 'ry': 12},
    'North China Core': {'cx': 854, 'cy': 202, 'rx': 22, 'ry': 16},
    'South China & Yangtze': {'cx': 852, 'cy': 246, 'rx': 22, 'ry': 16},
    'Korean Peninsula': {'cx': 902, 'cy': 216, 'rx': 9, 'ry': 15},
    'Japan Hokkaido': {'cx': 948, 'cy': 184, 'rx': 11, 'ry': 11},
    'Japan Honshu Arc': {'cx': 952, 'cy': 226, 'rx': 10, 'ry': 22},
    'Taiwan Island': {'cx': 904, 'cy': 270, 'rx': 7, 'ry': 12},
    'Indochina Peninsula Vietnam/Thailand': {'cx': 854, 'cy': 298, 'rx': 16, 'ry': 16},
    'Malay Peninsula': {'cx': 846, 'cy': 336, 'rx': 8, 'ry': 13},
    'Sumatra Island': {'cx': 836, 'cy': 372, 'rx': 11, 'ry': 18},
    'Java Island': {'cx': 878, 'cy': 392, 'rx': 18, 'ry': 7},
    'Borneo Heart': {'cx': 892, 'cy': 346, 'rx': 16, 'ry': 15},
    'Philippines Archipelago': {'cx': 930, 'cy': 310, 'rx': 10, 'ry': 16},
    
    # Oceania
    'Papua New Guinea': {'cx': 948, 'cy': 386, 'rx': 20, 'ry': 10},
    'Western Australia Outback': {'cx': 884, 'cy': 456, 'rx': 18, 'ry': 20},
    'Northern Territory Australia': {'cx': 924, 'cy': 432, 'rx': 16, 'ry': 14},
    'Queensland & Barrier Reef': {'cx': 966, 'cy': 442, 'rx': 14, 'ry': 18},
    'Central & South Australia': {'cx': 924, 'cy': 478, 'rx': 20, 'ry': 16},
    'New South Wales & Victoria': {'cx': 964, 'cy': 488, 'rx': 16, 'ry': 16},
    'Tasmania': {'cx': 960, 'cy': 530, 'rx': 9, 'ry': 7},
    'New Zealand North Island': {'cx': 1018, 'cy': 482, 'rx': 9, 'ry': 13},
    'New Zealand South Island': {'cx': 1004, 'cy': 516, 'rx': 9, 'ry': 15},
    'South Pacific Coral Isles': {'cx': 1038, 'cy': 428, 'rx': 9, 'ry': 7},
    
    # Antarctica
    'Antarctic Peninsula Graham Land': {'cx': 392, 'cy': 592, 'rx': 9, 'ry': 15},
    'Weddell Sea Ice Shelf': {'cx': 446, 'cy': 602, 'rx': 22, 'ry': 11},
    'Queen Maud Land Shelf': {'cx': 516, 'cy': 602, 'rx': 24, 'ry': 12},
    'Antarctic Polar Dome Hub': {'cx': 595, 'cy': 595, 'rx': 25, 'ry': 13},
    'Wilkes Land Ice Shelf': {'cx': 674, 'cy': 602, 'rx': 24, 'ry': 12},
    'Ross Ice Shelf East': {'cx': 748, 'cy': 602, 'rx': 24, 'ry': 11},
    'Ross Sea Ice Shelf West': {'cx': 815, 'cy': 598, 'rx': 20, 'ry': 11},
}

for isl in ISLES:
    if isl['name'] in nudges:
        isl.update(nudges[isl['name']])

# Run physics relaxation for 50 steps
for step in range(50):
    for i in range(len(ISLES)):
        isl1 = ISLES[i]
        cx1, cy1, rx1, ry1 = isl1['cx'], isl1['cy'], isl1['rx'], isl1['ry']
        
        # Check boundary pull
        dx = (cx1 - ecx) / erx
        dy = (cy1 - ecy) / ery
        dist_norm = math.hypot(dx, dy)
        if dist_norm > 0.90:
            push = (dist_norm - 0.90) * 15
            isl1['cx'] -= (dx / dist_norm) * push
            isl1['cy'] -= (dy / dist_norm) * push
            
        for j in range(i + 1, len(ISLES)):
            isl2 = ISLES[j]
            cx2, cy2, rx2, ry2 = isl2['cx'], isl2['cy'], isl2['rx'], isl2['ry']
            d = math.hypot(cx1 - cx2, cy1 - cy2)
            if d == 0: continue
            ang = math.atan2(cy2 - cy1, cx2 - cy1)
            r1 = math.hypot(rx1 * math.cos(ang), ry1 * math.sin(ang))
            r2 = math.hypot(rx2 * math.cos(ang), ry2 * math.sin(ang))
            target_d = r1 + r2 + 4.5
            if d < target_d:
                overlap = target_d - d
                f_x = math.cos(ang) * overlap * 0.4
                f_y = math.sin(ang) * overlap * 0.4
                isl1['cx'] -= f_x
                isl1['cy'] -= f_y
                isl2['cx'] += f_x
                isl2['cy'] += f_y

# Check stats after relaxation
oob = []
overlaps = []
for i in range(len(ISLES)):
    isl1 = ISLES[i]
    cx1, cy1, rx1, ry1 = isl1['cx'], isl1['cy'], isl1['rx'], isl1['ry']
    dx = (cx1 - ecx) / erx
    dy = (cy1 - ecy) / ery
    dist_norm = math.hypot(dx, dy)
    if dist_norm > 0.93:
        oob.append((isl1['name'], dist_norm))
    for j in range(i + 1, len(ISLES)):
        isl2 = ISLES[j]
        cx2, cy2, rx2, ry2 = isl2['cx'], isl2['cy'], isl2['rx'], isl2['ry']
        d = math.hypot(cx1 - cx2, cy1 - cy2)
        ang = math.atan2(cy2 - cy1, cx2 - cy1)
        r1 = math.hypot(rx1 * math.cos(ang), ry1 * math.sin(ang))
        r2 = math.hypot(rx2 * math.cos(ang), ry2 * math.sin(ang))
        clearance = d - (r1 + r2)
        if clearance < 3.0:
            overlaps.append((isl1['name'], isl2['name'], d, r1 + r2, clearance))

print('Final OOB count:', len(oob))
print('Final Overlaps (<3px):', len(overlaps))

# Round to 1 decimal place or int
for isl in ISLES:
    isl['cx'] = round(isl['cx'], 1)
    isl['cy'] = round(isl['cy'], 1)
    isl['rx'] = round(isl['rx'], 1)
    isl['ry'] = round(isl['ry'], 1)

# Write out python code
with open('scratch/relaxed_isles.py', 'w') as f:
    f.write('RELAXED_ISLES = [\n')
    for isl in ISLES:
        f.write(f'    {repr(isl)},\n')
    f.write(']\n')
print('Wrote scratch/relaxed_isles.py successfully!')
