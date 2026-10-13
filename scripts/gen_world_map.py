#!/usr/bin/env python3
"""Generator for World Islands infrastructure SVG map."""

import math
import sys
from pathlib import Path

try:
    from map_common import n, pt, poly_path, smooth_island, hotspot, map_header, L, update_island_map
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from map_common import n, pt, poly_path, smooth_island, hotspot, map_header, L, update_island_map


# ==========================================================================
# WORLD ISLANDS (RECOGNIZABLE CONTINENTS: MAJOR CORES + SATELLITE ISLES)
# ==========================================================================
WORLD_ISLES = [
    # === NORTH AMERICA (27 Islands: Arctic, Canada, US, Florida, Baja, Mexico, Central America, Caribbean) ===
    {'name': 'Alaska North Slope', 'cx': 238.5, 'cy': 161.1, 'rx': 17, 'ry': 12, 'rot': -10, 'green': True},
    {'name': 'Alaska Peninsula and Aleutians', 'cx': 209.9, 'cy': 180.9, 'rx': 14, 'ry': 8, 'rot': -25},
    {'name': 'Yukon and Northwest Territories', 'cx': 273.7, 'cy': 147.5, 'rx': 17, 'ry': 13, 'rot': 10, 'green': True},
    {'name': 'Canadian Arctic Islands', 'cx': 312.0, 'cy': 126.0, 'rx': 21, 'ry': 12, 'rot': 5, 'sand_light': True},
    {'name': 'Baffin Island', 'cx': 358.8, 'cy': 122.9, 'rx': 17, 'ry': 13, 'rot': 25, 'sand_light': True},
    {'name': 'Greenland Isle', 'cx': 424.0, 'cy': 112.0, 'rx': 25, 'ry': 26, 'rot': 20, 'sand_light': True},
    {'name': 'Western Canada Alberta', 'cx': 266.0, 'cy': 186.0, 'rx': 15, 'ry': 14, 'rot': -15, 'green': True},
    {'name': 'Canadian Rockies and British Columbia', 'cx': 235.7, 'cy': 197.0, 'rx': 12, 'ry': 15, 'rot': 15, 'shape': 'arc', 'green': True},
    {'name': 'Canadian Shield Ontario', 'cx': 308.1, 'cy': 174.0, 'rx': 20, 'ry': 15, 'rot': 10, 'green': True},
    {'name': 'Quebec and Labrador', 'cx': 361.2, 'cy': 164.0, 'rx': 21, 'ry': 17, 'rot': 15, 'green': True},
    {'name': 'Newfoundland and Maritimes', 'cx': 404.0, 'cy': 178.0, 'rx': 14, 'ry': 12, 'rot': 25, 'green': True},
    {'name': 'US Pacific Northwest', 'cx': 244.1, 'cy': 230.5, 'rx': 13, 'ry': 15, 'rot': 15, 'shape': 'arc'},
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

    # === SOUTH AMERICA (16 Islands: Colombia, Venezuela, Guyana, Amazon, Brazil, Andes, Argentina, Patagonia) ===
    {'name': 'Colombia and Northern Andes', 'cx': 354.0, 'cy': 382.0, 'rx': 15, 'ry': 13, 'rot': -20},
    {'name': 'Venezuela and Orinoco', 'cx': 390.0, 'cy': 370.0, 'rx': 17, 'ry': 11, 'rot': 10, 'green': True},
    {'name': 'Guyana Coast', 'cx': 424.0, 'cy': 378.0, 'rx': 13, 'ry': 9, 'rot': 20, 'green': True},
    {'name': 'Peru and Central Andes', 'cx': 342.0, 'cy': 420.0, 'rx': 13, 'ry': 19, 'rot': -15},
    {'name': 'Amazon Basin Heart', 'cx': 385.5, 'cy': 409.0, 'rx': 22, 'ry': 20, 'rot': 0, 'green': True},
    {'name': 'Brazil Northeast Bulge', 'cx': 446.8, 'cy': 415.4, 'rx': 20, 'ry': 16, 'rot': 20, 'green': True},
    {'name': 'Central Brazil and Cerrado Plateau', 'cx': 415.1, 'cy': 438.5, 'rx': 16, 'ry': 15, 'rot': 10, 'green': True},
    {'name': 'Bolivia and Pantanal', 'cx': 379.8, 'cy': 448.5, 'rx': 16, 'ry': 15, 'rot': 5},
    {'name': 'Paraguay and Gran Chaco Basin', 'cx': 366.3, 'cy': 479.4, 'rx': 13, 'ry': 14, 'rot': 5},
    {'name': 'Brazil Southeast Coast', 'cx': 436.4, 'cy': 469.3, 'rx': 18, 'ry': 17, 'rot': 25, 'green': True},
    {'name': 'Chile Andes Strip', 'cx': 338.2, 'cy': 489.1, 'rx': 9, 'ry': 25, 'rot': 8, 'shape': 'arc'},
    {'name': 'Argentina Pampas Core', 'cx': 384.6, 'cy': 511.7, 'rx': 17, 'ry': 19, 'rot': 5, 'shape': 'taper'},
    {'name': 'Uruguay and Rio de la Plata', 'cx': 417.8, 'cy': 505.1, 'rx': 12, 'ry': 12, 'rot': 15, 'green': True},
    {'name': 'Patagonia Southern Wedge', 'cx': 369.4, 'cy': 546.7, 'rx': 13, 'ry': 15, 'rot': 8, 'shape': 'taper'},
    {'name': 'Tierra del Fuego', 'cx': 379.3, 'cy': 572.1, 'rx': 11, 'ry': 7, 'rot': 10},
    {'name': 'Falkland Islands', 'cx': 402.0, 'cy': 565.0, 'rx': 7, 'ry': 5, 'rot': 0},

    # === ATLANTIC AND EUROPE (16 Islands: Iceland, Ireland, Great Britain, Scandinavia, Western Europe, Central Europe, Iberia, Italy, Greece, East Europe) ===
    {'name': 'Iceland', 'cx': 494.0, 'cy': 128.0, 'rx': 13, 'ry': 9, 'rot': -10, 'sand_light': True},
    {'name': 'Ireland', 'cx': 498.0, 'cy': 176.0, 'rx': 9, 'ry': 12, 'rot': 15},
    {'name': 'Great Britain', 'cx': 524.0, 'cy': 166.0, 'rx': 12, 'ry': 20, 'rot': -20, 'shape': 'arc'},
    {'name': 'Norway Fjord Coast', 'cx': 558.0, 'cy': 130.0, 'rx': 11, 'ry': 20, 'rot': 20, 'shape': 'arc', 'green': True},
    {'name': 'Denmark and Jutland Peninsula', 'cx': 564.0, 'cy': 168.0, 'rx': 9, 'ry': 13, 'rot': 10, 'shape': 'arc', 'green': True},
    {'name': 'Sweden and Finland', 'cx': 592.0, 'cy': 134.0, 'rx': 15, 'ry': 20, 'rot': 15, 'green': True},
    {'name': 'Western Europe Mainland Core', 'cx': 544.0, 'cy': 214.0, 'rx': 18, 'ry': 14, 'rot': 5, 'green': True, 'hub': 'eu'},
    {'name': 'France and Biscay Bay', 'cx': 512.6, 'cy': 229.7, 'rx': 13, 'ry': 13, 'rot': -10, 'green': True},
    {'name': 'Central Europe Germany and Alps', 'cx': 582.0, 'cy': 204.0, 'rx': 15, 'ry': 13, 'rot': 0, 'green': True},
    {'name': 'Iberian Peninsula', 'cx': 500.0, 'cy': 260.1, 'rx': 16, 'ry': 15, 'rot': -10},
    {'name': 'Italy Boot Peninsula', 'cx': 564.0, 'cy': 260.0, 'rx': 8, 'ry': 15, 'rot': 35},
    {'name': 'Sicily and Malta', 'cx': 562.0, 'cy': 288.0, 'rx': 6, 'ry': 4, 'rot': -15},
    {'name': 'Balkans and Greece', 'cx': 602.0, 'cy': 256.0, 'rx': 14, 'ry': 13, 'rot': 15},
    {'name': 'Danube Basin and Romania', 'cx': 614.8, 'cy': 224.6, 'rx': 14, 'ry': 12, 'rot': 15, 'green': True},
    {'name': 'Poland and Baltic States', 'cx': 618.0, 'cy': 178.0, 'rx': 16, 'ry': 13, 'rot': 10, 'green': True},
    {'name': 'Eastern Europe Ukraine Plains', 'cx': 646.6, 'cy': 209.7, 'rx': 17, 'ry': 15, 'rot': 5},

    # === AFRICA (18 Islands: Morocco, Sahara, Libya, Egypt, Senegal, Guinea Coast, Nigeria, Sudan, Horn, Congo, Rift, Angola, Cape, Madagascar) ===
    {'name': 'Morocco and Atlas', 'cx': 503.2, 'cy': 319.7, 'rx': 14, 'ry': 10, 'rot': -15},
    {'name': 'Sahara Core Northwest', 'cx': 540.2, 'cy': 326.2, 'rx': 19, 'ry': 14, 'rot': 0},
    {'name': 'Libya and Central Sahara', 'cx': 581.0, 'cy': 326.0, 'rx': 17, 'ry': 13, 'rot': 0},
    {'name': 'Egypt and Nile Delta', 'cx': 622.0, 'cy': 318.0, 'rx': 17, 'ry': 13, 'rot': 15},
    {'name': 'West Africa Senegal Bulge', 'cx': 476.0, 'cy': 362.0, 'rx': 15, 'ry': 13, 'rot': -25},
    {'name': 'Gulf of Guinea Ivory Coast', 'cx': 514.0, 'cy': 368.0, 'rx': 17, 'ry': 11, 'rot': -5, 'green': True},
    {'name': 'Nigeria and Sahel', 'cx': 558.0, 'cy': 364.0, 'rx': 18, 'ry': 13, 'rot': 0},
    {'name': 'Sudan and Nubia Basin', 'cx': 616.0, 'cy': 362.0, 'rx': 16, 'ry': 13, 'rot': 15},
    {'name': 'Horn of Africa Somalia', 'cx': 658.0, 'cy': 366.0, 'rx': 17, 'ry': 13, 'rot': 35, 'shape': 'taper'},
    {'name': 'Central African Savannah', 'cx': 539.5, 'cy': 397.3, 'rx': 13, 'ry': 12, 'rot': 0, 'green': True},
    {'name': 'Congo Basin Rainforest', 'cx': 576.3, 'cy': 408.3, 'rx': 21, 'ry': 17, 'rot': 5, 'green': True},
    {'name': 'East Africa Rift and Lakes', 'cx': 619.1, 'cy': 410.0, 'rx': 17, 'ry': 19, 'rot': 10, 'green': True},
    {'name': 'Angola Atlantic Coast', 'cx': 540.0, 'cy': 450.0, 'rx': 13, 'ry': 18, 'rot': -15, 'shape': 'arc'},
    {'name': 'Zambia and Zimbabwe Plateau', 'cx': 582.0, 'cy': 456.0, 'rx': 17, 'ry': 15, 'rot': 5},
    {'name': 'Mozambique Channel Coast', 'cx': 622.0, 'cy': 460.0, 'rx': 12, 'ry': 18, 'rot': -15, 'shape': 'arc', 'green': True},
    {'name': 'Namibia and Kalahari', 'cx': 556.0, 'cy': 496.0, 'rx': 14, 'ry': 16, 'rot': -5},
    {'name': 'South Africa Cape', 'cx': 594.0, 'cy': 512.0, 'rx': 19, 'ry': 15, 'rot': 5, 'shape': 'taper'},
    {'name': 'Madagascar Island', 'cx': 664.0, 'cy': 472.0, 'rx': 11, 'ry': 22, 'rot': -20, 'green': True},

    # === ASIA AND MIDDLE EAST (35 Islands: Russia, Urals, Siberia, Baikal, Kamchatka, Levant, Arabia, Central Asia, Kazakhstan, Pamir, Iran, India, Tibet, China, Korea, Japan, Indochina, Indonesia) ===
    {'name': 'European Russia Core', 'cx': 671.1, 'cy': 156.2, 'rx': 20, 'ry': 16, 'rot': 5, 'green': True},
    {'name': 'Ural Mountains and West Siberia', 'cx': 718.5, 'cy': 142.1, 'rx': 25, 'ry': 16, 'rot': 0},
    {'name': 'Central Siberia Plateau', 'cx': 776.8, 'cy': 130.8, 'rx': 30, 'ry': 16, 'rot': 0},
    {'name': 'Lake Baikal and Sayan Range', 'cx': 825.0, 'cy': 142.0, 'rx': 16, 'ry': 12, 'rot': -5, 'green': True},
    {'name': 'East Siberia and Yakutia', 'cx': 868.0, 'cy': 130.0, 'rx': 27, 'ry': 16, 'rot': -5},
    {'name': 'Kamchatka and Bering Shore', 'cx': 926.4, 'cy': 141.4, 'rx': 13, 'ry': 16, 'rot': 25, 'shape': 'arc'},
    {'name': 'Sakhalin Island Arc', 'cx': 947.9, 'cy': 162.8, 'rx': 7, 'ry': 13, 'rot': 10, 'shape': 'arc'},
    {'name': 'Levant and Mesopotamia', 'cx': 662.0, 'cy': 270.0, 'rx': 15, 'ry': 12, 'rot': 15},
    {'name': 'Arabian Peninsula', 'cx': 670.0, 'cy': 312.0, 'rx': 20, 'ry': 16, 'rot': -25},
    {'name': 'Central Asian Steppes', 'cx': 724.0, 'cy': 198.0, 'rx': 20, 'ry': 14, 'rot': 5},
    {'name': 'Kazakhstan and Altai Steppes', 'cx': 766.0, 'cy': 185.0, 'rx': 18, 'ry': 13, 'rot': 10},
    {'name': 'Pamir and Hindu Kush Plateau', 'cx': 752.0, 'cy': 234.0, 'rx': 16, 'ry': 13, 'rot': 25},
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
    {'name': 'East China Coast and Shanghai', 'cx': 895.3, 'cy': 240.0, 'rx': 13, 'ry': 14, 'rot': 15, 'green': True},
    {'name': 'South China and Yangtze', 'cx': 859.6, 'cy': 251.6, 'rx': 20, 'ry': 16, 'rot': 0, 'green': True},
    {'name': 'Korean Peninsula', 'cx': 908.0, 'cy': 209.6, 'rx': 9, 'ry': 15, 'rot': 20},
    {'name': 'Japan Hokkaido', 'cx': 948.1, 'cy': 191.6, 'rx': 11, 'ry': 11, 'rot': -20},
    {'name': 'Japan Honshu Arc', 'cx': 954.1, 'cy': 228.7, 'rx': 10, 'ry': 22, 'rot': 35, 'shape': 'arc'},
    {'name': 'Taiwan Island', 'cx': 908.0, 'cy': 272.0, 'rx': 7, 'ry': 12, 'rot': 25, 'shape': 'arc'},
    {'name': 'Indochina Peninsula Vietnam/Thailand', 'cx': 854.0, 'cy': 298.0, 'rx': 16, 'ry': 16, 'rot': 15},
    {'name': 'Malay Peninsula', 'cx': 846.0, 'cy': 336.0, 'rx': 8, 'ry': 13, 'rot': 15, 'shape': 'arc'},
    {'name': 'Sumatra Island', 'cx': 836.0, 'cy': 372.0, 'rx': 11, 'ry': 18, 'rot': -35, 'green': True, 'shape': 'arc'},
    {'name': 'Java Island', 'cx': 878.0, 'cy': 392.0, 'rx': 18, 'ry': 7, 'rot': 5, 'green': True},
    {'name': 'Borneo Heart', 'cx': 892.0, 'cy': 346.0, 'rx': 16, 'ry': 15, 'rot': 10, 'green': True},
    {'name': 'Sulawesi and Moluccas', 'cx': 924.0, 'cy': 358.0, 'rx': 11, 'ry': 14, 'rot': 25, 'shape': 'arc', 'green': True},
    {'name': 'Philippines Archipelago', 'cx': 932.0, 'cy': 310.0, 'rx': 10, 'ry': 16, 'rot': 20},

    # === OCEANIA (12 Islands: Papua New Guinea, Australia Outback, Queensland Reef, Central Australia, New South Wales, Tasmania, New Zealand) ===
    {'name': 'Papua New Guinea', 'cx': 948.0, 'cy': 386.0, 'rx': 20, 'ry': 10, 'rot': -10},
    {'name': 'Solomon Islands and Coral Archipelago', 'cx': 996.0, 'cy': 396.0, 'rx': 14, 'ry': 8, 'rot': -20},
    {'name': 'Western Australia Outback', 'cx': 884.0, 'cy': 456.0, 'rx': 18, 'ry': 20, 'rot': 10},
    {'name': 'Northern Territory Australia', 'cx': 924.0, 'cy': 432.0, 'rx': 16, 'ry': 14, 'rot': -5},
    {'name': 'Queensland and Barrier Reef', 'cx': 966.0, 'cy': 442.0, 'rx': 14, 'ry': 18, 'rot': -25, 'shape': 'arc', 'green': True},
    {'name': 'Central and South Australia', 'cx': 924.0, 'cy': 478.0, 'rx': 20, 'ry': 16, 'rot': 0, 'green': True, 'hub': 'oc'},
    {'name': 'Great Australian Bight and Adelaide', 'cx': 892.0, 'cy': 497.2, 'rx': 14, 'ry': 12, 'rot': 15, 'green': True},
    {'name': 'New South Wales and Victoria', 'cx': 964.0, 'cy': 488.0, 'rx': 16, 'ry': 16, 'rot': 20, 'green': True},
    {'name': 'Tasmania', 'cx': 959.6, 'cy': 529.6, 'rx': 9, 'ry': 7, 'rot': 0},
    {'name': 'New Zealand North Island', 'cx': 1018.0, 'cy': 482.0, 'rx': 9, 'ry': 13, 'rot': -35, 'shape': 'arc'},
    {'name': 'New Zealand South Island', 'cx': 992.2, 'cy': 507.2, 'rx': 9, 'ry': 15, 'rot': -30, 'shape': 'arc'},
    {'name': 'South Pacific Coral Isles', 'cx': 1038.0, 'cy': 428.0, 'rx': 9, 'ry': 7, 'rot': 20},

    # === ANTARCTICA (9 Islands: Antarctic Peninsula, Weddell Sea, Polar Dome Hub, Wilkes, Ross Shelves, Marie Byrd Land) ===
    {'name': 'Ellsworth Land Ice Shelf', 'cx': 348.9, 'cy': 581.7, 'rx': 17, 'ry': 9, 'rot': 10, 'sand_light': True},
    {'name': 'Antarctic Peninsula Graham Land', 'cx': 396.5, 'cy': 592.3, 'rx': 9, 'ry': 15, 'rot': -35, 'shape': 'arc', 'sand_light': True},
    {'name': 'Weddell Sea Ice Shelf', 'cx': 446.0, 'cy': 602.0, 'rx': 22, 'ry': 11, 'sand_light': True},
    {'name': 'Queen Maud Land Shelf', 'cx': 516.0, 'cy': 602.0, 'rx': 24, 'ry': 12, 'sand_light': True},
    {'name': 'Antarctic Polar Dome Hub', 'cx': 595.0, 'cy': 595.0, 'rx': 25, 'ry': 13, 'sand_light': True, 'hub': 'an'},
    {'name': 'Wilkes Land Ice Shelf', 'cx': 674.0, 'cy': 602.0, 'rx': 24, 'ry': 12, 'sand_light': True},
    {'name': 'Ross Ice Shelf East', 'cx': 748.0, 'cy': 602.0, 'rx': 24, 'ry': 11, 'sand_light': True},
    {'name': 'Ross Sea Ice Shelf West', 'cx': 812.1, 'cy': 592.0, 'rx': 20, 'ry': 11, 'sand_light': True},
    {'name': 'Marie Byrd Land Shelf', 'cx': 863.7, 'cy': 575.6, 'rx': 18, 'ry': 11, 'rot': -10, 'sand_light': True},
]

    # Inter-island footbridges
    bridges = [
        # --- North America ---
        ((286.0, 224.0), (331.1, 213.7)),  # US Rocky Mountains and Plains to US Midwest and Great Lakes
        ((308.1, 174.0), (331.1, 213.7)),  # Canadian Shield Ontario to US Midwest and Great Lakes
        ((331.1, 213.7), (361.2, 164.0)),  # US Midwest and Great Lakes to Quebec and Labrador
        ((361.2, 164.0), (358.8, 122.9)),  # Quebec and Labrador to Baffin Island
        ((331.1, 213.7), (374.0, 212.0)),  # US Midwest and Great Lakes to US East Coast and New England
        ((331.1, 213.7), (342.0, 256.0)),  # US Midwest and Great Lakes to US South and Gulf Coast
        ((342.0, 256.0), (382.0, 268.0)),  # US South and Gulf Coast to Florida Peninsula
        ((286.0, 224.0), (298.0, 260.0)),  # US Rocky Mountains and Plains to Texas and Southern Great Plains
        ((298.0, 260.0), (278.0, 296.0)),  # Texas and Southern Great Plains to Northern Mexico
        ((278.0, 296.0), (298.0, 328.0)),  # Northern Mexico to Southern Mexico
        ((298.0, 328.0), (338.0, 318.0)),  # Southern Mexico to Yucatan Peninsula
        ((298.0, 328.0), (328.0, 352.0)),  # Southern Mexico to Central America Isthmus
        ((361.2, 164.0), (404.0, 178.0)),  # Quebec and Labrador to Newfoundland and Maritimes

        # --- South America ---
        ((354.0, 382.0), (390.0, 370.0)),  # Colombia and Northern Andes to Venezuela and Orinoco
        ((354.0, 382.0), (385.5, 409.0)),  # Colombia and Northern Andes to Amazon Basin Heart
        ((342.0, 420.0), (385.5, 409.0)),  # Peru and Central Andes to Amazon Basin Heart
        ((390.0, 370.0), (424.0, 378.0)),  # Venezuela and Orinoco to Guyana Coast
        ((385.5, 409.0), (379.8, 448.5)),  # Amazon Basin Heart to Bolivia and Pantanal
        ((385.5, 409.0), (446.8, 415.4)),  # Amazon Basin Heart to Brazil Northeast Bulge
        ((385.5, 409.0), (415.1, 438.5)),  # Amazon Basin Heart to Central Brazil and Cerrado Plateau
        ((415.1, 438.5), (436.4, 469.3)),  # Central Brazil and Cerrado Plateau to Brazil Southeast Coast
        ((379.8, 448.5), (366.3, 479.4)),  # Bolivia and Pantanal to Paraguay and Gran Chaco Basin
        ((338.2, 489.1), (366.3, 479.4)),  # Chile Andes Strip to Paraguay and Gran Chaco Basin
        ((366.3, 479.4), (384.6, 511.7)),  # Paraguay and Gran Chaco Basin to Argentina Pampas Core
        ((384.6, 511.7), (417.8, 505.1)),  # Argentina Pampas Core to Uruguay and Rio de la Plata
        ((384.6, 511.7), (369.4, 546.7)),  # Argentina Pampas Core to Patagonia Southern Wedge
        ((369.4, 546.7), (379.3, 572.1)),  # Patagonia Southern Wedge to Tierra del Fuego
        ((379.3, 572.1), (402.0, 565.0)),  # Tierra del Fuego to Falkland Islands

        # --- Europe ---
        ((498.0, 176.0), (524.0, 166.0)),  # Ireland to Great Britain
        ((524.0, 166.0), (544.0, 214.0)),  # Great Britain to Western Europe Mainland Core
        ((544.0, 214.0), (512.6, 229.7)),  # Western Europe Mainland Core to France and Biscay Bay
        ((512.6, 229.7), (500.0, 260.1)),  # France and Biscay Bay to Iberian Peninsula
        ((544.0, 214.0), (582.0, 204.0)),  # Western Europe Mainland Core to Central Europe Germany and Alps
        ((582.0, 204.0), (564.0, 168.0)),  # Central Europe Germany and Alps to Denmark and Jutland Peninsula
        ((564.0, 168.0), (592.0, 134.0)),  # Denmark and Jutland Peninsula to Sweden and Finland
        ((564.0, 168.0), (558.0, 130.0)),  # Denmark and Jutland Peninsula to Norway Fjord Coast
        ((582.0, 204.0), (614.8, 224.6)),  # Central Europe Germany and Alps to Danube Basin and Romania
        ((582.0, 204.0), (618.0, 178.0)),  # Central Europe Germany and Alps to Poland and Baltic States
        ((614.8, 224.6), (646.6, 209.7)),  # Danube Basin and Romania to Eastern Europe Ukraine Plains
        ((618.0, 178.0), (646.6, 209.7)),  # Poland and Baltic States to Eastern Europe Ukraine Plains

        # --- Africa ---
        ((503.2, 319.7), (540.2, 326.2)),  # Morocco and Atlas to Sahara Core Northwest
        ((540.2, 326.2), (581.0, 326.0)),  # Sahara Core Northwest to Libya and Central Sahara
        ((581.0, 326.0), (622.0, 318.0)),  # Libya and Central Sahara to Egypt and Nile Delta
        ((514.0, 368.0), (558.0, 364.0)),  # Gulf of Guinea Ivory Coast to Nigeria and Sahel
        ((558.0, 364.0), (581.0, 326.0)),  # Nigeria and Sahel to Libya and Central Sahara
        ((558.0, 364.0), (616.0, 362.0)),  # Nigeria and Sahel to Sudan and Nubia Basin
        ((558.0, 364.0), (576.3, 408.3)),  # Nigeria and Sahel to Congo Basin Rainforest
        ((576.3, 408.3), (619.1, 410.0)),  # Congo Basin Rainforest to East Africa Rift and Lakes
        ((576.3, 408.3), (582.0, 456.0)),  # Congo Basin Rainforest to Zambia and Zimbabwe Plateau
        ((582.0, 456.0), (622.0, 460.0)),  # Zambia and Zimbabwe Plateau to Mozambique Channel Coast
        ((582.0, 456.0), (594.0, 512.0)),  # Zambia and Zimbabwe Plateau to South Africa Cape

        # --- Asia ---
        ((671.1, 156.2), (718.5, 142.1)),  # European Russia Core to Ural Mountains and West Siberia
        ((718.5, 142.1), (776.8, 130.8)),  # Ural Mountains and West Siberia to Central Siberia Plateau
        ((776.8, 130.8), (825.0, 142.0)),  # Central Siberia Plateau to Lake Baikal and Sayan Range
        ((825.0, 142.0), (868.0, 130.0)),  # Lake Baikal and Sayan Range to East Siberia and Yakutia
        ((825.0, 142.0), (807.4, 179.3)),  # Lake Baikal and Sayan Range to Mongolia Steppes
        ((718.5, 142.1), (724.0, 198.0)),  # Ural Mountains to Central Asian Steppes
        ((724.0, 198.0), (766.0, 185.0)),  # Central Asian Steppes to Kazakhstan and Altai Steppes
        ((766.0, 185.0), (807.4, 179.3)),  # Kazakhstan and Altai Steppes to Mongolia Steppes
        ((766.0, 185.0), (776.8, 130.8)),  # Kazakhstan and Altai Steppes to Central Siberia Plateau
        ((724.0, 198.0), (752.0, 234.0)),  # Central Asian Steppes to Pamir and Hindu Kush Plateau
        ((752.0, 234.0), (782.0, 264.0)),  # Pamir and Hindu Kush Plateau to Northern India and Himalayas
        ((752.0, 234.0), (745.0, 278.0)),  # Pamir and Hindu Kush Plateau to Pakistan and Indus Basin
        ((712.0, 256.0), (752.0, 234.0)),  # Persian Plateau to Pamir and Hindu Kush Plateau
        ((752.0, 234.0), (816.2, 225.8)),  # Pamir and Hindu Kush Plateau to Tibetan High Plateau
        ((807.4, 179.3), (855.2, 200.7)),  # Mongolia Steppes to North China Core
        ((816.2, 225.8), (855.2, 200.7)),  # Tibetan High Plateau to North China Core
        ((855.2, 200.7), (886.0, 174.0)),  # North China Core to Manchuria and Amur River Basin
        ((855.2, 200.7), (908.0, 209.6)),  # North China Core to Korean Peninsula
        ((855.2, 200.7), (895.3, 240.0)),  # North China Core to East China Coast and Shanghai
        ((855.2, 200.7), (859.6, 251.6)),  # North China Core to South China and Yangtze
        ((859.6, 251.6), (854.0, 298.0)),  # South China and Yangtze to Indochina Peninsula Vietnam/Thailand
        ((782.0, 264.0), (816.0, 288.0)),  # Northern India and Himalayas to Bengal and Ganges Delta
        ((816.0, 288.0), (854.0, 298.0)),  # Bengal and Ganges Delta to Indochina Peninsula Vietnam/Thailand
        ((854.0, 298.0), (846.0, 336.0)),  # Indochina Peninsula Vietnam/Thailand to Malay Peninsula
        ((892.0, 346.0), (854.0, 298.0)),  # Borneo Heart to Indochina Peninsula Vietnam/Thailand
        ((892.0, 346.0), (924.0, 358.0)),  # Borneo Heart to Sulawesi and Moluccas

        # --- Oceania ---
        ((884.0, 456.0), (924.0, 478.0)),  # Western Australia Outback to Central and South Australia
        ((924.0, 432.0), (924.0, 478.0)),  # Northern Territory Australia to Central and South Australia
        ((924.0, 478.0), (966.0, 442.0)),  # Central and South Australia to Queensland and Barrier Reef
        ((924.0, 478.0), (892.0, 497.2)),  # Central and South Australia to Great Australian Bight and Adelaide
        ((924.0, 478.0), (964.0, 488.0)),  # Central and South Australia to New South Wales and Victoria
        ((964.0, 488.0), (959.6, 529.6)),  # New South Wales and Victoria to Tasmania (Bass Strait Bridge)
        ((1018.0, 482.0), (992.2, 507.2)),  # New Zealand North Island to New Zealand South Island

        # --- Antarctica Chain ---
        ((348.9, 581.7), (396.5, 592.3)),  # Ellsworth Land to Antarctic Peninsula Graham Land
        ((396.5, 592.3), (446.0, 602.0)),  # Antarctic Peninsula Graham Land to Weddell Sea Ice Shelf
        ((446.0, 602.0), (516.0, 602.0)),  # Weddell Sea Ice Shelf to Queen Maud Land Shelf
        ((516.0, 602.0), (595.0, 595.0)),  # Queen Maud Land Shelf to Antarctic Polar Dome Hub

        # ==================== INTER-CONTINENTAL BRIDGES ====================
        # 1. North America <-> South America & Caribbean
        ((328.0, 352.0), (354.0, 382.0)),  # Central America Isthmus to Colombia and Northern Andes (Panama Bridge)
        ((382.0, 268.0), (398.0, 304.0)),  # Florida Peninsula to Cuba and Greater Antilles
        ((398.0, 304.0), (424.0, 322.0)),  # Cuba and Greater Antilles to Bahamas and Caribbean Chain

        # 2. Europe <-> Africa
        ((564.0, 260.0), (562.0, 288.0)),  # Italy Boot Peninsula to Sicily and Malta
        ((562.0, 288.0), (581.0, 326.0)),  # Sicily and Malta to Libya and Central Sahara

        # 3. Africa <-> Asia & Middle East
        ((622.0, 318.0), (670.0, 312.0)),  # Egypt and Nile Delta to Arabian Peninsula (Sinai/Red Sea Bridge)
        ((622.0, 318.0), (662.0, 270.0)),  # Egypt and Nile Delta to Levant and Mesopotamia (Suez Bridge)
        ((658.0, 366.0), (670.0, 312.0)),  # Horn of Africa Somalia to Arabian Peninsula (Bab-el-Mandeb Strait Bridge)

        # 4. Europe <-> Asia
        ((602.0, 256.0), (662.0, 270.0)),  # Balkans and Greece to Levant and Mesopotamia (Bosphorus Bridge)
        ((646.6, 209.7), (662.0, 270.0)),  # Eastern Europe Ukraine Plains to Levant and Mesopotamia (Caucasus Bridge)
        ((646.6, 209.7), (671.1, 156.2)),  # Eastern Europe Ukraine Plains to European Russia Core
        ((618.0, 178.0), (671.1, 156.2)),  # Poland and Baltic States to European Russia Core
        ((662.0, 270.0), (712.0, 256.0)),  # Levant and Mesopotamia to Persian Plateau
        ((712.0, 256.0), (745.0, 278.0)),  # Persian Plateau to Pakistan and Indus Basin
        ((745.0, 278.0), (782.0, 264.0)),  # Pakistan and Indus Basin to Northern India and Himalayas

        # 5. Asia <-> Oceania & Australia
        ((846.0, 336.0), (836.0, 372.0)),  # Malay Peninsula to Sumatra Island (Malacca Strait Bridge)
        ((836.0, 372.0), (878.0, 392.0)),  # Sumatra Island to Java Island (Sunda Strait Bridge)
        ((878.0, 392.0), (892.0, 346.0)),  # Java Island to Borneo Heart
        ((924.0, 358.0), (948.0, 386.0)),  # Sulawesi and Moluccas to Papua New Guinea
        ((948.0, 386.0), (924.0, 432.0)),  # Papua New Guinea to Northern Territory Australia (Arafura Sea Bridge)
        ((948.0, 386.0), (996.0, 396.0)),  # Papua New Guinea to Solomon Islands

        # 6. South America <-> Antarctica
        ((379.3, 572.1), (396.5, 592.3)),  # Tierra del Fuego to Antarctic Peninsula Graham Land (Drake Passage Bridge)

        # 7. North America <-> Europe (Stepping Stones)
        ((358.8, 122.9), (424.0, 112.0)),  # Baffin Island to Greenland Isle
        ((494.0, 128.0), (524.0, 166.0)),  # Iceland to Great Britain
    ]

