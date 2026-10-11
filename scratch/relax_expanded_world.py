import math
import copy

ecx, ecy, erx, ery = 600, 345, 540, 305

ISLES_130 = [
    # === NORTH AMERICA (27 Islands) ===
    {'name': 'Alaska North Slope', 'cx': 234.0, 'cy': 156.0, 'rx': 17, 'ry': 12, 'rot': -10, 'green': True},
    {'name': 'Alaska Peninsula and Aleutians', 'cx': 206.0, 'cy': 178.0, 'rx': 14, 'ry': 8, 'rot': -25},
    {'name': 'Yukon and Northwest Territories', 'cx': 272.0, 'cy': 148.0, 'rx': 17, 'ry': 13, 'rot': 10, 'green': True},
    {'name': 'Canadian Arctic Islands', 'cx': 312.0, 'cy': 126.0, 'rx': 21, 'ry': 12, 'rot': 5, 'sand_light': True},
    {'name': 'Baffin Island', 'cx': 358.8, 'cy': 122.9, 'rx': 17, 'ry': 13, 'rot': 25, 'sand_light': True},
    {'name': 'Greenland Isle', 'cx': 424.0, 'cy': 112.0, 'rx': 25, 'ry': 26, 'rot': 20, 'sand_light': True},
    {'name': 'Western Canada Alberta', 'cx': 266.0, 'cy': 186.0, 'rx': 15, 'ry': 14, 'rot': -15, 'green': True},
    {'name': 'Canadian Rockies and British Columbia', 'cx': 236.0, 'cy': 198.0, 'rx': 12, 'ry': 15, 'rot': 15, 'shape': 'arc', 'green': True},
    {'name': 'Canadian Shield Ontario', 'cx': 308.1, 'cy': 174.0, 'rx': 20, 'ry': 15, 'rot': 10, 'green': True},
    {'name': 'Quebec and Labrador', 'cx': 361.2, 'cy': 164.0, 'rx': 21, 'ry': 17, 'rot': 15, 'green': True},
    {'name': 'Newfoundland and Maritimes', 'cx': 404.0, 'cy': 178.0, 'rx': 14, 'ry': 12, 'rot': 25, 'green': True},
    {'name': 'US Pacific Northwest', 'cx': 244.0, 'cy': 230.0, 'rx': 13, 'ry': 15, 'rot': 15, 'shape': 'arc'},
    {'name': 'California Coast', 'cx': 248.0, 'cy': 266.0, 'rx': 11, 'ry': 16, 'rot': 20, 'shape': 'arc'},
    {'name': 'US Rocky Mountains and Plains', 'cx': 286.0, 'cy': 224.0, 'rx': 19, 'ry': 15, 'rot': 0},
    {'name': 'US Midwest and Great Lakes', 'cx': 331.1, 'cy': 213.7, 'rx': 19, 'ry': 15, 'rot': 5, 'green': True, 'hub': 'na'},
    {'name': 'US East Coast and New England', 'cx': 374.0, 'cy': 212.0, 'rx': 17, 'ry': 16, 'rot': -25, 'green': True},
    {'name': 'US South and Gulf Coast', 'cx': 342.0, 'cy': 256.0, 'rx': 21, 'ry': 14, 'rot': -5},
    {'name': 'Texas and Southern Great Plains', 'cx': 298.0, 'cy': 260.0, 'rx': 16, 'ry': 14, 'rot': 0, 'shape': 'taper'},
    {'name': 'Florida Peninsula', 'cx': 382.0, 'cy': 268.0, 'rx': 10, 'ry': 16, 'rot': -30},
    {'name': 'Baja California', 'cx': 246.0, 'cy': 304.0, 'rx': 6, 'ry': 16, 'rot': 25, 'shape': 'arc'},
    {'name': 'Northern Mexico', 'cx': 278.0, 'cy': 296.0, 'rx': 16, 'ry': 14, 'rot': 15},
    {'name': 'Southern Mexico', 'cx': 298.0, 'cy': 328.0, 'rx': 14, 'ry': 13, 'rot': 25, 'shape': 'taper'},
    {'name': 'Yucatan Peninsula', 'cx': 338.0, 'cy': 318.0, 'rx': 13, 'ry': 11, 'rot': 20, 'shape': 'taper', 'green': True},
    {'name': 'Central America Isthmus', 'cx': 328.0, 'cy': 352.0, 'rx': 11, 'ry': 8, 'rot': 35, 'shape': 'arc'},
    {'name': 'Cuba and Greater Antilles', 'cx': 398.0, 'cy': 304.0, 'rx': 17, 'ry': 7, 'rot': -15},
    {'name': 'Bahamas and Caribbean Chain', 'cx': 424.0, 'cy': 322.0, 'rx': 9, 'ry': 6, 'rot': 25},
    {'name': 'Hawaii Pacific Outpost', 'cx': 155.0, 'cy': 255.0, 'rx': 10, 'ry': 7, 'rot': 20},

    # === SOUTH AMERICA (16 Islands) ===
    {'name': 'Colombia and Northern Andes', 'cx': 354.0, 'cy': 382.0, 'rx': 15, 'ry': 13, 'rot': -20},
    {'name': 'Venezuela and Orinoco', 'cx': 390.0, 'cy': 370.0, 'rx': 17, 'ry': 11, 'rot': 10, 'green': True},
    {'name': 'Guyana Coast', 'cx': 424.0, 'cy': 378.0, 'rx': 13, 'ry': 9, 'rot': 20, 'green': True},
    {'name': 'Peru and Central Andes', 'cx': 342.0, 'cy': 420.0, 'rx': 13, 'ry': 19, 'rot': -15},
    {'name': 'Amazon Basin Heart', 'cx': 388.0, 'cy': 412.0, 'rx': 22, 'ry': 20, 'rot': 0, 'green': True},
    {'name': 'Brazil Northeast Bulge', 'cx': 446.0, 'cy': 416.0, 'rx': 20, 'ry': 16, 'rot': 20, 'green': True},
    {'name': 'Central Brazil and Cerrado Plateau', 'cx': 416.0, 'cy': 442.0, 'rx': 16, 'ry': 15, 'rot': 10, 'green': True},
    {'name': 'Bolivia and Pantanal', 'cx': 378.0, 'cy': 456.0, 'rx': 16, 'ry': 15, 'rot': 5},
    {'name': 'Paraguay and Gran Chaco Basin', 'cx': 370.0, 'cy': 484.0, 'rx': 13, 'ry': 14, 'rot': 5},
    {'name': 'Brazil Southeast Coast', 'cx': 434.0, 'cy': 466.0, 'rx': 18, 'ry': 17, 'rot': 25, 'green': True},
    {'name': 'Chile Andes Strip', 'cx': 342.0, 'cy': 488.0, 'rx': 9, 'ry': 25, 'rot': 8, 'shape': 'arc'},
    {'name': 'Argentina Pampas Core', 'cx': 382.0, 'cy': 512.0, 'rx': 17, 'ry': 19, 'rot': 5, 'shape': 'taper'},
    {'name': 'Uruguay and Rio de la Plata', 'cx': 414.0, 'cy': 506.0, 'rx': 12, 'ry': 12, 'rot': 15, 'green': True},
    {'name': 'Patagonia Southern Wedge', 'cx': 372.0, 'cy': 546.0, 'rx': 13, 'ry': 15, 'rot': 8, 'shape': 'taper'},
    {'name': 'Tierra del Fuego', 'cx': 368.0, 'cy': 576.0, 'rx': 11, 'ry': 7, 'rot': 10},
    {'name': 'Falkland Islands', 'cx': 402.0, 'cy': 565.0, 'rx': 7, 'ry': 5, 'rot': 0},

    # === EUROPE (16 Islands) ===
    {'name': 'Iceland', 'cx': 494.0, 'cy': 128.0, 'rx': 13, 'ry': 9, 'rot': -10, 'sand_light': True},
    {'name': 'Ireland', 'cx': 498.0, 'cy': 176.0, 'rx': 9, 'ry': 12, 'rot': 15},
    {'name': 'Great Britain', 'cx': 524.0, 'cy': 166.0, 'rx': 12, 'ry': 20, 'rot': -20, 'shape': 'arc'},
    {'name': 'Norway Fjord Coast', 'cx': 558.0, 'cy': 130.0, 'rx': 11, 'ry': 20, 'rot': 20, 'shape': 'arc', 'green': True},
    {'name': 'Denmark and Jutland Peninsula', 'cx': 564.0, 'cy': 168.0, 'rx': 9, 'ry': 13, 'rot': 10, 'shape': 'arc', 'green': True},
    {'name': 'Sweden and Finland', 'cx': 592.0, 'cy': 134.0, 'rx': 15, 'ry': 20, 'rot': 15, 'green': True},
    {'name': 'Western Europe Mainland Core', 'cx': 544.0, 'cy': 214.0, 'rx': 18, 'ry': 14, 'rot': 5, 'green': True, 'hub': 'eu'},
    {'name': 'France and Biscay Bay', 'cx': 516.0, 'cy': 228.0, 'rx': 13, 'ry': 13, 'rot': -10, 'green': True},
    {'name': 'Central Europe Germany and Alps', 'cx': 582.0, 'cy': 204.0, 'rx': 15, 'ry': 13, 'rot': 0, 'green': True},
    {'name': 'Iberian Peninsula', 'cx': 500.0, 'cy': 260.0, 'rx': 16, 'ry': 15, 'rot': -10},
    {'name': 'Italy Boot Peninsula', 'cx': 564.0, 'cy': 260.0, 'rx': 8, 'ry': 15, 'rot': 35},
    {'name': 'Sicily and Malta', 'cx': 562.0, 'cy': 288.0, 'rx': 6, 'ry': 4, 'rot': -15},
    {'name': 'Balkans and Greece', 'cx': 602.0, 'cy': 256.0, 'rx': 14, 'ry': 13, 'rot': 15},
    {'name': 'Danube Basin and Romania', 'cx': 616.0, 'cy': 224.0, 'rx': 14, 'ry': 12, 'rot': 15, 'green': True},
    {'name': 'Poland and Baltic States', 'cx': 618.0, 'cy': 178.0, 'rx': 16, 'ry': 13, 'rot': 10, 'green': True},
    {'name': 'Eastern Europe Ukraine Plains', 'cx': 646.0, 'cy': 210.0, 'rx': 17, 'ry': 15, 'rot': 5},

    # === AFRICA (18 Islands) ===
    {'name': 'Morocco and Atlas', 'cx': 503.8, 'cy': 319.8, 'rx': 14, 'ry': 10, 'rot': -15},
    {'name': 'Sahara Core Northwest', 'cx': 541.7, 'cy': 326.1, 'rx': 19, 'ry': 14, 'rot': 0},
    {'name': 'Libya and Central Sahara', 'cx': 580.0, 'cy': 326.0, 'rx': 17, 'ry': 13, 'rot': 0},
    {'name': 'Egypt and Nile Delta', 'cx': 622.0, 'cy': 318.0, 'rx': 17, 'ry': 13, 'rot': 15},
    {'name': 'West Africa Senegal Bulge', 'cx': 476.0, 'cy': 362.0, 'rx': 15, 'ry': 13, 'rot': -25},
    {'name': 'Gulf of Guinea Ivory Coast', 'cx': 514.0, 'cy': 368.0, 'rx': 17, 'ry': 11, 'rot': -5, 'green': True},
    {'name': 'Nigeria and Sahel', 'cx': 558.0, 'cy': 364.0, 'rx': 18, 'ry': 13, 'rot': 0},
    {'name': 'Sudan and Nubia Basin', 'cx': 616.0, 'cy': 362.0, 'rx': 16, 'ry': 13, 'rot': 15},
    {'name': 'Horn of Africa Somalia', 'cx': 658.0, 'cy': 366.0, 'rx': 17, 'ry': 13, 'rot': 35, 'shape': 'taper'},
    {'name': 'Central African Savannah', 'cx': 542.0, 'cy': 398.0, 'rx': 13, 'ry': 12, 'rot': 0, 'green': True},
    {'name': 'Congo Basin Rainforest', 'cx': 576.0, 'cy': 408.0, 'rx': 21, 'ry': 17, 'rot': 5, 'green': True},
    {'name': 'East Africa Rift and Lakes', 'cx': 618.0, 'cy': 410.0, 'rx': 17, 'ry': 19, 'rot': 10, 'green': True},
    {'name': 'Angola Atlantic Coast', 'cx': 540.0, 'cy': 450.0, 'rx': 13, 'ry': 18, 'rot': -15, 'shape': 'arc'},
    {'name': 'Zambia and Zimbabwe Plateau', 'cx': 582.0, 'cy': 456.0, 'rx': 17, 'ry': 15, 'rot': 5},
    {'name': 'Mozambique Channel Coast', 'cx': 622.0, 'cy': 460.0, 'rx': 12, 'ry': 18, 'rot': -15, 'shape': 'arc', 'green': True},
    {'name': 'Namibia and Kalahari', 'cx': 556.0, 'cy': 496.0, 'rx': 14, 'ry': 16, 'rot': -5},
    {'name': 'South Africa Cape', 'cx': 594.0, 'cy': 512.0, 'rx': 19, 'ry': 15, 'rot': 5, 'shape': 'taper'},
    {'name': 'Madagascar Island', 'cx': 664.0, 'cy': 472.0, 'rx': 11, 'ry': 22, 'rot': -20, 'green': True},

    # === ASIA AND MIDDLE EAST (32 Islands) ===
    {'name': 'European Russia Core', 'cx': 671.1, 'cy': 156.2, 'rx': 20, 'ry': 16, 'rot': 5, 'green': True},
    {'name': 'Ural Mountains and West Siberia', 'cx': 718.5, 'cy': 142.1, 'rx': 25, 'ry': 16, 'rot': 0},
    {'name': 'Central Siberia Plateau', 'cx': 776.8, 'cy': 130.8, 'rx': 30, 'ry': 16, 'rot': 0},
    {'name': 'East Siberia and Yakutia', 'cx': 868.0, 'cy': 130.0, 'rx': 27, 'ry': 16, 'rot': -5},
    {'name': 'Kamchatka and Bering Shore', 'cx': 933.8, 'cy': 144.5, 'rx': 13, 'ry': 16, 'rot': 25, 'shape': 'arc'},
    {'name': 'Sakhalin Island Arc', 'cx': 946.0, 'cy': 164.0, 'rx': 7, 'ry': 13, 'rot': 10, 'shape': 'arc'},
    {'name': 'Levant and Mesopotamia', 'cx': 662.0, 'cy': 270.0, 'rx': 15, 'ry': 12, 'rot': 15},
    {'name': 'Arabian Peninsula', 'cx': 670.0, 'cy': 312.0, 'rx': 20, 'ry': 16, 'rot': -25},
    {'name': 'Central Asian Steppes', 'cx': 724.0, 'cy': 198.0, 'rx': 20, 'ry': 14, 'rot': 5},
    {'name': 'Persian Plateau', 'cx': 712.0, 'cy': 256.0, 'rx': 17, 'ry': 14, 'rot': 20},
    {'name': 'Pakistan and Indus Basin', 'cx': 745.0, 'cy': 278.0, 'rx': 14, 'ry': 15, 'rot': 20},
    {'name': 'Northern India and Himalayas', 'cx': 782.0, 'cy': 264.0, 'rx': 19, 'ry': 13, 'rot': 15},
    {'name': 'Bengal and Ganges Delta', 'cx': 816.0, 'cy': 288.0, 'rx': 14, 'ry': 14, 'rot': 15, 'green': True},
    {'name': 'Indian Peninsula Triangle', 'cx': 776.0, 'cy': 318.0, 'rx': 20, 'ry': 24, 'rot': 15, 'green': True, 'shape': 'taper'},
    {'name': 'Sri Lanka Pearl', 'cx': 792.0, 'cy': 366.0, 'rx': 7, 'ry': 9, 'rot': 10},
    {'name': 'Mongolia Steppes', 'cx': 807.4, 'cy': 179.3, 'rx': 23, 'ry': 13, 'rot': 0},
    {'name': 'Tibetan High Plateau', 'cx': 816.2, 'cy': 225.8, 'rx': 20, 'ry': 12, 'rot': 10},
    {'name': 'Manchuria and Amur River Basin', 'cx': 886.0, 'cy': 174.0, 'rx': 17, 'ry': 13, 'rot': 10, 'green': True},
    {'name': 'North China Core', 'cx': 855.2, 'cy': 200.7, 'rx': 21, 'ry': 16, 'rot': 5, 'green': True, 'hub': 'asia'},
    {'name': 'East China Coast and Shanghai', 'cx': 892.0, 'cy': 238.0, 'rx': 13, 'ry': 14, 'rot': 15, 'green': True},
    {'name': 'South China and Yangtze', 'cx': 864.0, 'cy': 250.0, 'rx': 20, 'ry': 16, 'rot': 0, 'green': True},
    {'name': 'Korean Peninsula', 'cx': 906.0, 'cy': 214.0, 'rx': 9, 'ry': 15, 'rot': 20},
    {'name': 'Japan Hokkaido', 'cx': 948.0, 'cy': 188.0, 'rx': 11, 'ry': 11, 'rot': -20},
    {'name': 'Japan Honshu Arc', 'cx': 954.0, 'cy': 228.0, 'rx': 10, 'ry': 22, 'rot': 35, 'shape': 'arc'},
    {'name': 'Taiwan Island', 'cx': 908.0, 'cy': 272.0, 'rx': 7, 'ry': 12, 'rot': 25, 'shape': 'arc'},
    {'name': 'Indochina Peninsula Vietnam/Thailand', 'cx': 854.0, 'cy': 298.0, 'rx': 16, 'ry': 16, 'rot': 15},
    {'name': 'Malay Peninsula', 'cx': 846.0, 'cy': 336.0, 'rx': 8, 'ry': 13, 'rot': 15, 'shape': 'arc'},
    {'name': 'Sumatra Island', 'cx': 836.0, 'cy': 372.0, 'rx': 11, 'ry': 18, 'rot': -35, 'green': True, 'shape': 'arc'},
    {'name': 'Java Island', 'cx': 878.0, 'cy': 392.0, 'rx': 18, 'ry': 7, 'rot': 5, 'green': True},
    {'name': 'Borneo Heart', 'cx': 892.0, 'cy': 346.0, 'rx': 16, 'ry': 15, 'rot': 10, 'green': True},
    {'name': 'Sulawesi and Moluccas', 'cx': 924.0, 'cy': 358.0, 'rx': 11, 'ry': 14, 'rot': 25, 'shape': 'arc', 'green': True},
    {'name': 'Philippines Archipelago', 'cx': 932.0, 'cy': 310.0, 'rx': 10, 'ry': 16, 'rot': 20},

    # === OCEANIA (12 Islands) ===
    {'name': 'Papua New Guinea', 'cx': 948.0, 'cy': 386.0, 'rx': 20, 'ry': 10, 'rot': -10},
    {'name': 'Solomon Islands and Coral Archipelago', 'cx': 996.0, 'cy': 396.0, 'rx': 14, 'ry': 8, 'rot': -20},
    {'name': 'Western Australia Outback', 'cx': 884.0, 'cy': 456.0, 'rx': 18, 'ry': 20, 'rot': 10},
    {'name': 'Northern Territory Australia', 'cx': 924.0, 'cy': 432.0, 'rx': 16, 'ry': 14, 'rot': -5},
    {'name': 'Queensland and Barrier Reef', 'cx': 966.0, 'cy': 442.0, 'rx': 14, 'ry': 18, 'rot': -25, 'shape': 'arc', 'green': True},
    {'name': 'Central and South Australia', 'cx': 924.0, 'cy': 478.0, 'rx': 20, 'ry': 16, 'rot': 0, 'green': True, 'hub': 'oc'},
    {'name': 'Great Australian Bight and Adelaide', 'cx': 894.0, 'cy': 496.0, 'rx': 14, 'ry': 12, 'rot': 15, 'green': True},
    {'name': 'New South Wales and Victoria', 'cx': 964.0, 'cy': 488.0, 'rx': 16, 'ry': 16, 'rot': 20, 'green': True},
    {'name': 'Tasmania', 'cx': 959.7, 'cy': 529.7, 'rx': 9, 'ry': 7, 'rot': 0},
    {'name': 'New Zealand North Island', 'cx': 1018.0, 'cy': 482.0, 'rx': 9, 'ry': 13, 'rot': -35, 'shape': 'arc'},
    {'name': 'New Zealand South Island', 'cx': 994.1, 'cy': 508.6, 'rx': 9, 'ry': 15, 'rot': -30, 'shape': 'arc'},
    {'name': 'South Pacific Coral Isles', 'cx': 1038.0, 'cy': 428.0, 'rx': 9, 'ry': 7, 'rot': 20},

    # === ANTARCTICA (9 Islands) ===
    {'name': 'Ellsworth Land Ice Shelf', 'cx': 342.0, 'cy': 602.0, 'rx': 17, 'ry': 9, 'rot': 10, 'sand_light': True},
    {'name': 'Antarctic Peninsula Graham Land', 'cx': 394.0, 'cy': 590.0, 'rx': 9, 'ry': 15, 'rot': -35, 'shape': 'arc', 'sand_light': True},
    {'name': 'Weddell Sea Ice Shelf', 'cx': 446.0, 'cy': 602.0, 'rx': 22, 'ry': 11, 'sand_light': True},
    {'name': 'Queen Maud Land Shelf', 'cx': 516.0, 'cy': 602.0, 'rx': 24, 'ry': 12, 'sand_light': True},
    {'name': 'Antarctic Polar Dome Hub', 'cx': 595.0, 'cy': 595.0, 'rx': 25, 'ry': 13, 'sand_light': True, 'hub': 'an'},
    {'name': 'Wilkes Land Ice Shelf', 'cx': 674.0, 'cy': 602.0, 'rx': 24, 'ry': 12, 'sand_light': True},
    {'name': 'Ross Ice Shelf East', 'cx': 748.0, 'cy': 602.0, 'rx': 24, 'ry': 11, 'sand_light': True},
    {'name': 'Ross Sea Ice Shelf West', 'cx': 812.4, 'cy': 592.6, 'rx': 20, 'ry': 11, 'sand_light': True},
    {'name': 'Marie Byrd Land Shelf', 'cx': 864.0, 'cy': 576.0, 'rx': 18, 'ry': 11, 'rot': -10, 'sand_light': True},
]

