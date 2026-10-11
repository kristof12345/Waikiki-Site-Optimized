import math

# We want each continent to be tightly grouped, with narrow canals (~4-8px) inside,
# and wide oceans between continents.

ISLES = [
    # =========================================================================
    # 1. NORTH AMERICA (Tightly grouped triangular continent)
    # =========================================================================
    # Alaska & Northwest
    {"name": "Alaska North Slope", "cx": 220, "cy": 138, "rx": 22, "ry": 14, "rot": -10, "green": True},
    {"name": "Alaska Peninsula & Aleutians", "cx": 182, "cy": 168, "rx": 16, "ry": 10, "rot": -25},
    {"name": "Yukon & Northwest Territories", "cx": 258, "cy": 148, "rx": 20, "ry": 16, "rot": 10, "green": True},
    
    # Canada & Arctic Archipelago
    {"name": "Canadian Arctic Islands", "cx": 305, "cy": 125, "rx": 24, "ry": 13, "rot": 5, "sand_light": True},
    {"name": "Baffin Island", "cx": 360, "cy": 122, "rx": 18, "ry": 14, "rot": 25, "sand_light": True},
    {"name": "Greenland Isle", "cx": 420, "cy": 110, "rx": 26, "ry": 28, "rot": 20, "sand_light": True},
    {"name": "Western Canada Alberta", "cx": 255, "cy": 182, "rx": 19, "ry": 16, "rot": -15, "green": True},
    {"name": "Canadian Shield Ontario", "cx": 300, "cy": 175, "rx": 24, "ry": 17, "rot": 10, "green": True},
    {"name": "Quebec & Labrador", "cx": 355, "cy": 165, "rx": 22, "ry": 18, "rot": 15, "green": True},
    
    # Continental United States
    {"name": "US Pacific Northwest", "cx": 240, "cy": 220, "rx": 16, "ry": 18, "rot": 15, "shape": "arc"},
    {"name": "California Coast", "cx": 246, "cy": 260, "rx": 13, "ry": 20, "rot": 20, "shape": "arc"},
    {"name": "US Rocky Mountains & Plains", "cx": 282, "cy": 225, "rx": 24, "ry": 20, "rot": 0},
    {"name": "US Midwest & Great Lakes", "cx": 328, "cy": 215, "rx": 22, "ry": 18, "rot": 5, "green": True, "hub": "na"},
    {"name": "US East Coast & New England", "cx": 372, "cy": 210, "rx": 18, "ry": 18, "rot": -25, "green": True},
    {"name": "US South & Gulf Coast", "cx": 325, "cy": 256, "rx": 24, "ry": 16, "rot": -5},
    {"name": "Florida Peninsula", "cx": 372, "cy": 272, "rx": 11, "ry": 18, "rot": -30},
    
    # Mexico & Central America & Caribbean
    {"name": "Baja California", "cx": 242, "cy": 300, "rx": 7, "ry": 18, "rot": 25, "shape": "arc"},
    {"name": "Northern Mexico", "cx": 278, "cy": 292, "rx": 18, "ry": 16, "rot": 15},
    {"name": "Southern Mexico", "cx": 298, "cy": 326, "rx": 16, "ry": 14, "rot": 25, "shape": "taper"},
    {"name": "Central America Isthmus", "cx": 326, "cy": 350, "rx": 12, "ry": 8, "rot": 35, "shape": "arc"},
    {"name": "Cuba & Greater Antilles", "cx": 395, "cy": 305, "rx": 18, "ry": 8, "rot": -15},
    {"name": "Bahamas & Caribbean Chain", "cx": 422, "cy": 322, "rx": 10, "ry": 6, "rot": 25},
    {"name": "Hawaii Pacific Outpost", "cx": 155, "cy": 255, "rx": 10, "ry": 7, "rot": 20},

    # =========================================================================
    # 2. SOUTH AMERICA (Tapered triangle: Venezuela, Colombia, Amazon, Brazil bulge, Andes, Cape Horn)
    # =========================================================================
    {"name": "Colombia & Northern Andes", "cx": 352, "cy": 382, "rx": 16, "ry": 14, "rot": -20},
    {"name": "Venezuela & Orinoco", "cx": 388, "cy": 372, "rx": 18, "ry": 12, "rot": 10, "green": True},
    {"name": "Guyana Coast", "cx": 422, "cy": 380, "rx": 14, "ry": 10, "rot": 20, "green": True},
    {"name": "Peru & Central Andes", "cx": 344, "cy": 420, "rx": 14, "ry": 22, "rot": -15},
    {"name": "Amazon Basin Heart", "cx": 390, "cy": 415, "rx": 26, "ry": 24, "rot": 0, "green": True},
    {"name": "Brazil Northeast Bulge", "cx": 444, "cy": 418, "rx": 22, "ry": 18, "rot": 20, "green": True},
    {"name": "Bolivia & Pantanal", "cx": 382, "cy": 462, "rx": 18, "ry": 18, "rot": 5},
    {"name": "Brazil Southeast Coast", "cx": 428, "cy": 465, "rx": 20, "ry": 20, "rot": 25, "green": True},
    {"name": "Chile Andes Strip", "cx": 348, "cy": 485, "rx": 10, "ry": 34, "rot": 8, "shape": "arc"},
    {"name": "Argentina Pampas Core", "cx": 382, "cy": 508, "rx": 19, "ry": 22, "rot": 5, "shape": "taper"},
    {"name": "Patagonia Southern Wedge", "cx": 372, "cy": 552, "rx": 14, "ry": 18, "rot": 8, "shape": "taper"},
    {"name": "Tierra del Fuego", "cx": 368, "cy": 586, "rx": 12, "ry": 8, "rot": 10},
    {"name": "Falkland Islands", "cx": 405, "cy": 582, "rx": 8, "ry": 6, "rot": 0},

    # =========================================================================
    # 3. EUROPE (British Isles, Scandinavia, Western Europe, Alps, Iberia, Italy, Greece, Eastern Europe)
    # =========================================================================
    {"name": "Iceland", "cx": 492, "cy": 128, "rx": 14, "ry": 10, "rot": -10, "sand_light": True},
    {"name": "Ireland", "cx": 498, "cy": 178, "rx": 10, "ry": 13, "rot": 15},
    {"name": "Great Britain", "cx": 525, "cy": 168, "rx": 13, "ry": 22, "rot": -20, "shape": "arc"},
    {"name": "Norway Fjord Coast", "cx": 560, "cy": 132, "rx": 13, "ry": 24, "rot": 20, "shape": "arc", "green": True},
    {"name": "Sweden & Finland", "cx": 592, "cy": 135, "rx": 17, "ry": 24, "rot": 15, "green": True},
    {"name": "Western Europe Mainland Core", "cx": 546, "cy": 215, "rx": 20, "ry": 16, "rot": 5, "green": True, "hub": "eu"},
    {"name": "Central Europe Germany & Alps", "cx": 584, "cy": 205, "rx": 17, "ry": 14, "rot": 0, "green": True},
    {"name": "Iberian Peninsula", "cx": 504, "cy": 258, "rx": 18, "ry": 16, "rot": -10},
    {"name": "Italy Boot Peninsula", "cx": 564, "cy": 262, "rx": 9, "ry": 16, "rot": 35},
    {"name": "Sicily & Malta", "cx": 562, "cy": 290, "rx": 7, "ry": 5, "rot": -15},
    {"name": "Balkans & Greece", "cx": 602, "cy": 258, "rx": 15, "ry": 14, "rot": 15},
    {"name": "Poland & Baltic States", "cx": 618, "cy": 180, "rx": 17, "ry": 14, "rot": 10, "green": True},
    {"name": "Eastern Europe Ukraine Plains", "cx": 642, "cy": 215, "rx": 20, "ry": 16, "rot": 5},

    # =========================================================================
    # 4. AFRICA (North Africa, West Africa bulge, Congo, Horn, Angola coast, Cape, Madagascar)
    # =========================================================================
    {"name": "Morocco & Atlas", "cx": 512, "cy": 325, "rx": 16, "ry": 12, "rot": -15},
    {"name": "Sahara Core Northwest", "cx": 548, "cy": 332, "rx": 22, "ry": 16, "rot": 0},
    {"name": "Egypt & Nile Delta", "cx": 618, "cy": 320, "rx": 18, "ry": 14, "rot": 15},
    {"name": "West Africa Senegal Bulge", "cx": 476, "cy": 365, "rx": 16, "ry": 14, "rot": -25},
    {"name": "Gulf of Guinea Ivory Coast", "cx": 515, "cy": 372, "rx": 18, "ry": 12, "rot": -5, "green": True},
    {"name": "Nigeria & Sahel", "cx": 560, "cy": 370, "rx": 22, "ry": 14, "rot": 0},
    {"name": "Horn of Africa Somalia", "cx": 655, "cy": 368, "rx": 18, "ry": 14, "rot": 35, "shape": "taper"},
    {"name": "Congo Basin Rainforest", "cx": 562, "cy": 412, "rx": 24, "ry": 20, "rot": 5, "green": True},
    {"name": "East Africa Rift & Lakes", "cx": 614, "cy": 415, "rx": 18, "ry": 22, "rot": 10, "green": True},
    {"name": "Angola Atlantic Coast", "cx": 542, "cy": 455, "rx": 14, "ry": 20, "rot": -15, "shape": "arc"},
    {"name": "Zambia & Zimbabwe Plateau", "cx": 585, "cy": 462, "rx": 18, "ry": 16, "rot": 5},
    {"name": "Namibia & Kalahari", "cx": 558, "cy": 500, "rx": 15, "ry": 18, "rot": -5},
    {"name": "South Africa Cape", "cx": 594, "cy": 515, "rx": 20, "ry": 16, "rot": 5, "shape": "taper"},
    {"name": "Madagascar Island", "cx": 662, "cy": 475, "rx": 12, "ry": 24, "rot": -20, "green": True},

    # =========================================================================
    # 5. ASIA & MIDDLE EAST (Eurasian giant: Russia, Central Asia, Arabia, India, China, Korea, Japan, Indochina, Indonesia)
    # =========================================================================
    # Northern Eurasia / Russia
    {"name": "European Russia Core", "cx": 680, "cy": 160, "rx": 22, "ry": 18, "rot": 5, "green": True},
    {"name": "Ural Mountains & West Siberia", "cx": 732, "cy": 145, "rx": 28, "ry": 18, "rot": 0},
    {"name": "Central Siberia Plateau", "cx": 800, "cy": 138, "rx": 34, "ry": 18, "rot": 0},
    {"name": "East Siberia & Yakutia", "cx": 875, "cy": 135, "rx": 30, "ry": 18, "rot": -5},
    {"name": "Kamchatka & Bering Shore", "cx": 940, "cy": 142, "rx": 14, "ry": 18, "rot": 25, "shape": "arc"},

    # Middle East & Central Asia
    {"name": "Levant & Mesopotamia", "cx": 662, "cy": 272, "rx": 16, "ry": 13, "rot": 15},
    {"name": "Arabian Peninsula", "cx": 670, "cy": 315, "rx": 22, "ry": 18, "rot": -25},
    {"name": "Central Asian Steppes", "cx": 724, "cy": 202, "rx": 22, "ry": 15, "rot": 5},
    {"name": "Persian Plateau", "cx": 712, "cy": 260, "rx": 18, "ry": 15, "rot": 20},
    
    # South Asia (India triangle)
    {"name": "Pakistan & Indus Basin", "cx": 745, "cy": 282, "rx": 15, "ry": 16, "rot": 20},
    {"name": "Northern India & Himalayas", "cx": 782, "cy": 268, "rx": 22, "ry": 14, "rot": 15},
    {"name": "Indian Peninsula Triangle", "cx": 776, "cy": 322, "rx": 22, "ry": 26, "rot": 15, "green": True, "shape": "taper"},
    {"name": "Sri Lanka Pearl", "cx": 792, "cy": 372, "rx": 8, "ry": 10, "rot": 10},

    # East Asia (Mongolia, China, Korea, Japan)
    {"name": "Mongolia Steppes", "cx": 795, "cy": 182, "rx": 26, "ry": 14, "rot": 0},
    {"name": "Tibetan High Plateau", "cx": 810, "cy": 228, "rx": 22, "ry": 13, "rot": 10},
    {"name": "North China Core", "cx": 855, "cy": 205, "rx": 24, "ry": 18, "rot": 5, "green": True, "hub": "asia"},
    {"name": "South China & Yangtze", "cx": 852, "cy": 250, "rx": 24, "ry": 18, "rot": 0, "green": True},
    {"name": "Korean Peninsula", "cx": 904, "cy": 218, "rx": 10, "ry": 16, "rot": 20},
    {"name": "Japan Hokkaido", "cx": 952, "cy": 185, "rx": 12, "ry": 12, "rot": -20},
    {"name": "Japan Honshu Arc", "cx": 955, "cy": 228, "rx": 11, "ry": 24, "rot": 35, "shape": "arc"},
    {"name": "Taiwan Island", "cx": 906, "cy": 272, "rx": 8, "ry": 13, "rot": 25, "shape": "arc"},

    # Southeast Asia & Island Arcs
    {"name": "Indochina Peninsula Vietnam/Thailand", "cx": 854, "cy": 302, "rx": 17, "ry": 18, "rot": 15},
    {"name": "Malay Peninsula", "cx": 846, "cy": 340, "rx": 9, "ry": 16, "rot": 15, "shape": "arc"},
    {"name": "Sumatra Island", "cx": 836, "cy": 375, "rx": 12, "ry": 22, "rot": -35, "green": True, "shape": "arc"},
    {"name": "Java Island", "cx": 878, "cy": 395, "rx": 20, "ry": 8, "rot": 5, "green": True},
    {"name": "Borneo Heart", "cx": 892, "cy": 348, "rx": 18, "ry": 16, "rot": 10, "green": True},
    {"name": "Philippines Archipelago", "cx": 932, "cy": 312, "rx": 11, "ry": 18, "rot": 20},

    # =========================================================================
    # 6. OCEANIA (Australia, Papua, New Zealand, Pacific)
    # =========================================================================
    {"name": "Papua New Guinea", "cx": 952, "cy": 388, "rx": 22, "ry": 11, "rot": -10},
    {"name": "Western Australia Outback", "cx": 884, "cy": 458, "rx": 20, "ry": 22, "rot": 10},
    {"name": "Northern Territory Australia", "cx": 926, "cy": 435, "rx": 18, "ry": 15, "rot": -5},
    {"name": "Queensland & Barrier Reef", "cx": 968, "cy": 445, "rx": 15, "ry": 20, "rot": -25, "shape": "arc", "green": True},
    {"name": "Central & South Australia", "cx": 925, "cy": 482, "rx": 22, "ry": 18, "rot": 0, "green": True, "hub": "oc"},
    {"name": "New South Wales & Victoria", "cx": 966, "cy": 492, "rx": 18, "ry": 18, "rot": 20, "green": True},
    {"name": "Tasmania", "cx": 962, "cy": 535, "rx": 10, "ry": 8, "rot": 0},
    {"name": "New Zealand North Island", "cx": 1025, "cy": 488, "rx": 10, "ry": 14, "rot": -35, "shape": "arc"},
    {"name": "New Zealand South Island", "cx": 1012, "cy": 526, "rx": 10, "ry": 17, "rot": -30, "shape": "arc"},
    {"name": "South Pacific Coral Isles", "cx": 1045, "cy": 430, "rx": 10, "ry": 7, "rot": 20},

    # =========================================================================
    # 7. ANTARCTICA (Great southern polar ice shelf with Antarctic Peninsula)
    # =========================================================================
    {"name": "Antarctic Peninsula Graham Land", "cx": 395, "cy": 585, "rx": 10, "ry": 18, "rot": -35, "shape": "arc", "sand_light": True},
    {"name": "Weddell Sea Ice Shelf", "cx": 450, "cy": 602, "rx": 24, "ry": 11, "sand_light": True},
    {"name": "Queen Maud Land Shelf", "cx": 520, "cy": 602, "rx": 26, "ry": 12, "sand_light": True},
    {"name": "Antarctic Polar Dome Hub", "cx": 595, "cy": 595, "rx": 26, "ry": 13, "sand_light": True, "hub": "an"},
    {"name": "Wilkes Land Ice Shelf", "cx": 670, "cy": 602, "rx": 26, "ry": 12, "sand_light": True},
    {"name": "Ross Ice Shelf East", "cx": 745, "cy": 602, "rx": 26, "ry": 11, "sand_light": True},
    {"name": "Ross Sea Ice Shelf West", "cx": 815, "cy": 598, "rx": 22, "ry": 11, "sand_light": True},
]

print(f"Total isles: {len(ISLES)}")