def world_svg(t):
    ecx, ecy, erx, ery = 600, 345, 540, 305
    o = map_header(t["world_aria"])
    o += [
        "<!-- Lagoon Shallows -->",
        f'<ellipse cx="{ecx}" cy="{ecy}" rx="{erx}" ry="{ery}" fill="url(#lagoon-glow)" />',
        "<!-- Wave Break Line -->",
        f'<ellipse cx="{ecx}" cy="{ecy}" rx="{erx + 25}" ry="{ery + 23}" fill="none" stroke="rgba(255,255,255,0.14)" stroke-dasharray="6 8" />',
    ]

    # Oval flood defense breakwater (4 storm gates: N, S, E, W)
    arcs = []
    gap = 5
    for start in (0, 90, 180, 270):
        a = math.radians(start + gap)
        b = math.radians(start + 90 - gap)
        pa = (ecx + erx * math.cos(a), ecy + ery * math.sin(a))
        pb = (ecx + erx * math.cos(b), ecy + ery * math.sin(b))
        arcs.append(f"M{pt(pa)} A{erx},{ery} 0 0 1 {pt(pb)}")
    ring = " ".join(arcs)
    o += [
        "<!-- Outer Oval Flood Defense Breakwater (4 Storm Gates: N, S, E, W) -->",
        f'<path d="{ring}" fill="none" stroke="#2ba29e" stroke-width="26" stroke-linecap="round" opacity="0.45" />',
        f'<path class="map-frond-edge" d="{ring}" stroke-width="15" />',
        f'<path class="map-frond" d="{ring}" stroke-width="12.5" />',
    ]

    # Gate beacons
    o.append('<g class="twinkle">')
    for start in (0, 90, 180, 270):
        for s, col in ((-1, "#ef4444"), (1, "#22c55e")):
            a = math.radians(start + s * gap)
            o.append(f'<circle cx="{n(ecx + erx * math.cos(a))}" cy="{n(ecy + ery * math.sin(a))}" r="3.5" fill="{col}" />')
    o.append("</g>")

    # MULTIPLE ISLANDS
    o.append("<!-- RECOGNIZABLE WORLD CONTINENTS (VARIED SHAPES, ZERO OVERLAPS) -->")
    o.append('<g id="world-islands-group">')
    for i, isle in enumerate(WORLD_ISLES):
        cls = "map-sand-light" if isle.get("sand_light") else "map-sand"
        shape = isle.get("shape", "organic")
        d = smooth_island(isle["cx"], isle["cy"], isle["rx"], isle["ry"], rot=isle.get("rot", 0), seed=i + 1, shape=shape)
        o.append(f'<!-- {isle["name"]} -->')
        o.append(f'<path class="{cls}" d="{d}" />')
        if isle.get("green"):
            d_grn = smooth_island(isle["cx"], isle["cy"], isle["rx"] * 0.65, isle["ry"] * 0.65, rot=isle.get("rot", 0), seed=i + 10, shape=shape)
            o.append(f'<path class="map-greenery" d="{d_grn}" />')
    o.append("</g>")

    # Hub architectures on main continental islands
    us_hub = (331.1, 213.7)
    eu_hub = (544.0, 214.0)
    asia_hub = (855.2, 200.7)
    oc_hub = (924.0, 478.0)
    an_hub = (595.0, 595.0)

    o += [
        "<!-- Continental Hub Pavilions and Features -->",
        f'<rect x="{us_hub[0] - 16}" y="{us_hub[1] - 9}" width="32" height="18" rx="3" class="map-urban" />',
        f'<rect x="{eu_hub[0] - 14}" y="{eu_hub[1] - 8}" width="28" height="16" rx="3" class="map-urban" />',
        f'<rect x="{asia_hub[0] - 18}" y="{asia_hub[1] - 9}" width="36" height="18" rx="3" class="map-urban" />',
        f'<ellipse cx="{an_hub[0]}" cy="{an_hub[1]}" rx="24" ry="9" fill="#38bdf8" stroke="#ffffff" stroke-width="1.6" opacity="0.85" />',
    ]

    o.append("<!-- Inter-Island Arched Footbridges -->")
    o.append('<g stroke="#ffffff" stroke-width="2.2" stroke-linecap="round">')
    for b1, b2 in bridges:
        o.append(f'<line x1="{b1[0]}" y1="{b1[1]}" x2="{b2[0]}" y2="{b2[1]}" />')
    o.append("</g>")

    # Continental Cable Car
    tele_path = [us_hub, eu_hub]
    o += [
        "<!-- Continental Cable Car) -->",
        f'<path class="map-cableway" d="{poly_path(tele_path, close=False)}" />',
    ]
    for p in tele_path:
        o.append(f'<circle cx="{n(p[0])}" cy="{n(p[1])}" r="5" fill="#f43f5e" stroke="#ffffff" stroke-width="1.8" />')

    # Submerged suites in coral lagoon
    sub_suites = (695, 405)
    o += ["<!-- Submerged Reef Observation Suites -->"]
    for ddx, ddy in ((-12, -10), (14, 12)):
        o += [
            f'<g transform="translate({sub_suites[0] + ddx}, {sub_suites[1] + ddy})">',
            '<circle cx="0" cy="0" r="7" fill="#0284c7" stroke="#38bdf8" stroke-width="2" />',
            '<circle cx="0" cy="0" r="2.6" fill="#ffffff" class="twinkle" />',
            "</g>",
        ]

    # Geographic Map Labels
    o += [
        "<!-- Geographic Map Labels -->",
        '<g class="map-label-group">',
        f'<text class="map-label-text" x="600" y="690">{t["perimeter"]}</text>',
        f'<text class="map-label-text" x="130" y="328">{t["west_gate"]}</text>',
        f'<text class="map-label-text" x="1060" y="328">{t["east_gate"]}</text>',
        "</g>",
    ]

    # 8 Interactive Hotspots
    tele_mid = ((eu_hub[0] + asia_hub[0]) / 2, (eu_hub[1] + asia_hub[1]) / 2)
    spots = [
        (1, us_hub[0], us_hub[1], "#f43f5e", "NA Casino and Theme Park"),
        (2, eu_hub[0], eu_hub[1], "#c29a57", "European Summit and Diplomatic Pavilions"),
        (3, asia_hub[0], asia_hub[1], "#38bdf8", "Asian Innovation Hub"),
        (4, tele_mid[0], tele_mid[1], "#f43f5e", "Continental Teleferic"),
        (5, sub_suites[0], sub_suites[1], "#0284c7", "Submerged Reef Suites"),
        (6, an_hub[0], an_hub[1], "#38bdf8", "Antarctic Climate Dome"),
        (7, oc_hub[0], oc_hub[1], "#22c55e", "Oceania Dolphin Sanctuary"),
        (8, ecx, ecy - ery, "#2ba29e", "Flood Barrier Storm Gates"),
    ]
    o.append("<!-- INTERACTIVE HOTSPOT PINS -->")
    for i, x, y, col, name in spots:
        o.append(f"<!-- Hotspot {i}: {name} -->")
        o += hotspot(i, x, y, col)
    o.append("</svg>")
    return o


def main():
    update_island_map(1, world_svg)


if __name__ == "__main__":
    main()