pinned = {'US Midwest and Great Lakes', 'Western Europe Mainland Core', 'North China Core', 'Central and South Australia', 'Antarctic Polar Dome Hub'}

for step in range(80):
    for i in range(len(ISLES_130)):
        isl1 = ISLES_130[i]
        if isl1['name'] in pinned:
            continue
        cx1, cy1, rx1, ry1 = isl1['cx'], isl1['cy'], isl1['rx'], isl1['ry']
        
        # Ellipse constraint
        dx = (cx1 - ecx) / erx
        dy = (cy1 - ecy) / ery
        dist_norm = math.hypot(dx, dy)
        if dist_norm > 0.90:
            push = (dist_norm - 0.90) * 15
            isl1['cx'] -= (dx / dist_norm) * push
            isl1['cy'] -= (dy / dist_norm) * push
            
        for j in range(len(ISLES_130)):
            if i == j: continue
            isl2 = ISLES_130[j]
            cx2, cy2, rx2, ry2 = isl2['cx'], isl2['cy'], isl2['rx'], isl2['ry']
            d = math.hypot(cx1 - cx2, cy1 - cy2)
            if d == 0: continue
            ang = math.atan2(cy1 - cy2, cx1 - cx2)
            r1 = math.hypot(rx1 * math.cos(ang), ry1 * math.sin(ang))
            r2 = math.hypot(rx2 * math.cos(ang), ry2 * math.sin(ang))
            target_d = r1 + r2 + 4.8
            if d < target_d:
                overlap = target_d - d
                mult = 0.5 if isl2['name'] not in pinned else 1.0
                isl1['cx'] += math.cos(ang) * overlap * mult
                isl1['cy'] += math.sin(ang) * overlap * mult

oob = []
overlaps = []
for i in range(len(ISLES_130)):
    isl1 = ISLES_130[i]
    cx1, cy1, rx1, ry1 = isl1['cx'], isl1['cy'], isl1['rx'], isl1['ry']
    dx = (cx1 - ecx) / erx
    dy = (cy1 - ecy) / ery
    dist_norm = math.hypot(dx, dy)
    if dist_norm > 0.93:
        oob.append((isl1['name'], dist_norm))
    for j in range(i + 1, len(ISLES_130)):
        isl2 = ISLES_130[j]
        cx2, cy2, rx2, ry2 = isl2['cx'], isl2['cy'], isl2['rx'], isl2['ry']
        d = math.hypot(cx1 - cx2, cy1 - cy2)
        ang = math.atan2(cy2 - cy1, cx2 - cy1)
        r1 = math.hypot(rx1 * math.cos(ang), ry1 * math.sin(ang))
        r2 = math.hypot(rx2 * math.cos(ang), ry2 * math.sin(ang))
        clearance = d - (r1 + r2)
        if clearance < 3.0:
            overlaps.append((isl1['name'], isl2['name'], d, r1 + r2, clearance))

print('Total Islands:', len(ISLES_130))
print('Final OOB count (>0.93):', len(oob))
print('Final Overlaps (<3px clearance):', len(overlaps))
for a, b, d, req, cl in overlaps:
    print(f'  Overlap: {a} <-> {b}: clearance={cl:.2f}px')

for isl in ISLES_130:
    isl['cx'] = round(isl['cx'], 1)
    isl['cy'] = round(isl['cy'], 1)
    isl['rx'] = round(isl['rx'], 1)
    isl['ry'] = round(isl['ry'], 1)

with open('scratch/relaxed_130_isles.py', 'w') as f:
    f.write('WORLD_ISLES_130 = [\n')
    for isl in ISLES_130:
        f.write(f'    {repr(isl)},\n')
    f.write(']\n')
print('Wrote scratch/relaxed_130_isles.py successfully!')
